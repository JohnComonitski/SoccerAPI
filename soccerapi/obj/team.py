import json
from .fixture import Fixture
from .statistic import Statistic
from ..lib.utils import key_to_name, name_to_key, traverse_dict
from datetime import datetime

class Team:
    def __init__(self, team_data, db):
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
    
    def name(self):
        return self.team_name
    
    def export(self):
        data = self.to_json()

        file_name = "team_" + str(self.id) + ".json"
        with open(file_name, "w") as file:
            json.dump(data, file, indent=4)

    def to_json(self):
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
    
    def import_data(self, data):
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
            
    def profile(self):
        if self.fapi_profile:
            return self.fapi_profile
        else:
            player = self.fapi.make_request("/teams?id=" + self.fapi_id, {})
            if(len(player["response"]) > 0):
                self.fapi_profile = player["response"][0]["team"]
                return self.fapi_profile 
        return None
    
    def country(self):
        return self.team_country
    
    def players(self):
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
    
    def fixtures(self, year = None):
        res = self.fapi.get_team_schedule(self, year)

        if(res["success"]):
            return res["res"]["matches"]
        else:
            if( self.debug ):
                print(res["error_string"]) 
            return []
        
    def fixture(self, date = None):
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

    def leagues(self):
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
        if(len(res["response"]) > 0):
            for league in res["response"]:
                fapi_league_id = league["league"]["id"]
                db_league = self.db.search("leagues", { "fapi_league_id" : fapi_league_id })
                if(len(db_league) > 0):
                    leagues.append(db_league[0])
            
        return leagues
    
    def market_value(self, year = None):
        res = self.tm.get_team_value(self, year)

        if(res["success"]):
            return res["res"]["market_value"]
        else:
            if(1 or self.debug ):
                print(res["error_string"]) 
            return 0
        
    def market_value_over_time(self):
        res = self.tm.get_team_value_over_time(self)

        if(res["success"]):
            return res["res"]["market_value_by_year"]
        else:
            if(1 or self.debug ):
                print(res["error_string"]) 
            return 0

    def statistics(self):
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

    def statistic(self, stat):
        stat_key = None
        if(key_to_name(stat)):
            stat_key = stat
        elif(name_to_key(stat)):
            stat_key = name_to_key(stat)

        stats = self.statistics()
        if stat_key and stat_key in stats:
            return stats[stat_key]
        return Statistic({ "key" : stat_key, "value" : 0 })

    def opponent_statistics(self):
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
