# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

import logging

import multiprocessing

logger = multiprocessing.get_logger()
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())

def start_rip(interface):
    """Tell ripper process to start doing it
    """

    interface.queue_to_rip.send('START_RIP')

# EOF

