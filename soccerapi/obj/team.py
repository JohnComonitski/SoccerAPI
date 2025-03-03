import json
from .fixture import Fixture
from .statistic import Statistic
from ..lib.utils import key_to_name, name_to_key, traverse_dict
from datetime import datetime
from typing import Optional


class Team:
    r"""The Team object.

      :ivar id: Team's Soccer API ID.
      :vartype id: str
      :ivar fbref_id: Teams's FBRef ID.
      :vartype fbref_id: str
      :vartype fbref_stat_detail_level: str
      :ivar tm_id: Team's Transfermarkt ID.
      :vartype tm_id: str
      :ivar fapi_id: Team's API-Football ID
      :vartype fapi_id: str
      :ivar db: PostgreSQL database initalization object.
      :vartype db: PostgreSQL
    """
    def __init__(self, team_data, db):
        r"""Create a new instance.

        :param team_data:
        :param db: PostgreSQL database initalization object.
        :type team_data:
        :type db: PostgreSQL
        """
        #From Team Data
        self.table = "teams"
        self.team_name = team_data["team_name"]
        self.team_country = team_data["country_code"]
        self.id = team_data["team_id"]
        self.fbref_id = team_data["fbref_team_id"]
        self.tm_id = team_data["tm_team_id"]
        self.fapi_id = team_data["fapi_team_id"]
        #Cached Data
        self.fapi_profile = None
        self.stats_cache = None
        self.opps_stats_cache = None
        #Packages
        self.db = db 
        app = db.app
        self.debug = app["debug"]
        self.fapi = app["fapi"]
        self.tm = app["tm"]
        self.fbref = app["fbref"]
        self.understat = app["understat"]
        self.visualize = app["visualize"]
    
    def __str__(self):
        return f"Team({self.team_name} - {self.country()})"
    
    def __repr__(self):
        return f"Team({self.team_name} - {self.country()})"
    
    def name(self) -> str:
        r"""Get the name of the Team object.

        :returns: the name.
        :rtype: str
        """
        return self.team_name
    
    def export(self):
        r"""Export the Team object as a JSON file.

        .. note:: The output filename is in the format ``team_{self.id}.json``.
        """
        data = self.to_json()

        file_name = "team_" + str(self.id) + ".json"
        with open(file_name, "w") as file:
            json.dump(data, file, indent=4)

    def to_json(self) -> dict:
        r"""Get a JSON representation of the Team object.

        :rtype: dict
        """
        return traverse_dict({
            "object" : "team",
            "team_name" : self.team_name,
            "team_country" : self.team_country,
            "id" : self.id,
            "fbref_id" : self.fbref_id,
            "tm_id" : self.tm_id,
            "fapi_id" : self.fapi_id,
            "fapi_profile" : self.fapi_profile,
            "statistics" : self.stats_cache,
            "opp_statistics" : self.opps_stats_cache
        })
    
    def import_data(self, data: dict[str]):
        r"""Populate Team object data based on a Team JSON file.

        :param data: JSON representation of the Team object.
        :type data: dict[str]
        :ivar fapi_profile:
        :ivar stats_cache:
        :ivar opps_stats_cache:
        """
        if "fapi_profile" in data:
            self.fapi_profile = data["fapi_profile"]

        if "statistics" in data and data["statistics"]:
            stats = {}
            for key in data["statistics"]:
                stat_data = data["statistics"][key]
                if "key" in stat_data:
                    stats[key] = Statistic(stat_data)
                else:
                    stats[key] = data["statistics"]
            
            self.stats_cache = stats

        if "opp_statistics" in data and data["opp_statistics"]:
            stats = {}
            for key in data["opp_statistics"]:
                stat_data = data["opp_statistics"][key]
                if "key" in stat_data:
                    stats[key] = Statistic(stat_data)
                else:
                    stats[key] = data["opp_statistics"]
            self.opps_stats_cache = stats
            
    def profile(self) -> dict | None:
        r"""Return the API-Football profile of the Team object.

        :ivar fapi_profile:
        :returns: the API-Foorball profile or ``None`` in case the response is
          empty.
        :rtype: dict | None
        """
        if self.fapi_profile:
            return self.fapi_profile
        else:
            res = self.fapi.make_request("/teams?id=" + self.fapi_id, {})
            if(res["success"]):
                profile = res["res"]
                if(len(profile["response"]) > 0):
                    self.fapi_profile = profile["response"][0]["team"]
                    return self.fapi_profile
            else:
                if( self.debug ):
                    print(res["error_string"])
        return None
    
    def country(self) -> str:
        r"""Get the country the Team object is from.

        :returns: a country code.
        :rtype: str
        """
        return self.team_country
    
    def players(self) -> list:
        r"""Get the current Team object players.

        :returns: a list of players or an empty list
        :rtype: list
        """
        players = []
        res = self.fapi.get_players_on_team(self)

        if(res["success"]):
            for player in res["res"]["players"][0]['players']:
                fapi_player_id = player["id"]
                db_player = self.db.search("players", { "fapi_player_id" : fapi_player_id })
                if(len(db_player) > 0):
                    players.append(db_player[0])
        else:
            if( self.debug ):
                print(res["error_string"]) 
        return players
    
    def fixtures(self, year: Optional[str] = None) -> list[Fixture] | list:
        r"""Get a list of Team objects Fixtures for a given year.

        :param year: the year to be selected. If this parameter is not set, get
          the current value.
        :type year: Optional[str]
        :returns: a list of Fixture, or an empty list in case of error.
        :rtype: list[Fixture] | list

        .. important:: Gets info from the previous year if the current month is
           between January and June, or the current year otherwise.
        """
        res = self.fapi.get_team_schedule(self, year)

        if(res["success"]):
            fixtures = []
            for fixture in res["res"]["matches"]:
                fixtures.append(Fixture(fixture, self.db))
            return fixtures
        else:
            if( self.debug ):
                print(res["error_string"]) 
            return []
        
    def fixture(self, date: str = None) -> Fixture | None:
        r"""Get a Team object Fixture for a given date.

        :param date: the date to be selected.
        :type date: str
        :returns: a Fixture object, or ``None`` in case of error.
        :rtype: Fixture | None

        .. important:: In contrast to the ``fixtures`` method, the ``date``
           parameter is required here!
        """

        res = self.fapi.get_team_fixtures_on_date(self, date)

        if(res["success"]):
            if len(res["res"]["matches"]) > 0:
                match_data = res["res"]["matches"][0]
                return Fixture(match_data, self.db)
            return None
        else:
            if(1 or self.debug ):
                print(res["error_string"]) 
            return None

    def leagues(self) -> list:
        r"""Returns the Leagues a team is competing in currently.

        :returns: a list of Leagues, or an uninitialized list if the response
          is empty.
        :rtype: list

        .. important:: Gets info from the previous year if the current month is
           between January and June, or the current year otherwise.
        """
        year = ""
        current_date = datetime.now()
        if 1 <= current_date.month <= 6:
            previous_year = current_date.year - 1
            year = str(previous_year)
        else:
            year = str(current_date.year)
        
        res = self.fapi.make_request("/leagues", {
            "season" : year,
            "team" : self.fapi_id
        })

        leagues = []
        if(res["success"]):
            if(len(res["res"]) > 0):
                fapi_leagues = res["res"]
                for league in fapi_leagues["response"]:
                    fapi_league_id = league["league"]["id"]
                    db_league = self.db.search("leagues", { "fapi_league_id" : fapi_league_id })
                    if(len(db_league) > 0):
                        leagues.append(db_league[0])
            else:
                if( self.debug ):
                    print(res["error_string"])
            
        return leagues
    
    def market_value(self, year: Optional[str] = None):
        r"""Get the Teams's Transfermarkt Market Value for a given year.

        :param year: the year to be selected. If this parameter is not set, get
          the current value.
        :type year: Optional[str]
        :rtype: int
        """
        res = self.tm.get_team_value(self, year)

        if(res["success"]):
            return res["res"]["market_value"]
        else:
            if(1 or self.debug ):
                print(res["error_string"]) 
            return 0
        
    def market_value_over_time(self) -> dict[int] | int:
        r"""Get the Teams's Transfermarkt Market Value over time.

        :returns: an object or ``0`` in case of error.
        :rtype: dict[int]
        """
        res = self.tm.get_team_value_over_time(self)

        if(res["success"]):
            return res["res"]["market_value_by_year"]
        else:
            if(1 or self.debug ):
                print(res["error_string"]) 
            return 0

    def statistics(self) -> str:
        r"""Returns the Team object FBRef Statistics for a given year.

        :returns: a hash of Statistic objects.
        :rtype: str
        """
        stats = self.stats_cache

        if stats:
            return stats
        res = self.fbref.get_team_stats(self)
        if(res["success"]):
            stats = res["res"]["stats"]
        else:
            if(self.debug):
                print(res["error_string"])
            stats = {}
        self.stats_cache = stats

        return self.stats_cache

    def statistic(self, stat) -> Statistic:
        r"""Get the Team object FBRef statistics for a given year and Statistic.

        :param stat: internal or display name of a statistic.
        :type stat: str
        :returns: a Statistic object.
        :rtype: Statistic
        """
        stat_key = None
        if(key_to_name(stat)):
            stat_key = stat
        elif(name_to_key(stat)):
            stat_key = name_to_key(stat)

        stats = self.statistics()
        if stat_key and stat_key in stats:
            return stats[stat_key]
        return Statistic({ "key" : stat_key, "value" : 0 })

    def opponent_statistics(self) -> str:
        r"""Get the Team object Opposition FBRef statistics for a given year.

        :returns: a Statistic object.
        :rtype: Statistic
        :returns: a hash of Statistic objects.
        :rtype: str
        """
        stats = self.opps_stats_cache

        if stats:
            return stats

        res = self.fbref.get_team_opposition_stats(self)
        if(res["success"]):
            stats = res["res"]["stats"]
        else:
            if(self.debug):
                print(res["error_string"])
            stats = {}
        self.opps_stats_cache = stats

        return self.opps_stats_cache
