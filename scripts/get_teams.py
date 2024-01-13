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

def update_team_ids(league, team):
    team_name = team["team_name"]

    google_search = 'https://www.google.com/search?q=' + team_name.replace(" ", "+") + "+transfermarkt+" + league.replace(" ", "+")
    doc = google_limiter.call(make_request, google_search)
    search_results = doc.find("div", id="search")
    if(not search_results):
        print("--- Google Rate Limit Fail ---")
        return -1

    search_results = search_results.find_all("div", class_ = 'MjjYud')
    if(search_results):
        if(len(search_results) > 0):
            team_url = search_results[0]
            team_url = team_url.find("a")
            if(team_url):
                team_url = team_url["href"]
                regex_pattern = r'https:\/\/www.transfermarkt\.us\/.*\/startseite\/verein\/([0-9]*)'
                match = re.match(regex_pattern, team_url)
                if match:
                    print("  --  " + team["team_name"] +  "'s TM ID was updated ")
                    api.db.update("teams", str(team["team_id"]), {"tm_team_id" : str(match.group(1))})

    google_search = 'https://www.google.com/search?q=' + team_name.replace(" ", "+") + "+fbref+" + league.replace(" ", "+")
    doc = google_limiter.call(make_request, google_search)
    search_results = doc.find("div", id="search")
    if(not search_results):
        print("--- Google Rate Limit Fail ---")
        return -1

    search_results = search_results.find_all("div", class_ = 'MjjYud')
    if(search_results):
        if(len(search_results) > 0):
            team_url = search_results[0]
            team_url = team_url.find("a")
            if(team_url):
                team_url = team_url["href"]
                regex_pattern = r'https:\/\/fbref\.com\/en\/squads\/([a-zA-Z0-9]*)\/.*'
                match = re.match(regex_pattern, team_url)
                if match:
                    print("  --  " + team["team_name"] +  "'s FBRef ID was updated ")
                    api.db.update("teams", str(team["team_id"]), {"fbref_team_id" : str(match.group(1))})

    return 1

db_leagues = api.db.get_all("leagues")

db_countries = api.db.get_all("countries")
countries = {}
for country in db_countries:
    countries[country["country"]] = country["country_code"]

print("Searching for new teams")
for league in db_leagues:

    teams = api.fapi.get_teams_in_league(league, year=None)
    if(teams["success"]):
        teams = teams["res"]

        for team in teams["teams"]:
            id = team['team']['id']
            name = team['team']['name']

            teams_search = api.db.search("teams", { "fapi_team_id" : id })
            if(len(teams_search) == 0):
                print("  Adding " + name + " in " + league["league_name"])

                country_code = ""
                if team['team']["country"] in countries:
                    country_code = countries[team['team']["country"]]

                api.db.create("teams",[{
                    "country_code" : country_code, 
                    "fapi_team_id" : id,
                    "team_name" : name
                }])
                db_team = api.db.search("teams", { "fapi_team_id" : id })[0]

                print("  Searching For " + db_team["team_name"] + " Foreign IDs")
                res = update_team_ids(league["league_name"], db_team)
                if( res < 0 ):
                    break