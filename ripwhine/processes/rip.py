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

RIP_CMD = ['cdparanoia', '-X']

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

        ## Set when ripping, through verifying the path is ok
        self.path_to_disc = None

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

    def check_destination(self, track_tuples):
        """Make sure we know where the music goes
        """

        disc_id, artist, year, disc = track_tuples[0][:4]
        year_disc = '%s - %s' % (year, disc)

        path_to_artist = os.path.join(self.interface.destination_dir, artist)
        path_to_disc = os.path.join(path_to_artist, year_disc)
        symlink_to_disc = os.path.join(path_to_artist, disc)

        if not os.path.exists(path_to_artist):
            os.mkdir(path_to_artist)
            logger.info('Created %s' % path_to_artist)

        ## Maybe I could clean up half-rips but do not care
        if not os.path.exists(path_to_disc):
            os.mkdir(path_to_disc)
            os.symlink(path_to_disc, symlink_to_disc)
            logger.info('Created %s' % path_to_disc)

        ## Create a file with the mbid used
        f = open(os.path.join(path_to_disc, 'musicbrainz.id'), 'wb')
        f.write('%s\n' % disc_id)
        f.close()

        self.path_to_disc = path_to_disc

    def rip_track(self, track_data):
        """Rip one track
        """

        ## Num and name
        filename = '%s. %s.wav' % track_data

        wav_destination = os.path.join(self.path_to_disc, filename)

        cmd = RIP_CMD[:]
        cmd.append(track_data[0])
        cmd.append(wav_destination)

        retval = subprocess.call(cmd)

        return retval

    def start_rip(self):
        """Drrn drrn
        """

        ## Snatch what to rip
        track_tuples = self.interface.queue_to_rip_interface.recv()
        if not isinstance(track_tuples, tuple):
            logger.error('Something wicked this way came: %s' % str(track_tuples))

            self.interface.queue_to_rip_interface.send('FAILED_RIP')
            return

        ## Is the destination safe?
        try:
            self.check_destination(track_tuples)
        except IOError, e:
            logger.error('[FAIL] %s' % e)
            self.interface.queue_to_rip_interface.send('FAILED_RIP')
            return

        ## Because we wait on subprocess.call(), no need to verify states
        for track in track_tuples:
            track_num = track[4]
            track_name = track[5]
            on_disc = track[6]
            if not on_disc:
                logger.warn('[IGNORE] Not on disc: %s' % track_name)
                continue

            retval = self.rip_track(track[-3:-1])
            if retval:
                logger.error('[FAIL] Command died on status %s' % retval)
                self.interface.queue_to_rip_interface.send('FAILED_RIP')
                return
                
            logger.info('[SUCCESS] %s. %s' % track[-2:])

            self.interface.queue_to_encode.send('START_ENCODE')
            self.interface.queue_to_encode.send((self.path_to_disc, (track_num, track_name)))

        self.interface.queue_to_rip_interface.send('FINISHED_RIP')

def start_rip_process(interface):
    rip = Rip(interface)

    p = multiprocessing.Process(target=rip, name='Rip')
    p.start()

    return p

# EOF

