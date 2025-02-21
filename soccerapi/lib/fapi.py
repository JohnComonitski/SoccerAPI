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

    def make_request(self, end_point, query):
        end_point = self.url + end_point
        response = requests.get(end_point, headers=self.fapi_headers, params=query)

        res = response.json()
        if(res and "errors" in res):
            return { "success" : 0, "res" : None , "error_string" : "Error: " + res["errors"]["requests"] }
        
        return res
    
    def get_players_on_team(self, team):
        res = {}
        if(not team.fapi_id):
            return { "success" : 0, "res" : { "players" : {res}}, "error_string" : "Error: Team object did not include a fapi_team_id" }
        fapi_team_id = team.fapi_id
        
        query = { "team" : fapi_team_id}
        response = self.make_request("/players/squads", query)
        if "response" in response:
            return { "success" : 1, "res" : { "players" : response['response']}, "error_string" : "" }
        
        return { "success" : 0, "res" : { "players" : {}}, "error_string" : "Error: " + str(response["errors"]) }
    
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
        if "response" in response:
            res = response['response']
            if(len(res) > 0):
                return { "success" : 1, "res" : { "teams" : res}, "error_string" : "" }
                
        return { "success" : 0, "res" : { "teams" : res}, "error_string" : "Error: " + str(response["errors"]) }

    def get_team_schedule(self, team, year):
        res = []
        if(not team.fapi_id):
            return { "success" : 0, "res" : { "matches" : res}, "error_string" : "Error: Team object did not include a fapi_team_id" }
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
        if "response" in response:
            res = response['response']
            if(len(res) > 0):

                for i in range(response['paging']['total'] - 1):
                    query["page"] = i + 2
                    next_page = response = self.make_request("/fixtures", query)
                    res += next_page["response"]

            return { "success" : 1, "res" : { "matches" : res}, "error_string" : "" }
        
        return { "success" : 0, "res" : { "matches" : res}, "error_string" : "Error: " + str(response["errors"]) }

    def get_league_schedule(self, league, year):
        res = []
        if(not league.fapi_id):
            return { "success" : 0, "res" : { "matches" : res}, "error_string" : "Error: League object did not include a fapi_league_id" }
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
        if "response" in response:
            res = response['response']
            if(len(res) > 0):

                for i in range(response['paging']['total'] - 1):
                    query["page"] = i + 2
                    next_page = response = self.make_request("/fixtures", query)
                    res += next_page["response"]

            return { "success" : 1, "res" : { "matches" : res}, "error_string" : "" }
        
        return { "success" : 0, "res" : { "matches" : res}, "error_string" : "Error: " + str(response["errors"]) }

    def get_league_fixtures_on_date(self, league, date):
        res = []
        if(not league.fapi_id):
            return { "success" : 0, "res" : { "matches" : res}, "error_string" : "Error: League object did not include a fapi_league_id" }
        fapi_league_id = league.fapi_id

        if not self.is_valid_date(date):
            return { "success" : 0, "res" : { "matches" : res}, "error_string" : "Error: Date given is not a valid date" }
        
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
        if "response" in response:
            res = response['response']
            if(len(res) > 0):

                for i in range(response['paging']['total'] - 1):
                    query["page"] = i + 2
                    next_page = response = self.make_request("/fixtures", query)
                    res += next_page["response"]

            return { "success" : 1, "res" : { "matches" : res}, "error_string" : "" }
        
        return { "success" : 0, "res" : { "matches" : res}, "error_string" : "Error: " + str(response["errors"]) }

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
        if "response" in response:
            res = response['response']
            if(len(res) > 0):

                for i in range(response['paging']['total'] - 1):
                    query["page"] = i + 2
                    next_page = response = self.make_request("/fixtures", query)
                    res += next_page["response"]

            return { "success" : 1, "res" : { "matches" : res}, "error_string" : "" }

        return { "success" : 0, "res" : { "matches" : res}, "error_string" : "Error: " + str(response["errors"]) }

    def get_line_up(self, fixture):
        res = {}

        query = { "fixture" : fixture.id }
        response = self.make_request("/fixtures/lineups", query)

        if "response" in response:
            res = response['response']
            if(len(res) > 0):
                return { "success" : 1, "res" : { "lineup" : res}, "error_string" : "" }

        return { "success" : 0, "res" : { "lineup" : res}, "error_string" : "Error: " + str(response["errors"]) }

