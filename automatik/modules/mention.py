# This is not a removable module. If you wish to disable it use the '!mk disable' command.

class Main:
    def __init__(self):
        self.SERVICE_NAME = "Mention"
        self.MODULE_ID = "mention"
        self.AUTHOR = "Default"

    def get_free_games(self):
        return []

# todo Altering the state of the mentions should have nothing to do with modules
