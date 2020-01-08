<img src="http://www.axyss.ovh/automatik/ak_logo.png" alt="automatik_logo" align="right" width="180" height="180"></img>
<h1>AutomatiK</h1>
</br>
<h2>¿Qué es AutomatiK?</h2>
AutomatiK es un <b>bot de Discord</b> cuya tarea es notificar a los usuarios sobre los juegos gratis de múltiples plataformas. Es completamente automático, tiene algunas <b>opciones configurables</b> y una base de datos integrada donde se almacena la información de los juegos.
</br>
</br>
Las plataformas actualmemte soportadas son:

- Epic Games
- Humble Bundle
</br>
<b>Aviso:</b> AutomatiK no fue creado con la intención de ser un bot público, debido a ello, <b>no soporta más de un servidor de Discord a la vez</b>, evita invitarlo a múltiples servidores.

<h2>¿Cómo puedo usarlo?</h2>

<b>Prerrequisitos:</b> <a href="https://www.python.org/downloads/">Python 3.6 o más</a> y <a href="https://pypi.org/project/discord.py/">discord.py</a>.
</br>
</br>
En primer lugar descargaremos el repositorio y lo extraeremos en una carpeta, tras ello, procederemos a crear la cuenta que el bot usará, si nunca lo has hecho sigue <a href="https://discordpy.readthedocs.io/en/latest/discord.html#creating-a-bot-account">este</a> tutorial. 

Once we've done It we have to link our local copy of AutomatiK with our new bot, to do so we will copy our bot's secret token (be careful not to copy the application's token instead) and paste It in the first line of the file <i>SToken.txt</i> located in the directory where we extracted the program before.

In the next place we will invite the bot to our server, follow <a href="https://discordpy.readthedocs.io/en/latest/discord.html#inviting-your-bot">this</a> guide to do so. <b>Make sure to give It administrator privileges.</b>

Now let's execute the bot from the terminal/console.
<h4>Windows</h4>

`python bot.py`
<h4>Linux</h4>

`python3 bot.py`
</br>
</br>
<i>Si lo hemos hecho todo correctamente veremos un mensaje como este:</i> `[INFO]: AutomatiK bot now online`
</br>
</br>
The last part is to start the principal process of the bot, use <b><i>!mk start</i></b> in the text channel where you want the notifications to show up, you will recieve a confirmation message and that's It.
</br>
</br>
<img src="http://www.axyss.ovh/automatik/command_success.png" align="bottom"></img>
</br>
<h2>Comandos</h2>
Automatik works with the prefix <b><i>!mk</i></b>. 
You can see all the available commands using <b><i>!mk helpme</i></b>
<h3>Example:</h3> <img src="http://www.axyss.ovh/automatik/helpme.png" alt="helpme_ss"></img>
<h2>Licencia</h2>
Todo el <b>software</b> de este repositorio se encuentra licenciado bajo la licencia MIT, mientras que <b>todo el contenido gráfico y logos</b> se encuentran licenciados bajo Creative Commons Attribution-ShareAlike 4.0 International, haz click en el logo de debajo para conocer las limitaciones de esta licencia.
</br>
</br>
<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Licencia de Creative Commons" src="http://www.axyss.ovh/automatik/cc_license.png" width="120" height="40"></a>
<h2>Sugerencias</h2>
<b>¿Tienes alguna sugerencia? ¿Crees que AutomatiK debería soportar una plataforma en particular?</b>
</br>
Abre una pull request, me encantaría escuchar vuestras ideas.
