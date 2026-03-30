import discord
from discord import app_commands
from discord.ext import commands

from automatik.core.services import ServiceLoader
from automatik.commands.components import (
    LanguageView,
    ChannelManagementView,
    ServicesManagementView,
    MentionManagementView
)


class AdminSlash(commands.Cog):
    def __init__(self, bot, languages, config, database):
        self.bot = bot
        self.languages = languages
        self.config = config
        self.database = database

    async def interaction_check(self, interaction) -> bool:
        return await self.bot.is_invoked(interaction)

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def channel(self, interaction):
        """Manage notification channel - select or unselect a channel to receive freebies."""
        guild_cfg = self.database.get_guild_config(interaction.guild)
        guild_lang = guild_cfg["lang"]
        guild_selected_channel = guild_cfg["selected_channel"]
        current_channel = interaction.guild.get_channel(guild_selected_channel) if guild_selected_channel else None

        embed = discord.Embed(
            title=self.languages.get_message(guild_lang, "channel_management"),
            description=self.languages.get_message(guild_lang, "channel_description"),
            color=0x00BFFF
        )

        if current_channel:
            embed.add_field(
                name=self.languages.get_message(guild_lang, "current_channel"),
                value=current_channel.mention,
                inline=False
            )
        else:
            embed.description += "\n" + self.languages.get_message(guild_lang, "no_channel_selected")
        view = ChannelManagementView(self.languages, self.database, interaction.guild, guild_selected_channel)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def services(self, interaction):
        """Manage services - enable or disable services and view their current status."""
        guild_cfg = self.database.get_guild_config(interaction.guild)
        guild_lang = guild_cfg["lang"]
        guild_services = guild_cfg["services"]

        embed = discord.Embed(
            title=self.languages.get_message(guild_lang, "services_management"),
            description=self.languages.get_message(guild_lang, "services_management_description"),
            color=0x00BFFF
        )

        services_status = []
        for service in ServiceLoader.services:
            status = guild_services.get(service.SERVICE_ID, True)
            status_text = self.languages.get_message(guild_lang, "service_enabled_status" if status else "service_disabled_status")
            services_status.append(f"**{service.SERVICE_NAME}** (`{service.SERVICE_ID}`): {status_text}")

        view = ServicesManagementView(self.languages, self.database, interaction.guild, guild_services)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def mention(self, interaction):
        """Manage mention role - select or unset the role that will be notified about freebies."""
        guild_cfg = self.database.get_guild_config(interaction.guild)
        guild_lang = guild_cfg["lang"]
        current_role_mention = guild_cfg["mention_role"]

        embed = discord.Embed(
            title=self.languages.get_message(guild_lang, "mention_management"),
            description=self.languages.get_message(guild_lang, "mention_description"),
            color=0x00BFFF
        )

        if current_role_mention:
            embed.add_field(
                name=self.languages.get_message(guild_lang, "current_mention_role"),
                value=current_role_mention,
                inline=False
            )
        else:
            embed.description += "\n" + self.languages.get_message(guild_lang, "no_mention_role")

        view = MentionManagementView(self.languages, self.database, interaction.guild, current_role_mention)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def language(self, interaction):
        """Manage language - select the language for messages and notifications."""
        guild_lang = self.database.get_guild_config(interaction.guild)["lang"]

        embed_langs = discord.Embed(
            title=self.languages.get_message(guild_lang, "languages"),
            description=self.languages.get_message(guild_lang, "languages_description"),
            color=0x00BFFF
        )

        current_language = self.languages.languages_data[guild_lang].language
        embed_langs.add_field(
            name=self.languages.get_message(guild_lang, "current_language"),
            value=f"{self.languages.get_language_emoji(guild_lang)} **{current_language}** (`{guild_lang}`)",
            inline=False
        )

        view = LanguageView(self.languages.languages_data, self.languages, self.database)
        await interaction.response.send_message(embed=embed_langs, view=view)

