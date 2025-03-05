import json
from datetime import datetime
from .statistic import Statistic 
from ..lib.utils import key_to_name, name_to_key, traverse_dict
from typing import Optional


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
        self.fbref_id = player_data["fbref_player_id"]
        self.tm_id = player_data["tm_player_id"]
        self.fapi_id = player_data["fapi_player_id"]
        self.understat_id = player_data["understat_player_id"]
        #Cached Data
        self.fapi_profile = None
        self.player_country = None
        self.team = None
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
        return f"Player({self.name()})"
    
    def __repr__(self):
        return f"Player({self.name()})"

    def name(self) -> str:
        r"""Get the name of the Player.

        :returns: the first and last names.
        :rtype: str
        """
        return self.first_name + " " + self.last_name
    
    def export(self):
        r"""Export the Player object as a JSON file.

        .. note:: The output filename is in the format ``player_{self.id}.json``.
        """
        data = self.to_json()

        file_name = "player_" + str(self.id) + ".json"
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
            "statistics" : self.stats_cache
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
        
        if "statistics" in data and data["statistics"]:
            stats = {}
            has_years = 0 
            first_key = next(iter(data["statistics"]))
            if "20" in first_key:
                has_years = 1

            if(has_years):
                for year in data["statistics"]:
                    if year not in stats:
                        stats[year] = {}
                    for key in data["statistics"][year]:
                        stat_data = data["statistics"][year][key]
                        if "key" in stat_data:
                            stats[year][key] = Statistic(stat_data)
                        else:
                            stats[year][key] = data["statistics"][year]
            else:
                for key in data["statistics"]:
                    stat_data = data["statistics"][key]
                    if "key" in stat_data:
                        stats[key] = Statistic(stat_data)
                    else:
                        stats[key] = data["statistics"]

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
        position_list = ["FB", "CB", "AM", "MF", "FW", "DM", "WM", "GK", "CM", "DF" ]
        
        res = self.fbref.player_positions(self)
        if(res["success"]):
            positions = []
            for position in position_list:
                if position in res["res"]:
                    positions.append(position)
            
            return positions
        else:
            if( self.debug ):
                print(res["error_string"])
            return []

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
                if(fapi_player["response"][0]):
                    fapi_team_id = fapi_player["response"][0]["team"]["id"]
                    db_team = self.db.search("teams", { "fapi_team_id" : fapi_team_id })
                    if(len(db_team)):
                        self.team = db_team[0]
            else:
                if( self.debug ):
                    print(res["error_string"])
            return self.team

    def market_value(self, year: Optional[str] = None) -> int:
        r"""Get the Player's Transfermarkt Market Value for a given year.

        :param year: the year to be selected. If this parameter is not set, get
          the current year.
        :type year: Optional[str]
        :rtype: int
        """
        if(year):
            res = self.tm.get_player_value_by_year(self, year)
        else:
            res = self.tm.get_player_value(self)

        if(res["success"]):
            return res["res"]["market_value"]
        else:
            if( self.debug ):
                print(res["error_string"])
            return 0

    def statistics(self, year = None) -> dict[Statistic]:
        r"""Returns the Player's FBRef Statistics for a given year.

        :param year: desired year for the statistics. If not set get the
          previous year if the current month is between January and June, or
          the current year otherwise.
        :type year: Optional[str]
        :returns: a hash of Statistic objects
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

        res = self.fbref.get_player_stats(self, year)
        if(res["success"]):
            if(year in res["res"]["stats"]):
                fbref_team_id = list(res["res"]["stats"][year].keys())[0]
                stats[year] = res["res"]["stats"][year][fbref_team_id]
            else:
                stats[year] = {}
        else:
            if(self.debug):
                print(res["error_string"])
            stats[year] = {}
        self.stats_cache = stats

        return self.stats_cache[year]

    def statistic(self, stat, year: Optional[str]  = None) -> Statistic:
        r"""Get the Player's FBRef statistics for a given year and statistic.

        :param stat: internal or display name of a statistic.
        :type stat: str
        :param year: desired year for the statistics. See the ``statistic``
          method for more information.
        :type year: Optional[str]
        :returns: a Statistic object.
        :rtype: Statistic
        """
        stat_key = None
        if(key_to_name(stat)):
            stat_key = stat
        elif(name_to_key(stat)):
            stat_key = name_to_key(stat)

        stats = self.statistics(year)
        if stat_key and stat_key in stats:
            return stats[stat_key]
        return 0

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
                "average_shot_distance" : Statistic( { "key" : "average_shot_distance", "value" : 0 }),
                "avg_actual_shot_distance" : Statistic({ "key" : "avg_actual_shot_distance", "value" : 0 })
            }    

    def shot_map(self):
        res = self.visualize.player_shot_map(self)
        
        if(not res["success"]):
            if( self.debug ):
                print(res["error_string"])
        return
