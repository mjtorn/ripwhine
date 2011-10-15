# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

import logging

import multiprocessing

logger = multiprocessing.get_logger()
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())

import subprocess

import sys

import traceback

## FIXME: replace with real ripping cmd ;)
RIP_CMD = 'sleep 0.1'

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
            logger.info('Ripper received: %s' % str(command))

            if dict(self.actions).has_key(command):
                try:
                    dict(self.actions)[command]()
                except Exception, e:
                    logger.error('[FAIL] %s' % e)
                    logger.error(''.join(traceback.format_exception(*sys.exc_info())))

    def start_rip(self):
        """Drrn drrn
        """

        ## Snatch what to rip
        track_tuples = self.interface.queue_to_rip_interface.recv()
        if not isinstance(track_tuples, tuple):
            logger.error('Something wicked this way came: %s' % str(track_tuples))

            self.interface.queue_to_rip_interface.send('FAILED_RIP')
            return

        ## Because we wait on subprocess.call(), no need to verify states
        for track in track_tuples:
            subprocess.call(RIP_CMD.split())
            logger.info('[SUCCESS] %s. %s' % track[-2:])

        self.interface.queue_to_rip_interface.send('FINISHED_RIP')
        self.interface.queue_to_encode.send('START_ENCODE')

def start_rip_process(interface):
    rip = Rip(interface)

    p = multiprocessing.Process(target=rip, name='Rip')
    p.start()

    return p

# EOF

