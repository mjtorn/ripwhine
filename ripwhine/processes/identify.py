# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

from ripwhine.cdrom import cddbid

import logging

import multiprocessing

logger = multiprocessing.get_logger()
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())

import subprocess

IDENTIFY_CMD = 'cdparanoia -Q'

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
                dict(self.actions)[command]()

    @classmethod
    def parse_cdparanoia(self, output):
        output = output.strip()
        lines = []
        in_tracks = False
        for line in output.splitlines():
            if in_tracks:
                lines.append(line)

            if line.startswith('='):
                in_tracks = True
            elif line.startswith('TOTAL'):
                break

        sectors = []
        for line in lines:
            split_line = line.split()
            if len(split_line) == 8:
                track_num, sector_end, time_end, sector_start, time_start, copy, pre, ch = split_line
            else:
                sector_start = split_line[1]

            sector_start = int(sector_start)

            ## Some googling says we need to add 150, but adding
            ## nothing yields the same id. Unintelligible.
            # --toc-offset does not fix beginning, so add manually
            #sectors.append(sector_start + 150)

            ## Add the sectors as-is to be safe
            sectors.append(sector_start)

        return sectors

    def identify(self):
        """Drrn drrn
        """

        ## cdparanoia talks to stderr
        output = subprocess.Popen(IDENTIFY_CMD.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if output.returncode:
            logger.error('[FAIL] (%d) %s' % (output.returncode, IDENTIFY_CMD))
            self.interface.queue_to_identify_interface.send('FAILED_IDENTIFY')

            return

        sectors = self.parse_cdparanoia(output.stderr.read())

        disc_id, disc_len = cddbid.discid(sectors)

        logger.info('[SUCCESS] Identified disc as: %s' % disc_id)

        self.interface.queue_to_identify_interface.send('FINISHED_IDENTIFY')

def start_identify_process(interface):
    identify = Identify(interface)

    p = multiprocessing.Process(target=identify, name='Identify')
    p.start()

    return p

# EOF

