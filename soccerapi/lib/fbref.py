from ..lib.ratelimiter import RateLimiter
from ..obj.statistic import Statistic
from ..lib.utils import key_to_name
import requests
import json

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

    def make_request(self, obj_type, obj_id):
        endpoint = f"https://3juig81jql.execute-api.us-west-2.amazonaws.com/v1/soccerapi/statistics?object_type={obj_type}&id={obj_id}"
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'}
        res = requests.get(endpoint, headers=headers)

        return json.loads(res.text)

    def query_for_stats(self, obj_type, obj_id, opp=False):
        raw_stats = self.make_request(obj_type, obj_id)
        
        tmp_stats = []
        if obj_type == "team":
            for stat in raw_stats:
                if opp:
                    if stat["is_opposition"] == True:
                        tmp_stats.append(stat)
                else:
                    if stat["is_opposition"] != True:
                        tmp_stats.append(stat)
        raw_stats = tmp_stats

        stats = {}
        context = { "object" : obj_type }
        context[obj_type] = obj_id

        if(obj_id == "player"):
            context["player"] = obj_id
            for stat in raw_stats:
                if "age" in stat and "age" not in context:
                    context["age"] = stat["age"]
                
        for stat in raw_stats:
            year = str(stat["year"])
            context["year"] = year
            if year not in stats:
                stats[year] = {}

            if obj_type == "player":
                team = stat["team_id"]
                context["team"] = team
                context["league"] = stat["league_id"]

                if team not in stats:
                    stats[year][team] = {}

            for key in stat:
                if key_to_name(key):
                    stat_data = {
                        "key" : key,
                        "context" : context
                    }
                    val = stat[key]
                    if( "float" in str(type(val)) or "int" in str(type(val))):
                        val = str(stat[key])

                    if(val is not None and str(val.strip()) != ""):
                        stat_data["value"] = str(val.strip())
                    else:
                        stat_data["value"] = "0"
                
                    if obj_type == "player":
                        stats[year][team][key] = Statistic(stat_data)
                    else:
                        stats[year][key] = Statistic(stat_data)

        return stats

    def get_stats(self, obj, opp=False):
        obj_type = obj.table[0:-1]
        obj_title = obj_type.capitalize()

        if(not obj.fbref_id ):
            return { "success" : 0, "res" : { "stats" : {} }, "error_string" : f"Error: {obj_title} object did not include an fbref_id" }

        stats = self.query_for_stats(obj_type, obj.id, opp)
        return { "success" : 1, "res" : { "stats" : stats }, "error_string" : "" }