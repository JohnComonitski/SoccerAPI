
# Soccer API

A Python library that connects [API-Football](https://www.api-football.com/) to several online football data providers and allow for the easier collection of league, team and player data for use by amature football data analysts.

# Data Sources

Soccer API is powered by a database mapping the IDs of over 82,000 players, 4200 teams, and 200 leagues. This allows for the seamless programatic access and combination of data across the following sites: 
 - API-Football
 - FBRef
 - Transfermarkt
 - Understat

# Getting Started

### 1. Install from Git

```bash
git install https://github.com/JohnComonitski/SoccerAPI
```

### 2. Install Dependencies

```py
!pip install -r ./SoccerAPI/requirements.txt
```

> **NOTE:** Psycopg2 may give you trouble installing. Consider installing from its **[binary](https://pypi.org/project/psycopg2-binary/)**.

### 3. Set Up Config

```py
config = {
    "fapi_host" : "api-football-v1.p.rapidapi.com",
    "fapi_key" : "API-FOOTBALL API KEY",
}
```

> **NOTE:** Many features in this library require a API-Football API key. You can get started with by using API-Football's free tier **[here](https://www.api-football.com/pricing)**, btu it is recommended for serious analysis or larger data collection projects you use a paid tier, otherwise you will be limited to 100 requests per day.

### 4. Instantiate Soccer API

```py
api = SoccerAPI(config)
```

### 5. Begin Data Collection or Analysis

```py
haaland = api.db.get("players", "82172")
stat = Haaland.statistic("shots")
```
> Collects Erling Haaland's number of shots this season.