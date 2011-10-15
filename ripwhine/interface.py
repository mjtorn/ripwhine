# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8

class Interface(object):
    """Handles interfacing with the user
    """

    def print_menu(self):
        """Present the options to the user
        """

        ## Start off easy
        menu = """
        1. exit
        """

        print menu

    def handle_input(self):
        """Read user input, validate, execute. Return True if more loops required
        """

        action = raw_input('>>> ')

        if action.isdigit():
            if int(action) == 1:
                return False

        return True

    def run(self):
        """Work-horse, nay, pwny
        """

        in_loop = True
        while in_loop:
            self.print_menu()
            in_loop = self.handle_input()

# EOF

