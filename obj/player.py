import json
from datetime import datetime
from SoccerAPI.obj.statistic import Statistic 
from SoccerAPI.lib.utils import key_to_name, name_to_key, traverse_dict

class Player:
    def __init__(self, player_data, db):
        #From Player Data
        self.first_name = player_data["first_name"]
        self.last_name = player_data["last_name"]
        self.id = player_data["player_id"]
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

    def name(self):
        return self.first_name + " " + self.last_name
    
    def export(self):
        data = self.to_json()

        file_name = "player_" + str(self.id) + ".json"
        with open(file_name, "w") as file:
            json.dump(data, file, indent=4)

    def to_json(self):
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
    
    def import_data(self, data):
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


    def profile(self):
        if self.fapi_profile:
            return self.fapi_profile
        else:
            player = self.fapi.make_request("/players/profiles?player=" + self.fapi_id, {})
            if(len(player["response"]) > 0):
                self.fapi_profile = player["response"][0]["player"]
                return self.fapi_profile 
        return None
    
    def positions(self):
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

    def country(self):
        if self.player_country:
            return self.player_country
        else:
            profile = self.profile()
            fapi_country = profile["nationality"]
            country = self.fapi.make_request("/countries?name=" + fapi_country, {})
            country_code = country["response"][0]["code"]
            res = self.db.search("countries", { "fapi_country_code" : country_code })
            if(len(res) > 0):
                self.player_country = res[0]["country_code"]
            return self.player_country
    
    def current_team(self):
        if self.team:
            return self.team
        else:
            fapi_player = self.fapi.make_request("/players/teams?player=" + self.fapi_id, {})
            if(fapi_player["response"][0]):
                fapi_team_id = fapi_player["response"][0]["team"]["id"]
                db_team = self.db.search("teams", { "fapi_team_id" : fapi_team_id })
                if(len(db_team)):
                    self.team = db_team[0]
            return self.team

    def market_value(self, year = None):
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

    def statistics(self, year = None):
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
            fbref_team_id = list(res["res"]["stats"][year].keys())[0]
            stats[year] = res["res"]["stats"][year][fbref_team_id]
        else:
            if(self.debug):
                print(res["error_string"])
            stats[year] = {}
        self.stats_cache = stats

        return self.stats_cache[year]

    def statistic(self, stat, year = None):
        stat_key = None
        if(key_to_name(stat)):
            stat_key = stat
        elif(name_to_key(stat)):
            stat_key = name_to_key(stat)

        stats = self.statistics(year)
        if stat_key and stat_key in stats:
            return stats[stat_key]
        return 0

    def fbref_image(self):
        res = self.fbref.get_player_image_url(self)

        if(res["success"]):
            return res["res"]
        else:
            if( self.debug ):
                print(res["error_string"])
            return 0

    def image(self):
        if not self.fapi_profile:
            return self.profile()['photo']
        else:
            return self.fapi_profile['photo']

    def scouting_data(self):
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

    def shots_over_season(self):
        res = self.understat.get_player_shots(self)
        
        if(res["success"]):
            return res["res"]
        else:
            if( self.debug ):
                print(res["error_string"])
            return []

    def analyze_shots(self, shots):
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
