
class InvalidGameDataException(Exception):
    """This exception must be raised whenever a service fails
       retrieving/parsing data and its output must be ignored by the bot."""
    def __init__(self, cause: Exception):
        self.message = "An error occurred while retrieving/parsing game data."
        self.__cause__ = cause
        super().__init__(self.message)
