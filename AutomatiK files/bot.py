# coding=utf-8

import discord
import asyncio
import epic_mod
import humble_mod
import time
import os
import json
import re
from discord.ext import commands

client = commands.Bot(command_prefix="!mk ", self_bot=False)

mainLoopStatus = False  # Variable which starts or stops the main loop

dataConfig = None  # Loaded configuration

# Template of the config
dataTemplate = {"role": "<@&1234>",
                "role_mention": False,
                "epic_status": True,
                "humble_status": True}

# -----------------------REGULAR FUNCTIONS-----------------------


def pm(message):
    """Ignores PM messages"""

    if "Direct Message with" in str(message):
        return True


def get_time():
    """Generates a string with the neccessary date and time format"""

    return time.strftime('[%Y/%m/%d]' + '[%H:%M]')


def generate_message(title, link, service):
    """Generates some messages the bot sends"""
    # If third parameter True, then the message is for discord
    # This lets the function knows where the message is going to be sent and add the mention if required

    global dataConfig
    draft = title + " is currently free on " + link + "."

    if dataConfig["role_mention"] and service:  # If role_mention is True, then add the role parameter from config
        draft = dataConfig["role"] + " " + draft

    return draft


def check_config_changes():
    """Checks the version of the config and updates It if necessary"""

    global dataConfig
    global dataTemplate

    templateKeys = list(dataTemplate.keys())
    currentKeys = list(dataConfig.keys())

    for i in templateKeys:  # Checks the differences between configs

        if i in currentKeys:
            continue

        else:
            edit_config(i, dataTemplate[i])  # Adds the element using the value from the template


def load_config():
    """Loads the config from the file (Don't execute It more than 1 time)"""

    global dataConfig
    global dataTemplate

    # print(tuple(dataTemplate.keys())[2])

    if "config.json" in os.listdir("."):  # If config file already exists

        with open("config.json", "r") as file:
            dataConfig = json.load(file)  # Loads config
            file.close()

    else:  # Creates the config file and writes the template into It

        with open("config.json", "w") as file:
            json.dump(dataTemplate, file)  # Injects the template
            file.close()
            dataConfig = dataTemplate  # Loads the template into the current config


def edit_config(key, value):
    """Only function which can alter both configs (permanent and loaded)"""

    global dataConfig

    dataConfig[key] = value  # Alters loaded config
    file = open("config.json", "w")

    json.dump(dataConfig, file)  # Rewrites the persistent config
    file.close()


# -----------------------EVENTS-----------------------


@client.event
async def on_ready():

    print(get_time() + "[INFO]: AutomatiK bot now online")

    load_config()

    check_config_changes()

    await client.change_presence(status=discord.Status.online,  # Changes status to "online"
                                 activity=discord.Game("!mk helpme")  # Changes activity (playing)
                                 )


@client.event
async def on_command_error(ctx, error):  # The second parameter is the error's information
    """Function used for error handling"""

    if isinstance(error, discord.ext.commands.MissingPermissions):
        """In case the user who tries to run the command does not have administrator perms, run this"""

        await ctx.channel.send(u"\u274C You don't have enough permissions to execute this command.")


# -----------------------COMMANDS-----------------------

@client.command()
@commands.has_permissions(administrator=True)
async def notify(ctx, *args):

    if pm(ctx.channel):
        return None

    args = list(args)  # args' default type: tuple
    separator = " "  # String that will be inserted between elements of the list when using .join

    # Stores the link in another variable and removes It from args
    link = args[-1]
    args.pop()

    gameName = separator.join(args)  # Converts list to string with spaces between elements

    await ctx.channel.purge(limit=1)

    await ctx.channel.send(generate_message(
        gameName, link, True) + f"\nThanks for notifying <@!{ctx.author.id}>."  # Adds politeness
    )


@client.command()
@commands.has_permissions(administrator=True)
async def mention(ctx, roleid):
    """Manages the mentions of the bot's messages"""

    if pm(ctx.channel):
        return None

    if re.search("^<@&\w", roleid) and re.search(">$", roleid):
        # If the string follows the std structure of a role <@&1234>, then...

        edit_config("role", roleid)

        print(get_time() + "[INFO]: AutomatiK will now mention:", roleid)
        await ctx.channel.send(u"\u2705 Role successfully established.")


@client.command()
async def helpme(ctx):
    """Help command that uses embeds"""

    embed_help = discord.Embed(title="AutomatiK Help", color=0x00BFFF)

    embed_help.set_footer(text="Project page: github.com/Axyss/AutomatiK",
                          icon_url="https://avatars3.githubusercontent.com/u/55812692"
                          )

    embed_help.set_thumbnail(
        url="https://raw.githubusercontent.com/Axyss/AutomatiK/master/AutomatiK%20files/assets/ak_logo.png"
    )

    embed_help.add_field(name="Commands", value="```!mk helpme - Shows all available commands." +
                         "\n!mk status - Shows bot's status. ```",
                         inline=False)

    embed_help.add_field(name="Admin commands", value="```" +
                         "\n!mk start - Starts the main process in the channel where the command is executed." +
                         "\n!mk stop - Stops the main process." +
                         "\n"
                         "\n!mk enable - Global command to enable diverse AutomatiK" +
                         " services (epic/humble/mention)."
                         "\n!mk disable - Global command to disable diverse AutomatiK services" +
                         " (epic/humble/mention)."
                         "\n"
                         "\n!mk mention (role) - Select which role will be mentioned in Automatik's messages. " +
                         "Example: '!mk role @MyRank'." +
                         "\n!mk notify (name) (link) - Notify games from non-supported platforms manually.```",
                         inline=False)

    await ctx.channel.send(embed=embed_help)


@client.command()
@commands.has_permissions(administrator=True)
async def start(ctx):
    """Starts the AutomatiK service"""

    global mainLoopStatus
    global dataConfig  # Gets config values

    if pm(ctx.channel):  # Checks if pm
        return None

    if mainLoopStatus:  # If service already stopped
        await ctx.channel.send(u"\u274C Main service is already started.")
        return None

    print(get_time() +
          "[INFO]: AutomatiK was started by",
          str(ctx.author)
          )

    await ctx.channel.send(u"\u2705 Main service started.")

    # Here is where the real function starts

    mainLoopStatus = True  # Changes It to True so the main loop can start

    while mainLoopStatus:  # MAIN LOOP

        # Epic Games methods
        epic_mod.obj.make_request()
        epic_mod.obj.process_request()

        # Humble Bundle methods
        humble_mod.obj.make_request()
        humble_mod.obj.process_request()

        # Epic Games caller
        if epic_mod.obj.check_database() and dataConfig["epic_status"]:  # Checks If Epic module is enabled in config

            gD = tuple(epic_mod.obj.gameData)  # Used to abbreviate since "with" did not work

            await ctx.channel.send(
                generate_message(gD[0], gD[1], True)
            )  # Sends message to the guild

        # Humble Bundle caller
        if humble_mod.obj.check_database() and dataConfig["humble_status"]:  # If Humble module is enabled in config

            # Message that will be sent to the guild.
            vGD = tuple(humble_mod.obj.validGameData)

            for i in vGD:
                await ctx.channel.send(
                    generate_message(i[0], i[1], True)
                )

        await asyncio.sleep(300)  # It will check free games every 5 minutes


@client.command()
@commands.has_permissions(administrator=True)
async def stop(ctx):
    """Stops the AutomatiK service"""

    global mainLoopStatus

    if pm(ctx.channel):
        return None

    if not mainLoopStatus:  # If service already stopped
        await ctx.channel.send(u"\u274C Main service is already stopped.")
        return None

    print(get_time() +
          "[INFO]: AutomatiK was stopped by",
          str(ctx.author)
          )

    await ctx.channel.send(u"\u2705 Main service stopped.")

    mainLoopStatus = False  # Stops the loop by changing the boolean which maintains It active


@client.command()
async def status(ctx):
    """Shows the status of the service"""

    global dataConfig
    global mainLoopStatus

    if pm(ctx.channel):
        return None

    if mainLoopStatus:
        mainService = u"ACTIVE \u2611"
    else:
        mainService = u"INACTIVE \u274C"

    if dataConfig["epic_status"]:
        epicModule = u"ACTIVE \u2611"
    else:
        epicModule = u"INACTIVE \u274C"

    if dataConfig["humble_status"]:
        humbleModule = u"ACTIVE \u2611"
    else:
        humbleModule = u"INACTIVE \u274C"

    if dataConfig["role_mention"]:
        roleMention = u"ACTIVE \u2611"
    else:
        roleMention = u"INACTIVE \u274C"

    await ctx.channel.send(f"> Main service: {mainService}"
                           "\n"
                           "\n>         Modules:"
                           f"\n> Epic:             {epicModule}"
                           f"\n> Humble:      {humbleModule}"
                           f"\n> Mentions:   {roleMention}")


@client.command()
@commands.has_permissions(administrator=True)
async def enable(ctx, service):
    """Global manager to enable some AutomatiK services"""

    if pm(ctx.channel):
        return None

    service = service.lower()  # Lowers the last argument

    if service == "epic":
        edit_config("epic_status", True)

    elif service == "humble":
        edit_config("humble_status", True)

    elif service == "mention":

        edit_config("role_mention", True)
        print(get_time() + "[INFO]: AutomatiK mentions enabled")
        await ctx.channel.send(u"\u2705 Mention module enabled.")
        return None

    else:
        await ctx.channel.send(u"\u274C Unknown parameter. Use !mk enable (Epic/Humble/Mention)")
        return None

    # This next lines will just be executed in case the command is correct

    print(get_time() + f"[INFO]: {service.capitalize()} module enabled")
    await ctx.channel.send(u"\u2705 " + f"{service.capitalize()} module enabled.")


@client.command()
@commands.has_permissions(administrator=True)
async def disable(ctx, service):
    """Global manager to disable some AutomatiK services"""

    if pm(ctx.channel):
        return None

    service = service.lower()

    if service == "epic":
        edit_config("epic_status", False)

    elif service == "humble":
        edit_config("humble_status", False)

    elif service == "mention":

        edit_config("role_mention", False)
        print(get_time() + "[INFO]: AutomatiK mentions disabled")
        await ctx.channel.send(u"\u2705 Mention module disabled.")
        return None

    else:
        await ctx.channel.send(u"\u274C Unknown parameter. Use !mk disable (Epic/Humble/Mention)")
        return None

    # This next lines will just be executed in case the command is correct

    print(get_time() + f"[INFO]: {service.capitalize()} module disabled")
    await ctx.channel.send(u"\u2705 " + f"{service.capitalize()} module disabled.")

# Creates the file where the secret token will be stored
try:
    open("SToken.txt", "x")

except FileExistsError:
    pass

else:  # If there weren't any exceptions, the file will be created
    STokenFile = open("SToken.txt", "w")
    STokenFile.write("Introduce your bot's secret token in this line.")


with open("SToken.txt", "r") as f:  # Reads the secret token and starts the bot

    try:
        client.run(str(f.readlines()[0]))  # Runs the bot using the token stored in the first line of SToken.txt

    except discord.errors.LoginFailure:  # Handles the error produced by an incorrect secret token
        print(get_time() + "[ERROR]: Please, enter a valid secret token in SToken.txt")
