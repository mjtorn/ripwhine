# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

from .. import __version__
## Large tuples are terrible to deal with
from collections import namedtuple

import logging
import multiprocessing
import musicbrainz2.disc as mbdisc
import musicbrainzngs
import sys
import traceback

logger = multiprocessing.get_logger()
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())

## MusicBrainz needs some setting up
musicbrainzngs.set_useragent('Ripwhine', __version__, 'https://github.com/mjtorn/ripwhine/')

## Maybe this should be a configurable
DEVICE = '/dev/cdrom'

TrackTuple = namedtuple(
    'TrackTuple',
    'disc_id release_id artist year title formatted_track_num track_title disc_num disc_count media_name')


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

            if command in dict(self.actions):
                try:
                    dict(self.actions)[command]()
                except Exception as e:
                    logger.error('[FAIL] %s' % e)
                    logger.error(''.join(traceback.format_exception(*sys.exc_info())))

    def identify(self):
        """Drrn drrn
        """

        ## XXX: Do we really need the old library for this?
        try:
            disc = mbdisc.readDisc(deviceName=DEVICE)
        except mbdisc.DiscError as e:
            logger.error('[FAIL] %s' % e)
            logger.error(''.join(traceback.format_exception(*sys.exc_info())))
            self.interface.queue_to_identify_interface.send('FAILED_IDENTIFY')

            return

        disc_id = disc.getId()
        submission_url = mbdisc.getSubmissionUrl(disc)
        logger.info('[URL] %s' % submission_url)

        logger.info('[SUCCESS] Identified disc as: %s' % disc_id)

        ## XXX: The library doesn't understand a tuple here
        includes = ['artist-credits', 'labels', 'release-rels', 'recordings']
        try:
            data = musicbrainzngs.get_releases_by_discid(disc_id, includes=includes)
        except musicbrainzngs.ResponseError as e:
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
        except Exception as e:
            logger.error('[FAIL] %s' % e)
            logger.error(''.join(traceback.format_exception(*sys.exc_info())))
            self.interface.queue_to_identify_interface.send('FAILED_IDENTIFY')

            return
        else:
            if not data:
                logger.error('[FAIL] No data returned. Check submission url')
                return

        try:
            releases = data['disc']['release-list']
        except KeyError:
            if 'cdstub' in data:
                logger.warn('[DISC] This release is only a stub, fill it in at MusicBrainz')
                self.interface.queue_to_identify_interface.send('NO_DATA')
                return

        # Make the chance slimmer that selecting a release breaks if mb sends results in odd orders
        releases.sort()

        logger.info('[SUCCESS] Got %d releases' % len(releases))

        if len(releases) == 0:
            self.interface.queue_to_identify_interface.send('NO_DATA')

            self.interface.queue_to_identify_interface.send(submission_url)

            return
        elif len(releases) > 1:
            self.interface.queue_to_identify_interface.send('MULTIPLE_RELEASES')
            self.interface.queue_to_identify_interface.send(releases)

            rel_num = self.interface.queue_to_identify_interface.recv()
        else:
            rel_num = 0

        ## Which release do we want?
        release = releases[rel_num]

        ## Disc title
        title = release['title'].encode('utf-8')
        disambiguation = release.get('disambiguation', None)
        is_remaster = False
        for rel_release in release.get('release-relation-list', ()):
            if rel_release.get('type', None) == 'remaster':
                is_remaster = True
                break

        extra_str = ''
        if disambiguation:
            extra_str = '%s' % disambiguation
        if is_remaster:
            extra_str = '%s remaster' % extra_str

        extra_str = extra_str.strip()

        if extra_str:
            title = '%s (%s)' % (title, extra_str)

        ## Require release date
        date = release['date']
        if not date:
            self.interface.queue_to_identify_interface.send('NO_DATE')

            return

        year = date.split('-', 1)[0]

        ## 0th artist...
        if len(release['artist-credit']) > 1:
            self.interface.queue_to_identify_interface.send('TOO_MANY_ARTISTS')

            return

        artist_sort_name = release['artist-credit'][0]['artist']['sort-name']
        artist_sort_name = artist_sort_name.encode('utf-8')

        ## Media count and name
        disc_num = 1
        if 'medium-count' not in release:
            disc_count = len(release['medium-list'])
        else:
            disc_count = release['medium-count']

        medium_n = 0
        media_name = None
        if disc_count > 1:
            for medium_n, medium in enumerate(release['medium-list']):
                if 'title' in medium:
                    media_name = medium['title']
                else:
                    media_name = None
                if disc_id in [d['id'] for d in medium['disc-list']]:
                    disc_num = medium_n + 1
                    break

        # Pass the media_name along if required, otherwise it's None
        if media_name is not None and media_name == title:
            media_name = None

        ## Unlike the mb example code, disregard different track artists
        track_tuples = []
        for track in release['medium-list'][medium_n]['track-list']:
            formatted_track_num = '%02d' % int(track['number'])

            track_title = track['recording']['title'].encode('utf-8')
            track_tuple = TrackTuple(
                disc_id=disc_id,
                release_id=release['id'],
                artist=artist_sort_name,
                year=year,
                title=title,
                formatted_track_num=formatted_track_num,
                track_title=track_title,
                disc_num=disc_num,
                disc_count=disc_count,
                media_name=media_name)

            track_tuples.append(track_tuple)

        self.interface.queue_to_identify_interface.send('FINISHED_IDENTIFY')
        self.interface.queue_to_identify_interface.send(tuple(track_tuples))


def start_identify_process(interface):
    identify = Identify(interface)

    p = multiprocessing.Process(target=identify, name='Identify')
    p.start()

    return p

# EOF
