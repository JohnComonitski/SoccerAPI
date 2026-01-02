from ..lib.ratelimiter import RateLimiter
from ..obj.statistic import Statistic
from ..lib.utils import key_to_name

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

    def query_for_stats(self, db, obj_type, obj_id, opposition=False):
        query = f"SELECT * FROM statistics WHERE obj_type = '{obj_type}' AND obj_id = '{obj_id}'"
        if opposition:
            query += " AND is_opposition = true"
        raw_stats = db.raw_query(query)

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

    def get_player_stats(self, db, player):
        if(not player.fbref_id ):
            return { "success" : 0, "res" : { "stats" : {} }, "error_string" : "Error: Player object did not include an fbref_id" }

        stats = self.query_for_stats(db, "player", player.id)
        return { "success" : 1, "res" : { "stats" : stats }, "error_string" : "" }

    def get_team_stats(self, db, team):
        if(not team.fbref_id ):
            return { "success" : 0, "res" : { "stats" : {} }, "error_string" : "Error: Team object did not include an fbref_id" }
        
        stats = self.query_for_stats(db, "team", team.id)
        return { "success" : 1, "res" : { "stats" : stats }, "error_string" : "" }
    
    def get_team_opposition_stats(self, db, team):
        if(not team.fbref_id ):
            return { "success" : 0, "res" : { "stats" : {} }, "error_string" : "Error: Team object did not include an fbref_id" }
        
        stats = self.query_for_stats(db, "team", team.id, True)
        return { "success" : 1, "res" : { "stats" : stats }, "error_string" : "" }

    def get_league_stats(self, db, league):
        if(not league.fbref_id ):
            return { "success" : 0, "res" : { "stats" : {} }, "error_string" : "Error: League object did not include an fbref_id" }
        
        stats = self.query_for_stats(db, "league", league.id)
        return { "success" : 1, "res" : { "stats" : stats }, "error_string" : "" }