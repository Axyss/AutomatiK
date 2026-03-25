import discord
from discord import app_commands
from discord.ext import commands

from automatik import logger


class OwnerSlash(commands.Cog):
    def __init__(self, bot, languages, config, database):
        self.bot = bot
        self.languages = languages
        self.config = config
        self.database = database

    async def interaction_check(self, interaction) -> bool:
        return await self.bot.is_invoked(interaction)

    @app_commands.command()
    async def start(self, interaction):
        """Starts the main service globally."""
        guild_lang = self.database.get_guild_config(interaction.guild)["lang"]

        if self.bot.main_loop:
            await interaction.response.send_message(self.languages.get_message(guild_lang, "start_already"))
            return None

        self.bot.main_loop = True
        await interaction.response.send_message(self.languages.get_message(guild_lang, "start_success"))
        logger.info(
            f"Main loop started by {interaction.user} ({interaction.user.id}) "
            f"from guild '{interaction.guild.name}' ({interaction.guild.id})"
        )

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
        logger.info(
            f"Main loop stopped by {interaction.user} ({interaction.user.id}) "
            f"from guild '{interaction.guild.name}' ({interaction.guild.id})"
        )

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def reload(self, interaction):
        """Reloads configuration, services and language packages."""
        guild_lang = self.database.get_guild_config(interaction.guild)["lang"]

        logger.info(
            f"Reload triggered by {interaction.user} ({interaction.user.id}) "
            f"from guild '{interaction.guild.name}' ({interaction.guild.id})"
        )
        was_started = bool(self.bot.main_loop)
        self.bot.main_loop = False
        try:
            self.bot.load_resources()
            await interaction.response.send_message(self.languages.get_message(guild_lang, "reload_completed"))
            logger.info("Reload completed successfully")
        except:
            await interaction.response.send_message(self.languages.get_message(guild_lang, "unexpected_error"))
            logger.exception("Reload failed with an unexpected error")
        finally:
            self.bot.main_loop = bool(was_started)

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def stats(self, interaction):
        """Shows some overall statistics of the bot."""
        guild_lang = self.database.get_guild_config(interaction.guild)["lang"]

        embed_stats = discord.Embed(title="\U0001f4c8 " + self.languages.get_message(guild_lang, "stats"),
                                    description=self.languages.get_message(guild_lang, "stats_description"),
                                    color=0x00BFFF)

        embed_stats.add_field(name="Guilds", value=str(len(self.bot.guilds)))

        await interaction.response.send_message(embed=embed_stats)
