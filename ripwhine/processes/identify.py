# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

import musicbrainz2.disc as mbdisc

import logging

import multiprocessing

import musicbrainzngs

import subprocess

import sys

import traceback

from .. import __version__

logger = multiprocessing.get_logger()
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())

## MusicBrainz needs some setting up
musicbrainzngs.set_useragent('Ripwhine', __version__, 'https://github.com/mjtorn/ripwhine/')

class Identify(object):
    """Process persisting to do identifys on command
    """

    def __init__(self, interface):
        """Set interface in self so it can be used later
        """

        self.interface = interface

        self.actions = (
            ('IDENTIFY', self.identify),
        )

    def __call__(self):
        """Make this look like a function
        """

        logger.info('Identify process started')
        while True:
            command = self.interface.queue_to_identify_interface.recv()
            logger.info('Identify received: %s' % command)

            if dict(self.actions).has_key(command):
                try:
                    dict(self.actions)[command]()
                except Exception, e:
                    logger.error('[FAIL] %s' % e)
                    logger.error(''.join(traceback.format_exception(*sys.exc_info())))

    def identify(self):
        """Drrn drrn
        """

        ## XXX: Do we really need the old library for this?
        try:
            disc = mbdisc.readDisc(deviceName='/dev/sr0')
        except mbdisc.DiscError, e:
            logger.error('[FAIL] %s' % e)
            logger.error(''.join(traceback.format_exception(*sys.exc_info())))
            self.interface.queue_to_identify_interface.send('FAILED_IDENTIFY')

            return

        disc_id = disc.getId()
        submission_url = mbdisc.getSubmissionUrl(disc)

        logger.info('[SUCCESS] Identified disc as: %s' % disc_id)

        ## XXX: The library doesn't understand a tuple here
        includes = ['artist-credits', 'release-rels', 'recordings']
        try:
            data = musicbrainzngs.get_releases_by_discid(disc_id, includes=includes)
        except musicbrainzngs.ResponseError, e:
            ## Fake response to make flow easier
            if e.cause.code == 404:
                data = {
                    'disc': {
                        'id': disc_id,
                        'release-list': []
                    }
                }
            else:
                raise
        except Exception, e:
            logger.error('[FAIL] %s' % e)
            logger.error(''.join(traceback.format_exception(*sys.exc_info())))
            self.interface.queue_to_identify_interface.send('FAILED_IDENTIFY')

            return

        releases = data['disc']['release-list']

        logger.info('[SUCCESS] Got %d releases' % len(releases))

        if len(releases) == 0:
            self.interface.queue_to_identify_interface.send('NO_DATA')

            self.interface.queue_to_identify_interface.send(submission_url)

            return
        elif len(releases) > 1:
            logger.warn('[DISC] Got %d releases, running with the first one!' % len(releases))

        ## XXX Use the first release now, need to prompt in the future
        release = releases[0]

        logger.info('[URL] %s' % submission_url)

        ## release.tracks contains tracks not on this actual disc, cope
        disc_tracks = disc.getTracks()

        ## Unlike the mb example code, disregard different track artists
        track_num = 1
        track_tuples = []
        for track in release.tracks:
            ## XXX TODO FIXME Just do it, gonna use NGS for disc stuff anyway in the future
            on_disc = True
            for disc_track in disc_tracks:
                dt_offset, dt_length = disc_track
                # The ratio is somewhat precisely 1.0 / 75 * 1000 == 13.333
                dt_len_seconds = dt_length * 1000 / 75
                if dt_len_seconds == track.duration:
                    on_disc = True
                    break

            formatted_track_num = '%02d' % track_num

            year = release.getEarliestReleaseDate()
            year = year.split('-')[0] # disregard the exact date

            title = release.title
            #if is_remaster:
            #    title = '%s (remaster)' % title
            track_tuple = (disc_id, release.artist.sortName, year, title, formatted_track_num, track.title, on_disc)

            track_num += 1

            track_tuples.append(track_tuple)

        self.interface.queue_to_identify_interface.send('FINISHED_IDENTIFY')
        self.interface.queue_to_identify_interface.send(tuple(track_tuples))

def start_identify_process(interface):
    identify = Identify(interface)

    p = multiprocessing.Process(target=identify, name='Identify')
    p.start()

    return p

# EOF

