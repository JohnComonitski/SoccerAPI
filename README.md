# Soccer API

A Python library that connects [API-Football](https://www.api-football.com/)
to several online football data providers and allow for the easier collection
of league, team and player data for use by amature football data analysts.

<!--TOC-->

## Features

## Data Sources

Soccer API is powered by a database mapping the IDs of over 82,000 players,
4200 teams, and 200 leagues. This allows for the seamless programatic access
and combination of data across the following sites: 

- [API-Football](https://www.api-football.com/)
- [FBRef](https://fbref.com)
- [Transfermarkt](https://www.transfermarkt.com/)
- [Understat](https://understat.com/)

## Getting Started

1. clone the repository

   ```shell
   git clone https://github.com/JohnComonitski/SoccerAPI.git
   ```

2. move to the project directory

   ```shell
   cd SoccerAPI
   ```

3. create and acrivate a Python
   [virtual environment](https://docs.python.org/3/library/venv.html#creating-virtual-environments)
4. install the Python dependencies

   ```shell
   pip install -r requirements.txt
   ```

   > [!NOTE]
   > Psycopg2 may give you trouble installing. For this reason the project uses
   > the [binary](https://pypi.org/project/psycopg2-binary/) version of the
   > library.

5. create a new Python file and set up the configuration

   ```python
   import soccerapi.soccerapi

   config = {
       "fapi_host" : "api-football-v1.p.rapidapi.com",
       "fapi_key" : "API-FOOTBALL API KEY",
   }
   ```

> [!NOTE]
> Many features in this library require a API-Football API key. You can get started with by using API-Football's free tier **[here](https://www.api-football.com/pricing)**. For serious analysis, or for larger data collection projects, it is recommended you use a paid tier, otherwise you will be limited to 100 requests per day.

6. Instantiate Soccer API

   ```python
   api = soccerapi.soccerapi.SoccerAPI(config)
   ```

7. Begin Data Collection or Analysis

   ```python
   haaland = api.db.get("players", "82172")
   stat = haaland.statistic("shots")
   ```

   > Collects Erling Haaland's number of shots this season.

## License

MIT License
Copyright (c) 2025 John Comonitski
