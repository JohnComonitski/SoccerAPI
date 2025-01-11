from datetime import datetime

class League:
    def __init__(self, league_data, db):
        #From League Data
        self.league_name = league_data["league_name"]
        self.id = league_data["league_id"]
        self.country = league_data["country_code"]
        self.fbref_id = league_data["fbref_league_id"]
        self.tm_id = league_data["tm_league_id"]
        self.fapi_id = league_data["fapi_league_id"]
        #Cached Data
        self.teams_cache = {}
        self.fapi_profile = None
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
    
    def name(self):
        return self.league_name
    
    def profile(self):
        if self.fapi_profile:
            return self.fapi_profile
        else:
            player = self.fapi.make_request("/leagues?id=" + self.fapi_id, {})
            if(len(player["response"]) > 0):
                self.fapi_profile = player["response"][0]["league"]
                return self.fapi_profile 
        return None

    def teams(self, year = None):
        teams = self.teams_cache

        if not year:
            current_date = datetime.now()
            if 1 <= current_date.month <= 6:
                previous_year = current_date.year - 1
                year = str(previous_year)
            else:
                year = str(current_date.year)

        if year in teams:
            print("cache hit")
            return teams[year]

        teams_list = []
        res = self.fapi.get_teams_in_league(self, year)
        if(res["success"]):
            for team in res["res"]["teams"]:
                fapi_team_id = team["team"]["id"]
                db_team = self.db.search("teams", { "fapi_team_id" : fapi_team_id })
                if(len(db_team) > 0):
                    teams_list.append(db_team[0])
            teams[year] = teams_list
        else:
            if( self.debug ):
                print(res["error_string"])
            teams[year] = teams_list

        self.teams_cache = teams
        return self.teams_cache[year]

    def fixtures(self, date = None):
        if(date is None):
            date = datetime.now().strftime("%Y-%m-%d")

        res = self.fapi.get_league_fixtures_on_date(self, date)

        if(res["success"]):
            return res["res"]["matches"][0]
        else:
            if(1 or self.debug ):
                print(res["error_string"]) 
            return []

    def fixture_list(self, year = None):
        res = self.fapi.get_league_schedule(self, year)

        if(res["success"]):
            return res["res"]["matches"][0]
        else:
            if(1 or self.debug ):
                print(res["error_string"]) 
            return []

    def market_value(self, year = None):
        res = self.tm.get_league_value(self, year)

        if(res["success"]):
            return res["res"]["market_value"]
        else:
            if(1 or self.debug ):
                print(res["error_string"]) 
            return 0
        
    def market_value_over_time(self):
        res = self.tm.get_league_value_over_time(self)

        if(res["success"]):
            return res["res"]["market_value_by_year"]
        else:
            if(1 or self.debug ):
                print(res["error_string"]) 
            return 0