# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

import logging

import multiprocessing

import subprocess

logger = multiprocessing.get_logger()
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())

def do_eject():
    """Process target for ejecting
    """

    logger.info('[EJECT] Ejecting')
    retval = subprocess.call('eject')
    if retval == 0:
        logger.info('[EJECT] OK')
    else:
        logger.info('[EJECT] %s' % retval)

def eject(interface):
    """Spawn it
    """

    p = multiprocessing.Process(target=do_eject)
    p.start()

# EOF

