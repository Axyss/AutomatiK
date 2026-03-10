import discord
from discord import app_commands
from discord.ext import commands

from automatik import LOGO_URL, AVATAR_URL, logger


class OwnerSlash(commands.Cog):
    def __init__(self, bot, languages, config, database):
        self.bot = bot
        self.languages = languages
        self.config = config
        self.database = database

    @app_commands.command()
    async def start(self, interaction):
        """Starts the main service globally."""
        guild_lang = self.database.get_guild_config(interaction.guild)["lang"]

        if self.bot.main_loop:
            await interaction.response.send_message(self.languages.get_message(guild_lang, "start_already"))
            return None

        self.bot.main_loop = True
        await interaction.response.send_message(self.languages.get_message(guild_lang, "start_success"))
        logger.info(f"Main service was started globally by {str(interaction.user)}")

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def stop(self, interaction):
        """Stops the main service globally."""
        guild_lang = self.database.get_guild_config(interaction.guild)["lang"]

        if not self.bot.main_loop:  # If service already stopped
            await interaction.response.send_message(self.languages.get_message(guild_lang, "stop_already"))
            return None

        self.bot.main_loop = False
        await interaction.response.send_message(self.languages.get_message(guild_lang, "stop_success"))
        logger.info(f"Main service was stopped globally by {str(interaction.author)}")

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def reload(self, interaction):
        """Reloads configuration, services and language packages."""
        guild_lang = self.database.get_guild_config(interaction.guild)["lang"]

        logger.info("Reloading..")
        was_started = bool(self.bot.main_loop)
        self.bot.main_loop = False
        try:
            self.bot.load_resources()
            await interaction.response.send_message(self.languages.get_message(guild_lang, "reload_completed"))
            logger.info("Reload completed")
        except:
            await interaction.response.send_message(self.languages.get_message(guild_lang, "unexpected_error"))
            logger.error("An error ocurred while reloading")
        finally:
            self.bot.main_loop = bool(was_started)

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def stats(self, interaction):
        """Shows some overall statistics of the bot."""
        guild_lang = self.database.get_guild_config(interaction.guild)["lang"]
        message_queue_len = len(self.bot.guilds) * (len(self.bot.game_queue_cache) + self.bot.game_queue.qsize())

        embed_stats = discord.Embed(title="\U0001f4c8 " + self.languages.get_message(guild_lang, "stats"),
                                    description=self.languages.get_message(guild_lang, "stats_description"),
                                    color=0x00BFFF)

        embed_stats.add_field(name="Guilds", value=str(len(self.bot.guilds)))
        embed_stats.add_field(name=self.languages.get_message(guild_lang, "stats_owners_field"),
                              value="\n".join(self.config.bot_owner))
        if message_queue_len:
            embed_stats.add_field(name=self.languages.get_message(guild_lang, "stats_message_queue_field"),
                                  value=self.languages.get_message(guild_lang, "stats_message_queue_value")
                                  .format(message_queue_len))
        else:  # No messages in the queues
            embed_stats.add_field(name=self.languages.get_message(guild_lang, "stats_message_queue_field"),
                                  value=self.languages.get_message(guild_lang, "stats_message_queue_empty_value")
                                  .format(message_queue_len))

        await interaction.response.send_message(embed=embed_stats)
