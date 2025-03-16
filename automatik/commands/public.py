import os

import discord
from discord.ext import commands
from discord import app_commands
from automatik import __version__, LOGO_URL, SRC_DIR, AVATAR_URL
from ..core.modules import ModuleLoader


class PublicSlash(commands.Cog):
    def __init__(self, bot, lm, cfg, mongo):
        self.bot = bot
        self.lm = lm
        self.cfg = cfg
        self.mongo = mongo

    @app_commands.command()
    async def help(self, interaction: discord.Interaction):
        """A simple help command."""
        guild_lang = self.mongo.get_guild_config(interaction.guild)["lang"]

        embed_help = discord.Embed(title=f"AutomatiK {__version__} Help ",
                                   description=self.lm.get_message(guild_lang, "help_description"),
                                   color=0x00BFFF)
        embed_help.set_thumbnail(url=LOGO_URL)
        embed_help.add_field(name=self.lm.get_message(guild_lang, "help_field1_name"),
                             value="".join(self.lm.get_message(guild_lang, "help_field1_value")),
                             inline=False)

        if interaction.user.guild_permissions.administrator:
            embed_help.add_field(name=u"\U0001F6E0 " + self.lm.get_message(guild_lang, "help_field2_name"),
                                 value="".join(self.lm.get_message(guild_lang, "help_field2_value")),
                                 inline=False)
        if await self.is_an_owner(interaction.user):  # If command author a bot owner
            embed_help.add_field(name=u"\U0001F451 " + self.lm.get_message(guild_lang, "help_field3_name"),
                                 value="".join(self.lm.get_message(guild_lang, "help_field3_value")),
                                 inline=False
                                 )
        await interaction.response.send_message(embed=embed_help)

    @app_commands.command()
    async def status(self, interaction):
        """Shows your current AutomatiK config."""
        guild_cfg = self.mongo.get_guild_config(interaction.guild)
        guild_lang = guild_cfg["lang"]

        embed_status = discord.Embed(title=self.lm.get_message(guild_lang, "status"),
                                     description=self.lm.get_message(guild_lang, "status_description"),
                                     color=0x00BFFF)
        embed_status.set_footer(text=self.lm.get_message(guild_lang, "help_footer"), icon_url=AVATAR_URL)
        embed_status.set_thumbnail(url=LOGO_URL)
        embed_status.add_field(name=self.lm.get_message(guild_lang, "status_main"),
                               value=self.lm.get_message(guild_lang, "status_active" if guild_cfg.get("selected_channel") else "status_inactive") + "\n" + guild_cfg[
                                         "selected_channel"])

        for i in ModuleLoader.modules:
            if guild_cfg["services"][i.MODULE_ID]:
                value = self.lm.get_message(guild_lang, "status_active")
            else:
                value = self.lm.get_message(guild_lang, "status_inactive")
            embed_status.add_field(name=i.SERVICE_NAME, value=value)
        await interaction.response.send_message(embed=embed_status)

    async def is_an_owner(self, user):
        return True
