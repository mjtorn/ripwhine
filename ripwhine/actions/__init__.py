from ripwhine.actions.sleep import do_sleep, sleep_process
from ripwhine.actions.rip import start_rip
from ripwhine.actions.identify import identify

import os

def change_dir(interface):
    """Set a new destination
    """

    old_destination_dir = interface.destination_dir
    interface.destination_dir = raw_input('dir? >> ')

    if not os.path.exists(interface.destination_dir):
        interface.destination_dir = old_destination_dir

        interface.queue_to_rip_interface.send('ENODIR')
    else:
        # I know this is hacky and ugly.
        interface.items[0][1] = 'dir [%s]' % interface.destination_dir

