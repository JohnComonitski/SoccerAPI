Tutorials
=========

Preparation
-----------

Before using the API you need to create a new SoccerAPI object

.. code-block:: python

   import soccerapi.soccerapi
   config = {"fapi_host" : "v3.football.api-sports.io", "fapi_key" : "API-FOOTBALL API KEY"}
   api = soccerapi.soccerapi.SoccerAPI(config)

All the following examples will use the ``api`` object just mentioned.

Examples
--------

Get objects using Soccer API IDs
````````````````````````````````

Use the ``get`` method from ``db`` to quickly grab objects if you know its
Soccer API primary key. Tables available to search on are players, teams and
leagues.

.. code-block:: python

   # Get Erling Haaland
   >>> api.db.get("players", "82172")
   Player(Erling Braut Haaland)

   # Get Premier League (man_city)
   >>> api.db.get("teams", "5874")
   Team(Manchester City - GB)

   # Get Premier League
   >>> api.db.get("leagues", "12")
   League(Premier League - GB)

Search objects using Foreign IDs
````````````````````````````````

Use the ``search`` method from ``db`` to search for objects using an object's
foreign ID. Tables available to search on are players, teams and leagues.

.. code-block:: python

   # Search for Erling Haaland using API-Football ID, Transfermarkt ID and FBRef ID respectively
   >>> api.db.search("players", { "fapi_player_id" : "1100"})
   [Player(Erling Braut Haaland)]

   >>> api.db.search("players", { "tm_player_id" : "418560"})
   [Player(Erling Braut Haaland)]

   >>> api.db.search("players", { "fbref_player_id" : "1f44ac21"})
   [Player(Sebastian Lie Haaland)]

   # Search for Man City using API-Football ID, Transfermarkt ID and FBRef ID respectively
   >>> api.db.search("teams", { "fapi_player_id" : "33"})
   soccerapi/lib/postgres.py, line 282, in search if str(query[key]) in self.cache[table_name][key]: KeyError: 'fapi_player_id'

   >>> api.db.search("teams", { "tm_player_id" : "985"})
   soccerapi/lib/postgres.py, line 282, in search if str(query[key]) in self.cache[table_name][key]: KeyError: 'tm_player_id'

   >>> api.db.search("teams", { "fbref_player_id" : "19538871"})
   soccerapi/lib/postgres.py, line 282, in search if str(query[key]) in self.cache[table_name][key]: KeyError: 'fbref_player_id'

   # Search for Premier League using API-Football ID, Transfermarkt ID and FBRef ID respectively
   >>> api.db.search("leagues", { "fapi_player_id" : "39"})
   soccerapi/lib/postgres.py, line 282, in search if str(query[key]) in self.cache[table_name][key]: KeyError: 'fapi_player_id'

   >>> api.db.search("leagues", { "tm_player_id" : "GB1"})
   soccerapi/lib/postgres.py, line 282, in search if str(query[key]) in self.cache[table_name][key]: KeyError: 'tm_player_id'

   >>> api.db.search("leagues", { "fbref_player_id" : "9"})
   soccerapi/lib/postgres.py, line 282, in search if str(query[key]) in self.cache[table_name][key]: KeyError: 'fbref_player_id'

Export an object
````````````````

Export and save a JSON representation of an object to a file. This can be
useful when work is performed across multiple scripts and you want to save
cached data such as statistics and API-Football profiles. This will allow you
to avoid redundant request calls and save time.


.. code-block:: python

   >>> haaland = api.db.get("players", "82172")

   # Prints JSON representation of object to the current directory.
   >>> haaland.export()

Import an object
````````````````

Import an object from a previosuly exported object JSON file.

.. code-block:: python

   >>> file_path = "player_82172.json"

   # Expecting a Soccer API JSON file in its path.
   >>> api.import_object(file_path)
   Player(Erling Braut Haaland)

Get objects from other objects
``````````````````````````````

.. code-block:: python

   # Get Erling Haaland.
   >>> haaland = api.db.search("players", { "fapi_player_id" : "1100"})[0]
   >>> print(haaland)
   Player(Erling Braut Haaland)

   # Get Haaland's current club.
   >>> man_city = haaland.current_team()
   >>> print(man_city)
   line 27, in make_request return { "success" : 0, "res" : None , "error_string" : "Error: " + res["errors"]["requests"] } TypeError: list indices must be integers or slices, not str

   # Get a list of all competition's City is currently in.
   >>> cities_leagues = man_city.leagues()
   print(cities_leagues)

   # Grab the Premier League from that list.
   >>> premier_league = cities_leagues[1]
   print(premier_league)

Get all Player's Statistics from this season
````````````````````````````````````````````

Scrape a player's FBRef statistics from this season.

.. code-block:: python

   >>> haaland = api.db.search("players", { "fapi_player_id" : "1100"})[0]

   # Returns statistics organized by team.
   >>> import pprint
   >>> pprint.pprint(haaland.statistics())
   {'aerials_lost': 37.0,
    'aerials_won': 43.0,
    'aerials_won_pct': 53.8,
    'assisted_shots': 24.0,
    'assists': 3.0,
    'assists_per90': 0.12,
    'average_shot_distance': 12.0,
    'ball_recoveries': 19.0,
    'blocked_passes': 8.0,
    'blocked_shots': 1.0,
    'blocks': 9.0,
    'cards_yellow': 2.0,
    'carries': 243.0,
    'carries_distance': 1207.0,
    'carries_into_final_third': 13.0,
    'carries_into_penalty_area': 17.0,
    'carries_progressive_distance': 444.0,
    'challenge_tackles': 1.0,
    'challenge_tackles_pct': 20.0,
    'challenges': 5.0,
    'challenges_lost': 4.0,
    'clearances': 21.0,
    'crosses': 3.0,
    'crosses_into_penalty_area': 1.0,
    'dispossessed': 20.0,
    'fbref_league_id': '9',
    'fouled': 12.0,
    'fouls': 20.0,
    'games': 25.0,
    'games_complete': 21.0,
    'games_starts': 25.0,
    'goals': 19.0,
    'goals_assists': 22.0,
    'goals_assists_pens_per90': 0.86,
    'goals_assists_per90': 0.9,
    'goals_pens': 18.0,
    'goals_pens_per90': 0.73,
    'goals_per90': 0.77,
    'goals_per_shot': 0.2,
    'goals_per_shot_on_target': 0.35,
    'interceptions': 4.0,
    'minutes': 2210.0,
    'minutes_90s': 24.6,
    'minutes_pct': 94.4,
    'minutes_per_game': 88.0,
    'minutes_per_start': 88.0,
    'miscontrols': 37.0,
    'npxg': 16.8,
    'npxg_net': 1.2,
    'npxg_per90': 0.68,
    'npxg_per_shot': 0.19,
    'npxg_xg_assist': 19.5,
    'npxg_xg_assist_per90': 0.79,
    'offsides': 4.0,
    'on_goals_against': 35.0,
    'on_goals_for': 51.0,
    'on_xg_against': 34.6,
    'on_xg_for': 45.3,
    'pass_xa': 1.7,
    'passes': 298.0,
    'passes_blocked': 7.0,
    'passes_completed': 193.0,
    'passes_completed_long': 4.0,
    'passes_completed_medium': 40.0,
    'passes_completed_short': 136.0,
    'passes_dead': 6.0,
    'passes_into_final_third': 8.0,
    'passes_into_penalty_area': 5.0,
    'passes_live': 291.0,
    'passes_long': 6.0,
    'passes_medium': 63.0,
    'passes_offsides': 1.0,
    'passes_pct': 64.8,
    'passes_pct_long': 66.7,
    'passes_pct_medium': 63.5,
    'passes_pct_short': 69.4,
    'passes_progressive_distance': 457.0,
    'passes_received': 388.0,
    'passes_short': 196.0,
    'passes_total_distance': 2332.0,
    'pens_att': 2.0,
    'pens_made': 1.0,
    'progressive_carries': 17.0,
    'progressive_passes': 16.0,
    'progressive_passes_received': 98.0,
    'shots': 92.0,
    'shots_free_kicks': 1.0,
    'shots_on_target': 51.0,
    'shots_on_target_pct': 55.4,
    'shots_on_target_per90': 2.08,
    'shots_per90': 3.75,
    'tackles': 7.0,
    'tackles_att_3rd': 3.0,
    'tackles_def_3rd': 2.0,
    'tackles_interceptions': 11.0,
    'tackles_mid_3rd': 2.0,
    'tackles_won': 4.0,
    'take_ons': 27.0,
    'take_ons_tackled': 15.0,
    'take_ons_tackled_pct': 55.6,
    'take_ons_won': 10.0,
    'take_ons_won_pct': 37.0,
    'through_balls': 1.0,
    'throw_ins': 1.0,
    'touches': 513.0,
    'touches_att_3rd': 317.0,
    'touches_att_pen_area': 158.0,
    'touches_def_3rd': 34.0,
    'touches_def_pen_area': 20.0,
    'touches_live_ball': 511.0,
    'touches_mid_3rd': 165.0,
    'xg': 18.3,
    'xg_assist': 2.7,
    'xg_assist_net': 0.3,
    'xg_assist_per90': 0.11,
    'xg_net': 0.7,
    'xg_per90': 0.75,
    'xg_xg_assist_per90': 0.86}

Get all Player's Statistics from last season
````````````````````````````````````````````

Scrape a player's FBRef statistics from a previous season.

.. code-block:: python

   >>> haaland = api.db.search("players", { "fapi_player_id" : "1100"})[0]

   # Returns statistics organized by team
   >>> import pprint
   >>> pprint.pprint(haaland.statistics("2023"))
      {'aerials_lost': 42.0,
       'aerials_won': 39.0,
       'aerials_won_pct': 48.1,
       'assisted_shots': 29.0,
       'assists': 5.0,
       'assists_per90': 0.18,
       'average_shot_distance': 11.9,
       'ball_recoveries': 47.0,
       'blocked_passes': 10.0,
       'blocked_shots': 1.0,
       'blocks': 11.0,
       'cards_yellow': 1.0,
       'carries': 357.0,
       'carries_distance': 1628.0,
       'carries_into_final_third': 13.0,
       'carries_into_penalty_area': 22.0,
       'carries_progressive_distance': 728.0,
       'challenge_tackles': 2.0,
       'challenge_tackles_pct': 66.7,
       'challenges': 3.0,
       'challenges_lost': 1.0,
       'clearances': 16.0,
       'crosses': 5.0,
       'dispossessed': 19.0,
       'fbref_league_id': '9',
       'fouled': 31.0,
       'fouls': 18.0,
       'games': 31.0,
       'games_complete': 20.0,
       'games_starts': 29.0,
       'games_subs': 2.0,
       'goals': 27.0,
       'goals_assists': 32.0,
       'goals_assists_pens_per90': 0.88,
       'goals_assists_per90': 1.13,
       'goals_pens': 20.0,
       'goals_pens_per90': 0.71,
       'goals_per90': 0.95,
       'goals_per_shot': 0.18,
       'goals_per_shot_on_target': 0.4,
       'interceptions': 2.0,
       'minutes': 2552.0,
       'minutes_90s': 28.4,
       'minutes_pct': 74.6,
       'minutes_per_game': 82.0,
       'minutes_per_start': 86.0,
       'minutes_per_sub': 25.0,
       'miscontrols': 41.0,
       'npxg': 22.9,
       'npxg_net': -2.9,
       'npxg_per90': 0.81,
       'npxg_per_shot': 0.2,
       'npxg_xg_assist': 27.2,
       'npxg_xg_assist_per90': 0.96,
       'offsides': 6.0,
       'on_goals_against': 25.0,
       'on_goals_for': 65.0,
       'on_xg_against': 26.2,
       'on_xg_for': 59.5,
       'pass_xa': 2.2,
       'passes': 388.0,
       'passes_blocked': 17.0,
       'passes_completed': 295.0,
       'passes_completed_long': 5.0,
       'passes_completed_medium': 56.0,
       'passes_completed_short': 197.0,
       'passes_dead': 12.0,
       'passes_free_kicks': 1.0,
       'passes_into_final_third': 16.0,
       'passes_into_penalty_area': 11.0,
       'passes_live': 375.0,
       'passes_long': 8.0,
       'passes_medium': 70.0,
       'passes_offsides': 1.0,
       'passes_pct': 76.0,
       'passes_pct_long': 62.5,
       'passes_pct_medium': 80.0,
       'passes_pct_short': 81.4,
       'passes_progressive_distance': 567.0,
       'passes_received': 489.0,
       'passes_short': 242.0,
       'passes_total_distance': 3234.0,
       'pens_att': 8.0,
       'pens_made': 7.0,
       'pens_won': 2.0,
       'progressive_carries': 35.0,
       'progressive_passes': 26.0,
       'progressive_passes_received': 126.0,
       'shots': 113.0,
       'shots_free_kicks': 1.0,
       'shots_on_target': 50.0,
       'shots_on_target_pct': 44.2,
       'shots_on_target_per90': 1.76,
       'shots_per90': 3.99,
       'tackles': 6.0,
       'tackles_att_3rd': 3.0,
       'tackles_interceptions': 8.0,
       'tackles_mid_3rd': 3.0,
       'tackles_won': 3.0,
       'take_ons': 30.0,
       'take_ons_tackled': 16.0,
       'take_ons_tackled_pct': 53.3,
       'take_ons_won': 12.0,
       'take_ons_won_pct': 40.0,
       'through_balls': 2.0,
       'throw_ins': 1.0,
       'touches': 636.0,
       'touches_att_3rd': 398.0,
       'touches_att_pen_area': 183.0,
       'touches_def_3rd': 36.0,
       'touches_def_pen_area': 15.0,
       'touches_live_ball': 628.0,
       'touches_mid_3rd': 206.0,
       'unused_subs': 1.0,
       'xg': 29.2,
       'xg_assist': 4.3,
       'xg_assist_net': 0.7,
       'xg_assist_per90': 0.15,
       'xg_net': -2.2,
       'xg_per90': 1.03,
       'xg_xg_assist_per90': 1.18}

Get a Player's Number of Shots from this season
```````````````````````````````````````````````

Scrape a player's FBRef Shot statistics from this season.

.. code-block:: python

   >>> haaland = api.db.search("players", { "fapi_player_id" : "1100"})[0]

   # Returns shots taken this season.
   >>> haaland.statistic("shots")
   92.0

Get a Player's current Transfermarkt Market Value
`````````````````````````````````````````````````

Scrape a player's TM Market Value.

.. code-block:: python

   >>> haaland = api.db.get("players", "82172")

   # Returns market value as an integer.
   >>> haaland.market_value()
   200000000.0

Using the year parameter when scraping a player's TM Market Value

.. code-block:: python

   >>> from datetime import datetime

   >>> haaland = api.db.get("players", "82172")
   
   # Get last five years.
   >>> current_year = datetime.now().year
   >>> last_five_years = [str(year) for year in range(current_year - 4, current_year + 1)]
   
   # Iterate over years and get market values
   >>> market_values = []
   >>> for year in last_five_years:
       value = haaland.market_value(year)
       market_values.append(value)

   >>> print(market_values)
   [150000000.0, 180000000.0, 180000000.0, 200000000.0, 0]

Get a Team's Transfermarkt Market Value
```````````````````````````````````````

Scrape a team's TM Market Value.


.. code-block:: python

   >>> man_city = api.db.get("teams", "5874")

   # Returns market value as an integer.
   >>> man_city.market_value()
   1300200000.0


Get a full Team's Transfermarkt Market Value
````````````````````````````````````````````

Scrape a Team TM Market Value of every player on a team.

.. code-block:: python

   >>> man_city = api.db.get("teams", "5874")
   
   # Iterate over each player in the squad and return their market value in a list of integers
   >>> [player.market_value() for player in man_city.players()]
   soccerapi/lib/fapi.py, line 27, in make_request return { "success" : 0, "res" : None , "error_string" : "Error: " + res["errors"]["requests"] } TypeError: list indices must be integers or slices, not str

Get a League's Transfermarkt Market Value
`````````````````````````````````````````

Scrape a League's TM Market Value.

.. code-block:: python

   >>> premier_league = api.db.get("leagues", "12")
   
   # Returns market value as an integer.
   >>> premier_league.market_value()
   9312660002.45

Get a the Transfermarkt Market Value of every player in a league
````````````````````````````````````````````````````````````````

Scrape the TM Market Value of every player in a league and store that data to a
dictionary. Their Soccer API ID is the key, while their market value is the
value.

.. code-block:: python

   >>> premier_league = api.db.get("leagues", "12")
   
   # Iterate over each player in the league and return their market value in
   # a dictionary.
   >>> market_values = { player.id: player.market_value() for team in premier_league.teams() for player in team.players() }
   soccerapi/lib/fapi.py, line 27, in make_request return { "success" : 0, "res" : None , "error_string" : "Error: " + res["errors"]["requests"] } KeyError: 'requests'

Get the Transfermarkt Market Value a team's starting XI in a given fixture
``````````````````````````````````````````````````````````````````````````

Find a team's fixture on a given date. Scrape the TM Market Value for the
starting XI of that team.

.. code-block:: python

   # Get a team's fixture from a given date.
   >>> wolves = api.db.search("teams", { "fapi_team_id" : "39"})[0]
   >>> fixture = wolves.fixture("2024-11-30")
   soccerapi/lib/fapi.py, line 27, in make_request return { "success" : 0, "res" : None , "error_string" : "Error: " + res["errors"]["requests"] } KeyError: 'requests'
   
   # Iterate over each player in the starting XI and store their market value
   # to a dictionary.
   >>> { player.id : { "player" : player, "market_value" : player.market_value() } for player in fixture.home_starting_xi() }

Get the team statistics from a given fixture
````````````````````````````````````````````

Get each team statistics from a match.

.. code-block:: python

   # Get a team's fixture from a given date.
   >>> wolves = api.db.search("teams", { "fapi_team_id" : "39"})[0]
   >>> fixture = wolves.fixture("2024-11-30")
   soccerapi/lib/fapi.py, line 27, in make_request return { "success" : 0, "res" : None , "error_string" : "Error: " + res["errors"]["requests"] }

   >>> fixture.statistics()

Get a player's statistics from a given fixture
``````````````````````````````````````````````

Find a team's fixture on a given date. Get the statistics for a given player
from that match.

.. code-block:: python

   # Get a team's fixture from a given date 
   >>> wolves = api.db.search("teams", { "fapi_team_id" : "39"})[0]
   >>> fixture = wolves.fixture("2024-11-30")
   soccerapi/lib/fapi.py, line 27, in make_request return { "success" : 0, "res" : None , "error_string" : "Error: " + res["errors"]["requests"] } KeyError: 'requests'
   
   # Get the starting XI.
   >>> xi = fixture.home_starting_xi()
   
   # Grab a player and get their statistics
   >>> kepa = xi[0]
   >>> fixture.statistics(kepa)

Get a team's statistics and their opposition statistics in the current season
`````````````````````````````````````````````````````````````````````````````

Get a team's statistics this season as well as their opposition statistcs. We
will then use this data to find how many shots that took and allowed so far
this season.

.. code-block:: python

   >>> man_city = api.db.get("teams", "5874")
   
   # Get team stats and opposition stats.
   >>> city_stats = man_city.statistics()
   >>> city_opps_stats = man_city.opponent_statistics()
   
   # Find the shots taken and shots allows this season.
   >>> print(man_city.name() + " had " + str(city_stats["shots"].value) + " shots this season.")
   Manchester City had 427.0 shots this season.

   >>> print(man_city.name() + " gave up " + str(city_opps_stats["shots"].value) + " shots this season.")
   Manchester City gave up 250.0 shots this season.
