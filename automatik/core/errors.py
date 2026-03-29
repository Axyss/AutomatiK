class GameRetrievalException(Exception):
    """This exception must be raised whenever a service fails
       to retrieve data (e.g. network or HTTP errors)."""
    def __init__(self, cause: Exception):
        self.message = "An error occurred while retrieving game data."
        self.__cause__ = cause
        super().__init__(self.message)


class InvalidGameDataException(Exception):
    """This exception must be raised whenever a service fails
       to parse the retrieved data and its output must be ignored by the bot."""
    def __init__(self, cause: Exception):
        self.message = "An error occurred while parsing game data."
        self.__cause__ = cause
        super().__init__(self.message)
