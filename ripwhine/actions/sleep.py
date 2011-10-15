# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

import logging

import multiprocessing

import time

logger = multiprocessing.log_to_stderr()
logger.setLevel(logging.INFO)

def do_sleep():
    """Process target for sleeping
    """

    logger.info('Sleeping')
    time.sleep(1)
    logger.info('Slept')

def sleep_process():
    """Spawn it
    """

    p = multiprocessing.Process(target=do_sleep)
    p.start()

# EOF

