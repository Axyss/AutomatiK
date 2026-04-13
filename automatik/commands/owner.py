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
    @app_commands.guild_only()
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
