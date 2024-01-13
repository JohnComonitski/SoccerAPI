from bs4 import BeautifulSoup
from datetime import datetime
import requests
import re
import sys
sys.path.append('../')

from soccerapi import SoccerAPI 
from lib.ratelimiter import RateLimiter

api = SoccerAPI()
google_limiter = RateLimiter(max_calls=3, interval=10)

def make_request(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'}
    result = requests.get(url, headers=headers)
    return BeautifulSoup(result.text, "html.parser")

def update_player_ids(team, player):
    player_name = player["first_name"] + " " + player["last_name"]

    google_search = 'https://www.google.com/search?q=' + player_name.replace(" ", "+") + "+transfermarkt+Player+Profile+" + team.replace(" ", "+")
    doc = google_limiter.call(make_request, google_search)
    search_results = doc.find("div", id="search")
    if(not search_results):
        print("--- Google Rate Limit Fail ---")
        return -1

    search_results = search_results.find_all("div", class_ = 'MjjYud')
    if(search_results):
        if(len(search_results) > 0):
            player_url = search_results[0]
            player_url = player_url.find("a")
            if(player_url):
                player_url = player_url["href"]
                regex_pattern = r'https:\/\/www.transfermarkt\.us\/.*\/profil\/spieler\/([0-9]*)'
                match = re.match(regex_pattern, player_url)
                if match:
                    print("  --  " + player["last_name"] +  "'s TM ID was updated ")
                    api.db.update("players", str(player["player_id"]), {"tm_player_id" : str(match.group(1))})

    google_search = 'https://www.google.com/search?q=' + player_name.replace(" ", "+") + "+fbref+" + team.replace(" ", "+")
    doc = google_limiter.call(make_request, google_search)
    search_results = doc.find("div", id="search")
    if(not search_results):
        print("--- Google Rate Limit Fail ---")
        return -1

    search_results = search_results.find_all("div", class_ = 'MjjYud')
    if(search_results):
        if(len(search_results) > 0):
            player_url = search_results[0]
            player_url = player_url.find("a")
            if(player_url):
                player_url = player_url["href"]
                regex_pattern = r'https:\/\/fbref\.com\/en\/players\/([a-zA-Z0-9]*)\/.*'
                match = re.match(regex_pattern, player_url)
                if match:
                    print("  --  " + player["last_name"] +  "'s FBRef ID was updated ")
                    api.db.update("players", str(player["player_id"]), {"fbref_player_id" : str(match.group(1))})

    return 1

db_teams = api.db.get_all("teams")

year = ""
current_date = datetime.now()
if 1 <= current_date.month <= 6:
    previous_year = current_date.year - 1
    year = str(previous_year)
else:
    year = str(current_date.year)

print("Searching for new players")
for team in db_teams:

    squad = api.fapi.get_players_on_team(team)
    if(squad["success"]):
        squad = squad["res"]["players"][0]["players"]

        for player in squad:
            id = player['id']
            players_search = api.db.search("players", { "fapi_player_id" : id })
            if(len(players_search) == 0):

                fapi_player = api.fapi.make_request("/players", { "id" : id, "season" : year })
                if(len(fapi_player["response"]) > 0):
                    fapi_player = fapi_player["response"][0]['player']

                    print("  Adding " + player["name"] + " on " + team["team_name"])
                    api.db.create("players",[{
                            "fapi_player_id" : id,
                            "first_name" : fapi_player["firstname"],
                            "last_name" : fapi_player["lastname"],
                        }]
                    )
                    db_player = api.db.search("players", { "fapi_player_id" : id })[0]

                    print("  Searching For " + db_player["last_name"] + " Foreign IDs")
                    res = update_player_ids(team["team_name"], db_player)
                    if( res < 0 ):
                        break

