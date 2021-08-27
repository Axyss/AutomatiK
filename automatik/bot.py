# coding=utf-8
import asyncio
import queue
import random

import discord
import psutil
from discord.ext import commands, tasks

from automatik import logger, __version__, LOGO_URL, AVATAR_URL
from .core.config import ConfigManager
from .core.db import Database
from .core.errors import InvalidGameDataException
from .core.lang import LangLoader
from .core.modules import ModuleLoader


class AutomatikBot(commands.Bot):
    def __init__(self, command_prefix, self_bot, intents):
        commands.Bot.__init__(self, command_prefix=command_prefix, self_bot=self_bot, intents=intents)
        self.is_first_exec = True  # Used inside 'on_ready' to execute certain parts of the method only once
        self.lm = LangLoader("./automatik/lang")
        self.cfg = ConfigManager("./automatik/config.yml")
        self.mongo = Database(host=self.cfg.get_mongo_value("host"),
                              port=self.cfg.get_mongo_value("port"),
                              username=self.cfg.get_mongo_value("user"),
                              password=self.cfg.get_mongo_value("password"),
                              auth_source=self.cfg.get_mongo_value("auth_source"),
                              auth_mechanism=self.cfg.get_mongo_value("auth_mechanism"))

        self.main_loop = False  # Variable used to start or stop the main loop
        self.game_queue = queue.Queue()  # Free games are stored here temporary while the 'broadcaster' routine
        # delivers the messages
        self.game_queue_cache = []

        self.load_resources()
        self.init_main_loop.start()
        self.init_message_broadcaster.start()
        self.remove_command("help")  # Must be removed before command init. so the 'help' alias is available
        self.init_commands()

    async def on_ready(self):
        if self.is_first_exec:
            logger.info(f"AutomatiK bot {__version__} online")
            self.is_first_exec = False
        await self.change_presence(status=discord.Status.online, activity=discord.Game("!mk help"))

    async def on_guild_join(self, guild):
        self.mongo.create_guild_config(guild)

    def load_resources(self):
        """Loads configuration, modules and language packages."""
        ModuleLoader.load_modules()
        self.cfg.load_config()
        self.lm.load_lang_packages()
        # Services are added to the documents from the 'configs' collection on runtime
        self.mongo.insert_missing_or_new_services()
        # todo add the equivalent to 'Database.insert_missing_or_new_services' for guild configs

    def generate_message(self, guild_cfg, game):
        """Generates a 'X free on Y' type message."""
        message = random.choice(self.lm.get_message(guild_cfg["lang"], "generic_messages")).format(game.NAME, game.LINK)

        if guild_cfg["services"]["mention"]:
            # todo Fix exception when the upper condition is True but there is no mention role set
            message = guild_cfg["mention_role"] + " " + message
        return message

    async def on_command_error(self, ctx, error):
        """Method used for error handling regarding the discord.py library."""
        if isinstance(error, discord.ext.commands.NoPrivateMessage) or isinstance(ctx.channel, discord.DMChannel):
            # Highest priority situation
            return None

        if isinstance(error, discord.ext.commands.CommandInvokeError):
            error = error.original  # CommandInvokeError is too generic, this gets the exception which raised it

        guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

        if isinstance(error, discord.ext.commands.MissingPermissions):
            # User lacks permissions
            await ctx.channel.send(self.lm.get_message(guild_lang, "missing_permissions"))

        elif isinstance(error, discord.ext.commands.errors.CommandNotFound):
            await ctx.channel.send(self.lm.get_message(guild_lang, "invalid_command"))

        elif isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
            await ctx.channel.send(self.lm.get_message(guild_lang, "cooldown_error").format(int(error.retry_after)))

        elif isinstance(error, discord.errors.Forbidden):
            # Bot kicked or lacks permissions to send messages
            pass

        else:  # Without this, unexpected errors wouldn't show up
            try:
                raise error
            except:
                logger.exception("Unexpected error")

    @tasks.loop(seconds=1)
    async def init_main_loop(self):
        if self.main_loop:  # MAIN LOOP
            for module in ModuleLoader.modules:
                try:
                    retrieved_free_games = module.get_free_games()
                    stored_free_games = self.mongo.get_free_games_by_module_id(module.MODULE_ID)
                except InvalidGameDataException:
                    logger.debug(f"Ignoring results from the '{module.MODULE_ID}' module this iteration")
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
                            # If the channel ID is invalid or the message couldn't be sent for other reasons
                            fail += 1
                        except:
                            fail += 1
                            logger.exception("Unexpected error")
            logger.info(f"Messages sent to all guilds. Success: {success} | Fail: {fail}")

    def init_commands(self):

        # Public commands

        @self.command(aliases=["help"])
        @commands.guild_only()
        @commands.cooldown(1, 60, commands.BucketType.user)
        async def helpme(ctx):
            """Help command that uses embeds."""
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

            embed_help = discord.Embed(title=f"AutomatiK {__version__} Help ",
                                       description=self.lm.get_message(guild_lang, "help_description"),
                                       color=0x00BFFF
                                       )
            embed_help.set_footer(text=self.lm.get_message(guild_lang, "help_footer"),
                                  icon_url=AVATAR_URL
                                  )
            embed_help.set_thumbnail(url=LOGO_URL)

            embed_help.add_field(name=self.lm.get_message(guild_lang, "help_field1_name"),
                                 value="".join(self.lm.get_message(guild_lang, "help_field1_value")),
                                 inline=False
                                 )
            if ctx.author.guild_permissions.administrator:
                embed_help.add_field(name=u"\U0001F6E0 " + self.lm.get_message(guild_lang, "help_field2_name"),
                                     value="".join(self.lm.get_message(guild_lang, "help_field2_value")),
                                     inline=False
                                     )
            if str(ctx.author) in self.cfg.get_general_value("bot_owners"):  # If command author a bot owner
                embed_help.add_field(name=u"\U0001F451 " + self.lm.get_message(guild_lang, "help_field3_name"),
                                     value="".join(self.lm.get_message(guild_lang, "help_field3_value")),
                                     inline=False
                                     )
            await ctx.channel.send(embed=embed_help)
            logger.debug(f"Command '{ctx.command}' invoked by {ctx.author}")

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        async def status(ctx):
            """Shows information about the bot based on the guild (modules, selected channel...)."""
            guild_cfg = self.mongo.get_guild_config(ctx.guild)
            guild_lang = guild_cfg["lang"]
            temp_value = None

            embed_status = discord.Embed(title=self.lm.get_message(guild_lang, "status"),
                                         description=self.lm.get_message(guild_lang, "status_description"),
                                         color=0x00BFFF
                                         )
            embed_status.set_footer(text=self.lm.get_message(guild_lang, "help_footer"),
                                    icon_url=AVATAR_URL
                                    )
            embed_status.set_thumbnail(url=LOGO_URL)

            if guild_cfg["selected_channel"]:
                temp_value = self.lm.get_message(guild_lang, "status_active") + "\n" + guild_cfg["selected_channel"]
            else:
                temp_value = self.lm.get_message(guild_lang, "status_inactive")

            embed_status.add_field(name=self.lm.get_message(guild_lang, "status_main"), value=temp_value)

            for i in ModuleLoader.modules:
                if guild_cfg["services"][i.MODULE_ID]:
                    value = self.lm.get_message(guild_lang, "status_active")
                else:
                    value = self.lm.get_message(guild_lang, "status_inactive")

                embed_status.add_field(name=i.SERVICE_NAME,
                                       value=value,
                                       )
            await ctx.channel.send(embed=embed_status)
            logger.debug(f"Command '{ctx.command}' invoked by {ctx.author}")

        # Guild administrator commands

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def select(ctx, channel=None):
            """Starts announcing free games in the guild where it is executed or in the specified channel."""
            guild_cfg = self.mongo.get_guild_config(ctx.guild)
            guild_lang = guild_cfg["lang"]
            selected_channel = ctx.channel.mention if channel is None else channel

            if channel is not None and not (channel.startswith("<#") and channel.endswith(">")):
                await ctx.channel.send(self.lm.get_message(guild_lang, "select_invalid_channel"))
                return None

            self.mongo.update_guild_config(ctx.guild, {"selected_channel": selected_channel})
            await ctx.channel.send(self.lm.get_message(guild_lang, "select_success").format(selected_channel))

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def unselect(ctx):
            """Stops announcing free games in the guild."""
            guild_cfg = self.mongo.get_guild_config(ctx.guild)
            guild_lang = guild_cfg["lang"]
            guild_selected_channel = guild_cfg["selected_channel"]

            if guild_selected_channel is None:
                await ctx.channel.send(self.lm.get_message(guild_lang, "unselect_already")
                                       .format(guild_selected_channel))
                return None

            self.mongo.update_guild_config(ctx.guild, {"selected_channel": None})
            await ctx.channel.send(self.lm.get_message(guild_lang, "unselect_success").format(guild_selected_channel))

        @self.command(aliases=["disable"])
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def enable(ctx, service):
            """Guild dependant command to enable/disable modules and other settings."""
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

            introduced_command = str(ctx.invoked_with)
            user_decision = True if introduced_command == "enable" else False

            for module in ModuleLoader.modules:
                if service.lower() == module.MODULE_ID.lower():
                    self.mongo.update_guild_config(ctx.guild, {"services." + service.lower(): user_decision})

                    await ctx.channel.send(
                        self.lm.get_message(guild_lang, f"module_{introduced_command}d").format(service)
                    )
                    logger.info(f"{service.capitalize()} module {introduced_command}d by {ctx.author}")
                    return True

            await ctx.channel.send(self.lm.get_message(guild_lang, f"enable_unknown").format(introduced_command))
            return False

        @self.command(aliases=["module"])
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def modules(ctx):
            """Shows information about the loaded modules."""
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

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

            await ctx.channel.send(embed=embed_module)

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def mention(ctx, mention_role):
            """Manages the mentions of the bot's messages."""
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

            # If the string follows the std structure of a role <@&1234>
            if mention_role.startswith("<@&") and mention_role.endswith(">"):
                self.mongo.update_guild_config(ctx.guild, {"mention_role": mention_role})
                await ctx.channel.send(self.lm.get_message(guild_lang, "mention_established"))
                logger.info(f"AutomatiK will now mention '{mention_role}'")
            else:
                await ctx.channel.send(self.lm.get_message(guild_lang, "mention_error"))

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def language(ctx, lang_code):
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

            if lang_code not in self.lm.get_lang_packages_metadata()[0]:  # If the language package does not exist
                await ctx.channel.send(self.lm.get_message(guild_lang, "language_error"))
                return

            self.mongo.update_guild_config(ctx.guild, {"lang": lang_code})
            await ctx.channel.send(self.lm.get_message(lang_code, "language_changed"))
            logger.info(f"Language changed to '{lang_code}' by {ctx.author}")

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def languages(ctx):
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]
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

            await ctx.channel.send(embed=embed_langs)

        # Owner commands
        # todo Replace if statements that check owners in commands for decorators

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        async def start(ctx):
            """Starts/stops the main loop that will look for free games every 5 minutes."""
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

            if str(ctx.author) not in self.cfg.get_general_value("bot_owners"):  # If command author not a bot owner
                return None

            if self.main_loop:
                await ctx.channel.send(self.lm.get_message(guild_lang, "start_already"))
                return None

            self.main_loop = True
            await ctx.channel.send(self.lm.get_message(guild_lang, "start_success"))
            logger.info(f"Main service was started globally by {str(ctx.author)}")

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        async def stop(ctx):
            """Stops the loop that looks for free games GLOBALLY."""
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

            if str(ctx.author) not in self.cfg.get_general_value("bot_owners"):  # If command author not a bot owner
                return None

            if not self.main_loop:  # If service already stopped
                await ctx.channel.send(self.lm.get_message(guild_lang, "stop_already"))
                return None

            self.main_loop = False
            await ctx.channel.send(self.lm.get_message(guild_lang, "stop_success"))
            logger.info(f"Main service was stopped globally by {str(ctx.author)}")

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def reload(ctx):
            """Reloads configuration, modules and language packages."""
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

            if str(ctx.author) not in self.cfg.get_general_value("bot_owners"):  # If command author not a bot owner
                return None
            logger.info("Reloading..")
            was_started = self.main_loop
            self.main_loop = False
            try:
                self.load_resources()
                await ctx.channel.send(self.lm.get_message(guild_lang, "reload_completed"))
                logger.info("Reload completed")
            except:
                await ctx.channel.send(self.lm.get_message(guild_lang, "unexpected_error"))
                logger.error("An error ocurred while reloading")
            finally:
                self.main_loop = was_started

        @self.command(aliases=["statistics"])
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        async def stats(ctx):
            """Shows some overall statistics of the bot."""
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]
            message_queue_len = len(self.guilds) * (len(self.game_queue_cache) + self.game_queue.qsize())

            if str(ctx.author) not in self.cfg.get_general_value("bot_owners"):  # If command author not a bot owner
                return None

            embed_stats = discord.Embed(title="\U0001f4c8 " + self.lm.get_message(guild_lang, "stats"),
                                        description=self.lm.get_message(guild_lang, "stats_description"),
                                        color=0x00BFFF)
            embed_stats.set_footer(text=self.lm.get_message(guild_lang, "help_footer"),
                                   icon_url=AVATAR_URL)
            embed_stats.set_thumbnail(url=LOGO_URL)

            embed_stats.add_field(name="Guilds", value=str(len(self.guilds)))
            embed_stats.add_field(name=self.lm.get_message(guild_lang, "stats_owners_field"),
                                  value="\n".join(self.cfg.get_general_value("bot_owners")))
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

            await ctx.channel.send(embed=embed_stats)
            logger.debug(f"Command '{ctx.command}' invoked by {ctx.author}")

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        async def shutdown(ctx):
            """Shuts down the bot process completely."""
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]
            message_queue_len = len(self.guilds) * (len(self.game_queue_cache) + self.game_queue.qsize())

            if str(ctx.author) not in self.cfg.get_general_value("bot_owners"):  # If command author not a bot owner
                return None

            if not self.game_queue.empty() or self.game_queue_cache:
                await ctx.channel.send(self.lm.get_message(guild_lang, "shutdown_abort").format(message_queue_len))
                return None

            await ctx.channel.send(self.lm.get_message(guild_lang, "shutdown_success"))
            logger.info("Shutting down..")
            self.main_loop = False
            await self.close()
