# coding=utf-8
import os
from datetime import datetime

import discord
from discord.ext import commands, tasks

import automatik.utils.cli
import automatik.utils.update
from automatik import logger, SRC_DIR
from automatik.core.llm import LLMParser
from automatik.utils.igdb_client import IGDBClient
from automatik.commands.admin import AdminSlash
from automatik.commands.owner import OwnerSlash
from automatik.core.config import Config
from automatik.core.database import Database
from automatik.core.errors import GameRetrievalException, InvalidGameDataException
from automatik.core.game import GameAdapter, Game
from automatik.core.language import LanguageManager
from automatik.core.services import ServiceLoader


class AutomatikBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        commands.Bot.__init__(self, command_prefix=command_prefix, intents=intents)
        self.is_first_execution = True
        self.languages = LanguageManager(os.path.join(SRC_DIR, "lang"))
        self.config = Config(".env")
        self.database = Database(self.config.DB_URI)
        self.llm_parser = LLMParser(self.config.LLM_MODEL) if self.config.LLM_MODEL else None
        self._debug_guild = discord.Object(id=self.config.DEBUG_GUILD_ID) if self.config.DEBUG_GUILD_ID else None
        self.igdb = IGDBClient(self.config.IGDB_CLIENT_ID, self.config.IGDB_CLIENT_SECRET) if self.config.IGDB_CLIENT_ID and self.config.IGDB_CLIENT_SECRET else None

        self.main_loop = True
        self.load_resources()
        self.remove_command("help")  # There is a default 'help' command which shows docstrings

    async def setup_hook(self):
        await self.add_cog(AdminSlash(self, self.languages, self.config, self.database))
        if self._debug_guild:
            await self.add_cog(OwnerSlash(self, self.languages, self.config, self.database), guild=self._debug_guild)

    async def close(self):
        if self._debug_guild:
            self.tree.clear_commands(guild=self._debug_guild)
            await self.tree.sync(guild=self._debug_guild)
        await super().close()

    async def on_ready(self):
        if self.is_first_execution:
            self.is_first_execution = False
            self.look_for_free_games.start()
            await self.tree.sync(guild=self._debug_guild)
            logger.info(
                f"Bot ready, logged in as {self.user} ({self.user.id}), "
                f"serving {len(self.guilds)} guild(s)"
            )
        await self.change_presence(status=discord.Status.online, activity=discord.Game("!mk help"))

    def load_resources(self):
        """Loads configuration, services and language packages."""
        ServiceLoader.load_services()
        self.languages.load_language_files()
        # Services are added to the documents from the 'configs' collection on runtime
        self.database.insert_missing_or_new_services()

    def create_game_embed(self, game: Game):
        service = ServiceLoader.get_service(game.SERVICE_ID)
        embed = discord.Embed(
            title=f"{game.NAME} is free!",
            url=game.LINK,
            color=service.EMBED_COLOR
        )
        embed.set_thumbnail(url="attachment://thumbnail.png")
        embed.set_author(name=service.SERVICE_NAME)
        embed.set_image(url=game.promo_img_url)

        if self.igdb is not None:
            igdb_data = self.igdb.get_game_data(game.NAME)
            # Game summary
            if igdb_data.get("summary"):
                summary = igdb_data["summary"]
                if len(summary) > 300:
                    summary = summary[:297] + "..."
                embed.description = summary

            # Game rating
            rating = igdb_data.get("total_rating") or igdb_data.get("aggregated_rating") or igdb_data.get("rating")
            if rating:
                rating_stars = IGDBClient.rating_to_stars(rating)
                embed.add_field(name="Rating", value=f"{rating_stars} ({rating/20:.1f}/5)", inline=True)

            # Game genres
            if igdb_data.get("genres"):
                genres = ", ".join([g["name"] for g in igdb_data["genres"][:3]])
                embed.add_field(name="Genres", value=genres, inline=True)

            # Game release year
            if igdb_data.get("first_release_date"):
                release_year = datetime.fromtimestamp(igdb_data["first_release_date"]).year
                embed.add_field(name="Released", value=str(release_year), inline=True)

        return embed, discord.File(f"automatik/services/assets/{service.SERVICE_IMAGE}", filename="thumbnail.png")

    async def on_command_error(self, interaction, error):
        """Method used for error handling regarding the discord.py library."""

        guild_lang = self.database.get_guild_config(interaction.guild)["lang"]
        if isinstance(error, commands.CommandInvokeError):
            error = error.original  # CommandInvokeError is too generic, this gets the exception which raised it

        if isinstance(error, commands.MissingPermissions):  # User lacks permissions
            await interaction.response.send_message(self.languages.get_message(guild_lang, "missing_permissions"))

        elif isinstance(error, commands.errors.CommandNotFound):
            await interaction.response.send_message(self.languages.get_message(guild_lang, "invalid_command"))

        elif isinstance(error, discord.errors.Forbidden):  # Bot kicked or lacks permissions
            pass

        elif isinstance(error, commands.errors.CheckFailure):
            # todo debug message
            pass

        else:  # Unexpected errors wouldn't show up without this, yep, I made the mistake once
            logger.exception(
                f"Unhandled error in command '{getattr(interaction.command, 'name', 'unknown')}' "
                f"invoked by {interaction.author} in guild '{interaction.guild.name}' ({interaction.guild.id})",
                exc_info=error
            )

    @tasks.loop(minutes=15)
    async def look_for_free_games(self):
        free_games = []

        if not self.main_loop:
            return
        for service in ServiceLoader.services:
            stored_free_games = self.database.get_free_games_by_service_id(service.SERVICE_ID)
            try:
                retrieved_free_games = service.get_free_games()
            except GameRetrievalException:
                logger.warning(f"Failed to retrieve data from '{service.SERVICE_ID}', skipping", exc_info=True)
                continue
            except InvalidGameDataException:
                logger.warning(
                    f"Malformed data from '{service.SERVICE_ID}'"
                    + (", retrying with AI fallback" if self.llm_parser else ", skipping (no LLM configured)"),
                    exc_info=True
                )
                if self.llm_parser is None:
                    continue
                api_request = service.make_request()
                retrieved_free_games = [GameAdapter.to_object(game) for game in self.llm_parser.to_dict(api_request, service.SERVICE_ID)]
            except:  # Any unhandled exception in any service would abruptly stop the current iteration without this
                logger.exception(f"Unexpected error while fetching data from '{service.SERVICE_ID}'")
                continue

            new_games = [game for game in retrieved_free_games if game not in stored_free_games]
            expired_games = [game for game in stored_free_games if game not in retrieved_free_games]

            for game in new_games:
                self.database.create_free_game(game)
                free_games.append(game)
                logger.info(f"New free game detected on '{service.SERVICE_ID}': '{game.NAME}'")

            for game in expired_games:
                self.database.move_to_past_free_games(game)
                logger.info(f"Game no longer free on '{service.SERVICE_ID}': '{game.NAME}'")

        if free_games:
            logger.info(f"Cycle complete: {len(free_games)} new free game(s) queued for broadcast")
        await self.broadcast_free_games(free_games)

    async def broadcast_free_games(self, free_games):
        if not free_games:
            return

        success, fail = 0, 0

        for guild in self.guilds:
            guild_config = self.database.get_guild_config(guild)
            for game in free_games:
                if guild_config["selected_channel"] and guild_config["services"][game.SERVICE_ID]:
                    game_embed, thumbnail = self.create_game_embed(game)
                    mention_content = guild_config.get("mention_role", "")
                    try:
                        await guild.get_channel(guild_config["selected_channel"]).send(content=mention_content, embed=game_embed, file=thumbnail)
                        success += 1
                    except (AttributeError, discord.errors.Forbidden):  # Invalid channel id or bot lacks permissions
                        logger.warning(f"Could not deliver '{game.NAME}' to guild '{guild.name}' ({guild.id}): invalid channel or missing permissions")
                        fail += 1
                    except:
                        logger.exception(f"Unexpected error delivering '{game.NAME}' to guild '{guild.name}' ({guild.id})")
                        fail += 1

        logger.info(
            f"Broadcast complete: {success} succeeded, {fail} failed "
            f"across {len(self.guilds)} guild(s)"
        )


    async def is_invoked(self, interaction: discord.Interaction):
        logger.debug(
            f"Command '/{interaction.command.name}' invoked by {interaction.user.name} "
            f"in guild '{interaction.guild.name}' ({interaction.guild.id})"
        )
        return True


if __name__ == "__main__":
    automatik.utils.cli.clear_console()
    automatik.utils.cli.print_ascii_art()
    logger.info("Starting AutomatiK...")
    automatik_bot = AutomatikBot(command_prefix="!mk ", intents=discord.Intents.default())
    automatik.utils.update.check_updates()
    try:
        automatik_bot.run(automatik_bot.config.discord_token, log_handler=None)
    except discord.errors.LoginFailure:
        logger.error("Login failed: 'DISCORD_TOKEN' is invalid or expired.")
