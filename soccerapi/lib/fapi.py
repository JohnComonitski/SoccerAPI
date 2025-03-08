from datetime import datetime
from bs4 import BeautifulSoup
import requests
import re

class FAPI:
    def __init__(self, config={}):
        self.url = "https://" + config["fapi_host"]
        self.fapi_headers = {
            "X-RapidAPI-Key": config["fapi_key"],
            "X-RapidAPI-Host": config["fapi_host"]
        }
    
    def is_valid_date(self, date_string):
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False
        
    def parse_error(self, errors):
        if(str(type(errors)) == "<class 'list'>"):
            if(len(errors) > 0):
                error = errors[0]
                keys = list(error.keys())
                if(len(keys) > 0):
                    return error[keys[0]]
        elif(str(type(errors))  == "<class 'dict'>"):
            keys = list(errors.keys())
            if(len(keys) > 0):
                return errors[keys[0]]
        return None

    def make_request(self, end_point, query):
        end_point = self.url + end_point
        response = requests.get(end_point, headers=self.fapi_headers, params=query)
        res = response.json()
        if("message" in res):
            if(len(list(res.keys())) == 1):
                return { "success" : 0, "res" : None , "error_string" : "Error: " + res["message"] }

        if("errors" in res):
            error = self.parse_error(res["errors"])
        
        if(error):
            return { "success" : 0, "res" : None , "error_string" : "Error: " + error }
        
        return { "success" : 1, "res" : res , "error_string" : "" }
    
    def get_players_on_team(self, team):
        res = {}
        if(not team.fapi_id):
            return { "success" : 0, "res" : { "players" : {res}}, "error_string" : "Error: Team object did not include a fapi_team_id" }
        fapi_team_id = team.fapi_id
        
        query = { "team" : fapi_team_id}
        response = self.make_request("/players/squads", query)
        
        if(response["success"]):
            response = response["res"]
            if "response" in response:
                return { "success" : 1, "res" : { "players" : response['response']}, "error_string" : "" }
            
        return { "success" : 0, "res" : { "players" : {}}, "error_string" : "Error: " + response["error_string"] }
    
    def get_teams_in_league(self, league, year):
        res = []
        if(not league.fapi_id):
            return { "success" : 0, "res" : { "teams" : res}, "error_string" : "Error: League object did not include a fapi_league_id" }
        fapi_league_id = league.fapi_id

        if not year:
            current_date = datetime.now()
            if 1 <= current_date.month <= 6:
                previous_year = current_date.year - 1
                year = str(previous_year)
            else:
                year = str(current_date.year)
        
        query = { "league" : fapi_league_id, "season" : year}
        response = self.make_request("/teams", query)
        if(response["success"]):
            response = response["res"]
            if "response" in response:
                res = response['response']
                if(len(res) > 0):
                    return { "success" : 1, "res" : { "teams" : res}, "error_string" : "" }
                    
        return { "success" : 0, "res" : { "teams" : res}, "error_string" : "Error: " + response["error_string"] }

    def get_team_schedule(self, team, year):
        fixtures = []
        if(not team.fapi_id):
            return { "success" : 0, "res" : { "matches" : fixtures }, "error_string" : "Error: Team object did not include a fapi_team_id" }
        fapi_team_id = team.fapi_id
            
        if not year:
            current_date = datetime.now()
            if 1 <= current_date.month <= 6:
                previous_year = current_date.year - 1
                year = str(previous_year)
            else:
                year = str(current_date.year)
        
        query = { "team" : fapi_team_id, "season" : year}
        response = self.make_request("/fixtures", query)
        if(response["success"]):
            response = response["res"]
            if "response" in response:
                fixtures = response['response']
                if(len(fixtures) > 0):

                    for i in range(response['paging']['total'] - 1):
                        query["page"] = i + 1
                        next_page = response = self.make_request("/fixtures", query)
                        if(next_page["success"]):
                            next_page = next_page["res"]
                            fixtures += next_page["response"]

                return { "success" : 1, "res" : { "matches" : fixtures }, "error_string" : "" }
        return { "success" : 0, "res" : { "matches" : fixtures }, "error_string" : "Error: " + response["error_string"] }

    def get_league_schedule(self, league, year):
        fixtures = []
        if(not league.fapi_id):
            return { "success" : 0, "res" : { "matches" : fixtures }, "error_string" : "Error: League object did not include a fapi_league_id" }
        fapi_league_id = league.fapi_id

        if not year:
            current_date = datetime.now()
            if 1 <= current_date.month <= 6:
                previous_year = current_date.year - 1
                year = str(previous_year)
            else:
                year = str(current_date.year)
        
        query = { "league" : fapi_league_id, "season" : year}
        response = self.make_request("/fixtures", query)
        if(response["success"]):
            response = response["res"]
            if "response" in response:
                fixtures = response['response']
                if(len(fixtures) > 0):
                    for i in range(response['paging']['total'] - 1):
                        query["page"] = i + 1
                        next_page = response = self.make_request("/fixtures", query)
                        if(next_page["success"]):
                            next_page = next_page["res"]
                            fixtures += next_page["response"]

                return { "success" : 1, "res" : { "matches" : fixtures }, "error_string" : "" }
            
        return { "success" : 0, "res" : { "matches" : fixtures }, "error_string" : "Error: " + response["error_string"] }

    def get_league_fixtures_on_date(self, league, date):
        fixtures = []
        if(not league.fapi_id):
            return { "success" : 0, "res" : { "matches" : fixtures }, "error_string" : "Error: League object did not include a fapi_league_id" }
        fapi_league_id = league.fapi_id

        if not self.is_valid_date(date):
            return { "success" : 0, "res" : { "matches" : fixtures }, "error_string" : "Error: Date given is not a valid date" }
        
        year = date.split("-")[0]
        month = int(date.split("-")[1])
        season = datetime.strptime(date, '%Y-%m-%d')
        if 1 <= month <= 6:
            previous_year = season.year - 1
            year = str(previous_year)
        else:
            year = str(season.year)
        
        query = { "league" : fapi_league_id, "season" : year, "date" : date}
        response = self.make_request("/fixtures", query)
        if(response["success"]):
            response = response["res"]
            if "response" in response:
                fixtures = response['response']
                if(len(fixtures) > 0):

                    for i in range(response['paging']['total'] - 1):
                        query["page"] = i + 2
                        next_page = response = self.make_request("/fixtures", query)
                        if(next_page["success"]):
                            next_page = next_page["res"]
                            fixtures += next_page["response"]

                return { "success" : 1, "res" : { "matches" : fixtures}, "error_string" : "" }
            
        return { "success" : 0, "res" : { "matches" : fixtures}, "error_string" : "Error: " + response["error_string"] }

    def get_team_fixtures_on_date(self, team, date):
        res = []
        if(not date):
            return { "success" : 0, "res" : { "matches" : res}, "error_string" : "Error: No date was provided" }

        if(not team.fapi_id):
            return { "success" : 0, "res" : { "matches" : res}, "error_string" : "Error: Team object did not include a fapi_team_id" }
        fapi_team_id = team.fapi_id

        if not self.is_valid_date(date):
            return { "success" : 0, "res" : { "matches" : res}, "error_string" : "Error: Date did not match '%Y-%m-%d' format" }
        
        year = date.split("-")[0]
        month = int(date.split("-")[1])
        season = datetime.strptime(date, "%Y-%m-%d")

        if 1 <= month <= 6:
            previous_year = season.year - 1
            year = str(previous_year)
        else:
            year = str(season.year)
        
        query = { "team" : fapi_team_id, "season" : year, "date" : date}
        response = self.make_request("/fixtures", query)
        if(response["success"]):
            response = response["res"]
            if "response" in response:
                res = response['response']
                if(len(res) > 0):
                    for i in range(response['paging']['total'] - 1):
                        query["page"] = i + 1
                        next_page = response = self.make_request("/fixtures", query)
                        if(next_page["success"]):
                            next_page = next_page["res"]
                            fixtures += next_page["response"]
                return { "success" : 1, "res" : { "matches" : res}, "error_string" : "" }

        return { "success" : 0, "res" : { "matches" : res}, "error_string" : "Error: " + response["error_string"] }

    def get_line_up(self, fixture):
        res = {}

        query = { "fixture" : fixture.id }
        response = self.make_request("/fixtures/lineups", query)
        if(response["success"]):
            response = response["res"]
            if "response" in response:
                res = response['response']
                if(len(res) > 0):
                    return { "success" : 1, "res" : { "lineup" : res }, "error_string" : "" }

        return { "success" : 0, "res" : { "lineup" : res}, "error_string" : "Error: " + response["error_string"] }

