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
from core.config_manager import ConfigManager
from core.module_manager import db, Game


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
            module_name = os.path.splitext(i)[0]
            module_extension = os.path.splitext(i)[1]

            if module_extension == ".py" and module_name != "__init__":
                try:
                    # noinspection PyPep8Naming
                    imported_module = importlib.import_module(f"modules.{module_name}")
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
        Loader.imported_modules = [importlib.reload(i) for i in Loader.imported_modules]  # Reimports the modules
        importlib.invalidate_caches()
        logger.info(f"{len(Loader.imported_modules)} modules loaded")
        return [getattr(i, "Main")() for i in Loader.imported_modules]  # Instances from the modules


class Client(commands.Bot, LangManager, ConfigManager):

    VERSION = "v1.3"

    def __init__(self, command_prefix, self_bot):
        commands.Bot.__init__(self, command_prefix=command_prefix, self_bot=self_bot)
        LangManager.__init__(self, lang_dir="lang/")
        ConfigManager.__init__(self, config_name="config.json")

        self.main_loop = False  # Variable which starts or stops the main loop
        self.MODULES = None
        self.LOGO_URL = "https://raw.githubusercontent.com/Axyss/AutomatiK/master/AutomatiK%20files/assets/ak_logo.png"
        self.AVATAR_URL = "https://avatars3.githubusercontent.com/u/55812692"
        self.remove_command("help")
        self.is_started = False
        self.init_commands()

    async def on_ready(self):
        if not self.is_started:  # Prevents the next lines from executing more than once when reconnecting
            self.load_resources()

            updater = updates.Updates(local_version=Client.VERSION, link="https://github.com/Axyss/AutomatiK/releases/")
            threading.Thread(target=updater.start_checking, daemon=True).start()  # Update checker
            threading.Thread(target=self.cli, daemon=True).start()

            await self.change_presence(status=discord.Status.online,  # Changes status to "online"
                                       activity=discord.Game("!mk help")  # Changes activity (playing)
                                       )
            logger.info(f"AutomatiK bot {Client.VERSION} now online")
            self.is_started = True

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
        self.load_config()
        self.create_config_keys(self.MODULES)
        self.check_config_changes()
        self.load_lang(self.data_config["lang"])
        return True

    def get_status(self, service):
        """Translates boolean values to the strings showed in '!mk status'."""
        return self.lang["status_active"] if self.data_config[service] else self.lang["status_inactive"]

    def generate_message(self, title, link):
        """Generates the messages for the free games."""
        draft = random.choice(self.lang["generic_messages"]).format(title, link)
        if self.data_config["mention_status"]:  # Adds the mention_status value from config
            draft = self.data_config["mentioned_role"] + " " + draft

        return draft

    async def on_command_error(self, ctx, error):  # The second parameter is the error's information
        """Method used for error handling regarding the discord.py library."""
        if isinstance(error, discord.ext.commands.MissingPermissions):
            await ctx.channel.send(self.lang["missing_permissions"])

        elif isinstance(error, discord.ext.commands.errors.NoPrivateMessage):
            pass

        elif isinstance(error, discord.ext.commands.errors.CommandNotFound):
            await ctx.channel.send(self.lang["invalid_command"])

        elif isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
            await ctx.channel.send(self.lang["cooldown_error"].format(int(error.retry_after)))
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
            args = list(args)

            # Stores the link in another variable and removes It from args
            link = args[-1]
            args.pop()

            game_name = " ".join(args)  # Converts list to string with spaces between elements
            await ctx.channel.purge(limit=1)
            await ctx.channel.send(self.generate_message(game_name, link)
                                   + self.lang["notify_thanks"].format(ctx.author.id)  # Adds politeness
                                   )

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def mention(ctx, role_id):
            """Manages the mentions of the bot's messages."""
            if re.search("^<@&\w", role_id) and re.search(">$", role_id):
                # If the string follows the std structure of a role <@&1234>
                self.edit_config("mentioned_role", role_id)
                await ctx.channel.send(self.lang["mention_established"])
                logger.info(f"AutomatiK will now mention '{role_id}'")
            else:
                await ctx.channel.send(self.lang["mention_error"])

        @self.command(aliases=["help"])
        @commands.guild_only()
        @commands.cooldown(1, 60, commands.BucketType.user)
        async def helpme(ctx):
            """Help command that uses embeds."""
            embed_help = discord.Embed(title=f"AutomatiK {Client.VERSION} Help ",
                                       description=self.lang["embed_description"],
                                       color=0x00BFFF
                                       )
            embed_help.set_footer(text=self.lang["embed_footer"],
                                  icon_url=self.AVATAR_URL
                                  )
            embed_help.set_thumbnail(url=self.LOGO_URL)

            embed_help.add_field(name=self.lang["embed_field1_name"],
                                 value="".join(self.lang["embed_field1_value"]), inline=False
                                 )
            embed_help.add_field(name=u"\U0001F6E0 " + self.lang["embed_field2_name"],
                                 value="".join(self.lang["embed_field2_value"]),
                                 inline=False)

            await ctx.channel.send(embed=embed_help)
            logger.debug(f"Command '{ctx.command}' invoked by {ctx.author}")

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def start(ctx):
            """Starts the AutomatiK service."""
            if self.main_loop:  # If service already started
                await ctx.channel.send(self.lang["start_already"])
                return None

            self.main_loop = True  # Changes It to True so the main loop can start
            await ctx.channel.send(self.lang["start_success"].format("<#" + str(ctx.channel.id) + ">"))
            logger.info(f"Main service was started on #{ctx.channel} by {str(ctx.author)}")

            while self.main_loop:  # MAIN LOOP
                for i in self.MODULES:
                    if not self.data_config[f"{i.MODULE_ID}_status"]:  # Prevents games from getting added to the db
                        continue                                       # when a module isn't enabled
                    free_games = i.get_free_games()
                    # If there is at least one element this will put It in a list
                    free_games = [free_games] if isinstance(free_games, Game) else free_games
                    if free_games:
                        try:  # Checks if module author specified a threshold
                            i.THRESHOLD
                        except AttributeError:
                            i.THRESHOLD = 6
                        free_games = db.check_database(f"{i.MODULE_ID.upper()}_TABLE", free_games, int(i.THRESHOLD))
                        for j in free_games:
                            await ctx.channel.send(self.generate_message(j.name, j.link))

                await asyncio.sleep(300)  # It will look for free games every 5 minutes

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def stop(ctx):
            """Stops the AutomatiK service"""
            if not self.main_loop:  # If service already stopped
                await ctx.channel.send(self.lang["stop_already"])
                return False

            self.main_loop = False  # Stops the loop by changing the boolean which maintains It active
            await ctx.channel.send(self.lang["stop_success"])
            logger.info(f"Main service was stopped by {str(ctx.author)}")

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        async def status(ctx):
            """Shows the bot's status."""
            embed_status = discord.Embed(title=self.lang["status"],
                                         description=self.lang["status_description"],
                                         color=0x00BFFF
                                         )
            embed_status.set_footer(text=self.lang["embed_footer"],
                                    icon_url=self.AVATAR_URL
                                    )
            embed_status.set_thumbnail(url=self.LOGO_URL)
            embed_status.add_field(name=self.lang["status_main"], value=self.lang["status_active"]
                                   if self.main_loop else self.lang["status_inactive"]
                                   )

            for i in self.MODULES:
                embed_status.add_field(name=i.SERVICE_NAME,
                                       value=self.get_status(f"{i.MODULE_ID}_status")
                                       )
            await ctx.channel.send(embed=embed_status)
            logger.debug(f"Command '{ctx.command}' invoked by {ctx.author}")

        @self.command(aliases=["module"])
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def modules(ctx):
            """Shows information about the loaded modules."""
            module_ids = [i.MODULE_ID for i in self.MODULES]
            module_names = [i.SERVICE_NAME for i in self.MODULES]
            module_authors = [i.AUTHOR for i in self.MODULES]

            embed_module = discord.Embed(title=self.lang["modules"],
                                         description=self.lang["modules_description"],
                                         color=0x00BFFF
                                         )
            embed_module.set_footer(text=self.lang["embed_footer"],
                                    icon_url=self.AVATAR_URL
                                    )
            embed_module.set_thumbnail(url=self.LOGO_URL)
            embed_module.add_field(name="**ModuleID**", value="\n".join(module_ids))
            embed_module.add_field(name=self.lang["modules_service"], value="\n".join(module_names))
            embed_module.add_field(name=self.lang["modules_author"], value="\n".join(module_authors))

            await ctx.channel.send(embed=embed_module)

        @self.command(aliases=["disable"])
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def enable(ctx, service):
            """Global manager to enable/disable modules and some other services."""
            introduced_command = str(ctx.invoked_with)
            user_decision = True if introduced_command == "enable" else False

            for i in self.MODULES:
                if service.lower() == i.MODULE_ID.lower():
                    self.edit_config(f"{i.MODULE_ID}_status", user_decision)

                    await ctx.channel.send(self.lang[f"module_{introduced_command}d"].format(service.capitalize()))
                    logger.info(f"{service.capitalize()} module {introduced_command}d by {ctx.author}")
                    return True

            await ctx.channel.send(self.lang[f"{introduced_command}_unknown"])
            return False

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def language(ctx, lang_code):

            if (lang_code + ".json") not in os.listdir("lang"):  # If the language .json does not exist
                await ctx.channel.send(self.lang["language_error"])

            else:  # Edits the config value which contains what lang is going to be loaded
                self.edit_config("lang", lang_code)
                self.load_lang(self.data_config["lang"])  # Reloads the language
                await ctx.channel.send(self.lang["language_changed"])
                logger.info(f"Language changed to '{lang_code}' by {ctx.author}")

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def languages(ctx):
            lang_name, lang_author = self.get_lang_metadata()
            lang_ids = self.get_lang_ids()

            embed_langs = discord.Embed(title=self.lang["languages"],
                                        description=self.lang["languages_description"],
                                        color=0x00BFFF
                                        )
            embed_langs.set_footer(text=self.lang["embed_footer"],
                                   icon_url=self.AVATAR_URL
                                   )
            embed_langs.set_thumbnail(url=self.LOGO_URL)
            embed_langs.add_field(name="LangID", value="\n".join(lang_ids))
            embed_langs.add_field(name=self.lang["language"], value="\n".join(lang_name))
            embed_langs.add_field(name=self.lang["modules_author"], value="\n".join(lang_author))

            await ctx.channel.send(embed=embed_langs)

        @self.command()
        @commands.guild_only()
        @commands.cooldown(2, 10, commands.BucketType.user)
        @commands.has_permissions(administrator=True)
        async def reload(ctx):
            """Reloads configuration, modules and language packages."""
            logger.info("Reloading...")
            was_started = bool(self.main_loop)
            self.main_loop = False
            self.load_resources(reload=True)
            self.main_loop = was_started

            await ctx.channel.send(self.lang["reload_completed"])
            logger.info("Reload completed")


if __name__ == "__main__":

    automatik = Client(command_prefix="!mk ", self_bot=False)
    try:
        automatik.run(base64.b64decode(Loader.start().encode("utf-8")).decode("utf-8"))

    except discord.errors.LoginFailure:
        logger.error("Invalid token, please make sure It's valid. Press enter to exit...")
        os.remove("Secret Token.json")
        input()
