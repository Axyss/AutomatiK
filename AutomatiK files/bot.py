# coding=utf-8

import discord
import asyncio
from discord.ext import commands

import epic_mod
import humble_mod
import updates

import time
import os
import json
import re
import threading

client = commands.Bot(command_prefix="!mk ", self_bot=False)

mainLoopStatus = False  # Variable which starts or stops the main loop

dataConfig = None  # Loaded configuration
langM = None

# Template of the config
dataTemplate = {"role": "<@&1234>",
                "role_mention": False,
                "epic_status": True,
                "humble_status": True,
                "lang": "en_EN"}

# -----------------------REGULAR FUNCTIONS-----------------------


def pm(message):
    """Ignores PM messages"""

    if "Direct Message with" in str(message):
        return True


def get_time():
    """Generates a string with the neccessary date and time format"""

    return time.strftime('[%Y/%m/%d]' + '[%H:%M]')


def generate_message(title, link):
    """Generates some messages the bot sends"""
    # If third parameter True, then the message is for discord
    # This lets the function knows where the message is going to be sent and adds the mention if required

    global dataConfig
    global langM

    draft = langM["procedural_message"].format(title, link)

    if dataConfig["role_mention"]:  # If role_mention is True, then adds the role parameter from config
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
    """Loads the config from the file"""

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


def load_lang():
    """Loads the language file based on the 'lang' option from config.json"""

    global dataConfig
    global langM

    file = open(f"lang/{dataConfig['lang']}.json", "r", encoding="utf-8")
    langM = json.load(file)["messages"]
    file.close()


def get_available_languages():
    """Obtains a list containing all the available languages for AutomatiK"""

    language_list = os.listdir("lang/")  # Obtains the name of the files in lang to generate a list

    parsed_language_list = []

    for i in language_list:  # Adds to the new list the file names without their extensions
        parsed_language_list.append(i[0:i.rindex(".")])

    # Converts all the parsed list into a string with separators
    parsed_language_list = "/".join(parsed_language_list)

    return parsed_language_list

# -----------------------EVENTS-----------------------


@client.event
async def on_ready():

    print(get_time() + "[INFO]: AutomatiK bot now online")

    load_config()
    load_lang()

    check_config_changes()

    """Start of the version checker"""

    obj = updates.Check_Updates(local_version="v1.1_4",
                                link="https://github.com/Axyss/AutomatiK/releases")
    threading.Thread(target=obj.start_checking).start()  # Starts thread that checks updates

    """End of the version checker"""

    await client.change_presence(status=discord.Status.online,  # Changes status to "online"
                                 activity=discord.Game("!mk helpme")  # Changes activity (playing)
                                 )


@client.event
async def on_command_error(ctx, error):  # The second parameter is the error's information
    """Function used for error handling"""
    global langM

    if isinstance(error, discord.ext.commands.MissingPermissions):
        """In case the user who tries to run the command does not have administrator perms, run this"""

        await ctx.channel.send(langM["missing_permissions"])


# -----------------------COMMANDS-----------------------

@client.command()
@commands.has_permissions(administrator=True)
async def notify(ctx, *args):

    global langM

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
        gameName, link) + langM["notify_thanks"].format(ctx.author.id)  # Adds politeness
    )


@client.command()
@commands.has_permissions(administrator=True)
async def mention(ctx, roleid):
    """Manages the mentions of the bot's messages"""

    global langM

    if pm(ctx.channel):
        return None

    if re.search("^<@&\w", roleid) and re.search(">$", roleid):
        # If the string follows the std structure of a role <@&1234>, then...

        edit_config("role", roleid)

        print(get_time() + "[INFO]: AutomatiK will now mention:", roleid)
        await ctx.channel.send(langM["mention_established"])


@client.command()
async def helpme(ctx):
    """Help command that uses embeds"""
    global langM

    embed_help = discord.Embed(title="AutomatiK Help", color=0x00BFFF)

    embed_help.set_footer(text=langM["embed_footer"],
                          icon_url="https://avatars3.githubusercontent.com/u/55812692"
                          )

    embed_help.set_thumbnail(
        url="http://www.axyss.ovh/automatik/ak_logo.png"
    )

    embed_help.add_field(name=langM["embed_field1_name"],
                         value=langM["embed_field1_value"],
                         inline=False)

    embed_help.add_field(name=langM["embed_field2_name"],
                         value=langM["embed_field2_value"].format(get_available_languages()),
                         inline=False)

    await ctx.channel.send(embed=embed_help)


@client.command()
@commands.has_permissions(administrator=True)
async def start(ctx):
    """Starts the AutomatiK service"""

    global mainLoopStatus
    global dataConfig  # Gets config values
    global langM

    if pm(ctx.channel):  # Checks if pm
        return None

    if mainLoopStatus:  # If service already started
        await ctx.channel.send(langM["start_already"])
        return None

    print(get_time() +
          "[INFO]: AutomatiK was started by",
          str(ctx.author)
          )

    await ctx.channel.send(langM["start_success"])

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

            evGD = tuple(epic_mod.obj.validGameData)

            for i in evGD:

                await ctx.channel.send(
                    generate_message(i[0], i[1])
                )

        # Humble Bundle caller
        if humble_mod.obj.check_database() and dataConfig["humble_status"]:  # If Humble module is enabled in config

            # Message that will be sent to the guild.
            hvGD = tuple(humble_mod.obj.validGameData)

            for i in hvGD:

                await ctx.channel.send(
                    generate_message(i[0], i[1])
                )

        await asyncio.sleep(300)  # It will check free games every 5 minutes


@client.command()
@commands.has_permissions(administrator=True)
async def stop(ctx):
    """Stops the AutomatiK service"""

    global mainLoopStatus
    global langM

    if pm(ctx.channel):
        return None

    if not mainLoopStatus:  # If service already stopped
        await ctx.channel.send(langM["stop_already"])
        return None

    print(get_time() +
          "[INFO]: AutomatiK was stopped by",
          str(ctx.author)
          )

    await ctx.channel.send(langM["stop_success"])

    mainLoopStatus = False  # Stops the loop by changing the boolean which maintains It active


@client.command()
async def status(ctx):
    """Shows the status of the service"""

    global dataConfig
    global mainLoopStatus
    global langM

    if pm(ctx.channel):
        return None

    if mainLoopStatus:
        mainService = langM["status_active"]
    else:
        mainService = langM["status_inactive"]

    if dataConfig["epic_status"]:
        epicModule = langM["status_active"]
    else:
        epicModule = langM["status_inactive"]

    if dataConfig["humble_status"]:
        humbleModule = langM["status_active"]
    else:
        humbleModule = langM["status_inactive"]

    if dataConfig["role_mention"]:
        roleMention = langM["status_active"]
    else:
        roleMention = langM["status_inactive"]

    await ctx.channel.send(langM["status"].format(
        mainService, epicModule, humbleModule, roleMention)
    )


@client.command()
@commands.has_permissions(administrator=True)
async def enable(ctx, service):
    """Global manager to enable some AutomatiK services"""

    global langM

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
        await ctx.channel.send(langM["mention_enabled"])
        return None

    else:
        await ctx.channel.send(langM["enable_unknown"])
        return None

    # This next lines will just be executed in case the command is correct

    print(get_time() + f"[INFO]: {service.capitalize()} module enabled")
    await ctx.channel.send(langM["module_enabled"].format(service.capitalize()))


@client.command()
@commands.has_permissions(administrator=True)
async def disable(ctx, service):
    """Global manager to disable some AutomatiK services"""

    global langM

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
        await ctx.channel.send(langM["mention_disabled"])
        return None

    else:
        await ctx.channel.send(langM["disable_unknown"])
        return None

    # This next lines will just be executed in case the command is correct

    print(get_time() + f"[INFO]: {service.capitalize()} module disabled")
    await ctx.channel.send(langM["module_disabled"].format(service.capitalize()))


@client.command()
@commands.has_permissions(administrator=True)
async def language(ctx, langcode):

    global langM

    edit_config("lang", langcode)  # Edits the config value which contains what lang is going to be loaded
    load_lang()  # Reloads the language

    print(get_time() + f"[INFO]: Language changed to {langcode}")
    await ctx.channel.send(langM["language_changed"])


# Creates the file where the secret token will be stored
try:
    open("SToken.txt", "x")

except FileExistsError:
    pass

else:  # If there weren't any exceptions, the file will be written

    STokenFile = open("SToken.txt", "w")
    STokenFile.write("Introduce your bot's secret token in this line.")
    STokenFile.close()


with open("SToken.txt", "r") as f:  # Reads the secret token and starts the bot

    try:
        client.run(str(f.readlines()[0]))  # Runs the bot using the token stored in the first line of SToken.txt

    except discord.errors.LoginFailure:  # Handles the error produced by an incorrect secret token
        print(get_time() + "[ERROR]: Please, enter a valid secret token in SToken.txt")
        input("Press enter to close...")  # Avoids the window from closing instantaneously
