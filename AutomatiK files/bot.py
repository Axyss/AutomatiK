# coding=utf-8
import os
import re
import threading
import asyncio
import base64
import json
import importlib
import random
import time

import discord
from discord.ext import commands

from core import updates
from core.log_manager import logger
from core.lang_manager import LangManager
from core.game import Game
from core.config_manager import ConfigManager
from core.db_manager import DatabaseManager


class Loader:
    imported_modules = []
    ascii_art = r"""                _                        _   _ _  __
     /\        | |                      | | (_) |/ /
    /  \  _   _| |_ ___  _ __ ___   __ _| |_ _| ' /
   / /\ \| | | | __/ _ \| '_ ` _ \ / _` | __| |  <
  / ____ \ |_| | || (_) | | | | | | (_| | |_| | . \
 /_/    \_\__,_|\__\___/|_| |_| |_|\__,_|\__|_|_|\_\  {}
                                               """

    @staticmethod
    def print_ascii_art():
        print(Loader.ascii_art.format(Client.VERSION))
        time.sleep(0.1)

    @staticmethod
    def start():
        """Adds the ascii art and requests the token at the start of the program."""
        Client.clear_console()
        Loader.print_ascii_art()
        token = Loader.load_token()

        Client.clear_console()
        Loader.print_ascii_art()

        logger.info("Loading...")
        return token

    @staticmethod
    def load_token():
        if "Secret Token.json" not in os.listdir("."):  # Requests token and writes It in "Secret Token.json"
            with open("Secret Token.json", "w") as token_file:
                logger.info("Please introduce your bot's secret token: ")
                token = base64.b64encode(input().encode("utf-8")).decode("utf-8")  # Encodes token
                json.dump({"secret_token": token}, token_file, indent=2)
        else:  # Loads token from file
            with open("Secret Token.json") as token_file:
                try:
                    token = json.load(token_file)["secret_token"]
                except json.decoder.JSONDecodeError:  # Avoids exception when closing without providing a valid token
                    token_file.close()
                    os.remove("Secret Token.json")
                    token = Loader.load_token()
        return token

    @staticmethod
    def load_modules():
        """Imports and instances all the modules automagically."""
        modules = []

        for i in os.listdir("modules"):
            module_name, module_extension = os.path.splitext(i)

            if module_extension == ".py" and module_name != "__init__":
                try:
                    imported_module = importlib.import_module(f"modules.{module_name}")  # Imports module
                    # Creates an instance of the Main class of the imported module
                    Klass = getattr(imported_module, "Main")
                    Loader.imported_modules.append(imported_module)
                    modules.append(Klass())
                except AttributeError:
                    logger.exception(f"Module '{module_name}' couldn't be loaded")
                except:
                    logger.exception(f"Unexpected error while loading module {module_name}")

        logger.info(f"{len(modules)} modules loaded")
        return modules

    @staticmethod
    def reload_modules():
        """Reimports and instances all the modules automagically."""
        Loader.imported_modules = [importlib.reload(i) for i in Loader.imported_modules]  # Re-imports the modules
        importlib.invalidate_caches()
        logger.info(f"{len(Loader.imported_modules)} modules loaded")
        return [getattr(i, "Main")() for i in Loader.imported_modules]  # Instances from the modules


class Client(commands.Bot):
    VERSION = "v2.0"

    def __init__(self, command_prefix, self_bot, intents):
        commands.Bot.__init__(self, command_prefix=command_prefix, self_bot=self_bot, intents=intents)
        self.lm = LangManager(lang_dir="./lang/")
        self.cfg = ConfigManager("config.json")
        self.mongo = DatabaseManager(host=self.cfg.get_mongo_host(),
                                     # int conversion in case 'port' comes from an env var
                                     port=int(self.cfg.get_mongo_port()),
                                     username=self.cfg.get_mongo_user(),
                                     password=self.cfg.get_mongo_pwd(),
                                     auth_source=self.cfg.get_mongo_auth_source(),
                                     auth_mechanism=self.cfg.get_mongo_auth_mechanism())

        self.LOGO_URL = "https://raw.githubusercontent.com/Axyss/AutomatiK/master/docs/assets/ak_logo.png"
        self.AVATAR_URL = "https://avatars3.githubusercontent.com/u/55812692"
        self.MODULES = None  # Contains the instance of the Main class of every module
        self.main_loop = False  # Variable used to start or stop the main loop

        self.remove_command("help")
        self.init_commands()

    async def on_ready(self):
        if self.MODULES is None:  # Prevents the next lines from executing more than once when reconnecting
            self.load_resources()

            updater = updates.Updates(local_version=Client.VERSION, link="https://github.com/Axyss/AutomatiK/releases/")
            threading.Thread(target=updater.start_checking, daemon=True).start()  # Update checker
            threading.Thread(target=self.cli, daemon=True).start()

            await self.change_presence(status=discord.Status.online,
                                       activity=discord.Game("!mk help")
                                       )
            logger.info(f"AutomatiK bot {Client.VERSION} now online")

    @staticmethod
    def clear_console():
        local_os = os.name
        if local_os in ("nt", "dos"):
            os.system("cls")
        elif local_os in ("linux", "osx", "posix"):
            os.system("clear")
        else:
            print("\n" * 120)

    def cli(self):
        """Manages the console commands."""
        while True:
            cli_command = input("")

            if cli_command == "shutdown":
                self.main_loop = False
                logger.info("Stopping...")
                os._exit(1)
            else:
                logger.error("Unknown terminal command. Use 'shutdown' to stop the bot.")

    def load_resources(self, reload=False):
        """Loads configuration, modules and language packages."""
        self.MODULES = Loader.reload_modules() if reload else Loader.load_modules()
        self.cfg.load_config()
        self.lm.load_lang_packages()
        return True

    def generate_message(self, ctx, title, link):
        """Generates the messages for the free games."""
        guild_cfg = self.mongo.get_guild_config(ctx.guild)
        guild_lang = guild_cfg["lang"]

        draft = random.choice(self.lm.get_message(guild_lang, "generic_messages")).format(title, link)
        if guild_cfg["mention_status"]:  # Adds the mention_status value from config
            draft = guild_cfg["mentioned_role"] + " " + draft

        return draft

    async def on_command_error(self, ctx, error):  # The second parameter is the error's information
        """Method used for error handling regarding the discord.py library."""
        guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

        if isinstance(error, discord.ext.commands.MissingPermissions):
            await ctx.channel.send(self.lm.get_message(guild_lang, "missing_permissions"))

        elif isinstance(error, discord.ext.commands.errors.NoPrivateMessage):
            pass

        elif isinstance(error, discord.ext.commands.errors.CommandNotFound):
            await ctx.channel.send(self.lm.get_message(guild_lang, "invalid_command"))

        elif isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
            await ctx.channel.send(self.lm.get_message(guild_lang, "cooldown_error").format(int(error.retry_after)))
        else:
            try:
                raise error
            except:
                logger.exception("Unexpected error")

    def init_commands(self):

        @self.command()
        @commands.guild_only()
        @commands.cooldown(3, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def notify(ctx, *args):
            """Command to notify free games from non-supported platforms."""
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

            args = list(args)
            link = args[-1]
            args.pop()
            game_name = " ".join(args)  # Uses the args to generate the game name

            await ctx.channel.purge(limit=1)
            await ctx.channel.send(self.generate_message(ctx, game_name, link) +
                                   self.lm.get_message(guild_lang, "notify_thanks").format(ctx.author.id)
                                   )  # Adds politeness

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def mention(ctx, role_id):
            """Manages the mentions of the bot's messages."""
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

            if re.search("^<@&\w", role_id) and re.search(">$", role_id):
                # If the string follows the std structure of a role <@&1234>
                self.mongo.update_guild_config(ctx.guild, {"mention_role": role_id})
                await ctx.channel.send(self.lm.get_message(guild_lang, "mention_established"))
                logger.info(f"AutomatiK will now mention '{role_id}'")
            else:
                await ctx.channel.send(self.lm.get_message(guild_lang, "mention_error"))

        @self.command(aliases=["help"])
        @commands.guild_only()
        @commands.cooldown(1, 60, commands.BucketType.user)
        async def helpme(ctx):
            """Help command that uses embeds."""
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

            embed_help = discord.Embed(title=f"AutomatiK {Client.VERSION} Help ",
                                       description=self.lm.get_message(guild_lang, "embed_description"),
                                       color=0x00BFFF
                                       )
            embed_help.set_footer(text=self.lm.get_message(guild_lang, "embed_footer"),
                                  icon_url=self.AVATAR_URL
                                  )
            embed_help.set_thumbnail(url=self.LOGO_URL)

            embed_help.add_field(name=self.lm.get_message(guild_lang, "embed_field1_name"),
                                 value="".join(self.lm.get_message(guild_lang, "embed_field1_value")), inline=False
                                 )
            embed_help.add_field(name=u"\U0001F6E0 " + self.lm.get_message(guild_lang, "embed_field2_name"),
                                 value="".join(self.lm.get_message(guild_lang, "embed_field2_value")),
                                 inline=False)

            await ctx.channel.send(embed=embed_help)
            logger.debug(f"Command '{ctx.command}' invoked by {ctx.author}")

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def start(ctx):
            """Starts the AutomatiK service."""
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

            if self.main_loop:  # If service already started
                await ctx.channel.send(self.lm.get_message(guild_lang, "start_already"))
                return None

            self.main_loop = True  # Changes It to True so the main loop can start
            await ctx.channel.send(
                self.lm.get_message(guild_lang, "start_success").format("<#" + str(ctx.channel.id) + ">")
            )
            logger.info(f"Main service was started on #{ctx.channel} by {str(ctx.author)}")

            while self.main_loop:  # MAIN LOOP
                for i in self.MODULES:
                    free_games = i.get_free_games()
                    if free_games:
                        free_games = db.check_database(f"{i.MODULE_ID.upper()}_TABLE", free_games, int(i.THRESHOLD))
                        for j in free_games:
                            await ctx.channel.send(self.generate_message(j.name, j.link))

                await asyncio.sleep(300)  # It will look for free games every 5 minutes

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def stop(ctx):
            """Stops the main service on the guild where It is executed"""
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

            if not self.main_loop:  # If service already stopped
                await ctx.channel.send(self.lm.get_message(guild_lang, "stop_already"))
                return False

            self.main_loop = False  # Stops the loop by changing the boolean which maintains It active
            await ctx.channel.send(self.lm.get_message(guild_lang, "stop_success"))
            logger.info(f"Main service was stopped by {str(ctx.author)}")

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        async def status(ctx):
            """Shows the bot's status."""
            cfg = self.mongo.get_guild_config(ctx.guild)

            embed_status = discord.Embed(title=self.lm.get_message(cfg["lang"], "status"),
                                         description=self.lm.get_message(cfg["lang"], "status_description"),
                                         color=0x00BFFF
                                         )
            embed_status.set_footer(text=self.lm.get_message(cfg["lang"], "embed_footer"),
                                    icon_url=self.AVATAR_URL
                                    )
            embed_status.set_thumbnail(url=self.LOGO_URL)
            embed_status.add_field(name=self.lm.get_message(cfg["lang"], "status_main"),
                                   value=self.lm.get_message(cfg["lang"], "status_active")
                                   if cfg["services"]["main"]
                                   else self.lm.get_message(cfg["lang"], "status_inactive")
                                   )

            for i in self.MODULES:
                value = self.lm.get_message(cfg["lang"], "status_active") \
                    if cfg["services"][i.MODULE_ID] else self.lm.get_message(cfg["lang"], "status_inactive")

                embed_status.add_field(name=i.SERVICE_NAME,
                                       value=value,
                                       )
            await ctx.channel.send(embed=embed_status)
            logger.debug(f"Command '{ctx.command}' invoked by {ctx.author}")

        @self.command(aliases=["module"])
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def modules(ctx):
            """Shows information about the loaded modules."""
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

            module_ids = [i.MODULE_ID for i in self.MODULES]
            module_names = [i.SERVICE_NAME for i in self.MODULES]
            module_authors = [i.AUTHOR for i in self.MODULES]

            embed_module = discord.Embed(title=self.lm.get_message(guild_lang, "modules"),
                                         description=self.lm.get_message(guild_lang, "modules_description"),
                                         color=0x00BFFF
                                         )
            embed_module.set_footer(text=self.lm.get_message(guild_lang, "embed_footer"),
                                    icon_url=self.AVATAR_URL
                                    )
            embed_module.set_thumbnail(url=self.LOGO_URL)
            embed_module.add_field(name="**ModuleID**", value="\n".join(module_ids))
            embed_module.add_field(name=self.lm.get_message(guild_lang, "modules_service"),
                                   value="\n".join(module_names)
                                   )
            embed_module.add_field(name=self.lm.get_message(guild_lang, "modules_author"),
                                   value="\n".join(module_authors)
                                   )

            await ctx.channel.send(embed=embed_module)

        @self.command(aliases=["disable"])
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def enable(ctx, service):
            """Global manager to enable/disable modules and other services."""
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

            introduced_command = str(ctx.invoked_with)
            user_decision = True if introduced_command == "enable" else False

            for i in self.MODULES:
                if service.lower() == i.MODULE_ID.lower():
                    self.mongo.update_guild_config(ctx.guild, {"services." + service.lower(): user_decision})

                    await ctx.channel.send(
                        self.lm.get_message(guild_lang, f"module_{introduced_command}d").format(f"**{service}**")
                    )
                    logger.info(f"{service.capitalize()} module {introduced_command}d by {ctx.author}")
                    return True

            await ctx.channel.send(self.lm.get_message(guild_lang, f"{introduced_command}_unknown"))
            return False

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def language(ctx, lang_code):
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

            if lang_code not in self.lm.get_lang_packages_metadata()[0]:  # If the language .json does not exist
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
            lang_ids, lang_names, lang_authors = self.lm.get_lang_packages_metadata()
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

            embed_langs = discord.Embed(title=self.lm.get_message(guild_lang, "languages"),
                                        description=self.lm.get_message(guild_lang, "languages_description"),
                                        color=0x00BFFF
                                        )
            embed_langs.set_footer(text=self.lm.get_message(guild_lang, "embed_footer"),
                                   icon_url=self.AVATAR_URL
                                   )
            embed_langs.set_thumbnail(url=self.LOGO_URL)
            embed_langs.add_field(name="LangID", value="\n".join(lang_ids))
            embed_langs.add_field(name=self.lm.get_message(guild_lang, "language"), value="\n".join(lang_names))
            embed_langs.add_field(name=self.lm.get_message(guild_lang, "modules_author"), value="\n".join(lang_authors))

            await ctx.channel.send(embed=embed_langs)

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def reload(ctx):
            """Reloads configuration, modules and language packages."""
            guild_lang = self.mongo.get_guild_config(ctx.guild)["lang"]

            logger.info("Reloading...")
            was_started = bool(self.main_loop)
            self.main_loop = False
            self.load_resources(reload=True)
            self.main_loop = was_started

            await ctx.channel.send(self.lm.get_message(guild_lang, "reload_completed"))
            logger.info("Reload completed")


if __name__ == "__main__":

    automatik = Client(command_prefix="!mk ", self_bot=False, intents=discord.Intents.default())
    try:
        automatik.run(base64.b64decode(Loader.start().encode("utf-8")).decode("utf-8"))

    except discord.errors.LoginFailure:
        logger.error("Invalid token, please make sure It's valid. Press enter to exit...")
        os.remove("Secret Token.json")
        input()
