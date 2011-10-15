# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

from ripwhine import actions, processes

import multiprocessing

import logging

logger = multiprocessing.get_logger()
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())

class Interface(object):
    """Handles interfacing with the user
    """

    def __init__(self):
        """Set the menu items and actions
        """

        # Some of these are for testing
        self.items = (
            ('i', 'identify'),
            ('r', 'rip'),
            ('s', 'sleep'),
            ('q', 'exit'),
        )

        self.actions = (
            ('i', actions.identify),
            ('r', actions.start_rip),
            ('s', actions.sleep_process),
            ('q', lambda interface: False),
        )

        # Set up communications
        self.queue_to_rip, self.queue_to_rip_interface = multiprocessing.Pipe()
        self.queue_to_encode, self.queue_to_encode_interface = multiprocessing.Pipe()
        self.queue_to_identify, self.queue_to_identify_interface = multiprocessing.Pipe()

    def print_menu(self):
        """Present the options to the user
        """

        for item in self.items:
            print '%s. %s' % item

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

        self.rip_process.terminate()
        self.encode_process.terminate()
        self.identify_process.terminate()

# EOF

