from datetime import datetime
from bs4 import BeautifulSoup
import requests
import re

class TM:
    def __init__(self):
        pass

    def make_request(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'}
        result = requests.get(url, headers=headers)
        return BeautifulSoup(result.text, "html.parser")
    
    def parse_value(self, input_string):
        pattern = r'€(\d+\.\d+|\d+)([kmbn]+)?'
        match = re.match(pattern, input_string, re.IGNORECASE)

        if match:
            value, unit = match.groups()
            value = float(value)
            unit_factors = {'k': 1e3, 'm': 1e6, 'b': 1e9, 'n': 1e9}
            if unit:
                value *= unit_factors.get(unit.lower(), 1)
            return value
        else:
            return 0

    def get_player_value(self, player):
        if("tm_player_id" not in player):
            return { "success" : 0, "res" : { "market_value" : 0 }, "error_string" : "Error: Player object did not include a tm_player_id" }
        
        tm_player_id = player["tm_player_id"]
        if(not tm_player_id):
            return { "success" : 0, "res" : { "market_value" : 0 }, "error_string" : "Error: Player object did not include a tm_player_id" }
        
        end_point = "https://www.transfermarkt.us/player-name/profil/spieler/"
        end_point += tm_player_id

        page = self.make_request(end_point)
        market_value = 0
        if(page):
            value_box = page.find("span", class_="waehrung")
            if(value_box and value_box.parent):
                value = value_box.parent.text.strip()
                if("€" in value):
                    if(len(value.split(" ")) > 0):
                        market_value = value.split(" ")[0]
                        return { "success" : 1, "res" : { "market_value" : self.parse_value(market_value) }, "error_string" : "" }
            
            return { "success" : 1, "res" : { "market_value" : 0 }, "error_string" : "" }

        return { "success" : 0, "res" : { "market_value" : 0 }, "error_string" : "Error: Player page could not be found" }

    def get_team_value(self, team, year):
        if("tm_team_id" not in team):
            return { "success" : 0, "res" : { "market_value" : 0 }, "error_string" : "Error: Team object did not include a tm_team_id" }
        
        tm_team_id = team["tm_team_id"]
        if(not tm_team_id):
            return { "success" : 0, "res" : { "market_value" : 0 }, "error_string" : "Error: Team object did not include a tm_team_id" }
        
        if not year:
            current_date = datetime.now()
            if 1 <= current_date.month <= 6:
                previous_year = current_date.year - 1
                year = str(previous_year)
            else:
                year = str(current_date.year)

        end_point = "https://www.transfermarkt.us/team-name/startseite/verein/"
        end_point += tm_team_id
        end_point += "?saison_id=" + year

        page = self.make_request(end_point)
        market_value = 0
        if(page):
            players_table = page.find("table", class_="items")
            if(players_table):
                players_values = page.find_all("td", class_="rechts hauptlink")
                if(players_values):
                    for player in players_values:
                        value = player.text.strip()
                        if("€" in value):
                            market_value += self.parse_value(value)
                    return { "success" : 1, "res" : { "market_value" : market_value }, "error_string" : "" }

        return { "success" : 0, "res" : { "market_value" : 0 }, "error_string" : "Error: Team page could not be found" }
    
    def get_team_value_over_time(self, team):
        year = 0
        current_date = datetime.now()
        if 1 <= current_date.month <= 6:
            previous_year = current_date.year - 1
            year = previous_year
        else:
            year = current_date.year

        years_list = [str(year) for year in range(2010, year + 1)]

        values_by_year = {}
        for year in years_list:
            value = self.get_team_value(team, str(year))
            if(value["success"]):
                values_by_year[str(year)] = value["res"]["market_value"]
            else:
                return { "success" : 0, "res" : { "market_value_by_year" : {} }, "error_string" : value["error_string"] }

        return { "success" : 1, "res" : { "market_value_by_year" : values_by_year }, "error_string" : ""  }

    def get_league_value(self, league, year):
        if("tm_league_id" not in league):
            return { "success" : 0, "res" : { "market_value" : 0 }, "error_string" : "Error: League object did not include a tm_league_id" }
        
        tm_league_id = league["tm_league_id"]
        if(not tm_league_id):
            return { "success" : 0, "res" : { "market_value" : 0 }, "error_string" : "Error: League object did not include a tm_league_id" }
        
        if not year:
            current_date = datetime.now()
            if 1 <= current_date.month <= 6:
                previous_year = current_date.year - 1
                year = str(previous_year)
            else:
                year = str(current_date.year)

        end_point = "https://www.transfermarkt.us/league/startseite/wettbewerb/"
        end_point += tm_league_id
        end_point += "/plus/?saison_id=" + year

        page = self.make_request(end_point)
        market_value = 0
        if(page):
            teams_table = page.find("table", class_="items")
            if(teams_table):
                teams_values = page.find_all("td", class_="rechts")
                if(teams_values):
                    for team in teams_values:
                        value_link = team.find("a")
                        if(value_link):
                            value = value_link.text.strip()
                            if("€" in value):
                                market_value += self.parse_value(value)
                    return { "success" : 1, "res" : { "market_value" : market_value }, "error_string" : ""  }

        return { "success" : 0, "res" : { "market_value" : 0 }, "error_string" : "Error: League page could not be found" }

    def get_league_value_over_time(self, league):
        year = 0
        current_date = datetime.now()
        if 1 <= current_date.month <= 6:
            previous_year = current_date.year - 1
            year = previous_year
        else:
            year = current_date.year

        years_list = [str(year) for year in range(2010, year + 1)]

        values_by_year = {}
        for year in years_list:
            value = self.get_league_value(league, str(year))
            if(value["success"]):
                values_by_year[str(year)] = value["res"]["market_value"]
            else:
                return { "success" : 0, "res" : { "market_value_by_year" : {} }, "error_string" :  value["error_string"] }

        return { "success" : 1, "res" : { "market_value_by_year" : values_by_year }, "error_string" : ""  }