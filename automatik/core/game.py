import datetime


class Game:
    def __init__(self, name, link, module_id, date=None):
        self.NAME = name
        self.LINK = link
        self.MODULE_ID = module_id  # Module ID of the module which generated the instance
        self.DATE = str(datetime.datetime.now()) if date is None else date

    def __eq__(self, other):
        """When comparing two Game objects only the link and module ID attributes will matter."""
        return True if self.LINK == other.LINK and self.MODULE_ID == other.MODULE_ID else False


class GameAdapter:
    @staticmethod
    def to_dict(game_obj):
        """Converts a 'Game' instance into a dictionary."""
        return {"name": game_obj.NAME,
                "link": game_obj.LINK,
                "module_id": game_obj.MODULE_ID,
                "date": game_obj.DATE}

    @staticmethod
    def to_object(game_dict):
        """Converts a compatible dictionary into a 'Game' instance."""
        return Game(name=game_dict["name"], link=game_dict["link"],
                    module_id=game_dict["module_id"], date=game_dict["date"])
