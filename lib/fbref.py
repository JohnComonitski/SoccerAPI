from SoccerAPI.lib.ratelimiter import RateLimiter
from SoccerAPI.obj.statistic import Statistic
from bs4 import BeautifulSoup
import unicodedata
import requests
import re

class FBRef:
    def __init__(self, config={}):
        max_calls = 5
        if "rate_limit_max_calls" in config:
            max_calls = config["rate_limit_max_calls"]

        interval = 60
        if "rate_limit_call_interval" in config:
            interval = config["rate_limit_call_interval"]

        self.limiter = RateLimiter(max_calls=max_calls, interval=interval)

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
                            key = stat_maping[str(col_count)]
                            
                            stat_data = {
                                "key" : key
                            }
                            if(str(col.text.strip()) != ""):
                                stat_data["value"] = str(col.text.strip())
                            else:
                                stat_data["value"] = "0"
                            stat = Statistic(stat_data)

                            if stat.value:
                                stats[year][team_id][key] = stat
                            col_count+= 1   
                    row_count += 1
        return stats

    def dynamic_scrape_table_footer(self, doc, table, stats, opponent=0):
        table = doc.find('table', {'id': re.compile(table)})
        if(table != None):
            table_footer = table.find("tfoot")
            rows = table_footer.find_all("tr")
            
            idx = 0
            footer_row = None
            for row in rows:
                if(idx == opponent):
                    footer_row = row
                idx += 1

            if(footer_row):
                cols = footer_row.find_all("td")
                for col in cols:
                    key = col['data-stat']

                    stat_data = {
                        "key" : key
                    }

                    if(str(col.text.strip()) != ""):
                        stat_data["value"] = str(col.text.strip())
                    else:
                        stat_data["value"] = "0"
                    stat = Statistic(stat_data)

                    stats[key] = stat
        
        return stats

    def get_player_stats(self, player, year):
        if(not player.fbref_id ):
            return { "success" : 0, "res" : { "stats" : {} }, "error_string" : "Error: Player object did not include an fbref_player_id" }
        
        fbref_player_id = player.fbref_id
        
        endpoint = "https://fbref.com/en/players/" + fbref_player_id + "/player-name"
        doc = self.limiter.call(self.make_request, endpoint)
        stats = {}

        #Get Stats
        if(doc):
            if("Rate Limited Request (429 error)" in doc.text):
                return  { "success" : 0, "res" : {}, "error_string" : "Error: We've been temporarily blocked by FBRef" }
    
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

    def get_player_image_url(self, player):
        endpoint = 'https://fbref.com/en/players/' + player.fbref_id + "/name"
        doc = self.limiter.call(self.make_request, endpoint)
        if doc:
            if("Rate Limited Request (429 error)" in doc.text):
                return  { "success" : 0, "res" : {}, "error_string" : "Error: We've been temporarily blocked by FBRef" }
    
        return  { "success" : 1, "res" : doc.find('div', class_='media-item').find('img').attrs['src'], "error_string" : "" }

    def get_scouting_data(self, player):
        player_stat_topics = ['Standard Stats', 'Shooting', 'Passing', 'Pass Types', 'Goal and Shot Creation', 'Defense', 'Possession', 'Miscellaneous Stats', 'Goalkeeping', 'Advanced Goalkeeping']
        player_stat_keys_raw = []
        player_stat_values = []

        #Find Scouting Report
        version = "365_m2"
        endpoint = "https://fbref.com/en/players/" + player.fbref_id + "/scout/" + version + "/Name"
        doc = self.limiter.call(self.make_request, endpoint)
        
        if doc:
            if("Rate Limited Request (429 error)" in doc.text):
                return  { "success" : 0, "res" : {}, "error_string" : "Error: We've been temporarily blocked by FBRef" }
    
        bs_scout = doc.find('div', {'id': re.compile(r'div_scout_full_')})
        
        if( not bs_scout ):
            version = "365_m1"
            endpoint = "https://fbref.com/en/players/" + player.fbref_id + "/scout/" + version + "/Name"
            doc = self.limiter.call(self.make_request, endpoint)
            bs_scout = doc.find('div', {'id': re.compile(r'div_scout_full_')})

        if( not bs_scout ):
            return { "success" : 0, "res" : {}, "error_string" : "Error: Player's scouting report could not be found" }
        
        stat_tables_keys = bs_scout.find("table", {'id': re.compile(r'scout_full_')} ).find_all('tr')
        stat_tables_p90Percentile = bs_scout.find("table", {'id': re.compile(r'scout_full_')}).find_all('td')

        for list_th in stat_tables_keys:
            if list_th.find('th').get_text() != "":
                if list_th.find('th').get_text() != "Statistic":
                    th = list_th.find('th')
                    if(th):
                        pattern = r'.*\sdata-endpoint="\/en\/ajax\/glossary\.cgi\?html=1&amp;stat=([a-z1-9_]+)\".*'
                        match = re.match(pattern, str(th))
                        if match:
                            key = match.group(1)
                            player_stat_keys_raw.append(key)

        for list_tb_n in range(0, len(stat_tables_p90Percentile),2):
            list_tb = stat_tables_p90Percentile[list_tb_n]
            new_list = [list_tb.get_text()]
            new_list.append(unicodedata.normalize("NFKD",stat_tables_p90Percentile[list_tb_n+1].get_text(strip=True)))
            player_stat_values.append(new_list)
       
        for stat in player_stat_values:
            if "" in stat:
                player_stat_values.remove(stat)
        for stat in player_stat_keys_raw:
            if stat in player_stat_topics:
                player_stat_keys_raw.remove(stat)

        stats = {}
        for i in range(len(player_stat_keys_raw)):
            key = player_stat_keys_raw[i]
            stats[key] = Statistic({ "key" : key, "value" : player_stat_values[i][0], "percentile" : player_stat_values[i][1]})

        return { "success" : 1, "res" : { "scouting_report" : stats }, "error_string" : "" }
    
    def player_positions(self, player):
        endpoint = 'https://fbref.com/en/players/' + player.fbref_id + "/name"
        doc = self.limiter.call(self.make_request, endpoint)
        if doc:
            if("Rate Limited Request (429 error)" in doc.text):
                return  { "success" : 0, "res" : {}, "error_string" : "Error: We've been temporarily blocked by FBRef" }
    
            info_box = doc.find("div", id="meta")
            if info_box:
                elements = info_box.find_all("p")
                for element in elements:
                    if "Position:" in element.text:
                        return  { "success" : 1, "res" : element.text, "error_string" : "" }
            return  { "success" : 0, "res" : "", "error_string" : "Error: Failed to find player position" }
        return  { "success" : 0, "res" : "", "error_string" : "Error: Player could not be found" }
    
    def get_team_stats(self, team):
        if(not team.fbref_id ):
            return { "success" : 0, "res" : { "stats" : {} }, "error_string" : "Error: Team object did not include an fbref_team_id" }
        
        fbref_team_id = team.fbref_id
        
        endpoint = "https://fbref.com/en/squads/" + fbref_team_id + "/team-name"
        doc = self.limiter.call(self.make_request, endpoint)
        stats = {}

        #Get Stats
        if(doc):
            if("Rate Limited Request (429 error)" in doc.text):
                return  { "success" : 0, "res" : {}, "error_string" : "Error: We've been temporarily blocked by FBRef" }
            
            tables = ["stats_keeper", "stats_keeper", "stats_standard", "stats_shooting", "stats_passing", "stats_passing_types", "stats_defense", "stats_possession", "stats_playing_time", "stats_misc"]
            for table in tables:
                stats = self.dynamic_scrape_table_footer(doc, table, stats)

            return { "success" : 1, "res" : { "stats" : stats }, "error_string" : "" }

        return  { "success" : 0, "res" : {}, "error_string" : "Error: Team page not found" }
    
    def get_team_opposition_stats(self, team):
        if(not team.fbref_id ):
            return { "success" : 0, "res" : { "stats" : {} }, "error_string" : "Error: Team object did not include an fbref_team_id" }
        
        fbref_team_id = team.fbref_id
        
        endpoint = "https://fbref.com/en/squads/" + fbref_team_id + "/team-name"
        doc = self.limiter.call(self.make_request, endpoint)
        stats = {}

        #Get Stats
        if(doc):
            if("Rate Limited Request (429 error)" in doc.text):
                return  { "success" : 0, "res" : {}, "error_string" : "Error: We've been temporarily blocked by FBRef" }
            
            tables = ["stats_keeper", "stats_keeper", "stats_standard", "stats_shooting", "stats_passing", "stats_passing_types", "stats_defense", "stats_possession", "stats_playing_time", "stats_misc"]
            for table in tables:
                stats = self.dynamic_scrape_table_footer(doc, table, stats, opponent=1)

            return { "success" : 1, "res" : { "stats" : stats }, "error_string" : "" }

        return  { "success" : 0, "res" : {}, "error_string" : "Error: Team page not found" }