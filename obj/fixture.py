from SoccerAPI.obj.statistic import Statistic

class Fixture:
    def __init__(self, match_data, db):
        #From Team Data
        self.match_data = match_data
        self.id = str(match_data["fixture"]["id"])
        self.fixture_details = match_data["fixture"]
        self.home_goals = match_data["goals"]["home"]
        self.away_goals = match_data["goals"]["away"]
        self.score_history = match_data["score"]

        #Inflate League
        league_id = match_data["league"]["id"]
        db_league = db.search("leagues", { "fapi_league_id" : league_id })
        if(len(db_league) > 0):
            self.league = db_league[0]
        else:
            self.league = match_data["league"]

        #Inflate Home Team
        home_id = match_data["teams"]["home"]["id"]
        db_team = db.search("teams", { "fapi_team_id" : home_id })
        if(len(db_team) > 0):
            self.home_team = db_team[0]
        else:
            self.home_team = match_data["teams"]["home"]

        #Inflate Away Team
        away_id = match_data["teams"]["away"]["id"]
        db_team = db.search("teams", { "fapi_team_id" : away_id })
        if(len(db_team) > 0):
            self.away_team = db_team[0]
        else:
            self.away_team = match_data["teams"]["away"]

        #Cached Data

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
        return f"Fixture({self.home_team.name()} vs {self.away_team.name()})"
    
    def __repr__(self):
        return f"Fixture({self.home_team.name()} vs {self.away_team.name()})"
    
    def __get_players_from_lineup(self, lineup, team_id, lineup_type):
        players = []
        if(lineup[0]["team"]["id"] == team_id):
            team = lineup[0]
        else:
            team = lineup[1]
        for player in team[lineup_type]:
            db_player = self.db.search("players", { "fapi_player_id" : player["player"]["id"] })
            if(len(db_player) > 0):
                players.append(db_player[0])
            else:
                players.append(player["player"])
        return players

    def home_starting_xi(self):
        res = self.fapi.get_line_up(self)
        team_id = self.home_team.fapi_id
        lineup_type = "startXI"

        if(res["success"]):
            return self.__get_players_from_lineup(res["res"]["lineup"], team_id, lineup_type)
        else:
            if(1 or self.debug ):
                print(res["error_string"]) 
            return []

    def away_starting_xi(self):
        res = self.fapi.get_line_up(self)
        team_id = self.away_team.fapi_id
        lineup_type = "startXI"

        if(res["success"]):
            return self.__get_players_from_lineup(res["res"]["lineup"], team_id, lineup_type)
        else:
            if(1 or self.debug ):
                print(res["error_string"]) 
            return []
    
    def home_team_sheet(self):
        res = self.fapi.get_line_up(self)
        team_id = self.home_team.fapi_id

        if(res["success"]):
            return {
                "startXI" : self.__get_players_from_lineup(res["res"]["lineup"], team_id, "startXI"),
                "substitutes" : self.__get_players_from_lineup(res["res"]["lineup"], team_id, "substitutes")
            }
        else:
            if(1 or self.debug ):
                print(res["error_string"]) 
            return []
    
    def away_team_sheet(self):
        res = self.fapi.get_line_up(self)
        team_id = self.away_team.fapi_id

        if(res["success"]):
            return {
                "startXI" : self.__get_players_from_lineup(res["res"]["lineup"], team_id, "startXI"),
                "substitutes" : self.__get_players_from_lineup(res["res"]["lineup"], team_id, "substitutes")
            }
        else:
            if(1 or self.debug ):
                print(res["error_string"]) 
            return []

    def statistics(self, player = None):
        if(player):
            mapping = {
                "cards_red" : "cards_red",
                "cards_yellow" : "cards_yellow",
                "dribbles_attempts" : "take_ons",
                "dribbles_past" : "take_ons_won",
                "dribbles_success" : "take_ons_won_pct",
                "games_minutes" : "minutes",
                "goals_assists" : "assists",
                "goes_total" : "goals",
                "passes_accuracy" : "passes_pct",
                "passes_key" : "assisted_shots",
                "passes_total" : "passes",
                "shots_on" : "shots_on_goal",
                "shots_total" : "shots",
                "tackles_blocks" : "blocks",
                "tackles_interceptions" : "interceptions",
                "tackles_total" : "tackles",
                "fouls_committed" : "fouls",
                "fouls_drawn" : "fouled",
                "goals_conceded" : "gk_goals_against",
                "goals_saves" : "gk_saves",
                "penalty_saved" : "gk_pens_saved"
            }
            endpoint = "/fixtures/players?fixture=" + self.id
            res = self.fapi.make_request(endpoint, {})
            stats = {}
            player_found = None
            if(len(res["response"]) > 0 ):
                for team in res["response"]:
                    for fapi_player in team["players"]:
                        if(str(fapi_player["player"]["id"]) == player.fapi_id):
                            player_found = fapi_player
                            break
                    if player_found:
                        break
            if(player_found):
                statistic = player_found["statistics"][0]
                for key1 in statistic:
                    if(statistic[key1]):
                        for key2 in statistic[key1]:
                            key = key1 + "_" + key2
                            if key in mapping:
                                val = statistic[key1][key2]
                                if val is None:
                                    val = 0
                                stats[mapping[key]] = Statistic({ "key" : mapping[key], "value" : val })  
            return stats
        else:
            mapping = {
                "Shots on Goal" : "shots_on_target",
                "Total Shots" : "shots",
                "Blocked Shots" : "blocks",
                "Fouls" : "fouls",
                "Corner Kicks" : "corner_kicks",
                "Offsides" : "offsides",
                "Ball Possession" : "possession",
                "Yellow Cards" : "cards_yellow",
                "Red Cards" : "cards_red",
                "Goalkeeper Saves" : "gk_saves",
                "Total passes" : "passes",
                "Passes accurate" : "passes_completed",
                "Passes %" : "passes_pct",
                "expected_goals" : "xg",
                "goals_prevented" : "gk_psxg_net"
            }
            
            endpoint = "/fixtures/statistics?fixture=" + self.id
            res = self.fapi.make_request(endpoint, {})
            stats = [ { "team" : self.home_team, "statistics" : {} }, { "team" : self.away_team, "statistics" : {} } ]
            if(len(res["response"]) > 0 ):
                idx = 0
                for team in res["response"]:
                    fapi_team_id = str(team["team"]["id"])
                    if stats[0]["team"].fapi_id == fapi_team_id:
                        idx = 0
                    elif stats[1]["team"].fapi_id == fapi_team_id:
                        idx = 1

                    stats[idx]["statistics"] = {}
                    for stat in team["statistics"]:
                        if stat["type"] in mapping:
                            key = mapping[stat["type"]]
                            stats[idx]["statistics"][key] = Statistic({ "key" : key, "value" : stat["value"] })   

            return stats