import discord
from discord.ext import commands
from discord import app_commands, ui
from automatik import __version__, LOGO_URL, SRC_DIR, AVATAR_URL, logger
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
        """Shows information about the loaded services."""
        guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]

        embed_service = discord.Embed(title=self.lm.get_message(guild_lang, "services"),
                                     description=self.lm.get_message(guild_lang, "services_description"),
                                     color=0x00BFFF)

        embed_service.set_footer(text=self.lm.get_message(guild_lang, "help_footer"), icon_url=AVATAR_URL)
        embed_service.set_thumbnail(url=LOGO_URL)

        embed_service.add_field(name="**ServiceID**", value="\n".join(ServiceLoader.get_service_ids()))

        embed_service.add_field(name=self.lm.get_message(guild_lang, "services_service"),
                               value="\n".join(ServiceLoader.get_service_names()))

        await interaction.response.send_message(embed=embed_service)

    @app_commands.command(name="service", )
    @app_commands.checks.has_permissions(administrator=True)
    async def enable(self, interaction, choice: str):
        """Modify the list of services you are interested in."""
        guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]
        user_decision = choice == "enable"

        for service in ServiceLoader.services:
            if choice.lower() == service.SERVICE_ID.lower():
                self.mongo.update_guild_config(interaction.guild, {"services." + choice.lower(): user_decision})
                await interaction.response.send_message(
                    self.lm.get_message(guild_lang, f"service_{choice}d").format(choice))
                logger.info(f"{choice.capitalize()} service {choice}d by {interaction.author}")
                return True

        await interaction.response.send_message(self.lm.get_message(guild_lang, f"enable_unknown").format(choice))

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
