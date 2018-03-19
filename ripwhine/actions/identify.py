# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

import logging
import multiprocessing

logger = multiprocessing.get_logger()
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())

def identify(interface):
    """Identify current disc
    """

    interface.queue_to_identify.send('IDENTIFY')

# EOF
