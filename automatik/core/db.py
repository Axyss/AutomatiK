import datetime

import pymongo
from pymongo.errors import DuplicateKeyError

from automatik.core.game import GameAdapter
from automatik.core.lang import logger
from automatik.core.services import ServiceLoader


class Database:
    def __init__(self, uri):
        self._db = pymongo.MongoClient(host=uri)["automatik"]
        self.CONFIG_TEMPLATE = {
            "_id": None,
            "name": None,
            "members": None,
            "selected_channel": None,  # Structure: <#1234>
            "mention_role": None,  # Structure: <@&1234>
            "lang": "en",
            "services": {},  # Services are represented by their SERVICE_IDs
            "join_date": str(datetime.datetime.now())
        }

    def _create_guild_config(self, guild):
        """Creates a new document in the 'configs' collection."""
        config = dict(self.CONFIG_TEMPLATE)
        config.update({"_id": str(guild.id), "name": guild.name, "members": guild.member_count,
                       "services": dict.fromkeys(ServiceLoader.get_service_ids(), True)})
        try:
            self._db["configs"].insert_one(config)
            return True
        except DuplicateKeyError:
            return False

    def insert_missing_or_new_services(self):
        """Inserts fields into the 'services' object of each document from the 'configs' collection."""
        for service in ServiceLoader.get_service_ids():
            self._db["configs"].update_many({f"services.{service}": {"$exists": False}},
                                            {"$set": {f"services.{service}": True}})
        return True

    def get_guild_config(self, guild):
        """Returns the configuration from a guild, creates said config if it didn't already exist."""
        self._create_guild_config(guild)  # This might be removed in the future to improve scalability
        return self._db["configs"].find_one({"_id": str(guild.id)})

    def update_guild_config(self, guild, update):
        """Updates the value of a determined field."""
        self._db["configs"].update_one({"_id": str(guild.id)}, {"$set": update})
        return True

    def create_free_game(self, game_obj):
        """Creates a new document in the 'free_games' collection."""
        self._db["free_games"].insert_one(GameAdapter.to_dict(game_obj))
        logger.info(f"New game '{game_obj.NAME}' ({game_obj.SERVICE_ID}) added to the database")
        return True

    def get_free_games_by_service_id(self, service_id):
        """Returns every document from the 'free_games' collection with a certain service ID."""
        free_games = []
        for game_dict in self._db["free_games"].find({"service_id": service_id}):
            free_games.append(GameAdapter.to_object(game_dict))
        return free_games

    def move_to_past_free_games(self, game_obj):
        """Moves a document from the 'free_games' collection to 'past_free_games' collection."""
        past_free_game_dict = self._db["free_games"].find_one_and_delete({"link": game_obj.LINK,
                                                                          "service_id": game_obj.SERVICE_ID})
        self._db["past_free_games"].insert_one(past_free_game_dict)
        logger.info(f"'{game_obj.NAME}' ({game_obj.SERVICE_ID}) moved to the 'past_free_games' database")
        return True
