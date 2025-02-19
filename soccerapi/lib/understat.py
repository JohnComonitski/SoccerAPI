from ..obj.statistic import Statistic
from datetime import datetime
from bs4 import BeautifulSoup
import json
import requests
import re

class Understat:
    def __init__(self):
        pass

    def make_request(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'}
        result = requests.get(url, headers=headers)
        return BeautifulSoup(result.text, "html.parser")

    def scrape_player_page(self, player, index):
        end_point = "https://understat.com/player/"
        page = self.make_request(end_point + player.understat_id)

        if(page):
            scripts = page.find_all('script')   
            if(len(scripts) > 0):
                #Script Data
                data = scripts[index].text
                ind_start = data.index("('")+2 
                ind_end = data.index("')") 
                json_data = data[ind_start:ind_end] 
                json_data = json_data.encode('utf8').decode('unicode_escape')

                return { "success" : 1, "res" : json.loads(json_data), "error_string" : "" }
        return { "success" : 0, "res" : {}, "error_string" : "Player page could not be found" }

    def get_player_shoting_statistics(self, player):
        return self.scrape_player_page(player, 1)

    def get_player_shots(self, player):
        return self.scrape_player_page(player, 3)

    def analyze_shot_data(self, data):
        goals = 0
        xG = 0
        x_points = 0
        x_points_actual = 0
        for shot in data:
            x_points += float(shot["X"]) * 100
            x_points_actual += ( float(shot["X"]) * 100) * 1.2
            xG += float(shot["xG"])
            if(shot["result"] == "Goal"):
                goals += 1

        return {
            "success" : 1,
            "res" : {
                "shots" : Statistic({ "key" : "shots", "value": len(data)}),
                "goals" : Statistic({ "key" : "goals", "value": goals}),
                "xg" : Statistic({ "key" : "goals", "value": xG}),
                "xg_per_shot" : Statistic({ "key" : "xg", "value": (xG / len(data))}),
                "avg_shot_distance" : Statistic( { "key" : "avg_shot_distance", "value" : ( x_points_actual /len(data)) }),
                "avg_actual_shot_distance" : Statistic({ "key" : "avg_actual_shot_distance", "value" : 120 - (x_points_actual /len(data) ) })
            },
            "error_string" : ""
        }
