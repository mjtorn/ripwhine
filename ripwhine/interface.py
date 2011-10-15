# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

from ripwhine import actions, processes

import multiprocessing

import logging

import os

logger = multiprocessing.get_logger()
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())

DEFAULT_DIR = '/tmp/'

class Interface(object):
    """Handles interfacing with the user
    """

    def __init__(self):
        """Set the menu items and actions
        """

        self.destination_dir = DEFAULT_DIR

        # Some of these are for testing
        self.items = [
            ['d', 'dir [%s]' % self.destination_dir],
            ('i', 'identify'),
            ('r', 'rip'),
            ('s', 'sleep'),
            ('q', 'exit'),
        ]

        self.actions = (
            ('d', actions.change_dir),
            ('i', actions.identify),
            ('r', actions.start_rip),
            ('s', actions.sleep_process),
            ('q', lambda interface: False),
        )

        # Set up communications
        self.queue_to_rip, self.queue_to_rip_interface = multiprocessing.Pipe()
        self.queue_to_encode, self.queue_to_encode_interface = multiprocessing.Pipe()
        self.queue_to_identify, self.queue_to_identify_interface = multiprocessing.Pipe()

        # Our current disc
        self.track_tuples = None

    def print_menu(self):
        """Present the options to the user
        """

        if self.track_tuples:
            artist, year, disc = self.track_tuples[0][:3]
            heading = '%s - %s (%s)' % (artist, disc, year)

            print heading

            for track in self.track_tuples:
                print ' * %s. %s' % (track[3], track[4])
        else:
            print '*** NO DISC ***'

        print

        for item in self.items:
            print '%s. %s' % (item[0], item[1])

    def handle_input(self):
        """Read user input, validate, execute. Return True if more loops required
        """

        action = raw_input('>>> ')

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

        in_loop = True
        while in_loop:
            self.print_menu()
            in_loop = self.handle_input()

            ## DEBUG
            if self.queue_to_rip.poll():
                logger.info('Received from ripper: %s' % self.queue_to_rip.recv())
            if self.queue_to_encode.poll():
                logger.info('Received from encoder: %s' % self.queue_to_encode.recv())
            if self.queue_to_identify.poll():
                from_identify = self.queue_to_identify.recv()
                logger.info('Received from identify: %s' % from_identify)

                if from_identify == 'FINISHED_IDENTIFY':
                    self.track_tuples = self.queue_to_identify.recv()
                    if not isinstance(self.track_tuples, list):
                        logger.error('Invalid return value type from identify!')
                        logger.error('%s' % self.track_tuples)

                        self.track_tuples = None

        self.rip_process.terminate()
        self.encode_process.terminate()
        self.identify_process.terminate()

# EOF

