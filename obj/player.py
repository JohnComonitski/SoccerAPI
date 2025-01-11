from datetime import datetime
from SoccerAPI.obj.statistic import Statistic

class Player:
    def __init__(self, player_data, db):
        #From Player Data
        self.first_name = player_data["first_name"]
        self.last_name = player_data["last_name"]
        self.id = player_data["player_id"]
        self.fbref_id = player_data["fbref_player_id"]
        self.tm_id = player_data["tm_player_id"]
        self.fapi_id = player_data["fapi_player_id"]
        self.understat_id = player_data["understat_player_id"]
        #Cached Data
        self.fapi_profile = None
        self.player_country = None
        self.team = None
        self.stats_cache = {}
        #Packages
        self.db = db 
        app = db.app
        self.debug = app["debug"]
        self.fapi = app["fapi"]
        self.tm = app["tm"]
        self.fbref = app["fbref"]
        self.understat = app["understat"]
        self.visualize = app["visualize"]
    
    def __str__(self):
        return f"Player({self.name()})"
    
    def __repr__(self):
        return f"Player({self.name()})"

    def __stat_key_to_name(self, key):
        mapping = {
            'aerials_lost': 'Aerials Lost',
            'aerials_won': 'Aerials Won',
            'aerials_won_pct': 'Aerials Won Pct',
            'assisted_shots': 'Key Passes',
            'assists': 'Assists',
            'assists_per90': 'Assists Per 90',
            'average_shot_distance': 'Avg Shot Distance',
            'ball_recoveries': 'Ball Recoveries',
            'blocked_passes': 'Blocked Passes',
            'blocked_shots': 'Blocked Shots',
            'blocks': 'Blocks',
            'cards_red': 'Red Cards',
            'cards_yellow': 'Yellow Cards',
            'cards_yellow_red': 'Cards',
            'carries': 'Carries',
            'carries_distance': 'Carries Distance',
            'carries_into_final_third': 'Carries Into Final 3rd',
            'carries_into_penalty_area': 'Carries Into Penalty Area',
            'carries_progressive_distance': 'Progressive Carry Distance',
            'challenge_tackles': 'Tackles Challenged',
            'challenge_tackles_pct': 'Tackles Challenged Pct',
            'challenges': 'Challenges',
            'challenges_lost': 'Challenges Lost',
            'clearances': 'Clearances',
            'corner_kicks': 'Corner Kicks',
            'corner_kicks_in': 'Corner Kicks In',
            'corner_kicks_out': 'Corner Kicks Out',
            'corner_kicks_straight': 'Corner Kicks Straight',
            'crosses': 'Crosses',
            'crosses_into_penalty_area': 'Crosses Into Penalty Area',
            'dispossessed': 'Dispossessed',
            'errors': 'Errors',
            'fouled': 'Fouled',
            'fouls': 'Fouls',
            'games': 'Matches',
            'games_complete': 'Matches Complete',
            'games_starts': 'Matches Started',
            'games_subs': 'Matches Substituted',
            'goals': 'Goals',
            'goals_assists': 'Goals Plus Assists',
            'goals_assists_pens_per90': 'Non-Penalty Goals Plus Assists per 90',
            'goals_assists_per90': 'Goals Plus Assists Per 90',
            'goals_pens': 'Non-Penalty Goals',
            'goals_pens_per90': 'Non-Penalty Goals per 90',
            'goals_per90': 'Goals Per 90',
            'goals_per_shot': 'Goals Per Shot',
            'goals_per_shot_on_target': 'Goals Per Shot on Targer',
            'interceptions': 'Interceptions',
            'minutes': 'Minutes',
            'minutes_90s': 'Minutes Per 90',
            'minutes_pct': 'Minutes Pct',
            'minutes_per_game': 'Minutes Per Game',
            'minutes_per_start': 'Minutes Per Start',
            'minutes_per_sub': 'Minuites Per Sub',
            'miscontrols': 'Misscontrols',
            'npxg': 'Non-Penalty xG',
            'npxg_net': 'Net Non-Penalty xG',
            'npxg_per90': 'Non-Penalty xG per 90',
            'npxg_per_shot': 'Non-Penalty xG per Shot',
            'npxg_xg_assist': 'Non-Penalty xGA',
            'npxg_xg_assist_per90': 'Non-Penalty xGA per 90',
            'offsides': 'Offsides',
            'on_goals_against': 'On-Field Goals Against',
            'on_goals_for': 'On-Field Goals For',
            'on_xg_against': 'On-Field xGA',
            'on_xg_for': 'On-Field xG',
            'own_goals': 'Own Goals',
            'pass_xa': 'Expected Assists',
            'passes': 'Passes',
            'passes_blocked': 'Passes Blocked',
            'passes_completed': 'Passes Completed',
            'passes_completed_long': 'Long Passes Completed',
            'passes_completed_medium': 'Medium Passes Completed',
            'passes_completed_short': 'Short Passes Completed',
            'passes_dead': 'Dead Ball Passes',
            'passes_free_kicks': 'Passes From Free Kicks',
            'passes_into_final_third': 'Passes Into Final Third',
            'passes_into_penalty_area': 'Passes Into Penalty Area',
            'passes_live': 'Live Ball Passes',
            'passes_long': 'Long Passes',
            'passes_medium': 'Medium Passes',
            'passes_offsides': 'Passes Offside',
            'passes_pct': 'Passing',
            'passes_pct_long': 'Long Pass Completion Pct',
            'passes_pct_medium': 'Medium Pass Completion Pct',
            'passes_pct_short': 'Short Pass Completion Pct',
            'passes_progressive_distance': 'Progressive Passes Distance',
            'passes_received': 'Passes Recieved',
            'passes_short': 'Short Passes',
            'passes_switches': 'Switches',
            'passes_total_distance': 'Total Passing Distance',
            'pens_att': 'Penalties Attempted',
            'pens_conceded': 'Penalties Conceeded',
            'pens_made': 'Penalties Made',
            'pens_won': 'Penalties Won',
            'progressive_carries': 'Progressive Carries',
            'progressive_passes': 'Progressive Passes',
            'progressive_passes_received': 'Progressive Passes Received',
            'shots': 'Shots',
            'shots_free_kicks': 'Shots From Freekicks',
            'shots_on_target': 'Shots On Targer',
            'shots_on_target_pct': 'Shots On Target Pct',
            'shots_on_target_per90': 'Shots On Target Per 90',
            'shots_per90': 'Shots Per 90',
            'tackles': 'Tackes',
            'tackles_att_3rd': 'Tackes in the Attacking 3rd',
            'tackles_def_3rd': 'Tackes in the Defensive 3rd',
            'tackles_interceptions': 'Tackles & Interceptions',
            'tackles_mid_3rd': 'Tackes in the Middle 3rd',
            'tackles_won': 'Tackles Won',
            'take_ons': 'Take Ons',
            'take_ons_tackled': 'Take Ons Tackled',
            'take_ons_tackled_pct': 'Take Ons Tackled Pct',
            'take_ons_won': 'Take Ons Won',
            'take_ons_won_pct': 'Take Ons Won Pct',
            'through_balls': 'Through Balls',
            'throw_ins': 'Throw Ins',
            'touches': 'Touches',
            'touches_att_3rd': 'Touches in the Attacking 3rd',
            'touches_att_pen_area': 'Touches in the Penalty Area',
            'touches_def_3rd': 'Touches in the Defensive 3rd',
            'touches_def_pen_area': 'Touches in the Defensive Penalty Area',
            'touches_live_ball': 'Live Ball Touches',
            'touches_mid_3rd': 'Touches in the Middle 3rd',
            'unused_subs': 'Unused as Sub',
            'xg': 'xG',
            'xg_assist': 'xGA',
            'xg_assist_net': 'Net xGA',
            'xg_assist_per90': 'xGA Per 90',
            'xg_net': 'Net xG',
            'xg_per90': 'xG Per 90',
            'xg_xg_assist_per90': 'xG + xAG/90'
        }

        if key in mapping:
            return mapping[key]
        else:
            return None
        
    def __stat_name_to_key(self, name):
        mapping = {
            'Aerials Lost': 'aerials_lost',
            'Aerials Won': 'aerials_won',
            'Aerials Won Pct': 'aerials_won_pct',
            'Key Passes': 'assisted_shots',
            'Assists': 'assists',
            'Assists Per 90': 'assists_per90',
            'Avg Shot Distance': 'average_shot_distance',
            'Ball Recoveries': 'ball_recoveries',
            'Blocked Passes': 'blocked_passes',
            'Blocked Shots': 'blocked_shots',
            'Blocks': 'blocks',
            'Red Cards': 'cards_red',
            'Yellow Cards': 'cards_yellow',
            'Cards': 'cards_yellow_red',
            'Carries': 'carries',
            'Carries Distance': 'carries_distance',
            'Carries Into Final 3rd': 'carries_into_final_third',
            'Carries Into Penalty Area': 'carries_into_penalty_area',
            'Progressive Carry Distance': 'carries_progressive_distance',
            'Tackles Challenged': 'challenge_tackles',
            'Tackles Challenged Pct': 'challenge_tackles_pct',
            'Challenges': 'challenges',
            'Challenges Lost': 'challenges_lost',
            'Clearances': 'clearances',
            'Corner Kicks': 'corner_kicks',
            'Corner Kicks In': 'corner_kicks_in',
            'Corner Kicks Out': 'corner_kicks_out',
            'Corner Kicks Straight': 'corner_kicks_straight',
            'Crosses': 'crosses',
            'Crosses Into Penalty Area': 'crosses_into_penalty_area',
            'Dispossessed': 'dispossessed',
            'Errors': 'errors',
            'Fouled': 'fouled',
            'Fouls': 'fouls',
            'Matches': 'games',
            'Matches Complete': 'games_complete',
            'Matches Started': 'games_starts',
            'Matches Substituted': 'games_subs',
            'Goals': 'goals',
            'Goals Plus Assists': 'goals_assists',
            'Non-Penalty Goals Plus Assists per 90': 'goals_assists_pens_per90',
            'Goals Plus Assists Per 90': 'goals_assists_per90',
            'Non-Penalty Goals': 'goals_pens',
            'Non-Penalty Goals per 90': 'goals_pens_per90',
            'Goals Per 90': 'goals_per90',
            'Goals Per Shot': 'goals_per_shot',
            'Goals Per Shot on Targer': 'goals_per_shot_on_target',
            'Interceptions': 'interceptions',
            'Minutes': 'minutes',
            'Minutes Per 90': 'minutes_90s',
            'Minutes Pct': 'minutes_pct',
            'Minutes Per Game': 'minutes_per_game',
            'Minutes Per Start': 'minutes_per_start',
            'Minuites Per Sub': 'minutes_per_sub',
            'Misscontrols': 'miscontrols',
            'Non-Penalty xG': 'npxg',
            'Net Non-Penalty xG': 'npxg_net',
            'Non-Penalty xG per 90': 'npxg_per90',
            'Non-Penalty xG per Shot': 'npxg_per_shot',
            'Non-Penalty xGA': 'npxg_xg_assist',
            'Non-Penalty xGA per 90': 'npxg_xg_assist_per90',
            'Offsides': 'offsides',
            'On-Field Goals Against': 'on_goals_against',
            'On-Field Goals For': 'on_goals_for',
            'On-Field xGA': 'on_xg_against',
            'On-Field xG': 'on_xg_for',
            'Own Goals': 'own_goals',
            'Expected Assists': 'pass_xa',
            'Passes': 'passes',
            'Passes Blocked': 'passes_blocked',
            'Passes Completed': 'passes_completed',
            'Long Passes Completed': 'passes_completed_long',
            'Medium Passes Completed': 'passes_completed_medium',
            'Short Passes Completed': 'passes_completed_short',
            'Dead Ball Passes': 'passes_dead',
            'Passes From Free Kicks': 'passes_free_kicks',
            'Passes Into Final Third': 'passes_into_final_third',
            'Passes Into Penalty Area': 'passes_into_penalty_area',
            'Live Ball Passes': 'passes_live',
            'Long Passes': 'passes_long',
            'Medium Passes': 'passes_medium',
            'Passes Offside': 'passes_offsides',
            'Passing': 'passes_pct',
            'Long Pass Completion Pct': 'passes_pct_long',
            'Medium Pass Completion Pct': 'passes_pct_medium',
            'Short Pass Completion Pct': 'passes_pct_short',
            'Progressive Passes Distance': 'passes_progressive_distance',
            'Passes Recieved': 'passes_received',
            'Short Passes': 'passes_short',
            'Switches': 'passes_switches',
            'Total Passing Distance': 'passes_total_distance',
            'Penalties Attempted': 'pens_att',
            'Penalties Conceeded': 'pens_conceded',
            'Penalties Made': 'pens_made',
            'Penalties Won': 'pens_won',
            'Progressive Carries': 'progressive_carries',
            'Progressive Passes': 'progressive_passes',
            'Progressive Passes Received': 'progressive_passes_received',
            'Shots': 'shots',
            'Shots From Freekicks': 'shots_free_kicks',
            'Shots On Targer': 'shots_on_target',
            'Shots On Target Pct': 'shots_on_target_pct',
            'Shots On Target Per 90': 'shots_on_target_per90',
            'Shots Per 90': 'shots_per90',
            'Tackes': 'tackles',
            'Tackes in the Attacking 3rd': 'tackles_att_3rd',
            'Tackes in the Defensive 3rd': 'tackles_def_3rd',
            'Tackles & Interceptions': 'tackles_interceptions',
            'Tackes in the Middle 3rd': 'tackles_mid_3rd',
            'Tackles Won': 'tackles_won',
            'Take Ons': 'take_ons',
            'Take Ons Tackled': 'take_ons_tackled',
            'Take Ons Tackled Pct': 'take_ons_tackled_pct',
            'Take Ons Won': 'take_ons_won',
            'Take Ons Won Pct': 'take_ons_won_pct',
            'Through Balls': 'through_balls',
            'Throw Ins': 'throw_ins',
            'Touches': 'touches',
            'Touches in the Attacking 3rd': 'touches_att_3rd',
            'Touches in the Penalty Area': 'touches_att_pen_area',
            'Touches in the Defensive 3rd': 'touches_def_3rd',
            'Touches in the Defensive Penalty Area': 'touches_def_pen_area',
            'Live Ball Touches': 'touches_live_ball',
            'Touches in the Middle 3rd': 'touches_mid_3rd',
            'Unused as Sub': 'unused_subs',
            'xG': 'xg',
            'xGA': 'xg_assist',
            'Net xGA': 'xg_assist_net',
            'xGA Per 90': 'xg_assist_per90',
            'Net xG': 'xg_net',
            'xG Per 90': 'xg_per90',
            'xG + xAG/90': 'xg_xg_assist_per90'
        }

        if name in mapping:
            return mapping[name]
        else:
            return None

    def name(self):
        return self.first_name + " " + self.last_name
    
    def profile(self):
        if self.fapi_profile:
            return self.fapi_profile
        else:
            player = self.fapi.make_request("/players/profiles?player=" + self.fapi_id, {})
            if(len(player["response"]) > 0):
                self.fapi_profile = player["response"][0]["player"]
                return self.fapi_profile 
        return None
    
    def positions(self):
        position_list = ["FB", "CB", "AM", "MF", "FW", "DM", "WM", "GK", "CM", "DF" ]
        
        res = self.fbref.player_positions(self)
        if(res["success"]):
            positions = []
            for position in position_list:
                if position in res["res"]:
                    positions.append(position)
            
            return positions
        else:
            if( self.debug ):
                print(res["error_string"])
            return []

    def country(self):
        if self.player_country:
            return self.player_country
        else:
            profile = self.profile()
            fapi_country = profile["nationality"]
            country = self.fapi.make_request("/countries?name=" + fapi_country, {})
            country_code = country["response"][0]["code"]
            res = self.db.search("countries", { "fapi_country_code" : country_code })
            if(len(res) > 0):
                self.player_country = res[0]["country_code"]
            return self.player_country
    
    def current_team(self):
        if self.team:
            return self.team
        else:
            fapi_player = self.fapi.make_request("/players/teams?player=" + self.fapi_id, {})
            if(fapi_player["response"][0]):
                fapi_team_id = fapi_player["response"][0]["team"]["id"]
                db_team = self.db.search("teams", { "fapi_team_id" : fapi_team_id })
                if(len(db_team)):
                    self.team = db_team[0]
            return self.team

    def market_value(self, year = None):
        if(year):
            res = self.tm.get_player_value_by_year(self, year)
        else:
            res = self.tm.get_player_value(self)

        if(res["success"]):
            return res["res"]["market_value"]
        else:
            if( self.debug ):
                print(res["error_string"])
            return 0

    def statistics(self, year = None):
        stats = self.stats_cache

        if not year:
            current_date = datetime.now()
            if 1 <= current_date.month <= 6:
                previous_year = current_date.year - 1
                year = str(previous_year)
            else:
                year = str(current_date.year)

        if year in stats:
            return stats[year]

        res = self.fbref.get_player_stats(self, year)
        if(res["success"]):
            fbref_team_id = list(res["res"]["stats"][year].keys())[0]
            stats[year] = res["res"]["stats"][year][fbref_team_id]
        else:
            if(self.debug):
                print(res["error_string"])
            stats[year] = {}
        self.stats_cache = stats

        return self.stats_cache[year]

    def stat(self, stat, year = None):
        stat_key = None
        if(self.__stat_key_to_name(stat)):
            stat_key = stat
        elif(self.__stat_name_to_key(stat)):
            stat_key = self.__stat_name_to_key(stat)

        stats = self.stats(year)
        if stat_key and stat_key in stats:
            return stats[stat_key]
        return 0

    def fbref_image(self):
        res = self.fbref.get_player_image_url(self)

        if(res["success"]):
            return res["res"]
        else:
            if( self.debug ):
                print(res["error_string"])
            return 0

    def image(self):
        if not self.fapi_profile:
            return self.profile()['photo']
        else:
            return self.fapi_profile['photo']

    def scouting_data(self):
        res = self.fbref.get_scouting_data(self)
        
        if(res["success"]):
            return res["res"]["scouting_report"]
        else:
            if( self.debug ):
                print(res["error_string"])
            return 0

    def pizza_plot(self, columns = None):
        res = self.visualize.player_pizza_plot(self, columns)
        
        if(not res["success"]):
            if( self.debug ):
                print(res["error_string"])
        return

    def shots_over_season(self):
        res = self.understat.get_player_shots(self)
        
        if(res["success"]):
            return res["res"]
        else:
            if( self.debug ):
                print(res["error_string"])
            return []

    def analyze_shots(self, shots):
        res = self.understat.analyze_shot_data(shots)
        
        if(res["success"]):
            return res["res"]
        else:
            if( self.debug ):
                print(res["error_string"])
            return {
                "shots" : Statistic({ "key" : "shots", "value": 0}),
                "goals" : Statistic({ "key" : "goals", "value": 0}),
                "xg" : Statistic({ "key" : "goals", "value": 0}),
                "xg_per_shot" : Statistic({ "key" : "xg", "value": 0}),
                "average_shot_distance" : Statistic( { "key" : "average_shot_distance", "value" : 0 }),
                "avg_actual_shot_distance" : Statistic({ "key" : "avg_actual_shot_distance", "value" : 0 })
            }    

    def shot_map(self):
        res = self.visualize.player_shot_map(self)
        
        if(not res["success"]):
            if( self.debug ):
                print(res["error_string"])
        return
