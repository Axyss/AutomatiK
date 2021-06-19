import pymongo
import datetime

from core.game import Game
from core.lang_manager import logger


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
                "selected_channel": None,  # Structure: <#1234>
                "mention_role": None,  # Structure: <@&1234>
                "lang": "en_EN",
                "services": {},  # Services are represented with their MODULE_IDs
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
        logger.info(f"New game '{game_obj.NAME}' ({game_obj.MODULE_ID}) added to the database")
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
        logger.info(f"'{game_obj.NAME}' ({game_obj.MODULE_ID}) moved to the 'past_free_games' database")
        return True

    def add_new_services(self, current_services):
        """Adds new service fields to the 'configs' database when new modules are added."""
        retrieved_services = list(self._db["configs"].aggregate([{"$sample": {"size": 1}}]))[0]["services"].keys()

        for service in current_services:
            if service not in retrieved_services:
                self._db["configs"].update_many({}, {"$set": {f"services.{service}": True}})
                logger.debug(f"New service '{service}' added to the database")
        return True
