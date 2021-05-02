import pymongo
import datetime

from core.game import Game


class DatabaseManager:
    def __init__(self, host, port, username, password, auth_source, auth_mechanism):
        self._db = pymongo.MongoClient(host=host,
                                       port=port,
                                       username=username,
                                       password=password,
                                       authSource=auth_source,
                                       authMechanism=auth_mechanism)[auth_source]
        self.CONFIG_TEMPLATE = \
            {
                "_id": None,
                "name": None,
                "members": None,
                "mention_role": "<@&1234>",
                "lang": "en_EN",
                "services": {
                    "main": False,
                    "mention": True,
                    "epic": True,
                    "humble": True,
                    "steam": True
                },
                "join_date": str(datetime.datetime.now())
            }

    def create_guild_config(self, guild):
        """Creates a new document in the 'configs' collection."""
        config = self.CONFIG_TEMPLATE
        config["_id"] = str(guild.id)
        config["name"] = guild.name
        config["members"] = guild.member_count
        try:
            self._db["configs"].insert(config)
            return True
        except pymongo.errors.DuplicateKeyError:
            return False

    def get_guild_config(self, guild):
        """Returns the configuration from a guild."""
        self.create_guild_config(guild)
        return self._db["configs"].find_one({"_id": str(guild.id)})

    def update_guild_config(self, guild, update):
        """Updates the value of a determined field."""
        self.create_guild_config(guild)
        self._db["configs"].update_one({"_id": str(guild.id)}, {"$set": update})
        return True

    def create_free_game(self, game_obj):
        """Creates a new document in the 'free_games' collection."""
        self._db["free_games"].insert(Game.to_dict(game_obj))
        return True

    def get_free_games_by_module_id(self, module_id):
        """Returns every document from the 'free_games' collection with a certain module ID."""
        free_games = []
        for game_dict in self._db["free_games"].find({"module_id": module_id}):
            free_games.append(Game.to_object(game_dict))
        return free_games

    def move_to_past_free_games(self, game_obj):
        """Moves a document from the 'free_games' collection to 'past_free_games' collection."""
        past_free_game_dict = self._db["free_games"].find_one_and_delete({"link": game_obj.LINK,
                                                                          "module_id": game_obj.MODULE_ID})
        self._db["past_free_games"].insert_one(past_free_game_dict)
        return True


