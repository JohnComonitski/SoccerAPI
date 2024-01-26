from SoccerAPI.soccerapi import SoccerAPI 
import pprint

pp = pprint.PrettyPrinter(indent=4)
pp = pprint.PrettyPrinter(width=41, compact=True)

api = SoccerAPI()
'''
# Getting a players value and stats
print("--------------TEST 1--------------")
Haaland = api.db.search("players", { "fapi_player_id" : "1100"})[0]
res = api.get_player_current_value_and_stats(Haaland)
pp.pprint(res)

# Getting the market values from a match
print("----Get Market Values from a Match----")
wolves = api.db.search("teams", { "fapi_team_id" : "39"})[0]
fixtures = api.fapi.get_team_fixtures_on_date(wolves, "2023-12-30")
if(fixtures["success"]):
    match = fixtures["res"]["matches"][0]["fixture"]["id"]
    lineups_with_values = api.get_line_up_value(match, team=None, include_subs=1)
    pp.pprint(lineups_with_values)

# Raw F-API request
print("----Search for Haaland Via Football API----")
res = api.fapi.make_request("/players", {
    "league": '39',
    "season": '2023',
    "search": 'Haaland'
})
pp.pprint(res)

# Get teams in league's values
print("----Get PL teams----")
pl = api.db.search("leagues", { "fapi_league_id" : "39"})[0]
res = api.get_teams_in_a_leagues_values(pl)
pp.pprint(res)
'''

print("----Get PL League Wide Stats----")
pl = api.db.search("leagues", { "fapi_league_id" : "39"})[0]
res = api.get_league_wide_player_stats(pl, save_results=False)
pp.pprint(res)

