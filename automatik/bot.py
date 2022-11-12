# coding=utf-8
import asyncio
import queue
import random
import os

import discord
import psutil
from discord.ext import commands, tasks
from discord import app_commands

from automatik import logger, __version__, LOGO_URL, AVATAR_URL, SRC_DIR
from .core.config import Config
from .core.db import Database
from .core.errors import InvalidGameDataException
from .core.lang import LangLoader
from .core.modules import ModuleLoader


class AutomatikBot(commands.Bot):
    def __init__(self, command_prefix, self_bot, intents):
        commands.Bot.__init__(self, command_prefix=command_prefix, self_bot=self_bot, intents=intents)
        self.is_first_exec = True  # Used inside 'on_ready' to execute certain parts of the method only once
        self.lm = LangLoader(os.path.join(SRC_DIR, "lang"))
        self.cfg = Config(".env")
        self.mongo = Database(host=self.cfg.db_host,
                              port=self.cfg.db_port,
                              username=self.cfg.db_root_user,
                              password=self.cfg.db_root_password,
                              auth_source=self.cfg.db_auth_source,
                              auth_mechanism=self.cfg.db_auth_mechanism)

        self.main_loop = False  # Variable used to start or stop the main loop
        self.game_queue = queue.Queue()  # Free games are stored here temporary while the 'broadcaster' routine
        # delivers the messages
        self.game_queue_cache = []

        self.load_resources()
        self.remove_command("help")  # There is a default 'help' command which shows docstrings
        self.init_commands()

    async def on_ready(self):
        if self.is_first_exec:
            self.is_first_exec = False

            self.init_main_loop.start()
            self.init_message_broadcaster.start()

            await self.tree.sync(guild=discord.Object(id=649270300982247449))
            logger.info("Bot Online")
        await self.change_presence(status=discord.Status.online, activity=discord.Game("!mk help"))

    def load_resources(self):
        """Loads configuration, modules and language packages."""
        ModuleLoader.load_modules()
        # todo Refactor this method 'load_resources'
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

        elif isinstance(error, commands.errors.CommandOnCooldown):
            await interaction.response.send_message(self.lm.get_message(guild_lang, "cooldown_error").format(int(error.retry_after)))

        elif isinstance(error, discord.errors.Forbidden):
            # Bot kicked or lacks permissions to send messages
            pass

        elif isinstance(error, commands.errors.CheckFailure):
            # todo debug message
            pass

        else:  # Without this, unexpected errors wouldn't show up
            logger.exception("Unexpected error", exc_info=error)

    @tasks.loop(seconds=1)
    async def init_main_loop(self):
        if self.main_loop:  # MAIN LOOP
            for module in ModuleLoader.modules:
                try:
                    retrieved_free_games = module.get_free_games()
                    stored_free_games = self.mongo.get_free_games_by_module_id(module.MODULE_ID)
                except InvalidGameDataException as error:
                    logger.info(f"Ignoring latest results from module: {module.MODULE_ID}."
                                f" Enable debug mode for more information")
                    logger.debug(f"InvalidGameDataException raised by module with MODULE_ID: '{module.MODULE_ID}'",
                                 exc_info=error)
                except:  # If this wasn't here, any unhandled exception in any module would crash the loop
                    logger.exception("Unexpected error while retrieving game data")
                else:
                    for game in retrieved_free_games:  # Looks for free games
                        if game not in stored_free_games:
                            self.mongo.create_free_game(game)
                            self.game_queue.put(game)

                    for game in stored_free_games:  # Looks for games that are no longer free
                        if game not in retrieved_free_games:
                            self.mongo.move_to_past_free_games(game)
            await asyncio.sleep(300)  # 5 minutes until the next iteration

    @tasks.loop(seconds=1)
    async def init_message_broadcaster(self):
        self.game_queue_cache = []  # Being here avoids not getting executed and not letting the bot to shutdown
        if not self.game_queue.empty():
            success, fail = 0, 0

            for i in range(self.game_queue.qsize()):
                # We move the current elements of the queue to a list so we can send all games at once to each guild
                # making a single call to the database per guild.
                self.game_queue_cache.append(self.game_queue.get())

            for guild in self.guilds:
                guild_cfg = self.mongo.get_guild_config(guild)
                for game in self.game_queue_cache:
                    if guild_cfg["selected_channel"] and guild_cfg["services"][game.MODULE_ID]:
                        selected_channel = guild_cfg["selected_channel"]
                        # Transforms "<#1234>" into 1234
                        selected_channel = int(
                            selected_channel[selected_channel.find("#") + 1: selected_channel.rfind(">")])
                        message = self.generate_message(guild_cfg, game)
                        try:
                            await guild.get_channel(selected_channel).send(message)
                            success += 1
                        except (AttributeError, discord.errors.Forbidden):
                            # If the channel ID is invalid or the bot lacks permissions
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

        # Public commands

        @self.tree.command(guild=discord.Object(id=649270300982247449))
        async def help(interaction: discord.Interaction):
            """A simple help command."""
            guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]

            embed_help = discord.Embed(title=f"AutomatiK {__version__} Help ",
                                       description=self.lm.get_message(guild_lang, "help_description"),
                                       color=0x00BFFF)
            embed_help.set_thumbnail(url=LOGO_URL)
            embed_help.add_field(name=self.lm.get_message(guild_lang, "help_field1_name"),
                                 value="".join(self.lm.get_message(guild_lang, "help_field1_value")),
                                 inline=False)

            if interaction.user.guild_permissions.administrator:
                embed_help.add_field(name=u"\U0001F6E0 " + self.lm.get_message(guild_lang, "help_field2_name"),
                                     value="".join(self.lm.get_message(guild_lang, "help_field2_value")),
                                     inline=False)
            if await self.is_an_owner(interaction.user):  # If command author a bot owner
                embed_help.add_field(name=u"\U0001F451 " + self.lm.get_message(guild_lang, "help_field3_name"),
                                     value="".join(self.lm.get_message(guild_lang, "help_field3_value")),
                                     inline=False
                                     )
            await interaction.response.send_message(embed=embed_help)

        @self.tree.command(guild=discord.Object(id=649270300982247449))
        async def status(interaction):
            """Shows your current AutomatiK config."""
            guild_cfg = self.mongo.get_guild_config(interaction.guild)
            guild_lang = guild_cfg["lang"]

            embed_status = discord.Embed(title=self.lm.get_message(guild_lang, "status"),
                                         description=self.lm.get_message(guild_lang, "status_description"),
                                         color=0x00BFFF)
            embed_status.set_footer(text=self.lm.get_message(guild_lang, "help_footer"), icon_url=AVATAR_URL)
            embed_status.set_thumbnail(url=LOGO_URL)
            embed_status.add_field(name=self.lm.get_message(guild_lang, "status_main"),
                                   value=self.lm.get_message(guild_lang, "status_active" if guild_cfg.get("selected_channel") else "status_inactive") + "\n" + guild_cfg[
                                             "selected_channel"])

            for i in ModuleLoader.modules:
                if guild_cfg["services"][i.MODULE_ID]:
                    value = self.lm.get_message(guild_lang, "status_active")
                else:
                    value = self.lm.get_message(guild_lang, "status_inactive")
                embed_status.add_field(name=i.SERVICE_NAME, value=value)
            await interaction.response.send_message(embed=embed_status)

        # Guild administrator commands

        @self.tree.command(guild=discord.Object(id=649270300982247449))
        @app_commands.checks.has_permissions(administrator=True)
        async def select(interaction, channel: discord.TextChannel):
            """Select a Text Channel to start receiving freebies."""
            guild_cfg = self.mongo.get_guild_config(interaction.guild)
            guild_lang = guild_cfg["lang"]

            self.mongo.update_guild_config(interaction.guild, {"selected_channel": channel.mention})
            await interaction.response.send_message(self.lm.get_message(guild_lang, "select_success").format(channel.mention))

        @self.tree.command(guild=discord.Object(id=649270300982247449))
        @app_commands.checks.has_permissions(administrator=True)
        async def unselect(interaction):
            """Unselects the previously selected Text Channel."""
            guild_cfg = self.mongo.get_guild_config(interaction.guild)
            guild_lang = guild_cfg["lang"]
            guild_selected_channel = guild_cfg["selected_channel"]

            if guild_selected_channel is None:
                await interaction.response.send_message(self.lm.get_message(guild_lang, "unselect_already")
                                       .format(guild_selected_channel))
                return None

            self.mongo.update_guild_config(interaction.guild, {"selected_channel": None})
            await interaction.response.send_message(self.lm.get_message(guild_lang, "unselect_success").format(guild_selected_channel))

        @self.tree.command(name="module", guild=discord.Object(id=649270300982247449))
        @app_commands.checks.has_permissions(administrator=True)
        async def enable(interaction, choice: str):
            """Modify the list of services you are interested in."""
            guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]

            user_decision = True if choice == "enable" else False

            for module in ModuleLoader.modules:
                if choice.lower() == module.MODULE_ID.lower():
                    self.mongo.update_guild_config(interaction.guild, {"services." + choice.lower(): user_decision})
                    await interaction.response.send_message(self.lm.get_message(guild_lang, f"module_{choice}d").format(choice))
                    logger.info(f"{choice.capitalize()} module {choice}d by {interaction.author}")
                    return True

            await interaction.response.send_message(self.lm.get_message(guild_lang, f"enable_unknown").format(choice))

        @self.tree.command(guild=discord.Object(id=649270300982247449))
        @app_commands.checks.has_permissions(administrator=True)
        async def modules(interaction):
            """Shows information about the loaded modules."""
            guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]

            embed_module = discord.Embed(title=self.lm.get_message(guild_lang, "modules"),
                                         description=self.lm.get_message(guild_lang, "modules_description"),
                                         color=0x00BFFF)

            embed_module.set_footer(text=self.lm.get_message(guild_lang, "help_footer"), icon_url=AVATAR_URL)
            embed_module.set_thumbnail(url=LOGO_URL)

            embed_module.add_field(name="**ModuleID**", value="\n".join(ModuleLoader.get_module_ids()))

            embed_module.add_field(name=self.lm.get_message(guild_lang, "modules_service"),
                                   value="\n".join(ModuleLoader.get_service_names()))

            embed_module.add_field(name=self.lm.get_message(guild_lang, "modules_author"),
                                   value="\n".join(ModuleLoader.get_module_authors()))

            await interaction.response.send_message(embed=embed_module)

        @self.tree.command(guild=discord.Object(id=649270300982247449))
        @app_commands.checks.has_permissions(administrator=True)
        async def mention(interaction, role: discord.Role):
            """Select which role will be notified freebies."""
            guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]

            self.mongo.update_guild_config(interaction.guild, {"mention_role": role.mention})
            await interaction.response.send_message(self.lm.get_message(guild_lang, "mention_established"))
            logger.info(f"AutomatiK will now mention '{role}'")

        @self.tree.command(guild=discord.Object(id=649270300982247449))
        @app_commands.checks.has_permissions(administrator=True)
        async def language(interaction, lang_code: str):
            """Select a language."""
            guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]

            if lang_code not in self.lm.get_lang_packages_metadata()[0]:  # If the language package does not exist
                await interaction.response.send_message(self.lm.get_message(guild_lang, "language_error"))
                return

            self.mongo.update_guild_config(interaction.guild, {"lang": lang_code})
            await interaction.response.send_message(self.lm.get_message(lang_code, "language_changed"))
            logger.info(f"Language changed to '{lang_code}' by {interaction.author}")

        @self.tree.command(guild=discord.Object(id=649270300982247449))
        @app_commands.checks.has_permissions(administrator=True)
        async def languages(interaction):
            """Shows a list of the available languages."""
            guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]
            lang_ids, lang_names, lang_authors = self.lm.get_lang_packages_metadata()

            embed_langs = discord.Embed(title=self.lm.get_message(guild_lang, "languages"),
                                        description=self.lm.get_message(guild_lang, "languages_description"),
                                        color=0x00BFFF
                                        )
            embed_langs.set_footer(text=self.lm.get_message(guild_lang, "help_footer"),
                                   icon_url=AVATAR_URL
                                   )
            embed_langs.set_thumbnail(url=LOGO_URL)
            embed_langs.add_field(name="LangID", value="\n".join(lang_ids))
            embed_langs.add_field(name=self.lm.get_message(guild_lang, "language"), value="\n".join(lang_names))
            embed_langs.add_field(name=self.lm.get_message(guild_lang, "modules_author"), value="\n".join(lang_authors))

            await interaction.response.send_message(embed=embed_langs)

        # Owner commands

        @self.tree.command(guild=discord.Object(id=649270300982247449))
        async def start(interaction):
            """Starts the main service globally."""
            guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]

            if self.main_loop:
                await interaction.response.send_message(self.lm.get_message(guild_lang, "start_already"))
                return None

            self.main_loop = True
            await interaction.response.send_message(self.lm.get_message(guild_lang, "start_success"))
            logger.info(f"Main service was started globally by {str(interaction.user)}")

        @self.tree.command(guild=discord.Object(id=649270300982247449))
        @app_commands.checks.has_permissions(administrator=True)
        async def stop(interaction):
            """Stops the main service globally."""
            guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]

            if not self.main_loop:  # If service already stopped
                await interaction.response.send_message(self.lm.get_message(guild_lang, "stop_already"))
                return None

            self.main_loop = False
            await interaction.response.send_message(self.lm.get_message(guild_lang, "stop_success"))
            logger.info(f"Main service was stopped globally by {str(interaction.author)}")

        @self.tree.command(guild=discord.Object(id=649270300982247449))
        @app_commands.checks.has_permissions(administrator=True)
        async def reload(interaction):
            """Reloads configuration, modules and language packages."""
            guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]

            logger.info("Reloading..")
            was_started = bool(self.main_loop)
            self.main_loop = False
            try:
                self.load_resources()
                await interaction.response.send_message(self.lm.get_message(guild_lang, "reload_completed"))
                logger.info("Reload completed")
            except:
                await interaction.response.send_message(self.lm.get_message(guild_lang, "unexpected_error"))
                logger.error("An error ocurred while reloading")
            finally:
                self.main_loop = bool(was_started)

        @self.tree.command(guild=discord.Object(id=649270300982247449))
        @app_commands.checks.has_permissions(administrator=True)
        async def stats(interaction):
            """Shows some overall statistics of the bot."""
            guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]
            message_queue_len = len(self.guilds) * (len(self.game_queue_cache) + self.game_queue.qsize())

            embed_stats = discord.Embed(title="\U0001f4c8 " + self.lm.get_message(guild_lang, "stats"),
                                        description=self.lm.get_message(guild_lang, "stats_description"),
                                        color=0x00BFFF)
            embed_stats.set_footer(text=self.lm.get_message(guild_lang, "help_footer"),
                                   icon_url=AVATAR_URL)
            embed_stats.set_thumbnail(url=LOGO_URL)

            embed_stats.add_field(name="Guilds", value=str(len(self.guilds)))
            embed_stats.add_field(name=self.lm.get_message(guild_lang, "stats_owners_field"),
                                  value="\n".join(self.cfg.bot_owner))
            embed_stats.add_field(name=self.lm.get_message(guild_lang, "stats_server_load_field"),
                                  value="CPU: **{}%** \nRAM: **{}%**".format(
                                      psutil.cpu_percent(), psutil.virtual_memory().percent))
            if message_queue_len:
                embed_stats.add_field(name=self.lm.get_message(guild_lang, "stats_message_queue_field"),
                                      value=self.lm.get_message(guild_lang, "stats_message_queue_value")
                                      .format(message_queue_len))
            else:  # No messages in the queues
                embed_stats.add_field(name=self.lm.get_message(guild_lang, "stats_message_queue_field"),
                                      value=self.lm.get_message(guild_lang, "stats_message_queue_empty_value")
                                      .format(message_queue_len))

            await interaction.response.send_message(embed=embed_stats)

        @self.tree.command(guild=discord.Object(id=649270300982247449))
        @app_commands.checks.has_permissions(administrator=True)
        async def shutdown(interaction):
            """Shuts down the bot process completely."""
            guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]
            message_queue_len = len(self.guilds) * (len(self.game_queue_cache) + self.game_queue.qsize())

            if not self.game_queue.empty() or self.game_queue_cache:
                await interaction.response.send_message(self.lm.get_message(guild_lang, "shutdown_abort").format(message_queue_len))
                return None

            await interaction.response.send_message(self.lm.get_message(guild_lang, "shutdown_success"))
            logger.info("Shutting down..")
            self.main_loop = False
            await self.close()
