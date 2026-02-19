import discord
from discord import app_commands
from discord.ext import commands

from automatik import LOGO_URL, AVATAR_URL, logger
from automatik.core.services import ServiceLoader
from automatik.commands.components import (
    LanguageView,
    ChannelManagementView,
    ServicesManagementView
)


class AdminSlash(commands.Cog):
    def __init__(self, bot, lm, cfg, mongo):
        self.bot = bot
        self.lm = lm
        self.cfg = cfg
        self.mongo = mongo

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def channel(self, interaction):
        """Manage notification channel - select or unselect a channel to receive freebies."""
        guild_cfg = self.mongo.get_guild_config(interaction.guild)
        guild_lang = guild_cfg["lang"]
        guild_selected_channel = guild_cfg["selected_channel"]
        current_channel = interaction.guild.get_channel(guild_selected_channel) if guild_selected_channel else None

        embed = discord.Embed(
            title=self.lm.get_message(guild_lang, "channel_management"),
            description=self.lm.get_message(guild_lang, "channel_description"),
            color=0x00BFFF
        )
        embed.set_footer(text=self.lm.get_message(guild_lang, "help_footer"), icon_url=AVATAR_URL)
        embed.set_thumbnail(url=LOGO_URL)

        if current_channel:
            embed.add_field(
                name=self.lm.get_message(guild_lang, "current_channel"),
                value=current_channel.mention,
                inline=False
            )
        else:
            embed.add_field(
                name=self.lm.get_message(guild_lang, "no_channel_selected"),
                value=self.lm.get_message(guild_lang, "select_channel_instruction"),
                inline=False
            )
        view = ChannelManagementView(self.lm, self.mongo, interaction.guild, guild_selected_channel)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def services(self, interaction):
        """Manage services - enable or disable services and view their current status."""
        guild_cfg = self.mongo.get_guild_config(interaction.guild)
        guild_lang = guild_cfg["lang"]
        guild_services = guild_cfg["services"]

        embed = discord.Embed(
            title=self.lm.get_message(guild_lang, "services_management"),
            description=self.lm.get_message(guild_lang, "services_management_description"),
            color=0x00BFFF
        )
        embed.set_footer(text=self.lm.get_message(guild_lang, "help_footer"), icon_url=AVATAR_URL)
        embed.set_thumbnail(url=LOGO_URL)

        services_status = []
        for service in ServiceLoader.services:
            status = guild_services.get(service.SERVICE_ID, True)
            status_text = self.lm.get_message(guild_lang, "service_enabled_status" if status else "service_disabled_status")
            services_status.append(f"**{service.SERVICE_NAME}** (`{service.SERVICE_ID}`): {status_text}")

        view = ServicesManagementView(self.lm, self.mongo, interaction.guild, guild_services)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def mention(self, interaction, role: discord.Role):
        """Select which role will be notified freebies."""
        guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]

        self.mongo.update_guild_config(interaction.guild, {"mention_role": role.mention})
        await interaction.response.send_message(self.lm.get_message(guild_lang, "mention_established"))
        logger.info(f"AutomatiK will now mention '{role}'")

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def language(self, interaction):
        """Shows a list of the available languages with interactive components."""
        guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]

        embed_langs = discord.Embed(
            title=f"{self.lm.get_message(guild_lang, 'languages')} 🌐",
            description=self.lm.get_message(guild_lang, "languages_description"),
            color=0x5865F2
        )

        embed_langs.set_footer(
            text=self.lm.get_message(guild_lang, "help_footer"),
            icon_url=AVATAR_URL
        )
        embed_langs.set_thumbnail(url=LOGO_URL)

        current_language = self.lm.languages_data[guild_lang].language
        embed_langs.add_field(
            name="📌 " + self.lm.get_message(guild_lang, "language") + " " + "(actual)",
            value=f"{self.lm.languages_data[guild_lang].emoji} **{current_language}** (`{guild_lang}`)",
            inline=False
        )

        view = LanguageView(self.lm.languages_data, self.lm, self.mongo)
        await interaction.response.send_message(embed=embed_langs, view=view)

