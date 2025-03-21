import discord
from discord.ext import commands
from discord import app_commands
from automatik import __version__, LOGO_URL, SRC_DIR, AVATAR_URL, logger
from automatik.core.modules import ModuleLoader


class AdminSlash(commands.Cog):
    def __init__(self, bot, lm, cfg, mongo):
        self.bot = bot
        self.lm = lm
        self.cfg = cfg
        self.mongo = mongo

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def select(self, interaction, channel: discord.TextChannel):
        """Select a Text Channel to start receiving freebies."""
        guild_cfg = self.mongo.get_guild_config(interaction.guild)
        guild_lang = guild_cfg["lang"]

        self.mongo.update_guild_config(interaction.guild, {"selected_channel": channel.id})
        await interaction.response.send_message(
            self.lm.get_message(guild_lang, "select_success").format(channel.mention))

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def unselect(self, interaction):
        """Unselects the previously selected Text Channel."""
        guild_cfg = self.mongo.get_guild_config(interaction.guild)
        guild_lang = guild_cfg["lang"]
        guild_selected_channel = guild_cfg["selected_channel"]

        if guild_selected_channel is None:
            await interaction.response.send_message(self.lm.get_message(guild_lang, "unselect_already")
                                                    .format(guild_selected_channel))
            return None

        self.mongo.update_guild_config(interaction.guild, {"selected_channel": None})
        await interaction.response.send_message(
            self.lm.get_message(guild_lang, "unselect_success").format(guild_selected_channel))

    @app_commands.command(name="module", )
    @app_commands.checks.has_permissions(administrator=True)
    async def enable(self, interaction, choice: str):
        """Modify the list of services you are interested in."""
        guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]

        user_decision = True if choice == "enable" else False

        for module in ModuleLoader.modules:
            if choice.lower() == module.MODULE_ID.lower():
                self.mongo.update_guild_config(interaction.guild, {"services." + choice.lower(): user_decision})
                await interaction.response.send_message(
                    self.lm.get_message(guild_lang, f"module_{choice}d").format(choice))
                logger.info(f"{choice.capitalize()} module {choice}d by {interaction.author}")
                return True

        await interaction.response.send_message(self.lm.get_message(guild_lang, f"enable_unknown").format(choice))

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def modules(self, interaction):
        """Shows information about the loaded modules."""
        guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]

        embed_module = discord.Embed(title=self.lm.get_message(guild_lang, "modules"),
                                     description=self.lm.get_message(guild_lang, "modules_description"),
                                     color=0x00BFFF)

        embed_module.set_footer(text=self.lm.get_message(guild_lang, "help_footer"), icon_url=AVATAR_URL)
        embed_module.set_thumbnail(url=LOGO_URL)

        embed_module.add_field(name="**ModuleID**", value="\n".join(ModuleLoader.get_module_ids()))

        embed_module.add_field(name=self.lm.get_message(guild_lang, "modules_service"),
                               value="\n".join(ModuleLoader.get_service_names()))

        embed_module.add_field(name=self.lm.get_message(guild_lang, "modules_author"),
                               value="\n".join(ModuleLoader.get_module_authors()))

        await interaction.response.send_message(embed=embed_module)

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
    async def language(self, interaction, lang_code: str):
        """Select a language."""
        guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]

        if lang_code not in self.lm.get_lang_packages_metadata()[0]:  # If the language package does not exist
            await interaction.response.send_message(self.lm.get_message(guild_lang, "language_error"))
            return

        self.mongo.update_guild_config(interaction.guild, {"lang": lang_code})
        await interaction.response.send_message(self.lm.get_message(lang_code, "language_changed"))
        logger.info(f"Language changed to '{lang_code}' by {interaction.author}")

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def languages(self, interaction):
        """Shows a list of the available languages."""
        guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]
        lang_ids, lang_names, lang_authors = self.lm.get_lang_packages_metadata()

        embed_langs = discord.Embed(title=self.lm.get_message(guild_lang, "languages"),
                                    description=self.lm.get_message(guild_lang, "languages_description"),
                                    color=0x00BFFF
                                    )
        embed_langs.set_footer(text=self.lm.get_message(guild_lang, "help_footer"),
                               icon_url=AVATAR_URL
                               )
        embed_langs.set_thumbnail(url=LOGO_URL)
        embed_langs.add_field(name="LangID", value="\n".join(lang_ids))
        embed_langs.add_field(name=self.lm.get_message(guild_lang, "language"), value="\n".join(lang_names))
        embed_langs.add_field(name=self.lm.get_message(guild_lang, "modules_author"), value="\n".join(lang_authors))

        await interaction.response.send_message(embed=embed_langs)