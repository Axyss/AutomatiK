<div align="center">
  <img src="https://raw.githubusercontent.com/Axyss/AutomatiK/master/docs/assets/ak_logo.png" alt="automatik_logo" width="180" height="180">
</div>

> **IMPORTANT**: This project is currently undergoing major refactors. Consider waiting until version 2.0 is released for production use.

## 📋 Overview

AutomatiK is a Discord bot that notifies users about free games from multiple platforms. It features an autonomous operation system, configuration options, an integrated database for game data storage, and a modular architecture that allows for easy extension.

### 🎮 Supported Platforms

- Steam
- Epic Games
- Humble Bundle
- Ubisoft Connect

## 🚀 Installation

### ⚙️ Prerequisites

- Python 3.6+
- Dependencies: discord.py, beautifulsoup4, requests

### 💻 Standard Installation

```bash
# Clone and enter repository
git clone https://github.com/Axyss/AutomatiK.git && cd AutomatiK

# Install dependencies
pip install -r requirements.txt

# Run the bot
python3 bot.py
```

Enter your Discord bot token when prompted, invite the bot to your server with admin privileges, and run `!mk start` in your desired notification channel.

### 🐳 Docker Installation

AutomatiK can also be run using Docker:

1. Configure environment variables:
   - Set `DISCORD_TOKEN` with your bot token
   - Set `BOT_OWNER` with your Discord user ID

2. Run with docker-compose:
   ```bash
   docker-compose up -d
   ```

3. Invite the bot to your server and use `!mk start` to initialize as with the standard installation.

## 📝 Usage

### 🤖 Commands

AutomatiK uses the prefix `!mk`. View available commands with `!mk help`.

![Help Command Example](https://raw.githubusercontent.com/Axyss/AutomatiK/master/docs/assets/help.png)

## 💡 Development

### 🧩 Creating Custom Modules

To develop your own modules for the bot, refer to the [module creation guide](https://github.com/Axyss/AutomatiK/blob/master/docs/module_guide.md).

## 📜 License

All software in this repository is licensed under the MIT license. The graphical content and logos are licensed under Creative Commons Attribution-ShareAlike 4.0 International.
