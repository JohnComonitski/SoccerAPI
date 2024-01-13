from datetime import datetime

from bs4 import BeautifulSoup
import requests
import re
import sys
sys.path.append('../')

from soccerapi import SoccerAPI 
from lib.ratelimiter import RateLimiter
google_limiter = RateLimiter(max_calls=3, interval=10)

def make_request(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'}
    result = requests.get(url, headers=headers)
    return BeautifulSoup(result.text, "html.parser")

def update_league_ids(league):
    league_name = league["league_name"]

    google_search = 'https://www.google.com/search?q=' + league_name.replace(" ", "+") + "+transfermarkt"
    doc = google_limiter.call(make_request, google_search)
    search_results = doc.find("div", id="search")
    if(not search_results):
        print("--- Google Rate Limit Fail ---")
        return -1

    search_results = search_results.find_all("div", class_ = 'MjjYud')
    if(search_results):
        if(len(search_results) > 0):
            league_url = search_results[0]
            league_url = league_url.find("a")
            if(league_url):
                league_url = league_url["href"]
                regex_pattern = r'https:\/\/www.transfermarkt\.us\/.*\/startseite\/wettbewerb\/([a-zA-Z0-9]*)'
                match = re.match(regex_pattern, league_url)
                if match:
                    print("  --  " + league_name +  "'s TM ID was updated ")
                    api.db.update("leagues", str(league["league_id"]), {"tm_league_id" : str(match.group(1))})

    google_search = 'https://www.google.com/search?q=' + league_name.replace(" ", "+") + "+fbref"
    doc = google_limiter.call(make_request, google_search)
    search_results = doc.find("div", id="search")
    if(not search_results):
        print("--- Google Rate Limit Fail ---")
        return -1

    search_results = search_results.find_all("div", class_ = 'MjjYud')
    if(search_results):
        if(len(search_results) > 0):
            league_url = search_results[0]
            league_url = league_url.find("a")
            if(league_url):
                league_url = league_url["href"]
                regex_pattern = r'https:\/\/fbref\.com\/en\/comps\/([a-zA-Z0-9]*)\/.*'
                match = re.match(regex_pattern, league_url)
                if match:
                    print("  --  " + league_name +  "'s FBRef ID was updated ")
                    api.db.update("leagues", str(league["league_id"]), {"fbref_league_id" : str(match.group(1))})

    return 1

api = SoccerAPI()

db_countries = api.db.get_all("countries")

print("Searching for new leagues")
for country in db_countries:
    new_leauges = []

    leagues = api.fapi.make_request("/leagues", { "code": country["fapi_country_code"] })
    if(len(leagues["response"]) > 0):
        leagues = leagues["response"]
        
        for league in leagues:
            id = league['league']['id']
            name = league['league']['name']

            leagues_search = api.db.search("leagues", { "fapi_league_id" : id })
            if(len(leagues_search) == 0):
                print("  Adding " + name + " in " + country["country"])
                api.db.create("leagues",[{
                    "country_code" : country["country_code"], 
                    "fapi_league_id" : id,
                    "league_name" : name
                }])
                db_league = api.db.search("leagues", { "fapi_league_id" : id })[0]

                print("  Searching For " + db_league["league_name"] + " Foreign IDs")
                res = update_league_ids(db_league)
                if( res < 0 ):
                    break