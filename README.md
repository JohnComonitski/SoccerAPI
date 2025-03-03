# Soccer API

A Python library that connects [API-Football](https://www.api-football.com/)
to several online football data providers and allow for the easier collection
of league, team and player data for use by amature football data analysts.

<!--TOC-->

- [Soccer API](#soccer-api)
  - [Documentation](#documentation)
  - [Features](#features)
  - [Data Sources](#data-sources)
  - [Getting Started](#getting-started)
  - [License](#license)

<!--TOC-->

## Documentation

The documentation covers practical examples with tutorials, quickstart and
object classes API.

[Documentation](http://johncomonitski.com/soccerapi/docs)

## Features

🏃 Access to the cross-site ID mapping of over 82,000 players
🛡️ Access to the cross-site ID mapping of over 4200 teams
🏆 Access to the cross-site ID mapping of over 200 leagues
💰 Get the latest market values of players, teams and leagues 
📊 Collect players, teams and match statistics
⚽ Access to near real-time fixture results and statistics
📅 Access to thousands of club's fixture lists and results & statistics from previous fixtures
🔎 Programmatically combine data from multiple sources to perform data driven scouting ([Example](https://medium.com/@johncomonitski/data-driven-scouting-with-python-and-soccer-api-88570c59f592))
 
Features Coming Soon:
📈 Generate data visualizations using player, club and league statistics

## Data Sources

Soccer API is powered by a database mapping the IDs of over 82,000 players,
4200 teams, and 200 leagues. This allows for the seamless programatic access
and combination of data across the following sites:

- [API-Football](https://www.api-football.com/)
- [FBRef](https://fbref.com)
- [Transfermarkt](https://www.transfermarkt.com/)
- [Understat](https://understat.com/)

*Note: Data collected by this library belongs to its respective rights holders. Data collected using this library should only be used for private projects/research and not commercial purposes.*

## Getting Started

1. clone the repository

   ```shell
   git clone https://github.com/JohnComonitski/SoccerAPI.git
   ```

2. move to the project directory

   ```shell
   cd SoccerAPI
   ```

3. create and activate a Python
   [virtual environment](https://docs.python.org/3/library/venv.html#creating-virtual-environments).
   On GNU/Linux systems this is as easy as:

   ```shell
   python3 -m venv .venv
   . .venv/bin/activate
   # Work inside the environment.
   ```

4. install the Python dependencies

   ```shell
   pip install -r requirements.txt
   ```

> [!NOTE]
> The standard Psycopg2 Python package may give you trouble installing. For
> this reason the project uses the [binary](https://pypi.org/project/psycopg2-binary/)
> version of that library.

5. create a new Python file and set up the configuration

   ```python
   import soccerapi.soccerapi

   config = {
       "fapi_host" : "API-FOOTBALL HOST",
       "fapi_key" : "API-FOOTBALL API KEY",
   }
   ```

> [!NOTE]
> Many features in this library require a API-Football API key. You can get
> started with by using API-Football's free tier
> **[here](https://www.api-football.com/pricing)**.
> For serious analysis, or for larger data collection projects, it is
> recommended you use a paid tier, otherwise you will be limited to 100
> requests per day.

6. instantiate a SoccerAPI object

   ```python
   api = soccerapi.soccerapi.SoccerAPI(config)
   ```

7. begin data collection or analysis

   ```python
   haaland = api.db.get("players", "82172")
   stat = haaland.statistic("shots")
   ```

   In this example we collect Erling Haaland's number of shots this season.

## License

MIT License
Copyright (c) 2025 John Comonitski
