# This is not a removable service. If you wish to disable it use the '!mk disable' command.

class Main:
    def __init__(self):
        self.SERVICE_NAME = "Mention"
        self.SERVICE_ID = "mention"

    def get_free_games(self):
        return []

# todo Altering the state of the mentions should have nothing to do with services
