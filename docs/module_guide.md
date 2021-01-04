# How to create AutomatiK modules (v1.3)

## Introduction
Even though AutomatiK can run perfectly fine without them, they bring the most important part to it, 
which is adding support to platforms and services. In the example below, we will work on the creation of a module
that will scrape the free games from an imaginary platform called **Great Games**.

### Structure of a module:

```python
from core.log_manager import logger
from core.module_manager import Game

class Main:
    def __init__(self):
        self.SERVICE_NAME = "Great Games"
        self.MODULE_ID = "ggames"
        self.AUTHOR = "Axyss"
    
    def get_free_games(self):
        return [Game("Minecraft", "https://.../minecraft"), 
                Game("The Stanley Parable", "https://.../stanley")]
```

## Step 1: File creation
The first step into the creation of a module would be cloning/downloading the repository and creating a file with 
the .py extension inside the _modules_ folder. The name of the module **doesn't need to meet any special criteria**.

## Step 2: Imports and dependencies
Our second step is to import the **Game class**, and the **logger object**. 
``` python
from core.log_manager import logger
from core.module_manager import Game
```
The **logger** object brings an organized and unified way to print all types of messages into the console and save
them in **.log** files. It supports multiple **levels** that can be used depending on the context of the message (debug,
error, info...).

|Level|Regular usage|
|------|------|
|CRITICAL|logger.critical("Message")|
|EXCEPTION|logger.exception("Message")|
|WARNING|logger.warning("Message")|
|INFO|logger.info("Message")|
|DEBUG|logger.debug("Message")|

They all are very similar, nevertheless, the **EXCEPTION** level must be contained inside a Python _except_ block.
Visit [this webpage](https://docs.python.org/3/library/logging.html "Logging library documentation") to learn more
about the logging library and the logging levels.

The **Game** class is used to create objects that represent free games. A **Game** object requires two positional 
parameters to be created: _name_ and _link_. 
<br>
_Example:_ 
``` python
Game("Counter-Strike: Global Offensive", "http://.../free-csgo")
```
Tip: It is recommended to use the libraries default modules use to retrieve and parse data. You can consult the 
entire list in the [requirements.txt](../requirements.txt "requirements.txt") file.

## Step 3: Methods and attributes

There are some minimum elements a module needs to be loaded and integrated properly, those are:

1. A class named **Main**.
2. The next attributes in the constructor of the **Main** class:
     - **SERVICE_NAME** _(String)_ : Name of the platform/s the module provides support to.
     - **AUTHOR** _(String)_ : Name/Nickname of the module's author.
     - **MODULE_ID** _(String)_ : Short name of the module that will be used in commands, **it must be unique** and 
       separated with underscores if contains more than one word. **It's not case-sensitive**.
       
         |Examples of ModuleIDs||
         |----------|:-------------:|
         |"great games"|❌|
         |"Great_Games"|✔️|
         |"great_games"|✔️|
   
3. The next methods inside the **Main** class:
   - **get_free_games()** : Method that will be called by the AutomatiK core, it has to return a list of Game 
     objects or False/[ ] if no free games were found by the module.
    

There are also **optional** elements that can be used if needed:
1. Attributes inside the **Main** class:
   - **THRESHOLD** _(Default: 6)_ _(int)_: The bot automatically detects if the **Game** objects retrieved from 
     a **get_free_games()** method have already been announced, to do so, it checks the last 6 registries added to
     the database table of the module they come from. The **THRESHOLD** attribute brings the ability to change the
     number of registries that will be taken from the database to decide if the game should be notified or not.
     <br>
     <br>
 ⚠️**WARNING**: **THRESHOLD** values that are too low may cause an infinite loop of notifications, while 
 very high ones may result in some games not being notified.
<br>
<br>     
2. Methods inside the **Main** class:
   - Nothing yet. 🚧
    
## Step 4: That's all!🎉

If you have followed all the steps correctly, you should have a fully working module similar to the one at
the beginning of this guide, the last step would be to create methods to scrape data from a web or an API and give the
module a real purpose. 

If you find any problems following this guide or with the bot itself, open a 
[GitHub Issue](https://github.com/Axyss/AutomatiK/issues "GitHub Issue") or join the 
[AutomatiK Discord server](https://discord.gg/psDtnwX "AutomatiK Discord server").
<br>
<br>
Happy coding :)
