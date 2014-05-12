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
            logger.info('Encoder received: %s' % str(command))

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
        filename = u'%s. %s' % track_data
        filename = filename.replace('/', '-')
        filename = filename.encode('utf-8')

        bkp_filename = filename

        logger.info('[ENC NAME] File name %d bytes: %s' % (len(filename), filename))

        ## Potential mangling required
        # fs limit is 256
        if len(filename) > 251:
            logger.warn('[WAV NAME] Long file name %d bytes' % len(filename))
            filename = filename[:251]

            wav_source = os.path.join(self.path_to_disc, filename)
        else:
            wav_source = os.path.join(self.path_to_disc, '%s.wav' % filename)

        # Reset filename for flac handling, in case it was mangled for wav
        filename = bkp_filename

        # fs limit is 256, 5 bytes for '.flac'
        if len(filename) > 251:
            logger.warn('[FLAC NAME] Long file name %d bytes' % len(filename))
            filename = filename[:251]

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

        path_to_disc, track_data = self.interface.queue_to_encode_interface.recv()
        if not isinstance(track_data, tuple):
            logger.error('Invalid data received, can not encode %s' % str(track_data))
            self.interface.queue_to_encode_interface.send('FAILED_ENCODE')

            return

        self.path_to_disc = path_to_disc

        retval = self.encode_track(track_data)
        if not retval:
            logger.info('[SUCCESS] %s. %s' % track_data)

        self.interface.queue_to_encode_interface.send('FINISHED_ENCODE')

def start_encode_process(interface):
    encode = Encode(interface)

    p = multiprocessing.Process(target=encode, name='Encode')
    p.start()

    return p

# EOF

