class Game:
    def __init__(self, name, link):
        self.name = name
        self.link = link

    def __eq__(self, other):
        """When comparing two Game objects only the link attribute will matter."""
        return True if self.link == other.link else False
