# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

import logging

import multiprocessing

logger = multiprocessing.get_logger()
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())

import subprocess

## FIXME: replace with real ripping cmd ;)
RIP_CMD = 'sleep 3'

class Rip(object):
    """Process persisting to do rips on command
    """

    def __init__(self, interface):
        """Set interface in self so it can be used later
        """

        self.interface = interface

        self.actions = (
            ('START_RIP', self.start_rip),
        )

    def __call__(self):
        """Make this look like a function
        """

        logger.info('Ripper process started')
        while True:
            command = self.interface.queue_to_rip_interface.recv()
            logger.info('Ripper received: %s' % command)

            if dict(self.actions).has_key(command):
                dict(self.actions)[command]()

    def start_rip(self):
        """Drrn drrn
        """

        ## Because we wait on subprocess.call(), no need to verify states
        subprocess.call(RIP_CMD.split())
        logger.info('Finished rip')

        self.interface.queue_to_rip_interface.send('FINISHED_RIP')

def start_rip_process(interface):
    rip = Rip(interface)

    p = multiprocessing.Process(target=rip, name='Rip')
    p.start()

    return p

# EOF

