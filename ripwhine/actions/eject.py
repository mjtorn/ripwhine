# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

import logging
import multiprocessing
import subprocess

logger = multiprocessing.get_logger()
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())

DEVICE = '/dev/cdrom'

EJECT_CMD = ['eject']

def do_eject(interface):
    """Process target for ejecting
    interface passed for state
    """

    cmd = EJECT_CMD[:]
    if interface.ejected:
        cmd.append('-t')
    cmd.append(DEVICE)

    logger.info('[EJECT] %sEjecting' % 'Un-' if interface.ejected else '')
    retval = subprocess.call(cmd)
    if retval == 0:
        logger.info('[EJECT] OK')
        interface.ejected = not interface.ejected
    else:
        logger.info('[EJECT] %s' % retval)

def eject(interface):
    """Spawn it
    """

    p = multiprocessing.Process(target=do_eject, args=(interface,))
    p.run()

# EOF
