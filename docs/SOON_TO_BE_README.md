<div align="center">
  <img src="https://raw.githubusercontent.com/Axyss/AutomatiK/master/docs/assets/ak_logo.png" alt="AutomatiK logo" width="180" height="180">
  <h3>AutomatiK</h3>
  <p>A Discord bot that tracks free game offers across multiple platforms and notifies your server.</p>

  ![Python 3.12](https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white)
  ![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white)
  ![License](https://img.shields.io/badge/license-MIT-green)
</div>

---

> [!NOTE]
> Readme under construction

## Features

## Getting Started

### Docker (recommended)

```bash
git clone https://github.com/Axyss/AutomatiK.git && cd AutomatiK
```

Set `DISCORD_TOKEN` and `DB_URI` in `docker-compose.yml`, then:

```bash
docker compose up -d
```

### Manual

**Requirements:** Python 3.12, and a running MongoDB instance.

```bash
git clone https://github.com/Axyss/AutomatiK.git && cd AutomatiK
pip install -r requirements.txt
cp .env.template .env
```

Fill in the values in the `DISCORD_TOKEN` and `DB_URI` in `.env`, then:

```bash
python -m automatik.bot
```

### First run

## Commands

## License
