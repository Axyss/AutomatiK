import discord
from discord import app_commands, ui
from discord.ext import commands

from automatik import LOGO_URL, AVATAR_URL, logger
from automatik.core.services import ServiceLoader


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

        current_language = self.lm.lang_pkgs[guild_lang].language
        embed_langs.add_field(
            name="📌 " + self.lm.get_message(guild_lang, "language") + " " + "(actual)",
            value=f"{self.lm.lang_pkgs[guild_lang].emoji} **{current_language}** (`{guild_lang}`)",
            inline=False
        )

        view = LanguageView(self.lm.lang_pkgs, self.lm, self.mongo)
        await interaction.response.send_message(embed=embed_langs, view=view)


class LanguageSelector(ui.Select):
    def __init__(self, lang_options, lm, mongo):
        self.lm = lm
        self.mongo = mongo

        options = []
        for lang_id, lang in lang_options.items():
            option = discord.SelectOption(
                label=lang.language,
                value=lang_id,
                emoji=lang.emoji,
                description=f"Author: {lang.author}"
            )
            options.append(option)

        super().__init__(
            placeholder="Select a language...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction):
        lang_code = self.values[0]
        self.mongo.update_guild_config(interaction.guild, {"lang": lang_code})
        await interaction.response.send_message(
            self.lm.get_message(lang_code, "language_changed"),
            ephemeral=True
        )


class LanguageView(ui.View):
    def __init__(self, lang_options, lm, mongo):
        super().__init__(timeout=300)
        self.add_item(LanguageSelector(lang_options, lm, mongo))


class ChannelManagementView(ui.View):
    def __init__(self, lm, mongo, guild, channel_id=None):
        super().__init__(timeout=300)
        self.lm = lm
        self.mongo = mongo
        self.guild = guild
        self.channel_id = channel_id
        guild_lang = self.mongo.get_guild_config(guild)["lang"]

        # Add channel selector dropdown
        self.add_item(ChannelSelector(guild.text_channels, lm, mongo, guild))

        # Add unselect button only if there's a channel selected
        if channel_id:
            unselect_btn = ui.Button(
                style=discord.ButtonStyle.danger,
                label=self.lm.get_message(guild_lang, "unselect_channel"),
                emoji="❌"
            )
            unselect_btn.callback = self.unselect_channel
            self.add_item(unselect_btn)

    async def interaction_check(self, interaction):
        """Verify that the user has administrator permissions"""
        return interaction.user.guild_permissions.administrator

    async def unselect_channel(self, interaction):
        guild_lang = self.mongo.get_guild_config(self.guild)["lang"]
        self.mongo.update_guild_config(self.guild, {"selected_channel": None})
        await interaction.response.send_message(
            self.lm.get_message(guild_lang, "unselect_success").format(self.channel_id),
            ephemeral=True
        )
        logger.info(f"Channel unselected in {self.guild.name}")
        self.stop()


class ChannelSelector(ui.Select):
    def __init__(self, channels, lm, mongo, guild):
        self.lm = lm
        self.mongo = mongo
        self.guild = guild
        guild_lang = self.mongo.get_guild_config(guild)["lang"]

        options = []
        for channel in channels[:25]:
            option = discord.SelectOption(
                label=channel.name,
                value=str(channel.id),
                description=channel.topic[:100] if channel.topic else None
            )
            options.append(option)

        super().__init__(
            placeholder=self.lm.get_message(guild_lang, "select_channel_placeholder"),
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction):
        guild_lang = self.mongo.get_guild_config(self.guild)["lang"]
        channel_id = int(self.values[0])
        channel = self.guild.get_channel(channel_id)

        self.mongo.update_guild_config(self.guild, {"selected_channel": channel_id})
        await interaction.response.send_message(
            self.lm.get_message(guild_lang, "select_success").format(channel.mention),
            ephemeral=True
        )
        logger.info(f"Channel selected: {channel.name} in {self.guild.name}")


class ServicesManagementView(ui.View):
    def __init__(self, lm, mongo, guild, services_status):
        super().__init__(timeout=300)
        self.lm = lm
        self.mongo = mongo
        self.guild = guild
        self.services_status = services_status

        for service in ServiceLoader.services[:20]:  # Limit to 20 to be safe with Discord limits
            is_enabled = services_status.get(service.SERVICE_ID, True)
            button = ui.Button(
                style=discord.ButtonStyle.success if is_enabled else discord.ButtonStyle.danger,
                label=service.SERVICE_NAME,
                emoji="✅" if is_enabled else "❌",
                custom_id=f"toggle_{service.SERVICE_ID}"
            )
            button.callback = self.create_toggle_callback(service.SERVICE_ID, service.SERVICE_NAME)
            self.add_item(button)

    async def interaction_check(self, interaction):
        """Verify that the user has administrator permissions"""
        return interaction.user.guild_permissions.administrator

    def create_toggle_callback(self, service_id, service_name):
        """Create a callback function for toggling a specific service."""
        async def toggle_callback(interaction):
            guild_lang = self.mongo.get_guild_config(self.guild)["lang"]
            current_status = self.services_status.get(service_id, True)
            new_status = not current_status

            self.mongo.update_guild_config(self.guild, {f"services.{service_id}": new_status})
            self.services_status[service_id] = new_status

            button = discord.utils.get(self.children, custom_id=f"toggle_{service_id}")
            if button:
                button.style = discord.ButtonStyle.success if new_status else discord.ButtonStyle.danger
                button.emoji = "✅" if new_status else "❌"

            embed = discord.Embed(
                title=self.lm.get_message(guild_lang, "services_management"),
                description=self.lm.get_message(guild_lang, "services_management_description"),
                color=0x00BFFF
            )
            embed.set_footer(text=self.lm.get_message(guild_lang, "help_footer"), icon_url=AVATAR_URL)
            embed.set_thumbnail(url=LOGO_URL)

            await interaction.response.edit_message(embed=embed, view=self)

            status_msg = "enabled" if new_status else "disabled"
            logger.info(f"Service '{service_name}' ({service_id}) {status_msg} in {self.guild.name} by {interaction.user}")

        return toggle_callback
