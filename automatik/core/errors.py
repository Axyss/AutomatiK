
class InvalidDataException(Exception):
    """This exception must be raised whenever a module fails
       retrieving/parsing data and its output must be ignored by the bot."""
    def __init__(self):
        self.message = "You can't do that"
        super().__init__(self.message)
