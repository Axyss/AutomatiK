<img src="http://www.axyss.ovh/automatik/ak_logo.png" alt="automatik_logo" align="right" width="180" height="180"></img>
<h1>AutomatiK</h1>
<b>Language:</b> <a href="README.md#automatik">English</a>, <a href="README_es_ES.md#automatik">Español</a>
<h2>¿Qué es AutomatiK?</h2>
AutomatiK es un <b>bot de Discord</b> cuya tarea es notificar a los usuarios sobre los juegos gratis de múltiples plataformas. Es completamente autónomo, tiene algunas <b>opciones configurables</b> y una base de datos integrada donde se almacena la información de los juegos ,y lo más importante, su <b>modularidad</b> nos proporciona la posibilidad de <b>programar nuestros propios módulos de forma muy sencilla.</b>
</br>
</br>
Las plataformas actualmemte soportadas son:

- Epic Games
- Humble Bundle
</br>
<b>Aviso:</b> AutomatiK no fue creado con la intención de ser un bot público, debido a ello, <b>no soporta más de un servidor de Discord a la vez</b>, evita invitarlo a múltiples servidores. No obstante, si lo único que quieres es recibir las notificaciones de los juegos gratis sin tener que configurar un bot, siempre puedes seguir la <a href="https://twitter.com/AutomatiK_bot">cuenta de Twitter de AutomatiK</a> o unirte a <a href="https://discord.gg/psDtnwX">este servidor de Discord.</a>

<h2>¿Cómo puedo usarlo?</h2>

<b>Prerrequisitos:</b>
- <a href="https://www.python.org/downloads/">Python 3.6 o superior</a>
- <a href="https://pypi.org/project/discord.py/">discord.py</a>
- <a href="https://pypi.org/project/beautifulsoup4/">BeautifulSoup4<a>
- <a href="https://pypi.org/project/requests/">requests<a>
Primero instalaremos Python y usaremos el comando `pip3 install -r requirements.txt` para instalar las dependencias anteriores.
Tras ello, tendremos que descargar el repositorio y extraerlo en una carpeta, después procederemos a crear la cuenta que el bot usará, si nunca lo has hecho sigue <a href="https://discordpy.readthedocs.io/en/latest/discord.html#creating-a-bot-account">este</a> tutorial. 

Una vez que lo hayamos hecho tendremos que vincular nuestra copia local de AutomatiK con la cuenta que hemos creado, para hacerlo copiaremos el secret token de nuestro bot (ten cuidado de no copiar el application's token por error) y lo pegaremos en la primera línea del archivo <i>SToken.txt</i> localizado en el directorio donde extrajimos anteriormente el repositorio.

A continuación invitaremos al bot a nuestro servidor, sigue <a href="https://discordpy.readthedocs.io/en/latest/discord.html#inviting-your-bot">esta</a> guía para hacerlo. <b>Asegúrate de proporcionarle permisos de administrador.</b>

Ahora ejecutaremos el bot desde el terminal/la consola.
<h4>Windows</h4>

`python bot.py`
<h4>Linux</h4>

`python3 bot.py`
</br>
</br>
<i>Si lo hemos hecho todo correctamente veremos un mensaje como este:</i> `[INFO]: AutomatiK bot now online`
</br>
</br>
La última parte consiste en iniciar el proceso principal del bot, usa <b><i>!mk start</i></b> en el canal de texto donde quieras que aparezcan las notificaciones, recibirás un mensaje de confirmación y eso es todo, AutomatiK ya se encontraría funcionando.
</br>
</br>
<img src="http://www.axyss.ovh/automatik/command_success_ES.png" align="bottom"></img>
</br>
<h2>Comandos</h2>
AutomatiK trabaja con el prefijo <b><i>!mk</i></b>. 
Puedes ver todos los comandos disponibles usando <b><i>!mk helpme</i></b>
<h3>Ejemplo:</h3> <img src="http://www.axyss.ovh/automatik/helpme_es_ES.png" alt="helpme"></img>
<h2>Licencia</h2>
Todo el <b>software</b> de este repositorio se encuentra licenciado bajo la licencia MIT, mientras que <b>todo el contenido gráfico y logos</b> se encuentran licenciados bajo Creative Commons Attribution-ShareAlike 4.0 International, haz click en el logo de debajo para conocer las limitaciones de esta licencia.
</br>
</br>
<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Licencia de Creative Commons" src="http://www.axyss.ovh/automatik/cc_license.png" width="120" height="40"></a>
<h2>Sugerencias</h2>
<b>¿Tienes alguna sugerencia? ¿Crees que AutomatiK debería soportar una plataforma en particular?</b>
</br>
Abre un Issue, me encantaría escuchar vuestras ideas.
