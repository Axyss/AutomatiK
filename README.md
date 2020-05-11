<img src="http://www.axyss.ovh/automatik/ak_logo.png" alt="automatik_logo" align="right" width="180" height="180"></img>
<h1>AutomatiK</h1>
<b>Language:</b> <a href="README.md#automatik">English</a>, <a href="README_es_ES.md#automatik">Español</a>
<br>
<br>
<b><a href="FUTURE.md">Next updates and the future of this project</a></b>
</br>
<h2>What is AutomatiK?</h2>
AutomatiK is a <b>Discord bot</b> whose task is to notify users about free games from multiple platforms. It's completely automatic, has some <b>configuration options</b> and a built-in database where game data is stored.
</br>
</br>
The currently supported platforms are:

- Epic Games
- Humble Bundle
</br>
<b>Disclaimer:</b> AutomatiK was never meant to be a public bot, due to that, <b>It does not support more than one Discord server at a time</b>, so avoid inviting It to multiple servers.

<h2>How can I use It?</h2>

<b>Prerequisites:</b> 
- <a href="https://www.python.org/downloads/">Python 3.6 or higher</a>
- <a href="https://pypi.org/project/discord.py/">discord.py</a>
- <a href="https://pypi.org/project/beautifulsoup4/">BeautifulSoup4<a>
- <a href="https://pypi.org/project/requests/">requests<a>
  
First of all we have to download the repository and extract It in a folder, then we will proceed to create a bot account, If you have never done It, then follow <a href="https://discordpy.readthedocs.io/en/latest/discord.html#creating-a-bot-account">this</a> tutorial. 

Once we've done It we have to link our local copy of AutomatiK with our new bot, to do so we will copy our bot's secret token (be careful not to copy the application's token instead) and paste It in the first line of the file <i>SToken.txt</i> located in the directory where we extracted the program before.

In the next place we will invite the bot to our server, follow <a href="https://discordpy.readthedocs.io/en/latest/discord.html#inviting-your-bot">this</a> guide to do so. <b>Make sure to give It administrator privileges.</b>

Now let's execute the bot from the terminal/console.
<h4>Windows</h4>

`python bot.py`
<h4>Linux</h4>

`python3 bot.py`
</br>
</br>
<i>If we've done everything correctly we will see a message like this:</i> `[INFO]: AutomatiK bot now online`
</br>
</br>
The last part consists on starting the principal process of the bot, use <b><i>!mk start</i></b> in the text channel where you want the notifications to show up, you will recieve a confirmation message... And that's It!
</br>
</br>
<img src="http://www.axyss.ovh/automatik/command_success.png" align="bottom"></img>
</br>
<h2>Commands</h2>
Automatik works with the prefix <b><i>!mk</i></b>. 
You can see all the available commands using <b><i>!mk helpme</i></b>
<h3>Example:</h3> <img src="http://www.axyss.ovh/automatik/helpme.png" alt="helpme_ss"></img>
<h2>License</h2>
All the <b>software</b> of this repository is licensed under the MIT license, while <b>all the graphical content and logos</b> are licensed under Creative Commons Attribution-ShareAlike 4.0 International, click the logo down below to know more about the limitations of this license.
</br>
</br>
<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Licencia de Creative Commons" src="http://www.axyss.ovh/automatik/cc_license.png" width="120" height="40"></a>
<h2>Suggestions</h2>
<b>Do you have any suggestion? Do you think AutomatiK should support an specific platform?</b>
</br>
Open an Issue, I'll be more than happy to hear your ideas.
