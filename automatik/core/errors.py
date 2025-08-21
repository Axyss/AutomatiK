
class InvalidGameDataException(Exception):
    """This exception must be raised whenever a service fails
       retrieving/parsing data and its output must be ignored by the bot."""
    def __init__(self):
        self.message = "An error occurred while retrieving/parsing game data."
        super().__init__(self.message)
