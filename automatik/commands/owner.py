import psutil
import discord
from discord.ext import commands
from discord import app_commands
from automatik import __version__, LOGO_URL, SRC_DIR, AVATAR_URL, logger


class OwnerSlash(commands.Cog):
    def __init__(self, bot, lm, cfg, mongo):
        self.bot = bot
        self.lm = lm
        self.cfg = cfg
        self.mongo = mongo

    @app_commands.command()
    async def start(self, interaction):
        """Starts the main service globally."""
        guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]

        if self.bot.main_loop:
            await interaction.response.send_message(self.lm.get_message(guild_lang, "start_already"))
            return None

        self.bot.main_loop = True
        await interaction.response.send_message(self.lm.get_message(guild_lang, "start_success"))
        logger.info(f"Main service was started globally by {str(interaction.user)}")

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def stop(self, interaction):
        """Stops the main service globally."""
        guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]

        if not self.bot.main_loop:  # If service already stopped
            await interaction.response.send_message(self.lm.get_message(guild_lang, "stop_already"))
            return None

        self.bot.main_loop = False
        await interaction.response.send_message(self.lm.get_message(guild_lang, "stop_success"))
        logger.info(f"Main service was stopped globally by {str(interaction.author)}")

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def reload(self, interaction):
        """Reloads configuration, modules and language packages."""
        guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]

        logger.info("Reloading..")
        was_started = bool(self.bot.main_loop)
        self.bot.main_loop = False
        try:
            self.bot.load_resources()
            await interaction.response.send_message(self.lm.get_message(guild_lang, "reload_completed"))
            logger.info("Reload completed")
        except:
            await interaction.response.send_message(self.lm.get_message(guild_lang, "unexpected_error"))
            logger.error("An error ocurred while reloading")
        finally:
            self.bot.main_loop = bool(was_started)

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def stats(self, interaction):
        """Shows some overall statistics of the bot."""
        guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]
        message_queue_len = len(self.bot.guilds) * (len(self.bot.game_queue_cache) + self.bot.game_queue.qsize())

        embed_stats = discord.Embed(title="\U0001f4c8 " + self.lm.get_message(guild_lang, "stats"),
                                    description=self.lm.get_message(guild_lang, "stats_description"),
                                    color=0x00BFFF)
        embed_stats.set_footer(text=self.lm.get_message(guild_lang, "help_footer"),
                               icon_url=AVATAR_URL)
        embed_stats.set_thumbnail(url=LOGO_URL)

        embed_stats.add_field(name="Guilds", value=str(len(self.bot.guilds)))
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

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def shutdown(self, interaction):
        """Shuts down the bot process completely."""
        guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]
        message_queue_len = len(self.bot.guilds) * (len(self.bot.game_queue_cache) + self.bot.game_queue.qsize())

        if not self.bot.empty() or self.bot.game_queue_cache:
            await interaction.response.send_message(
                self.lm.get_message(guild_lang, "shutdown_abort").format(message_queue_len))
            return None

        await interaction.response.send_message(self.lm.get_message(guild_lang, "shutdown_success"))
        logger.info("Shutting down..")
        self.bot.main_loop = False
        await self.bot.close()
