import discord
from discord import ui

from automatik import logger


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

