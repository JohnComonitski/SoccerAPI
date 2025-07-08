from ..lib.utils import traverse_dict
from .statistic import Statistic
import json
from typing import Optional

class Fixture:
    r"""The Fixture object.

    :ivar id: API-Football Fixture ID.
    :vartype id: str
    :ivar fixture-details: API-Football Fixture description.
    :vartype fixture-details: dict
    :ivar home_goals: goals scored by the home team.
    :vartype home_goals: int
    :ivar away_goals: goals scored by the away team.
    :vartype away_goals: int
    :ivar score_history: history of goals scored in match.
    :vartype score_history: dict
    :ivar league: League the Fixture is from.
    :vartype league: League
    :ivar home_team: home Team in Fixture.
    :vartype home_team: Team
    :ivar away_team: away Team in Fixture.
    :vartype away_team: Team
    :ivar db: a database instance.
    :vartype db: PostgreSQL
    """
    def __init__(self, match_data, db):
        #From Team Data
        self.match_data = match_data
        self.id = str(match_data["fixture"]["id"])
        self.fixture_details = match_data["fixture"]
        self.home_goals = match_data["goals"]["home"]
        self.away_goals = match_data["goals"]["away"]
        self.score_history = match_data["score"]

        #Inflate League
        self.league = None
        league_id = match_data["league"]["id"]
        db_league = db.search("leagues", { "fapi_id" : league_id })
        if(len(db_league) > 0):
            self.league = db_league[0]
        else:
            self.league = match_data["league"]

        #Inflate Home Team
        self.home_team = None
        home_id = match_data["teams"]["home"]["id"]
        db_team = db.search("teams", { "fapi_id" : home_id })
        if(len(db_team) > 0):
            self.home_team = db_team[0]
        else:
            self.home_team = match_data["teams"]["home"]

        #Inflate Away Team
        self.away_team = None
        away_id = match_data["teams"]["away"]["id"]
        db_team = db.search("teams", { "fapi_id" : away_id })
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
    
    def export(self, path: Optional[str] = "."):
        r"""Export the Fixture object as a JSON file.
            :param path: Directory to export the fixture object to. If not present, defaults to present working directory
            :type path: str
        .. note:: The output filename is in the format ``fixture_{self.id}.json``.
        """
        data = self.to_json()

        file_name = f"./{path}/fixture_{self.id}.json"
        with open(file_name, "w") as file:
            json.dump(data, file, indent=4)

    def to_json(self) -> dict:
        r"""Get a JSON representation of the Fixture object.

        :rtype: dict
        """
        return traverse_dict({
            "object" : "fixture",
            "match_data" : self.match_data,
            "id" : self.id,
            "fixture_details" : self.fixture_details,
            "home_goals" : self.home_goals,
            "away_goals" : self.away_goals,
            "score_history" : self.score_history,
            "league" : self.league,
            "home_team" : self.home_team,
            "away_team" : self.away_team
        }) 

    def __get_players_from_lineup(self, lineup, team_id, lineup_type):
        players = []
        if(lineup[0]["team"]["id"] == team_id):
            team = lineup[0]
        else:
            team = lineup[1]
        for player in team[lineup_type]:
            db_player = self.db.search("players", { "fapi_id" : player["player"]["id"] })
            if(len(db_player) > 0):
                players.append(db_player[0])
            else:
                players.append(player["player"])
        return players

    def home_starting_xi(self) -> list['Player']:
        r"""Get the home Team's starting XI.

        :returns: a list of home team's starting xi players, or an empty list in case of errors.
        :rtype: list[Player]
        """
        res = self.fapi.get_line_up(self)
        team_id = self.home_team.fapi_id
        lineup_type = "startXI"

        if(res["success"]):
            return self.__get_players_from_lineup(res["res"]["lineup"], team_id, lineup_type)
        else:
            if(1 or self.debug ):
                print(res["error_string"]) 
            return []

    def away_starting_xi(self) -> list['Player']:
        r"""Get the away Team's starting XI.

        :returns: a list of the away team's starting xi players, or an empty list in case of errors.
        :rtype: list[Player]
        """
        res = self.fapi.get_line_up(self)
        team_id = self.away_team.fapi_id
        lineup_type = "startXI"

        if(res["success"]):
            return self.__get_players_from_lineup(res["res"]["lineup"], team_id, lineup_type)
        else:
            if(1 or self.debug ):
                print(res["error_string"]) 
            return []
    
    def home_team_sheet(self) -> list['Player']:
        r"""Get the home Team's entire team sheet.

        :returns: a list of the home team's players on their team sheet, or an empty list in case of errors.
        :rtype: list[Player]
        """
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
    
    def away_team_sheet(self) -> list['Player']:
        r"""Get the away Team's entire team sheet.

        :returns: a list of the aways team's players on their team sheet, or an empty list in case of errors.
        :rtype: list[Player]
        """
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

    def statistics(self, player: Optional['Player'] = None) -> list[Statistic]:
        r"""Get the API-Football statistics from a Fixture for both teams or a given player.

        :param player: Player object you want the statistics of.
        :type player: Optional[Player]
        :returns: a hash of Statistic objects.
        :rtype: dict[Statistic]
        """
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
            stats = []
            if(res["success"]):
                res = res["res"]
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
            else:
                if( self.debug ):
                    print(res["error_string"])
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
            stats = []
            if(res["success"]):
                res = res["res"]
                stats = [ { "team" : self.home_team, "statistics" : {} }, { "team" : self.away_team, "statistics" : {} } ]
                if(len(res["response"]) > 0 ):
                    idx = 0
                    for team in res["response"]:
                        fapi_id = str(team["team"]["id"])
                        if stats[0]["team"].fapi_id == fapi_id:
                            idx = 0
                        elif stats[1]["team"].fapi_id == fapi_id:
                            idx = 1

                        stats[idx]["statistics"] = {}
                        for stat in team["statistics"]:
                            if stat["type"] in mapping:
                                key = mapping[stat["type"]]
                                stats[idx]["statistics"][key] = Statistic({ "key" : key, "value" : stat["value"] })   
            else:
                if( self.debug ):
                    print(res["error_string"])

            return stats
