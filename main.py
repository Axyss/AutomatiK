from threading import Thread

import discord

from automatik import logger
from automatik.bot import AutomatikBot
from automatik.utils.cli import clear_console, print_ascii_art
from automatik.utils.update import check_every_n_days

clear_console()
print_ascii_art()
logger.info("Loading..")
automatik = AutomatikBot(command_prefix="!mk ", self_bot=False, intents=discord.Intents.default())
Thread(target=check_every_n_days, args=[1], daemon=True).start()

try:
    automatik.run(automatik.cfg.discord_bot_token)
except discord.errors.LoginFailure:
    logger.error("Invalid 'discord_bot_token'. Press enter to exit..")
    input()
