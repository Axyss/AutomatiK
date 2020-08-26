from core.generic_mod import GenericModule


class Mention(GenericModule):

    def __init__(self):

        self.SERVICE_NAME = "Mention"
        self.MODULE_ID = "mention"
        self.AUTHOR = "Default"

    def get_free_games(self):

        return False
