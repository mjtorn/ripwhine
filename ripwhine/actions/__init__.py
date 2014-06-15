from ripwhine.actions.sleep import do_sleep, sleep_process
from ripwhine.actions.rip import start_rip
from ripwhine.actions.identify import identify
from ripwhine.actions.eject import eject

import os

import select
import sys

import termios
import tty

def change_dir(interface):
    """Set a new destination
    """

    old_settings = termios.tcgetattr(sys.stdin)

    try:
        tty.setcbreak(sys.stdin.fileno())
        poll = select.poll()
        poll.register(sys.stdin, select.POLLIN)

        old_destination_dir = interface.destination_dir

        sys.stdout.write('dir? >> ')
        sys.stdout.flush()

        destination_dir = ''
        while True:
            poll.poll()

            c = sys.stdin.read(1)

            sys.stdout.write(c)
            sys.stdout.flush()

            if ord(c) == 10 or ord(c) == 13:
                break
            elif ord(c) == 8: # backspace
                ## Some day maybe put a space under the cursor
                destination_dir = destination_dir[:-1]
            else:
                destination_dir = '%s%s' % (destination_dir, c)

        if not os.path.exists(destination_dir):
            interface.destination_dir = old_destination_dir

            interface.queue_to_rip_interface.send('ENODIR')
        else:
            interface.destination_dir = destination_dir

            # I know this is hacky and ugly.
            interface.items[0][0] = 'dir [%s]' % interface.destination_dir

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

