import pymongo
import datetime


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
        self.GAME_TEMPLATE = \
            {
                "_id": None,  # It's the game URL
                "name": None,
                "date": str(datetime.datetime.now())
            }

    def create_guild_config(self, guild):
        """Creates a new document in the 'configs' collection"""
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
        """Returns the configuration from a guild"""
        self.create_guild_config(guild)
        return self._db["configs"].find_one({"_id": str(guild.id)})

    def update_guild_config(self, guild, update):
        """Updates the value of a determined field"""
        self.create_guild_config(guild)
        self._db["configs"].update_one({"_id": str(guild.id)}, {"$set": update})
        return True

    def create_free_game(self, game_object):
        game = self.GAME_TEMPLATE
        game["_id"] = game_object.link
        game["name"] = game_object.name
        self._db["free_games"].insert(game)
        return True
