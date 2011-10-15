# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

import logging

import multiprocessing

import os

import subprocess

import sys

import traceback

logger = multiprocessing.get_logger()
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())

ENCODE_CMD = ['flac', '--best', '-o']

class Encode(object):
    """Process persisting to do encodes on command
    """

    def __init__(self, interface):
        """Set interface in self so it can be used later
        """

        self.interface = interface

        self.actions = (
            ('START_ENCODE', self.start_encode),
        )

        # Pull this from the ripper
        self.path_to_disc = None

    def __call__(self):
        """Make this look like a function
        """

        logger.info('Encoder process started')
        while True:
            command = self.interface.queue_to_encode_interface.recv()
            logger.info('Encoder received: %s' % command)

            if dict(self.actions).has_key(command):
                try:
                    dict(self.actions)[command]()
                except Exception, e:
                    logger.error('[FAIL] %s' % e)
                    logger.error(''.join(traceback.format_exception(*sys.exc_info())))

    def encode_track(self, track_data):
        """Encode one track
        """

        ## Num and name
        filename = '%s. %s' % track_data

        wav_source = os.path.join(self.path_to_disc, '%s.wav' % filename)
        flac_destination = os.path.join(self.path_to_disc, '%s.flac' % filename)

        cmd = ENCODE_CMD[:]
        cmd.append(flac_destination)
        cmd.append(wav_source)

        retval = subprocess.call(cmd)
        if retval:
            logger.error('[FAIL] Command died on status %s' % retval)
            self.interface.queue_to_rip_interface.send('FAILED_RIP')
        else:
            os.unlink(wav_source)

        return retval

    def start_encode(self):
        """Drrn drrn
        """

        ## Because we wait on subprocess.call(), no need to verify states
        subprocess.call(ENCODE_CMD.split())
        logger.info('Finished encode')

        self.interface.queue_to_encode_interface.send('FINISHED_ENCODE')

def start_encode_process(interface):
    encode = Encode(interface)

    p = multiprocessing.Process(target=encode, name='Encode')
    p.start()

    return p

# EOF

