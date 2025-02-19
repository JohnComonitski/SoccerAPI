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
        if(not player.tm_id):
            return { "success" : 0, "res" : { "market_value" : 0 }, "error_string" : "Error: Player object did not include a tm_player_id" }
        
        tm_player_id = player.tm_id

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

    def get_player_value_by_year(self, player, year):
        if(not player.tm_id):
            return { "success" : 0, "res" : { "market_value" : 0 }, "error_string" : "Error: Player object did not include a tm_player_id" }
        
        tm_player_id = player.tm_id
        
        end_point = "https://www.transfermarkt.us/player-name/leistungsdatendetails/spieler/"
        end_point += tm_player_id

        page = self.make_request(end_point)

        if(page):
            team_url = ""
            seasons_table = page.find("table", class_="items")
            if(seasons_table):
                body = seasons_table.find("tbody")
                rows = body.find_all("tr")
                for row in rows:
                    cols = row.find_all("td")
                    team_link = cols[3]
                    team_link = team_link.find("a")
                    if(team_link):
                        team_url = team_link["href"]
                        if year in team_url: 
                            break
            else:
                return { "success" : 1, "res" : { "market_value" : 0 }, "error_string" : "Error: Player seasons table could not be found" }

            if(team_url != ""):
                end_point = "https://www.transfermarkt.us" + team_url
                team_page = self.make_request(end_point)
                if(team_page):
                    player_table = team_page.find("table", class_="items")
                    if(player_table):
                        body = player_table.find("tbody")
                        rows = body.find_all("tr")
                        for row in rows:
                            cols = row.find_all("td")
                            if(len(cols) > 3):
                                player_link = cols[3]
                                player_link = player_link.find("a")
                                if(player_link):
                                    player_link = player_link["href"]
                                    pattern = r'\/.*\/profil\/spieler\/([a-zA-Z0-9]*)'
                                    match = re.match(pattern, player_link, re.IGNORECASE)
                                    if match:
                                        if(str(tm_player_id) == str(match.group(1))):
                                            return { "success" : 1, "res" : { "market_value" : self.parse_value(cols[-1].text) }, "error_string" : "" }
                                   
            return { "success" : 1, "res" : { "market_value" : 0 }, "error_string" : "Error: Player could not be found on a team in " + year }
        return { "success" : 1, "res" : { "market_value" : 0 }, "error_string" : "Error: Player page could not be found" }
    
    def get_team_value(self, team, year):
        if(not team.tm_id):
            return { "success" : 0, "res" : { "market_value" : 0 }, "error_string" : "Error: Team object did not include a tm_team_id" }     
        tm_team_id = team.tm_id
   
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
        if( not league.tm_id ):
            return { "success" : 0, "res" : { "market_value" : 0 }, "error_string" : "Error: League object did not include a tm_league_id" }       
        tm_league_id = league.tm_id

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