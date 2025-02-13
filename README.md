
# Soccer API

A simple to use Python library that connects [API-Football](https://www.api-football.com/) to several online football data providers and allow for the easier collection of league, team and player data for use by amature football data analysts.

# Getting Started

## 1. Install from Git

```bash
git install https://github.com/JohnComonitski/SoccerAPI
```

## 2. Install Dependencies

```py
!pip install -r ./SoccerAPI/requirements.txt
```

## 3. Set Up Config

```py
config = {
    "fapi_host" : "api-football-v1.p.rapidapi.com",
    "fapi_key" : "API-FOOTBALL API KEY",
}
```

> **NOTE:** Many features in this library require API-Football API tokens. Get started with API-Footballs free tier **[here](https://www.api-football.com/pricing)**, however it is recommended serious analysis or data collection be performed using a paid tier, otherwise you will be limited to 100 requests per day.

## 4. Instantiate Football API

```py
api = SoccerAPI(config)
```

## 5. Begin Data Collection or Analysis

```py
haaland = api.db.get("players", "82172")
stat = Haaland.statistic("shots")
```
> Collects Haaland's number of shots this season.