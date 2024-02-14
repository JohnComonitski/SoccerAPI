from SoccerAPI.lib.env import Env
from SoccerAPI.lib.postgres import PostgreSQL
from SoccerAPI.lib.tm import TM
from SoccerAPI.lib.fapi import FAPI
from SoccerAPI.lib.fbref import FBRef
from datetime import datetime
from tqdm import tqdm


class SoccerAPI():
    def __init__(self):
        env = Env()
        self.fbref = FBRef()
        self.tm = TM()
        self.fapi = FAPI(
            host=env.fapi_host,
            key=env.fapi_key
        )
        self.db = PostgreSQL(
            host=env.db_host,
            port=env.db_port,
            database=env.db_database,
            user=env.db_user,
            password=env.db_password
        ) 
        
        current_date = datetime.now()
        if 1 <= current_date.month <= 6:
            previous_year = current_date.year - 1
            self.this_year = str(previous_year)
        else:
            self.this_year = str(current_date.year)

    def get_player_current_value_and_stats(self, player):
        res={}
        with tqdm(total=2) as pbar:
            pbar.set_description("Getting %s's value" % player["last_name"])
            pbar.update(1)
            value = self.tm.get_player_value(player)
            if not value["success"]:
                return { "success" : 0, "res" : { "matches" : res}, "error_string" : value["error_string"] }

            pbar.set_description("Getting %s's stats" % player["last_name"])
            stats = self.fbref.get_player_stats(player, year=self.this_year)
            pbar.update(1)
            if not value["success"]:
                return { "success" : 0, "res" : { "matches" : res} }
            
        return { "success" : 1, "res" : { "value" : value["res"]["market_value"], "stats" : stats["res"]["stats"] }, "error_string" : value["error_string"] }
        
    def get_line_up_value(self, match, team, include_subs):
        res = {}
        lineup = self.fapi.get_line_up(match)
        if(lineup["success"]):
            lineups = lineup["res"]["lineup"]
            total = len(lineups[0]["startXI"]) + len(lineups[0]["substitutes"])
            total += len(lineups[1]["startXI"]) + len(lineups[1]["substitutes"])
            with tqdm(total=total) as pbar:
                idx = 0
                pbar.set_description("Getting Match Lineup's Values")
                for lineup in lineups:
                    if(team is not None):
                        if(team["fapi_team_id"] != str(lineup["team"]["id"])):
                            continue

                    eleven = lineup["startXI"]
                    idx_2 = 0
                    for player in eleven:
                        db_players = self.db.search("players", { "fapi_player_id" : player["player"]["id"] })
                        if(len(db_players) > 0):
                            db_player = db_players[0]
                            value = self.tm.get_player_value(db_player)
                            if(value["success"]):
                                lineups[idx]["startXI"][idx_2]["player"]["market_value"] = value["res"]["market_value"]
                            else:
                                lineups[idx]["startXI"][idx_2]["player"]["market_value"] = 0
                        else:
                            lineups[idx]["startXI"][idx_2]["player"]["market_value"] = 0
                        pbar.update(1)
                        idx_2 += 1

                    if(include_subs):
                        subs = lineup["substitutes"]
                        idx_2 = 0
                        for player in subs:
                            db_players = self.db.search("players", { "fapi_player_id" : player["player"]["id"] })
                            if(len(db_players) > 0):
                                db_player = db_players[0]
                                value = self.tm.get_player_value(db_player)
                                if(value["success"]):
                                    lineups[idx]["substitutes"][idx_2]["player"]["market_value"] = value["res"]["market_value"]
                                else:
                                    lineups[idx]["substitutes"][idx_2]["player"]["market_value"] = 0
                            else:
                                lineups[idx]["substitutes"][idx_2]["player"]["market_value"] = 0
                            pbar.update(1)
                            idx_2 += 1
                    idx += 1
                
                return { "success" : 1, "res" : { "lineup" : lineups}, "error_string" : "" }
        return { "success" : 0, "res" : { "lineup" : res}, "error_string" : lineup["error_string"] }

    def get_teams_in_a_leagues_values(self, league):
        res = self.fapi.get_teams_in_league(league, year=None)
        teams = []
        if res["success"]:
            teams = res["res"]["teams"]
            idx = 0
            pbar = tqdm(teams)
            for team in pbar:
                pbar.set_description("Getting %s's value" % team["team"]["name"])
                db_team = self.db.search("teams", {"fapi_team_id" : team["team"]["id"]})
                if(len(db_team) > 0):
                    db_team = db_team[0]
                    value = self.tm.get_team_value(db_team, year=None)
                    if(value["success"]):
                        teams[idx]["team"]["market_value"] = value["res"]["market_value"]
                    else:
                        teams[idx]["team"]["market_value"] = 0
                idx += 1
                
            return { "success" : 1, "res" : { "teams" : teams}, "error_string" : "" }
        return { "success" : 0, "res" : { "teams" : teams}, "error_string" : res["error_string"]  }
    
    def get_league_wide_player_stats(self, league, save_results):
        player_stats = {}
        res = self.fapi.get_teams_in_league(league, year=None)
        if(res["success"]):
            teams = res["res"]["teams"]
            team_pbar = tqdm(teams)
            for team in team_pbar:
                team_pbar.set_description("Getting %s's players" % team["team"]["name"])
                db_team = self.db.search("teams", { "fapi_team_id" : team["team"]["id"] })

                if(len(db_team) > 0):
                    db_team = db_team[0]
                    if db_team["team_id"] not in player_stats:
                        player_stats[db_team["team_id"]] = {}
                        player_stats[db_team["team_id"]]["team"] = db_team
                        player_stats[db_team["team_id"]]["players"] = {}
                    
                    res = self.fapi.get_players_on_team(db_team)
                    if(res["success"]):
                        players = res["res"]["players"][0]["players"]
                        player_pbar = tqdm(players, leave=False)
                        for player in player_pbar:
                            player_pbar.set_description("Getting %s's stats" % player["name"])
                            player_id = player["id"]
                            db_player = self.db.search("players", { "fapi_player_id" : player_id })
                            if(len(db_player) > 0):
                                db_player = db_player[0]
                                player_fbref_stats = self.fbref.get_player_stats(db_player, year=self.this_year)
                                if(player_fbref_stats["success"]):
                                    if(self.this_year in player_fbref_stats["res"]["stats"]):
                                        stats = player_fbref_stats["res"]["stats"][self.this_year]
                                        
                                        if(db_team["fbref_team_id"] in stats):
                                            player_stats[db_team["team_id"]]["players"][db_player["player_id"]] = {}
                                            player_stats[db_team["team_id"]]["players"][db_player["player_id"]]["stats"] = stats[db_team["fbref_team_id"]]
                                            player_stats[db_team["team_id"]]["players"][db_player["player_id"]]["player"] = db_player
                                            if save_results:
                                                insert_obj = stats[db_team["fbref_team_id"]]
                                                insert_obj["year"] = str(self.this_year)
                                                insert_obj["position"] = player_fbref_stats["res"]["stats"]["position"]
                                                insert_obj["player_id"] = db_player["player_id"]
                                                insert_obj["fbref_player_id"] = db_player["fbref_player_id"]
                                                insert_obj["league_id"] = league["league_id"]
                                                insert_obj["team_id"] = db_team["team_id"]
                                                insert_obj["fbref_team_id"] = db_team["fbref_team_id"]
                                                self.db.create("player_stats", [insert_obj])

                    else:
                        return { "success" : 0, "res" : { "players" : []}, "error_string" : res["error_string"]  }    
            return { "success" : 1, "res" : { "players" : player_stats}, "error_string" : ""  }          
        return { "success" : 0, "res" : { "players" : []}, "error_string" : res["error_string"]  }
    
    def get_team_player_stats(self, team, save_results):
        player_stats = {}

        db_team = team
        if db_team["team_id"] not in player_stats:
            player_stats[db_team["team_id"]] = {}
            player_stats[db_team["team_id"]]["team"] = db_team
            player_stats[db_team["team_id"]]["players"] = {}
        
        res = self.fapi.get_players_on_team(db_team)
        if(res["success"]):
            players = res["res"]["players"][0]["players"]
            player_pbar = tqdm(players, leave=False)
            for player in player_pbar:
                player_pbar.set_description("Getting %s's stats" % player["name"])
                player_id = player["id"]
                db_player = self.db.search("players", { "fapi_player_id" : player_id })
                if(len(db_player) > 0):
                    db_player = db_player[0]

                    player_fbref_stats = self.fbref.get_player_stats(db_player, year=self.this_year)
                    if(player_fbref_stats["success"]):
                        if(self.this_year in player_fbref_stats["res"]["stats"]):
                            stats = player_fbref_stats["res"]["stats"][self.this_year]
                            
                            if(db_team["fbref_team_id"] in stats):
                                player_stats[db_team["team_id"]]["players"][db_player["player_id"]] = {}
                                player_stats[db_team["team_id"]]["players"][db_player["player_id"]]["stats"] = stats[db_team["fbref_team_id"]]
                                player_stats[db_team["team_id"]]["players"][db_player["player_id"]]["player"] = db_player
                                if save_results:
                                    insert_obj = stats[db_team["fbref_team_id"]]
                                    #TODO: Get League
                                    
                                    insert_obj["year"] = str(self.this_year)
                                    insert_obj["position"] = player_fbref_stats["res"]["stats"]["position"]
                                    insert_obj["player_id"] = db_player["player_id"]
                                    insert_obj["fbref_player_id"] = db_player["fbref_player_id"]
                                    insert_obj["team_id"] = db_team["team_id"]
                                    insert_obj["fbref_team_id"] = db_team["fbref_team_id"]
                                    self.db.create("player_stats", [insert_obj])
                    else:
                        print(db_player)
                        print("-----------------------")
        else:
            return { "success" : 0, "res" : { "players" : []}, "error_string" : res["error_string"]  }    
        
        return { "success" : 1, "res" : { "players" : player_stats}, "error_string" : ""  }          
