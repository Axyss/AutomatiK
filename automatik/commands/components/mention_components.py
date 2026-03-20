import discord
from discord import ui

from automatik import logger


class RoleSelector(ui.RoleSelect):
    def __init__(self, languages, database, guild):
        self.languages = languages
        self.database = database
        self.guild = guild
        guild_lang = self.database.get_guild_config(guild)["lang"]

        super().__init__(
            placeholder=languages.get_message(guild_lang, "select_role_placeholder"),
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction):
        guild_lang = self.database.get_guild_config(self.guild)["lang"]
        role = self.values[0]

        self.database.update_guild_config(self.guild, {"mention_role": role.mention})
        await interaction.response.send_message(
            self.languages.get_message(guild_lang, "mention_established").format(role.mention),
            ephemeral=True
        )
        logger.info(f"Mention role set to '{role}' in {self.guild.name} by {interaction.user}")


class MentionManagementView(ui.View):
    def __init__(self, languages, database, guild, current_role_mention=None):
        super().__init__(timeout=300)
        self.languages = languages
        self.database = database
        self.guild = guild
        guild_lang = self.database.get_guild_config(guild)["lang"]

        self.add_item(RoleSelector(languages, database, guild))

        if current_role_mention:
            unset_btn = ui.Button(
                style=discord.ButtonStyle.danger,
                label=languages.get_message(guild_lang, "unset_mention_role"),
                emoji="✖️"
            )
            unset_btn.callback = self.unset_role
            self.add_item(unset_btn)

    async def interaction_check(self, interaction):
        """Verify that the user has administrator permissions"""
        return interaction.user.guild_permissions.administrator

    async def unset_role(self, interaction):
        guild_lang = self.database.get_guild_config(self.guild)["lang"]
        self.database.update_guild_config(self.guild, {"mention_role": None})
        await interaction.response.send_message(
            self.languages.get_message(guild_lang, "mention_role_unset"),
            ephemeral=True
        )
        logger.info(f"Mention role unset in {self.guild.name} by {interaction.user}")
        self.stop()
