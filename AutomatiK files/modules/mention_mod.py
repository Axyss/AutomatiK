# This is not a removable module. If you wish to disable It use the '!mk disable' command

class Mention:

    def __init__(self):

        self.SERVICE_NAME = "Mention"
        self.MODULE_ID = "mention"
        self.AUTHOR = "Default"

    def get_free_games(self):
        return False
