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
      :ivar understat_id: teams's Understat ID.
      :vartype understat_id: str
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
        self.fbref_id = team_data["fbref_id"]
        self.tm_id = team_data["tm_id"]
        self.understat_id = team_data["understat_id"]
        self.fapi_id = team_data["fapi_id"]
        #Cached Data
        self.fapi_profile = None
        self.stats_cache = {}
        self.opps_stats_cache = {}
        self.mv_cache = {}
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
        r"""Get the name of the Team.

        :returns: the name.
        :rtype: str
        """
        return self.team_name
    
    def short_name(self) -> str:
        r"""Get the short name of the Team.

        :returns: the team name.
        :rtype: str
        """
        return self.team_name
    
    def export(self, path: Optional[str] = "."):
        r"""Export the Team object as a JSON file.
            :param path: Directory to export the team object to. If not present, defaults to present working directory
            :type path: str
        .. note:: The output filename is in the format ``team_{self.id}.json``.
        """
        data = self.to_json()

        file_name = f"./{path}/team_{self.id}.json"
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
            "opp_statistics" : self.opps_stats_cache,
            "market_value" : self.mv_cache
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
            
            for year in data["statistics"]:
                if year not in stats:
                    stats[year] = {}

                for key in data["statistics"][year]:
                    stat_data = data["statistics"][year][key]
                    if "key" in stat_data:
                        if("context" in stat_data):
                            if("player" in stat_data["context"]):
                                stat_data["context"]["player"] = self.db.get("players", stat_data["context"]["player"])
                            if("team" in stat_data["context"]):
                                stat_data["context"]["team"] = self.db.get("teams", stat_data["context"]["team"])
                            if("league" in stat_data["context"]):
                                stat_data["context"]["league"] = self.db.get("leagues", stat_data["context"]["league"])
                        stats[year][key] = Statistic(stat_data)
                    else:
                        stats[year][key] = data["statistics"][year][key]
            
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

        if "market_value" in data:
            self.mv_cache = data["market_value"]

    def profile(self) -> dict | None:
        r"""Return the API-Football profile of the Team.

        :ivar fapi_profile:
        :returns: the API-Football profile or ``None`` in case the response is
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
        r"""Get the country the Team is from.

        :returns: a country code.
        :rtype: str
        """
        return self.team_country
    
    def players(self) -> list['Player']:
        r"""Get the player's on a Team.

        :returns: a list of players or an empty list
        :rtype: list['Player']
        """
        players = []
        res = self.fapi.get_players_on_team(self)

        if(res["success"]):
            for player in res["res"]["players"][0]['players']:
                fapi_id = player["id"]
                db_player = self.db.search("players", { "fapi_id" : fapi_id })
                if(len(db_player) > 0):
                    players.append(db_player[0])
        else:
            if( self.debug ):
                print(res["error_string"]) 
        return players
    
    def fixtures(self, year: Optional[str] = None) -> list[Fixture] | list:
        r"""Get a list of Team's Fixtures for a given year.

        :param year: the year to be selected. If this parameter is not set, get
          the current year.
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
        r"""Get a Team's Fixture for a given date.

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

    def leagues(self) -> list['League']:
        r"""Returns the Leagues a team is competing in currently.

        :returns: a list of Leagues, or an uninitialized list if the response
          is empty.
        :rtype: list['League']

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
                    fapi_id = league["league"]["id"]
                    db_league = self.db.search("leagues", { "fapi_id" : fapi_id })
                    if(len(db_league) > 0):
                        leagues.append(db_league[0])
            else:
                if( self.debug ):
                    print(res["error_string"])
            
        return leagues
    
    def market_value(self, year: Optional[str] = None) -> int:
        r"""Get the Teams's Transfermarkt Market Value for a given year.

        :param year: the year to be selected. If this parameter is not set, get
          the current year.
        :type year: Optional[str]
        :rtype: int
        """
        mv_cache = self.mv_cache

        current_date = datetime.now()
        if not year:    
            year = str(current_date.year)

        if year in mv_cache:
            return mv_cache[year]

        res = self.tm.get_team_value(self, year)

        if(res["success"]):        
            mv_cache[year] = res["res"]["market_value"]
        else:
            if( self.debug ):
                print(res["error_string"])
            mv_cache[year] = 0
    
        self.mv_cache = mv_cache
        return self.mv_cache[year]
        
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

    def statistics(self, year = None) -> dict[Statistic]:
        r"""Returns the Team's FBRef Statistics for a given year.
        
        :param year: the year to be selected. If this parameter is not set, get the current year.
        :type year: Optional[str]
        :returns: a hash of Statistic objects.
        :rtype: dict[Statistic]
        """
        stats = self.stats_cache

        if not year:
            current_date = datetime.now()
            if 1 <= current_date.month <= 6:
                previous_year = current_date.year - 1
                year = str(previous_year)
            else:
                year = str(current_date.year)

        if year in stats:
            return stats[year]
        
        res = self.fbref.get_team_stats(self, year)

        if(res["success"]):
            stats[year] = res["res"]["stats"]            
        else:
            if(self.debug):
                print(res["error_string"])
            stats[year] = {}

        new_stats = {}
        db_search_cache = {
            "leagues" : {},
            "teams" : {},
            "players" : {}
        }
        for stat_year in stats:
            new_stats[stat_year] = {}

            for key in stats[stat_year]:
                stat = stats[stat_year][key]
                for obj_type in ["league", "team", "player"]:
                    if obj_type in stat.context and str(type(stat.context[obj_type])) == "<class 'str'>":
                        id = str(stat.context[obj_type])
                        if id not in db_search_cache[f"{obj_type}s"]:
                            db_league = self.db.search(f"{obj_type}s", { "fbref_id" : stat.context[obj_type] })[0]
                            db_search_cache[f"{obj_type}s"][id] = db_league
                        stat.context[obj_type] = db_search_cache[f"{obj_type}s"][id]
                
                stats[stat_year][key] = stat

        self.stats_cache = stats
        return self.stats_cache[year]

    def statistic(self, stat, year: Optional[str] = None) -> Statistic:
        r"""Get the Team's FBRef statistics for a given year and Statistic.
        
        :param year: the year to be selected. If this parameter is not set, get the current year.
        :type year: Optional[str]
        :param stat: internal or display name of a statistic.
        :type stat: str
        :returns: a Statistic object.
        :rtype: Statistic
        """
        if not year:
            current_date = datetime.now()
            year = str(current_date.year)

        stat_key = None
        if(key_to_name(stat)):
            stat_key = stat
        elif(name_to_key(stat)):
            stat_key = name_to_key(stat)

        stats = self.statistics(year)
        if stat_key and stat_key in stats:
            return stats[stat_key]
        return Statistic({ "key" : stat_key, "value" : 0 })

    def opponent_statistics(self, year: Optional[str] = None) -> dict[Statistic]:
        r"""Get the Team's FBRef opposition statistics for a given year.
        
        :param year: the year to be selected. If this parameter is not set, get the current year.
        :type year: Optional[str]
        :returns: a Statistic object.
        :rtype: Statistic
        :returns: a hash of Statistic objects.
        :rtype: dict[Statistic]
        """
        stats = self.opps_stats_cache

        if not year:
            current_date = datetime.now()
            if 1 <= current_date.month <= 6:
                previous_year = current_date.year - 1
                year = str(previous_year)
            else:
                year = str(current_date.year)

        if year in stats:
            return stats[year]

        res = self.fbref.get_team_opposition_stats(self, year)
        if(res["success"]):
            stats[year] = res["res"]["stats"]
        else:
            if(self.debug):
                print(res["error_string"])
            stats[year] = {}

        new_stats = {}
        db_search_cache = {
            "leagues" : {},
            "teams" : {},
            "players" : {}
        }
        for stat_year in stats:
            new_stats[stat_year] = {}

            for key in stats[stat_year]:
                stat = stats[stat_year][key]
                for obj_type in ["league", "team", "player"]:
                    if obj_type in stat.context and str(type(stat.context[obj_type])) == "<class 'str'>":
                        id = str(stat.context[obj_type])
                        if id not in db_search_cache[f"{obj_type}s"]:
                            db_league = self.db.search(f"{obj_type}s", { "fbref_id" : stat.context[obj_type] })[0]
                            db_search_cache[f"{obj_type}s"][id] = db_league
                        stat.context[obj_type] = db_search_cache[f"{obj_type}s"][id]
                
                stats[stat_year][key] = stat

        self.opps_stats_cache = stats
        return self.opps_stats_cache[year]
    
    def opponent_statistic(self, stat, year: Optional[str] = None) -> Statistic:
        r"""Get the Team's FBRef opposition statistics for a given year and Statistic.
        
        :param year: the year to be selected. If this parameter is not set, get the current year.
        :type year: Optional[str]
        :param stat: internal or display name of a statistic.
        :type stat: str
        :returns: a Statistic object.
        :rtype: Statistic
        """
        if not year:
            current_date = datetime.now()
            year = str(current_date.year)

        stat_key = None
        if(key_to_name(stat)):
            stat_key = stat
        elif(name_to_key(stat)):
            stat_key = name_to_key(stat)

        stats = self.opponent_statistics(year)
        if stat_key and stat_key in stats:
            return stats[stat_key]
        return Statistic({ "key" : stat_key, "value" : 0 })