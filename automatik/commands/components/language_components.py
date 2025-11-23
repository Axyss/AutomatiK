import discord
from discord import ui


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

