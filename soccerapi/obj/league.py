from ..lib.utils import key_to_name, name_to_key, traverse_dict
from .fixture import Fixture
from .statistic import Statistic
from datetime import datetime
import json
from typing import Any, Optional

class League:
    r"""The soccer League object.

    :ivar table: the object type. This value cannot be changed and is fixed to
      ``leagues``.
    :vartype table: str
    :ivar id: League's Soccer API ID.
    :vartype id: str
    :ivar country: League's country.
    :vartype country: str
    :ivar tm_id: Leagues's Transfermarkt ID.
    :vartype tm_id: str
    :ivar fapi_id: League's API-Football ID.
    :vartype fapi_id: str
    :ivar understat_id: league's Understat ID.
    :vartype understat_id: str
    :ivar fbref_stat_detail_level: level of Statistic detail FBRef provides for
      this League object.
    :vartype fbref_stat_detail_level: str
    :ivar understat_id: Leagues's Understat ID.
    :vartype understat_id: str
    :ivar db: a database instance.
    :vartype db: PostgreSQL
    """
    def __init__(self, league_data, db):
        r"""Create a new instance.

        :param league_data: an object containing the League's data as strings.
        :param db: a database instance.
        :type player_data: dict
        :type db: PostgreSQL
        """
        #From League Data
        self.table = "leagues"
        self.league_name = league_data["league_name"]
        self.id = league_data["league_id"]
        self.country = league_data["country_code"]
        self.fbref_id = league_data["fbref_id"]
        self.fbref_stat_detail_level = league_data["fbref_stat_detail_level"]
        self.tm_id = league_data["tm_id"]
        self.understat_id = league_data["understat_id"]
        self.fapi_id = league_data["fapi_id"]
        #Cached Data
        self.teams_cache = {}
        self.fapi_profile = None
        self.mv_cache = {}
        self.stats_cache = {}
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
        return f"League({self.league_name} - {self.country})"
    
    def __repr__(self):
        return f"League({self.league_name} - {self.country})"

    def export(self, path: Optional[str] = "."):
        r"""Export the League object as a JSON file.
            :param path: Directory to export the league object to. If not present, defaults to present working directory
            :type path: str
        .. note:: The output filename is in the format ``league_{self.id}.json``.
        """
        data = self.to_json()

        file_name = f"./{path}/league_{self.id}.json"
        with open(file_name, "w") as file:
            json.dump(data, file, indent=4)

    def to_json(self) -> dict:
        r"""Get a JSON representation of the Player object.

        :rtype: dict
        """
        return traverse_dict({
            "object" : "league",
            "league_name" : self.league_name,
            "id" : self.id,
            "fbref_id" : self.fbref_id,
            "tm_id" : self.tm_id,
            "fapi_id" : self.fapi_id,
            "fapi_profile" : self.fapi_profile,
            "teams" : self.teams_cache,
            "statistics" : self.stats_cache,
            "market_value" : self.mv_cache,
        }) 
    
    def import_data(self, data: dict[str]):
        r"""Populate Leage object data based on a League JSON file.

        :param data: JSON representation of the League object.
        :ivar fapi_profile:
        :ivar team: A list of Team objects belonging to the League object.
        :type data: dict[str]
        """
        if "fapi_profile" in data:
            self.fapi_profile = data["fapi_profile"]

        if "team" in data and data["teams"]:
            teams = []
            for team in data["teams"]:
                team = self.db.get("teams", team["id"])
                team.import_data(data["team"])
                teams.append(team)
            self.team = teams

        if "market_value" in data:
            self.mv_cache = data["market_value"]


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

    def name(self) -> str:
        r"""Get the name of the League.

        :returns: the League name.
        :rtype: str
        """
        return self.league_name
    
    def profile(self) -> dict | None:
        r"""Return the API-Football profile of the League.

        :ivar fapi_profile:
        :returns: the API-Football profile or ``None`` in case the response is
          empty.
        :rtype: dict | None
        """
        if self.fapi_profile:
            return self.fapi_profile
        else:
            res = self.fapi.make_request("/leagues?id=" + self.fapi_id, {})
            if(res["success"]):
                profile = res["res"]
                if(len(profile["response"]) > 0):
                    self.fapi_profile = profile["response"][0]["league"]
                    return self.fapi_profile 
            else:
                if( self.debug ):
                    print(res["error_string"])
        return None

    def teams(self, year: Optional[str] = None) -> list['Team']:
        r"""Return the League's teams for a given year.

        :ivar teams_cache:
        :param year: desired year for the information. Defaults to ``None``.
        :type year: Optional[str]
        :returns: the list of Team objects, or an empty list in case of error.
        :rtype: List[Team]

        .. important:: Gets info from the previous year if the current month is
           between January and June, or the current year otherwise.
        """
        teams = self.teams_cache

        if not year:
            current_date = datetime.now()
            if 1 <= current_date.month <= 6:
                previous_year = current_date.year - 1
                year = str(previous_year)
            else:
                year = str(current_date.year)

        if year in teams:
            return teams[year]

        teams_list = []
        res = self.fapi.get_teams_in_league(self, year)
        if(res["success"]):
            for team in res["res"]["teams"]:
                fapi_id = team["team"]["id"]
                db_team = self.db.search("teams", { "fapi_id" : fapi_id })
                if(len(db_team) > 0):
                    teams_list.append(db_team[0])
            teams[year] = teams_list
        else:
            if( self.debug ):
                print(res["error_string"])
            teams[year] = teams_list

        self.teams_cache = teams
        return self.teams_cache[year]

    def fixtures(self, date: Optional[str] = None) -> list['Fixture']:
        r"""Get a list of League's Fixtures for a given date.

        :param date: the date to be selected. If this parameter is not set, get
          the current local timezone timestamp. Defaults to ``None``.
        :type date: Optional[str]
        :returns: a list of Fixture, or an empty list in case of error.
        :rtype: list[Fixture] | list
        """
        if(date is None):
            date = datetime.now().strftime("%Y-%m-%d")

        res = self.fapi.get_league_fixtures_on_date(self, date)

        if(res["success"]):
            fixtures = []
            for fixture in res["res"]["matches"]:
                fixtures.append(Fixture(fixture, self.db))
            return fixtures
        else:
            if(1 or self.debug ):
                print(res["error_string"]) 
            return []

    def fixture_list(self, year: Optional[str] = None) -> list['Fixture']:
        r"""Get a list of League's Fixtures for a given year.

        :param year: the year to be selected. If this parameter is not set, get
          the current value.
        :type year: Optional[str]
        :returns: a list of Fixture, or an empty list in case of error.
        :rtype: list[Fixture] | list
        """
        res = self.fapi.get_league_schedule(self, year)

        if(res["success"]):
            fixtures = []
            for fixture in res["res"]["matches"]:
                fixtures.append(Fixture(fixture, self.db))
            return fixtures
        else:
            if(1 or self.debug ):
                print(res["error_string"]) 
            return []

    def market_value(self, year: Optional[str] = None) -> int:
        r"""Get the League's Transfermarkt Market Value for a given year.

        :param year: the year to be selected. If this parameter is not set, get
          the current value.
        :type year: Optional[str]
        :rtype: int
        """
        mv_cache = self.mv_cache

        current_date = datetime.now()
        if not year:    
            year = str(current_date.year)

        if year in mv_cache:
            return mv_cache[year]

        res = self.tm.get_league_value(self, year)

        if(res["success"]):        
            mv_cache[year] = res["res"]["market_value"]
        else:
            if( self.debug ):
                print(res["error_string"])
            mv_cache[year] = 0
    
        self.mv_cache = mv_cache
        return self.mv_cache[year]
        
    def market_value_over_time(self) -> dict[int]:
        r"""Get the League's Transfermarkt Market Value over time.

        :returns: an object or ``0`` in case of error.
        :rtype: dict[int]
        """
        res = self.tm.get_league_value_over_time(self)

        if(res["success"]):
            return res["res"]["market_value_by_year"]
        else:
            if(1 or self.debug ):
                print(res["error_string"]) 
            return 0

    def statistics(self, year = None) -> dict[Statistic]:
        r"""Returns the League's FBRef Statistics for a given year.
        
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
        
        res = self.fbref.get_league_stats(self, year)

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
        r"""Get the League's FBRef statistics for a given year and Statistic.
        
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
