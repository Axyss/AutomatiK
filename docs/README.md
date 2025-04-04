<h1 style="text-align:center"> ❗🚧IMPORTANT🚧❗ </h1>
<h3 style="text-align:center">
This project is currently undergoing some major refactors. 
We recommend waiting until version 1.5 is released if you want to give it a try.
</h3>
<img src="https://raw.githubusercontent.com/Axyss/AutomatiK/master/docs/assets/ak_logo.png" alt="automatik_logo" align="right" width="180" height="180"></img>
<h1>AutomatiK</h1>
<b>Language:</b> <a href="README.md#automatik">English</a>, <a href="README_es_ES.md#automatik">Español</a>
<br>
<br>
<a href="https://www.codefactor.io/repository/github/axyss/automatik"><img src="https://www.codefactor.io/repository/github/axyss/automatik/badge" alt="CodeFactor" /></a>
<h2>What is AutomatiK?</h2>
AutomatiK is a <b>Discord bot</b> whose task is to notify users about free games from multiple platforms. It's completely autonomous, has some <b>configuration options</b>, a built-in database where game data is stored and, most importantly, it's <b>modularity</b> brings the ability to <b>code, add, and remove modules very easily.</b>
<br>
<br>
The default modules support the next services:

- Steam
- Epic Games
- Humble Bundle
- Ubisoft Connect
<br>
<s><b>Disclaimer:</b> AutomatiK was never meant to be a public bot, due to that, <b>it does not support more than one Discord server at a time</b>, avoid inviting it to multiple servers. Nevertheless <b>If you just want to receive the free games</b> notifications without setting-up a whole bot, you can always follow <a href="https://twitter.com/AutomatiK_bot">AutomatiK's Twitter account</a> or join <a href="https://discord.gg/psDtnwX">this Discord server.</a></s> This will change next update.

<h2>How can I use it?</h2>

<b>Prerequisites:</b> 
- <a href="https://www.python.org/downloads/">Python 3.6 or higher</a>
- <a href="https://pypi.org/project/discord.py/">discord.py</a>
- <a href="https://pypi.org/project/beautifulsoup4/">BeautifulSoup4<a>
- <a href="https://pypi.org/project/requests/">requests<a><br>
  
First we'll install Python and use the command `pip3 install -r requirements.txt` to install all the previous dependencies.
After that, we have to download the repository and extract it in a folder, then we will proceed to create a bot account, If you have never done it, then follow <a href="https://discordpy.readthedocs.io/en/latest/discord.html#creating-a-bot-account">this</a> tutorial. 

Once we've done it we have to link our local copy of AutomatiK with our new bot, to do so we will execute the program using the next command in the terminal:
<h4>Windows</h4>

`python bot.py`
<h4>Linux</h4>

`python3 bot.py`<br>
<br>
This will cause a message like this one: `[INFO]: Please introduce your bot's secret token:` to show up on the terminal. After this we'll simply paste our token there and press enter.
<br><i>If we've done everything correctly we will see a message like this:</i> `[INFO]: AutomatiK bot now online`

In the next place we will invite the bot to our server, follow <a href="https://discordpy.readthedocs.io/en/latest/discord.html#inviting-your-bot">this</a> guide to do so. <b>Make sure to give it administrator privileges.</b>
<br>
<br>
The last part consists on starting the principal process of the bot, use <b><i>!mk start</i></b> in the text channel where you want the notifications to show up, you will recieve a confirmation message... And that's it, our bot should be fully working! If we wanted to <b>stop the bot completely</b>, we need to use the command `shutdown` on
the terminal window where the bot is running.
<br>
<br>
<img src="https://raw.githubusercontent.com/Axyss/AutomatiK/master/docs/assets/command_success.png" align="bottom"></img>
<br>
<h2>Commands</h2>
Automatik works with the prefix <b><i>!mk</i></b>. 
You can see all the available commands using <b><i>!mk help</i></b>
<h3>Example:</h3> <img src="https://raw.githubusercontent.com/Axyss/AutomatiK/master/docs/assets/help.png" alt="helpme_ss" align="center"></img>
<h2>How can I code my own modules?</h2>
To learn how to create modules check <a href="https://github.com/Axyss/AutomatiK/blob/master/docs/module_guide.md">this guide.</a>
<h2>License</h2>
All the <b>software</b> of this repository is licensed under the MIT license, while <b>all the graphical content and logos</b> are licensed under Creative Commons Attribution-ShareAlike 4.0 International, click the logo down below to know more about the limitations of this license.
<br>
<br>
<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Licencia de Creative Commons" src="https://raw.githubusercontent.com/Axyss/AutomatiK/master/docs/assets/cc_by_sa.png" width="120" height="40"></a>
<h2>Suggestions</h2>
<b>Do you have any suggestion? Do you think AutomatiK should support an specific platform?</b>
<br>
Open an Issue, I'll be more than happy to hear your ideas.
