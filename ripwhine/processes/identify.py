# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

import logging

import multiprocessing

import musicbrainz2.disc as mbdisc
import musicbrainz2.webservice as mbws

import subprocess

import sys

import traceback

logger = multiprocessing.get_logger()
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())

## MusicBrainz needs some setting up
service = mbws.WebService()
query = mbws.Query(service)

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

        try:
            disc = mbdisc.readDisc()
        except mbdisc.DiscError, e:
            logger.error('[FAIL] %s' % e)
            self.interface.queue_to_identify_interface.send('FAILED_IDENTIFY')

            return

        disc_id = disc.getId()
        disc_uuid = disc.getId()

        logger.info('[SUCCESS] Identified disc as: %s' % disc_id)

        try:
            release_filter = mbws.ReleaseFilter(discId=disc_id)
            releases = query.getReleases(release_filter)
        except mbws.WebServiceError, e:
            logger.error('[FAIL] %s' % e)
            self.interface.queue_to_identify_interface.send('FAILED_IDENTIFY')

            return

        logger.info('[SUCCESS] Got %d releases' % len(releases))

        if len(releases) == 0:
            self.interface.queue_to_identify_interface.send('NO_DATA')

            return
        elif len(releases) > 1:
            logger.warn('[DISC] Got %d releases, running with the first one!' % len(releases))

        ## Use the first release
        release = releases[0].release

        ## Need to get additional data separately
        try:
            # releaseEvents required to get year
            release_includes = mbws.ReleaseIncludes(artist=True, tracks=True, releaseEvents=True)

            release = query.getReleaseById(release.getId(), release_includes)
        except mbws.WebServiceError, e:
            logger.error('[FAIL] %s' % e)
            self.interface.queue_to_identify_interface.send('FAILED_IDENTIFY')

            return

        ## Unlike the mb example code, disregard different track artists
        track_num = 1
        track_tuples = []
        for track in release.tracks:
            formatted_track_num = '%02d' % track_num

            year = release.getEarliestReleaseDate()
            year = year.split('-')[0] # disregard the exact date

            track_tuple = (release.artist.name, year, release.title, formatted_track_num, track.title)

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

