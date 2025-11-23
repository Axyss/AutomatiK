import discord
from discord import ui

from automatik import AVATAR_URL, LOGO_URL, logger
from automatik.core.services import ServiceLoader


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

