# coding=utf-8
import os
import random

import discord
from discord.ext import commands, tasks

import automatik.utils.cli
import automatik.utils.update
from automatik import logger, SRC_DIR
from automatik.commands.admin import AdminSlash
from automatik.commands.owner import OwnerSlash
from automatik.commands.public import PublicSlash
from automatik.core.config import Config
from automatik.core.db import Database
from automatik.core.errors import InvalidGameDataException
from automatik.core.lang import LangLoader
from automatik.core.modules import ModuleLoader


class AutomatikBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        commands.Bot.__init__(self, command_prefix=command_prefix, intents=intents)
        self.is_first_exec = True
        self.lm = LangLoader(os.path.join(SRC_DIR, "lang"))
        self.cfg = Config(".env")
        self.mongo = Database(self.cfg.DB_URI)

        self.main_loop = True  # Variable used to start or stop the main loop
        self.load_resources()
        self.remove_command("help")  # There is a default 'help' command which shows docstrings
        self.init_commands()

    async def setup_hook(self):
        # todo Refactor
        await self.add_cog(PublicSlash(self, self.lm, self.cfg, self.mongo),guild=discord.Object(id=485048883131711498))
        await self.add_cog(AdminSlash(self, self.lm, self.cfg, self.mongo), guild=discord.Object(id=485048883131711498))
        await self.add_cog(OwnerSlash(self, self.lm, self.cfg, self.mongo), guild=discord.Object(id=485048883131711498))

    async def on_ready(self):
        if self.is_first_exec:
            self.is_first_exec = False
            self.look_for_free_games.start()
            await self.tree.sync(guild=discord.Object(id=485048883131711498))
            logger.info("Bot Online")
        await self.change_presence(status=discord.Status.online, activity=discord.Game("!mk help"))

    def load_resources(self):
        """Loads configuration, modules and language packages."""
        ModuleLoader.load_modules()
        # todo Refactor
        # self.cfg.load_config()
        self.lm.load_lang_packages()
        # Services are added to the documents from the 'configs' collection on runtime
        self.mongo.insert_missing_or_new_services()

    def generate_message(self, guild_cfg, game):
        """Generates a 'X free on Y' type message."""
        message = random.choice(self.lm.get_message(guild_cfg["lang"], "generic_messages")).format(game.NAME, game.LINK)

        if guild_cfg["services"]["mention"] and guild_cfg["mention_role"]:
            message = guild_cfg["mention_role"] + " " + message
        return message

    async def on_command_error(self, interaction, error):
        """Method used for error handling regarding the discord.py library."""

        guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]
        if isinstance(error, commands.CommandInvokeError):
            error = error.original  # CommandInvokeError is too generic, this gets the exception which raised it

        if isinstance(error, commands.MissingPermissions):
            # User lacks permissions
            await interaction.response.send_message(self.lm.get_message(guild_lang, "missing_permissions"))

        # todo Add MissingRequiredArgument

        elif isinstance(error, commands.errors.CommandNotFound):
            await interaction.response.send_message(self.lm.get_message(guild_lang, "invalid_command"))

        # todo Plain unnecessary
        elif isinstance(error, commands.errors.CommandOnCooldown):
            await interaction.response.send_message(
                self.lm.get_message(guild_lang, "cooldown_error").format(int(error.retry_after)))

        elif isinstance(error, discord.errors.Forbidden):
            # Bot kicked or lacks permissions to send messages
            pass

        elif isinstance(error, commands.errors.CheckFailure):
            # todo debug message
            pass

        else:  # Unexpected errors wouldn't show up without this, yep, I made the mistake once
            logger.exception("Unexpected error", exc_info=error)

    @tasks.loop(minutes=5)
    async def look_for_free_games(self):
        free_games = []

        if not self.main_loop:
            return
        for module in ModuleLoader.modules:
            try:
                retrieved_free_games = module.get_free_games()
                stored_free_games = self.mongo.get_free_games_by_module_id(module.MODULE_ID)
            except InvalidGameDataException as error:
                logger.info(f"Ignoring latest results from module: {module.MODULE_ID}."
                            f" Enable debug mode for more information")
                logger.debug(f"InvalidGameDataException raised by module with MODULE_ID: '{module.MODULE_ID}'",
                             exc_info=error)
            except:  # Any unhandled exception in any module would abruptly stop the current iteration without this
                logger.exception("Unexpected error while retrieving game data")
            else:
                for game in retrieved_free_games:  # Looks for free games
                    if game not in stored_free_games:
                        self.mongo.create_free_game(game)
                        free_games.append(game)

                for game in stored_free_games:  # Looks for games that are no longer free
                    if game not in retrieved_free_games:
                        self.mongo.move_to_past_free_games(game)
        await self.broadcast_free_games(free_games)  # todo This is a blocking point for the method itself

    async def broadcast_free_games(self, free_games):
        success, fail = 0, 0

        for guild in self.guilds:
            guild_config = self.mongo.get_guild_config(guild)
            for game in free_games:
                if guild_config["selected_channel"] and guild_config["services"][game.MODULE_ID]:
                    message = self.generate_message(guild_config, game)
                    try:
                        await guild.get_channel(guild_config["selected_channel"]).send(message)
                        success += 1
                    except (AttributeError, discord.errors.Forbidden):  # Channel id invalid or bot lacks permissions
                        fail += 1
                    except:
                        fail += 1
                        logger.exception("Unexpected error")
        logger.info(f"Messages sent to all guilds. Success: {success} | Fail: {fail}")

    async def is_an_owner(self, interaction):
        return str(interaction) in self.cfg.bot_owner

    async def is_invoked(self, interaction):
        logger.debug(f"{interaction.command.name} invoked by {str(interaction.author)} on {interaction.guild.id}")
        return True

    def init_commands(self):
        pass

if __name__ == "__main__":
    automatik.utils.cli.clear_console()
    automatik.utils.cli.print_ascii_art()
    logger.info("Loading..")
    automatik_bot = AutomatikBot(command_prefix="!mk ", intents=discord.Intents.default())
    automatik.utils.update.check_updates()

    try:
        automatik_bot.run(automatik_bot.cfg.discord_token)
    except discord.errors.LoginFailure:
        logger.error("Invalid 'discord_bot_token'. Press enter to exit..")
