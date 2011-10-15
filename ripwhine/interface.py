# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

from ripwhine import actions

class Interface(object):
    """Handles interfacing with the user
    """

    def __init__(self):
        """Set the menu items and actions
        """

        # Some of these are for testing
        self.items = (
            ('s', 'sleep'),
            ('q', 'exit'),
        )

        self.actions = (
            ('s', actions.sleep_process),
            ('q', lambda interface: False),
        )

    def print_menu(self):
        """Present the options to the user
        """

        for item in self.items:
            print '%s. %s' % item

    def handle_input(self):
        """Read user input, validate, execute. Return True if more loops required
        """

        action = raw_input('>>> ')

        if action.isdigit():
            action = int(action)

        if dict(self.items).has_key(action):
            ## Probably not a good interface
            retval = dict(self.actions)[action](self)
            if retval is not None:
                return retval

        return True

    def run(self):
        """Work-horse, nay, pwny
        """

        in_loop = True
        while in_loop:
            self.print_menu()
            in_loop = self.handle_input()

# EOF

