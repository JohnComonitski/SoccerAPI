import json
from datetime import datetime
from .statistic import Statistic 
from ..lib.utils import key_to_name, name_to_key, traverse_dict
from typing import Optional
from .team import Team


class Player:
    r"""The Player object.

    :ivar table: the object type. This value cannot be changed and is fixed to
      ``player``.
    :ivar first_name: player's first name.
    :vartype first_name: str
    :ivar last_name: player's last name.
    :vartype last_name: str
    :ivar id: player's Soccer API ID.
    :vartype id: str
    :ivar tm_id: player's Transfermarkt ID.
    :vartype tm_id: str
    :ivar fapi_id: player's API-Football ID.
    :vartype fapi_id: str
    :ivar understat_id: player's Understat ID.
    :vartype understat_id: str
    :ivar db: a database instance.
    :vartype db: Any
    """
    def __init__(self, player_data: dict, db):
        r"""Create a new instance.

        :param player_data: an object containing the player's data as strings
        :param db: a database instance.
        :type player_data: dict
        :type db: Any
        """
        #From Player Data
        self.table: str = "players"
        self.first_name: str = player_data["first_name"]
        self.last_name: str = player_data["last_name"]
        self.id: str = player_data["player_id"]
        self.fbref_id = player_data["fbref_id"]
        self.tm_id = player_data["tm_id"]
        self.fapi_id = player_data["fapi_id"]
        self.understat_id = player_data["understat_id"]
        #Cached Data
        self.fapi_profile = None
        self.positions_cache = None
        self.player_country = None
        self.team = None
        self.stats_cache = None
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
        return f"Player({self.name()})"
    
    def __repr__(self):
        return f"Player({self.name()})"

    def name(self) -> str:
        r"""Get the name of the Player.

        :returns: the first and last names.
        :rtype: str
        """
        return self.first_name + " " + self.last_name
    
    def short_name(self) -> str:
        r"""Get the short name of the Player.

        :returns: the first initial and last names.
        :rtype: str
        """
        return self.first_name[0] + ". " + self.last_name
    
    def export(self, path: Optional[str] = "."):
        r"""Export the Player object as a JSON file.
            :param path: Directory to export the player object to. If not present, defaults to present working directory
            :type path: str
        .. note:: The output filename is in the format ``player_{self.id}.json``.
        """
        data = self.to_json()

        file_name = f"./{path}/player_{self.id}.json"
        with open(file_name, "w") as file:
            json.dump(data, file, indent=4)

    def to_json(self) -> dict:
        r"""Get a JSON representation of the Player object.

        :rtype: dict
        """
        return traverse_dict({
            "object" : "player",
            "first_name" : self.first_name,
            "last_name" : self.last_name,
            "id" : self.id,
            "fbref_id" : self.fbref_id,
            "tm_id" : self.tm_id,
            "fapi_id" : self.fapi_id,
            "understat_id" : self.understat_id,
            "fapi_profile" : self.fapi_profile,
            "player_country" : self.player_country,
            "team" : self.team,
            "statistics" : self.stats_cache,
            "positions" : self.positions_cache,
            "market_value" : self.mv_cache
        })
    
    def import_data(self, data: dict[str]):
        r"""Populate Player object's data based on a Player JSON file.

        :param data: JSON representation of the Player object.
        :ivar fapi_profile:
        :ivar player_country:
        :ivar team:
        :ivar stats_cache:
        :type data: dict[str]
        """
        if "fapi_profile" in data:
            self.fapi_profile = data["fapi_profile"]

        if "player_country" in data:
            self.player_country = data["player_country"]

        if "team" in data and data["team"]:
            team = self.db.get("teams", data["team"]["id"])
            team.import_data(data["team"])
            self.team = team

        if "market_value" in data:
            self.mv_cache = data["market_value"]
        
        if "statistics" in data and data["statistics"]:
            stats = {}

            for year in data["statistics"]:
                if year not in stats:
                    stats[year] = {}

                for team in data["statistics"][year]:
                    if team not in stats[year]:
                        stats[year][team] = {}

                    for key in data["statistics"][year][team]:
                        stat_data = data["statistics"][year][team][key]
                        if "key" in stat_data:
                            if("context" in stat_data):
                                if("player" in stat_data["context"]):
                                    stat_data["context"]["player"] = self.db.get("players", stat_data["context"]["player"])
                                if("team" in stat_data["context"]):
                                    stat_data["context"]["team"] = self.db.get("teams", stat_data["context"]["team"])
                                if("league" in stat_data["context"]):
                                    stat_data["context"]["league"] = self.db.get("leagues", stat_data["context"]["league"])
                            stats[year][team][key] = Statistic(stat_data)
                        else:
                            stats[year][team][key] = data["statistics"][year][team][key]

            self.stats_cache = stats

    def profile(self) -> dict | None:
        r"""Return the API-Football profile of the Player.

        :ivar fapi_profile:
        :returns: the API-Football profile or ``None`` in case the response is
          empty.
        :rtype: dict | None
        """
        if self.fapi_profile:
            return self.fapi_profile
        else:
            res = self.fapi.make_request("/players/profiles?player=" + self.fapi_id, {})
            
            if(res["success"]):
                player = res["res"]
                self.fapi_profile = player["response"][0]["player"]
                return self.fapi_profile 
            else:
                if( self.debug ):
                    print(res["error_string"])
        return None
    
    def positions(self) -> list[str]:
        r"""Get a list of positions the player is known to play.

        :returns: A list of positions in the form of two letter abbreviations.
        :rtype: list[str]
        """
        if self.positions_cache:
            return self.positions_cache
        else:
            if self.fbref_id is None:
                return []

            positions_list = []
            query = f"SELECT position FROM players WHERE player_id = '{self.id}'"
            res = self.db.raw_query(query)
            if(len(res) > 0 and res[0]["position"]):
                positions_list = res[0]["position"]

            if(len(positions_list) > 0):
                self.positions_cache = positions_list.split("-")
            else:
                self.positions_cache = []

            return self.positions_cache

    def country(self) -> str:
        r"""Get the country the Player is from.

        :ivar player_country: a country code.
        :type player_country: str
        :returns: a country code.
        :rtype: str
        """
        if self.player_country:
            return self.player_country
        else:
            profile = self.profile()
            if(profile):
                fapi_country = profile["nationality"]
                res = self.fapi.make_request("/countries?name=" + fapi_country, {})
                if(res["success"]):
                    country = res["res"]
                    country_code = country["response"][0]["code"]
                    res = self.db.search("countries", { "fapi_country_code" : country_code })
                    if(len(res) > 0):
                        self.player_country = res[0]["country_code"]
                    return self.player_country
                else:
                    if( self.debug ):
                        print(res["error_string"])
        return None
    
    def teams(self) -> 'Team':
        r"""Get the current teams of s Player.

        :ivar team: the player's teams.
        :returns: the teams the player is on.
        :rtype: list[Team]
        """
        teams = []
        res = self.fapi.make_request("/players/teams?player=" + self.fapi_id, {})
        if(res["success"]):
            fapi_player = res["res"]
            if(fapi_player["response"]):
                for team in fapi_player["response"]:
                    fapi_id = team["team"]["id"]
                    db_team = self.db.search("teams", { "fapi_id" : fapi_id })
                    if(len(db_team)):
                        teams.append(db_team[0])

        else:
            if( self.debug ):
                print(res["error_string"])
        return teams

    def current_team(self) -> 'Team':
        r"""Get the current team of the Player.

        :ivar team: the player's team.
        :returns: the team.
        :rtype: Team
        """
        if self.team:
            return self.team
        else:
            res = self.fapi.make_request("/players/teams?player=" + self.fapi_id, {})
            if(res["success"]):
                fapi_player = res["res"]
                seen_years = []

                while(True):
                    year = None
                    for team in fapi_player["response"]:
                        seasons = team['seasons']
                        for season in seasons:
                            if season in seen_years:
                                seasons.remove(season)

                        if(len(team['seasons']) > 0):
                            if( (year is None) or (max(team['seasons']) > year) ):
                                year = max(team['seasons'])
                    
                    if year is None:
                        return None

                    seen_years.append(year)

                    candidates = []
                    for team in fapi_player["response"]:
                        if year in team['seasons']:
                            candidates.append(team)

                    for team in candidates:
                        team_id = team["team"]["id"]
                        res = self.fapi.make_request("/teams?id=" + str(team_id), {})
                        if(not res['res']['response'][0]['team']['national']):
                            db_team = self.db.search("teams", { "fapi_id" : str(team_id) })
                            if(len(db_team)):
                                return db_team[0]
            else:
                if( self.debug ):
                    print(res["error_string"])

    def market_value(self, year: Optional[str] = None) -> int:
        r"""Get the Player's Transfermarkt Market Value for a given year.

        :param year: the year to be selected. If this parameter is not set, get
          the current year.
        :type year: Optional[str]
        :rtype: int
        """
        mv_cache = self.mv_cache

        current_date = datetime.now()
        if not year:    
            if 1 <= current_date.month <= 6:
                previous_year = current_date.year - 1
                year = str(previous_year)
            else:
                year = str(current_date.year)

        if year in mv_cache:
            return mv_cache[year]

        res = {}
        if(year != str(current_date.year)):
            res = self.tm.get_player_value_by_year(self, year)
        else:
            res = self.tm.get_player_value(self)

        if(res["success"]):        
            mv_cache[year] = res["res"]["market_value"]
        else:
            if( self.debug ):
                print(res["error_string"])
            mv_cache[year] = 0
    
        self.mv_cache = mv_cache
        return self.mv_cache[year]

    def statistics(self, year: Optional[str] = None, team: Optional[str | Team] = None ) -> dict[Statistic]:
        r"""Returns the Player's FBRef Statistics for a given year and team.

        :param year: desired year the statistics are from.
        :type year: Optional[str]
        :param team: desired team the player was playing for when the statistics were recorded (Given players can be on multiple teams in a season)
        :type team: Optional[str | Team]
        :returns: a hash of Statistic objects
        :rtype: dict[Statistic]
        """
        stats = self.stats_cache

        if stats is None:
            # No Cache, get stats from FBRef
            res = self.fbref.get_stats(self)

            if(res["success"]):
                stats = res["res"]["stats"]

                #Clean Up Fbref IDs, Make them Soccer API IDs & Objects
                new_stats = {}
                db_search_cache = {
                    "leagues" : {},
                    "teams" : {},
                    "players" : {}
                }
                for stat_year in stats:
                    new_stats[stat_year] = {}
                    for team_id in stats[stat_year]:
                        if team_id not in db_search_cache["teams"]:
                            db_team = self.db.get("teams", team_id )
                            if(db_team):
                                db_search_cache["teams"][team_id] = db_team

                        if team_id in db_search_cache["teams"]:
                            t_id = str(db_search_cache["teams"][team_id].id)
                        
                            for key in stats[stat_year][team_id]:
                                stat = stats[stat_year][team_id][key]
                                for obj_type in ["league", "team", "player"]:
                                    if obj_type in stat.context and str(type(stat.context[obj_type])) == "<class 'int'>":
                                        id = str(stat.context[obj_type])

                                        if id not in db_search_cache[f"{obj_type}s"]:
                                            db_obj = self.db.get(f"{obj_type}s", stat.context[obj_type])
                                            if(db_obj):
                                                db_search_cache[f"{obj_type}s"][id] = db_obj
                                            else:
                                                db_search_cache[f"{obj_type}s"][id] = None
                                        stat.context[obj_type] = db_search_cache[f"{obj_type}s"][id]    
                                stats[stat_year][team_id][key] = stat

                            new_stats[stat_year][t_id] = stats[stat_year][team_id]
                stats = new_stats
                self.stats_cache = new_stats
            else:
                if(self.debug):
                    print(res["error_string"])
                return {}

        stats_by_year = {}

        if year:
            if(year in stats):
                stats_by_year = stats[year]
            else:
                return {}
        else:
            keys = list(stats.keys())
            if(len(keys) > 0):
                year = max(keys)
            else:
                return {}
        stats_by_year = stats[year]

        if team:
            if(str(type(team)) != "<class 'str'>" ):
                team = str(team.id)
            if team not in stats_by_year:
                return {}
        else:
            keys = list(stats_by_year.keys())
            if(len(keys) > 0):
                team = None
                key_count = 0
                for key in keys:
                    if team is None:
                        team = key
                        key_count = len(list(stats_by_year[key].keys()))
                    elif(len(list(stats_by_year[key].keys())) > key_count):
                        team = key
                        key_count = len(list(stats_by_year[key].keys()))                
            else: 
                return {}

        stats_by_year[team]["year"] = year
        stats_by_year[team]["team"] = self.db.get("teams", team)
        return stats_by_year[team]

    def statistic(self, stat, year: Optional[str] = None, team: Optional[str | Team] = None ) -> Statistic:
        r"""Get the Player's FBRef statistics for a given year, team and statistic.

        :param stat: internal or display name of a statistic.
        :type stat: str
        :param year: desired year the statistic is from.
        :type year: Optional[str]
        :param team: desired team the player was playing for when the statistic was recorded (Given players can be on multiple teams in a season)
        :type team: Optional[str | Team]
        :returns: a Statistic object.
        :rtype: Statistic
        """
        stat_key = None
        if(key_to_name(stat)):
            stat_key = stat
        elif(name_to_key(stat)):
            stat_key = name_to_key(stat)

        stats = self.statistics(year=year, team=team)
        if stat_key and stat_key in stats:
            return stats[stat_key]

        return Statistic({ "key" : stat, "value" : 0, "percentile" : 0})

    def fbref_image(self) -> str:
        r"""Get a URL of the Player's FBRef image.

        :returns: a URL
        :rtype: str
        """
        res = self.fbref.get_player_image_url(self)

        if(res["success"]):
            return res["res"]
        else:
            if( self.debug ):
                print(res["error_string"])
            return 0

    def image(self) -> str:
        r"""Get a URL to the Player's API-Football image.

        :returns: a URL
        :rtype: str
        """
        if not self.fapi_profile:
            return self.profile()['photo']
        else:
            return self.fapi_profile['photo']

    def scouting_data(self) -> dict[Statistic] | int:
        r"""Get the Player's FBRef scouting profile.

        :returns: an dictionary of of Statistic objects or ``0`` in case of an
          error.
        :rtype: dict[Statistic] | int
        """
        res = self.fbref.get_scouting_data(self)
        
        if(res["success"]):
            return res["res"]["scouting_report"]
        else:
            if( self.debug ):
                print(res["error_string"])
            return 0

    def pizza_plot(self, columns = None):
        res = self.visualize.player_pizza_plot(self, columns)
        
        if(not res["success"]):
            if( self.debug ):
                print(res["error_string"])
        return

    def shots_over_season(self) -> list:
        r"""Get the raw Player's Understat shooting data over a season.

        :returns: a list of data, or an empty list in case of error.
        :rtype: list
        """
        res = self.understat.get_player_shots(self)
        
        if(res["success"]):
            return res["res"]
        else:
            if( self.debug ):
                print(res["error_string"])
            return []

    def analyze_shots(self, shots) -> dict[Statistic]:
        r"""Get the analysis of a Player's Understat shooting data.

        :returns: a dictionary of Statistic Objects. In case of an error
        :rtype: dict[Statistic]
        """
        res = self.understat.analyze_shot_data(shots)
        
        if(res["success"]):
            return res["res"]
        else:
            if( self.debug ):
                print(res["error_string"])
            return {
                "shots" : Statistic({ "key" : "shots", "value": 0}),
                "goals" : Statistic({ "key" : "goals", "value": 0}),
                "xg" : Statistic({ "key" : "goals", "value": 0}),
                "xg_per_shot" : Statistic({ "key" : "xg", "value": 0}),
                "avg_shot_distance" : Statistic( { "key" : "avg_shot_distance", "value" : 0 }),
                "avg_actual_shot_distance" : Statistic({ "key" : "avg_actual_shot_distance", "value" : 0 })
            }    

    def shot_map(self):
        res = self.visualize.player_shot_map(self)
        
        if(not res["success"]):
            if( self.debug ):
                print(res["error_string"])
        return
