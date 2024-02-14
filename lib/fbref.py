from SoccerAPI.lib.ratelimiter import RateLimiter
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import re

class FBRef:
    def __init__(self):
        self.limiter = RateLimiter(max_calls=15, interval=60)

    def make_request(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'}
        result = requests.get(url, headers=headers)
        return BeautifulSoup(result.text, "html.parser")
    
    def extract_position(self, input_string):
        pattern = r'^Position:\s.*\s\((.*)\).*'
        match = re.match(pattern, input_string)
        
        if match:
            return match.group(1)
        else:
            return None
    
    def dynamic_scrape_table(self, doc, table, stats, get_year):
        table = doc.find("table", id=table)
        if(table != None):
            table_body = table.find("tbody")
            rows = table_body.find_all("tr")
            row_count = 0
            stat_maping = {}
            for row in rows:
                col_count = 0
                year = row.find("th").text.strip()
                team_id = ""
                if("-" in year):
                    year = year.split("-")[0]
                
                if get_year is None or get_year == year:
                    if year not in stats:
                        stats[year] = {}

                    if (row.has_attr('id') and row["id"] == "stats"):
                        #Build Cols
                        cols = row.find_all("td")
                        for col in cols:
                            stat_maping[str(col_count)] = col['data-stat']
                            col_count+= 1              

                        #Get Data
                        col_count = 0
                        cols = row.find_all("td")

                        #Get Team
                        team = cols[1]
                        team_url = team.find("a")['href']
                        pattern = r'\/en\/squads\/([a-zA-Z0-9]*)\/.*'
                        match = re.match(pattern, team_url, re.IGNORECASE)

                        if match:
                            team_id = str(match.group(1))

                        if(team_id not in stats[year]):
                            stats[year][team_id] = {}

                        #Get League
                        if("league_name" not in stats[year][team_id]):
                            league = cols[3]
                            pattern = r'\/en\/comps\/([0-9]*)\/.*'
                            league_url = league.find("a")['href']
                            match = re.match(pattern, league_url, re.IGNORECASE)

                            if match:
                                league_id = str(match.group(1))

                            stats[year][team_id]["fbref_league_id"] = league_id

                        for col in cols:
                            if(str(col.text.strip()) != ""):
                                stats[year][team_id][stat_maping[str(col_count)]] = str(col.text.strip())
                            else:
                                stats[year][team_id][stat_maping[str(col_count)]] = "0"
                            col_count+= 1   
                    row_count += 1
            
        return stats

    def get_player_stats(self, player, year):
        if("fbref_player_id" not in player):
            return { "success" : 0, "res" : { "stats" : {} }, "error_string" : "Error: Player object did not include an fbref_player_id" }
        
        fbref_player_id = player["fbref_player_id"]
        if(not fbref_player_id):
            return { "success" : 0, "res" : { "stats" : {} }, "error_string" : "Error: Player object did not include an fbref_player_id" }
        
        endpoint = "https://fbref.com/en/players/" + fbref_player_id + "/player-name"
        doc = self.limiter.call(self.make_request, endpoint)
        stats = {}

        #Get Stats
        if(doc):
            #Get Position
            info = doc.find("div", id="info")
            if(info):
                info = info.find_all("p")
                for info_piece in info:
                    pos = info_piece.text.strip()
                    if("Position:" in pos):
                        stats["position"] = self.extract_position(pos)
                        if(stats["position"] == None):
                            stats["position"] = pos.split(" ")[1].split(" ▪")[0]

            if("position" not in stats):
                return { "success" : 0, "res" : { "stats" : {} }, "error_string" : "Error: Player could not be parsed" }
            
            tables = ["stats_keeper_adv_dom_lg", "stats_keeper_dom_lg", "stats_standard_dom_lg", "stats_shooting_dom_lg", "stats_passing_dom_lg", "stats_passing_types_dom_lg", "stats_defense_dom_lg", "stats_possession_dom_lg", "stats_playing_time_dom_lg", "stats_misc_dom_lg"]
            for table in tables:
                stats = self.dynamic_scrape_table(doc, table, stats, year)

            return { "success" : 1, "res" : { "stats" : stats }, "error_string" : "" }
        
        return { "success" : 0, "res" : { "stats" : stats }, "error_string" : "Error: Player page not found" }