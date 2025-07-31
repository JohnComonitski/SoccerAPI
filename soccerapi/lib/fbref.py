from ..lib.ratelimiter import RateLimiter
from ..obj.statistic import Statistic
from ..lib.postgres import PostgreSQL
from datetime import datetime
from bs4 import BeautifulSoup
import unicodedata
import requests
import re

class FBRef:
    def __init__(self, config={}, db = None):
        max_calls = 5
        if "rate_limit_max_calls" in config:
            max_calls = config["rate_limit_max_calls"]

        interval = 60
        if "rate_limit_call_interval" in config:
            interval = config["rate_limit_call_interval"]

        self.limiter = RateLimiter(max_calls=max_calls, interval=interval)

        self.db = None
        if db is not None:
            self.db = db

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
    
    def dynamic_scrape_table(self, doc, table_id, context = {}):
        stats = {}
        table = doc.find("table", id=table_id)
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
                
                if year not in stats:
                    stats[year] = {}
                context["year"] = year

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

                    context["team"] = None
                    if match:
                        fbref_team_id = str(match.group(1))
                        context["team"] = fbref_team_id
                        if(self.db):
                            team = self.db.search("teams", { "fbref_id" : fbref_team_id })
                            if(len(team) > 0):
                                team_id = team[0].id
                            else:
                                team_id = fbref_team_id
                        else:
                            team_id = fbref_team_id

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
                            context["league"] = league_id   

                    for col in cols:
                        key = stat_maping[str(col_count)]
                        
                        stat_data = {
                            "key" : key,
                            "context" : context
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

    def dynamic_scrape_table_footer(self, doc, table, stats, context, opponent=0):
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
                        "key" : key,
                        "context" : context
                    }

                    if(str(col.text.strip()) != ""):
                        stat_data["value"] = str(col.text.strip())
                    else:
                        stat_data["value"] = "0"
                    stat = Statistic(stat_data)

                    stats[key] = stat
        
        return stats

    def sum_table_columns(self, doc, table_id, context):
        stats = {}
        table = doc.find("table", id=table_id)
        if(table != None):
            table_body = table.find("tbody")
            rows = table_body.find_all("tr")
            row_count = 1
            stat_maping = {}
            for row in rows:
                col_count = 0

                #Build Cols
                cols = row.find_all("td")
                for col in cols:
                    stat_maping[str(col_count)] = col['data-stat']
                    col_count+= 1              

                #Get Data
                col_count = 0
                cols = row.find_all("td")

                for col in cols:
                    key = stat_maping[str(col_count)]
                    start_value = 0
                    if key in stats:
                        start_value = stats[key].value

                    stat_data = {
                        "key" : key,
                        "context" : context
                    }
                    if(str(col.text.strip()) != ""):
                        val = col.text.strip()
                        val = val.replace(",", "")

                        if( "+" in val):
                            val = float(val.replace("+", ""))
                        elif( "-" in val):
                            val = -1 * float(val.replace("-", ""))

                        stat_data["value"] = float(val) + start_value
                    else:
                        stat_data["value"] = 0
                    stats[key] = Statistic(stat_data)

                    col_count+= 1   
                row_count += 1

        for stat in stats:
            if( "avg" in stat):
                stat_data = {}
                stat_data["key"] = stat
                stat_data["value"] = ( stats[stat].value / row_count )
                stats[stat] = Statistic(stat_data)
                #print(f"{stat}: {stats[stat].value}")
            elif( "per_game" in stat):
                stat_data = {}
                stat_data["key"] = stat
                stat_data["value"] = ( stats[stat].value / ((stats["games"].value)/2) )
                stats[stat] = Statistic(stat_data)
                #print(f"{stat}: {stats[stat].value}")
            elif( "pct" in stat):
                stat_data = {}
                stat_data["key"] = stat
                stat_data["value"] = ( stats[stat].value / ((row_count) * 100) )
                stats[stat] = Statistic(stat_data)
                #print(f"{stat}: {stats[stat].value}")
            elif( "per90" in stat):       
                #print(f"{stat}: {stats[stat].value}")
                pass

        return stats 

    def get_player_stats(self, player, year):
        context = { "object" : "player", "player" : player }
        if(not player.fbref_id ):
            return { "success" : 0, "res" : { "stats" : {} }, "error_string" : "Error: Player object did not include an fbref_id" }
        
        fbref_id = player.fbref_id
        
        endpoint = "https://fbref.com/en/players/" + fbref_id + "/player-name"
        doc = self.limiter.call(self.make_request, endpoint)
        stats = {}

        #Get Stats
        if(doc):
            if("Rate Limited Request (429 error)" in doc.text):
                return  { "success" : 0, "res" : {}, "error_string" : "Error: We've been temporarily blocked by FBRef" }

            tables = ["stats_keeper_adv_dom_lg", "stats_keeper_dom_lg", "stats_standard_dom_lg", "stats_shooting_dom_lg", "stats_passing_dom_lg", "stats_passing_types_dom_lg", "stats_defense_dom_lg", "stats_possession_dom_lg", "stats_playing_time_dom_lg", "stats_misc_dom_lg"]
            for table in tables:
                table_stats = self.dynamic_scrape_table(doc, table, context)

                for year in table_stats:
                    if year not in stats:
                        stats[year] = table_stats[year]
                    else:
                        new_stats = table_stats[year]
                        for team in new_stats:
                            if team not in stats[year]:
                                stats[year][team] = new_stats[team]
                            else:
                                for stat in new_stats[team]:
                                    stats[year][team][stat] = new_stats[team][stat]

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
    
    def get_team_stats(self, team, year):
        context = { "object" : "team", "team" : team }

        if(not team.fbref_id ):
            return { "success" : 0, "res" : { "stats" : {} }, "error_string" : "Error: Team object did not include an fbref_id" }
        
        fbref_id = team.fbref_id

        year_string = ""
        last_year = None
        if not year:
            current_date = datetime.now()
            year = str(current_date.year)
        last_year = int(year) - 1
        year_string = str(last_year) + "-" + str(year)

        context["year"] = year
        
        endpoint = "https://fbref.com/en/squads/"  + fbref_id + "/" +  year_string + "/team-name"
        doc = self.limiter.call(self.make_request, endpoint)
        stats = {}

        #Get Stats
        if(doc):
            if("Rate Limited Request (429 error)" in doc.text):
                return  { "success" : 0, "res" : {}, "error_string" : "Error: We've been temporarily blocked by FBRef" }
            
            tables = ["stats_keeper", "stats_keeper", "stats_standard", "stats_shooting", "stats_passing", "stats_passing_types", "stats_defense", "stats_possession", "stats_playing_time", "stats_misc"]
            for table in tables:
                stats = self.dynamic_scrape_table_footer(doc, table, stats, context)

            return { "success" : 1, "res" : { "stats" : stats }, "error_string" : "" }

        return  { "success" : 0, "res" : {}, "error_string" : "Error: Team page not found" }
    
    def get_team_opposition_stats(self, team, year):
        context = { "object" : "team", "team" : team }

        if(not team.fbref_id ):
            return { "success" : 0, "res" : { "stats" : {} }, "error_string" : "Error: Team object did not include an fbref_id" }
        
        fbref_id = team.fbref_id
        
        year_string = ""
        last_year = None
        if not year:
            current_date = datetime.now()
            year = str(current_date.year)
        last_year = int(year) - 1
        year_string = str(last_year) + "-" + str(year)
        
        context["year"] = year

        endpoint = "https://fbref.com/en/squads/"  + fbref_id + "/" +  year_string + "/team-name"
        doc = self.limiter.call(self.make_request, endpoint)
        stats = {}

        #Get Stats
        if(doc):
            if("Rate Limited Request (429 error)" in doc.text):
                return  { "success" : 0, "res" : {}, "error_string" : "Error: We've been temporarily blocked by FBRef" }
            
            tables = ["stats_keeper", "stats_keeper", "stats_standard", "stats_shooting", "stats_passing", "stats_passing_types", "stats_defense", "stats_possession", "stats_playing_time", "stats_misc"]
            for table in tables:
                stats = self.dynamic_scrape_table_footer(doc, table, stats, context, opponent=1)

            return { "success" : 1, "res" : { "stats" : stats }, "error_string" : "" }

        return  { "success" : 0, "res" : {}, "error_string" : "Error: Team page not found" }

    def get_league_stats(self, league, year):
        context = { "object" : "league", "league" : league }
        if(not league.fbref_id ):
            return { "success" : 0, "res" : { "stats" : {} }, "error_string" : "Error: League object did not include an fbref_id" }
        
        fbref_id = league.fbref_id

        year_string = ""
        last_year = None
        if not year:
            current_date = datetime.now()
            year = str(current_date.year)
        last_year = int(year) - 1
        year_string = str(last_year) + "-" + str(year)

        context["year"] = year
        
        endpoint = "https://fbref.com/en/comps/"  + fbref_id + "/" +  year_string + "/league-name"
        doc = self.limiter.call(self.make_request, endpoint)
        stats = {}

        #Get Stats
        if(doc):
            if("Rate Limited Request (429 error)" in doc.text):
                return  { "success" : 0, "res" : {}, "error_string" : "Error: We've been temporarily blocked by FBRef" }
            
            tables = [ "stats_squads_standard_for", "stats_squads_keeper_for", "stats_squads_keeper_adv_for", "stats_squads_shooting_for", "stats_squads_passing_for", "stats_squads_passing_types_for", "stats_squads_gca_for", "stats_squads_defense_for", "stats_squads_possession_against", "stats_squads_playing_time_for", "stats_squads_misc_for"]
            for table in tables:
                new_stats = self.sum_table_columns(doc, table, context)
                stats.update(new_stats)

            return { "success" : 1, "res" : { "stats" : stats }, "error_string" : "" }

        return  { "success" : 0, "res" : {}, "error_string" : "Error: League page not found" }
