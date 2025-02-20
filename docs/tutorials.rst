Tutorials
=========

Preparation
-----------

Before using the API you need to create a new SoccerAPI object

.. code-block:: python

   import soccerapi.soccerapi
   config = {"fapi_host" : "api-football-v1.p.rapidapi.com", "fapi_key" : "API-FOOTBALL API KEY"}
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
   output here

   # Get Premier League (man_city)
   >>> api.db.get("teams", "5874")

   # Get Premier League
   >>> api.db.get("leagues", "12")


Search objects using Foreign IDs
````````````````````````````````

Use the ``search`` method from ``db`` to search for objects using an object's
foreign ID. Tables available to search on are players, teams and leagues.

.. code-block:: python

   # Search for Erling Haaland using API-Football ID, Transfermarkt ID and FBRef ID respectively
   >>> api.db.search("players", { "fapi_player_id" : "1100"})
   >>> api.db.search("players", { "tm_player_id" : "418560"})
   >>> api.db.search("players", { "fbref_player_id" : "1f44ac21"})

   # Search for Man City using API-Football ID, Transfermarkt ID and FBRef ID respectively
   >>> api.db.search("teams", { "fapi_player_id" : "33"})
   >>> api.db.search("teams", { "tm_player_id" : "985"})
   >>> api.db.search("teams", { "fbref_player_id" : "19538871"})

   # Search for Premier League using API-Football ID, Transfermarkt ID and FBRef ID respectively
   >>> api.db.search("leagues", { "fapi_player_id" : "39"})
   >>> api.db.search("leagues", { "tm_player_id" : "GB1"})
   >>> api.db.search("leagues", { "fbref_player_id" : "9"})
