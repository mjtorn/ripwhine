# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

from ripwhine import actions, processes

import multiprocessing

import logging

import os

import select

import sys

import termios

import tty

logger = multiprocessing.get_logger()
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())

DEFAULT_DIR = os.path.join(os.path.expanduser('~'), 'music')

class Interface(object):
    """Handles interfacing with the user
    """

    def __init__(self):
        """Set the menu items and actions
        """

        self.destination_dir = DEFAULT_DIR

        self.fail = True
        self.ejected = False

        if not os.path.exists(self.destination_dir):
            os.mkdir(self.destination_dir)

        # Some of these are for testing
        self.items = [
            ['d', 'dir [%s]' % self.destination_dir],
            ('i', 'identify'),
            ('r', 'rip'),
            ('e', 'eject'),
            ('f', 'toggle fail'),
            ('p', 'print menu'),
            ('s', 'sleep'),
            ('q', 'exit'),
        ]

        self.actions = (
            ('d', actions.change_dir),
            ('i', actions.identify),
            ('r', actions.start_rip),
            ('e', actions.eject),
            ('f', self.toggle_fail),
            ('p', self.print_menu),
            ('s', actions.sleep_process),
            ('q', lambda interface: False),
        )

        # Set up communications
        self.queue_to_rip, self.queue_to_rip_interface = multiprocessing.Pipe()
        self.queue_to_encode, self.queue_to_encode_interface = multiprocessing.Pipe()
        self.queue_to_identify, self.queue_to_identify_interface = multiprocessing.Pipe()

        # Our current disc
        self.track_tuples = None

        # submission url or anything else
        self.info_text = None

    @staticmethod
    def toggle_fail(self):
        """Toggle wether or not cdparanoia fails on a bad rip
        """

        self.fail = not self.fail

    @staticmethod
    def print_menu(self):
        """Present the options to the user
        """

        fail_str = 'Will %sfail cdparanoia on bad rip'

        if self.fail:
            print fail_str % ''
        else:
            print fail_str % 'not '

        if self.track_tuples:
            # Use the first one for disc info
            track_tuple = self.track_tuples[0]

            if track_tuple.disc_count > 9:
                disc = '%s (%02d/%02d)' % (track_tuple.title, track_tuple.disc_num, track_tuple.disc_count)
            elif track_tuple.disc_count > 1:
                disc = '%s (%d/%d)' % (track_tuple.title, track_tuple.disc_num, track_tuple.disc_count)
            else:
                disc = track_tuple.title

            if track_tuple.media_name is not None:
                disc = '%s %s' % (disc, track_tuple.media_name)

            heading = '%s: %s - %s (%s)' % (track_tuple.disc_id, track_tuple.artist, disc, track_tuple.year)

            print heading
        else:
            print '*** NO DISC ***'
            print self.info_text
            print '***************'

        print

        for item in self.items:
            print '%s. %s' % (item[0], item[1])

    def handle_input(self, poll):
        """Read user input, validate, execute. Return True if more loops required
        """

        print '>>> '
        poll.poll()
        action = sys.stdin.read(1)

        if action.isdigit():
            action = int(action)

        ## Call our action, giving ourself as interface argument
        if dict(self.items).has_key(action):
            retval = dict(self.actions)[action](self)
            if retval is not None:
                return retval

        return True

    def run(self):
        """Work-horse, nay, pwny
        """

        # Start the processes
        self.rip_process = processes.start_rip_process(self)
        self.encode_process = processes.start_encode_process(self)
        self.identify_process = processes.start_identify_process(self)

        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            poll = select.poll()
            poll.register(sys.stdin, select.POLLIN)

            in_loop = True
            while in_loop:
                self.print_menu(self)
                in_loop = self.handle_input(poll)

                if self.queue_to_rip.poll():
                    logger.info('Received from ripper: %s' % self.queue_to_rip.recv())
                if self.queue_to_encode.poll():
                    logger.info('Received from encoder: %s' % self.queue_to_encode.recv())
                if self.queue_to_identify.poll():
                    from_identify = self.queue_to_identify.recv()
                    logger.info('Received from identify: %s' % from_identify)

                    ## Store our tracks so rip and encode can use them
                    if from_identify == 'FINISHED_IDENTIFY':
                        self.track_tuples = self.queue_to_identify.recv()

                        if not isinstance(self.track_tuples, tuple):
                            logger.error('Invalid return value type from identify!')
                            logger.error('%s' % str(self.track_tuples))

                            self.track_tuples = None
                        else:
                            self.info_text = None
                    elif from_identify == 'NO_DATA':
                        self.track_tuples = None
                        submission_url = self.queue_to_identify.recv()
                        self.info_text = submission_url
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

        self.rip_process.terminate()
        self.encode_process.terminate()
        self.identify_process.terminate()

# EOF

