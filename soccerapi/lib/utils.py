import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def traverse_dict(d, parent_key=""):
    new_dict = {}
    for key, value in d.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        if isinstance(value, list):
            new_dict[key] = [ val.to_json() for val in value ]
        elif isinstance(value, dict):
            # Recursively process nested dictionary
            new_dict[key] = traverse_dict(value, full_key)
        elif( str(type(value)) == "<class 'SoccerAPI.soccerapi.obj.statistic.Statistic'>" ):
            new_dict[key] = value.to_json()
        elif( str(type(value)) == "<class 'SoccerAPI.soccerapi.obj.player.Player'>" ):
            new_dict[key] = value.to_json()
        elif( str(type(value)) == "<class 'SoccerAPI.soccerapi.obj.team.Team'>" ):
            new_dict[key] = value.to_json()
        elif( str(type(value)) == "<class 'SoccerAPI.soccerapi.obj.league.League'>" ):
            new_dict[key] = value.to_json()
        elif( str(type(value)) == "<class 'SoccerAPI.soccerapi.obj.fixture.Fixture'>" ):
            new_dict[key] = value.to_json()
        else:
            # Directly copy other values
            new_dict[key] = value
    return new_dict

def key_to_name(key):
    mapping = {
        'aerials_lost': 'Aerials Lost',
        'aerials_won': 'Aerials Won',
        'aerials_won_pct': 'Aerials Won Pct',
        'assisted_shots': 'Key Passes',
        'assists': 'Assists',
        'assists_per90': 'Assists Per 90',
        'avg_shot_distance': 'Avg Shot Distance',
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
        'goals_per_shot_on_target': 'Goals Per Shot on Target',
        'interceptions': 'Interceptions',
        'minutes': 'Minutes',
        'minutes_90s': 'Minutes Per 90',
        'minutes_pct': 'Minutes Pct',
        'minutes_per_game': 'Minutes Per Game',
        'minutes_per_start': 'Minutes Per Start',
        'minutes_per_sub': 'Minuites Per Sub',
        'miscontrols': 'Miscontrols',
        'npxg': 'Non-Penalty xG',
        'npxg_net': 'Net Non-Penalty xG',
        'npxg_per90': 'Non-Penalty xG per 90',
        'xg_per_shot': 'xG per Shot',
        'avg_actual_shot_distance' : "Average Actual Shot Distanct",
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
        'passes_pct': 'Passing Compltion Pct',
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
        'shots_on_target': 'Shots On Target',
        'shots_on_target_pct': 'Shots On Target Pct',
        'shots_on_target_per90': 'Shots On Target Per 90',
        'shots_per90': 'Shots Per 90',
        'tackles': 'Tackles',
        'tackles_att_3rd': 'Tackles in the Attacking 3rd',
        'tackles_def_3rd': 'Tackles in the Defensive 3rd',
        'tackles_interceptions': 'Tackles & Interceptions',
        'tackles_mid_3rd': 'Tackles in the Middle 3rd',
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
        'xg_xg_assist_per90': 'xG + xAG/90',
        'gk_psxg_net' : 'Post-Shot Expected Goals minus Goals Allowed',
        'gk_saves' : 'Saves',
        'gk_free_kick_goals_against' : "Free Kick Goals Against",
        'gk_corner_kick_goals_against' : "Corner Kick Goals Against",
        'gk_own_goals_against' : "Own Goals Scored Against Goalkeeper",
        'gk_psxg' : "Post Shot Expected Goals",
        'gk_psnpxg_per_shot_on_target_against' : "Post Shot Expected Goals Per Shot On Target",
        'gk_psxg_net_per90' : "Post Shot Expected Goals Per 90",
        'gk_passes_completed_launched' : "Passes Completed (Launched)",
        'gk_passes_launched' : "Passes Attempted (Launched)",
        'gk_passes_pct_launched' : "Pass Completion Percentage (Launched)",
        'gk_passes' : "Passes Attempted (GK)",
        'gk_passes_throws' : "Throws Attempted",
        'gk_pct_passes_launched' : "Launch Pct",
        'gk_passes_length_avg' : "Average Pass Length",
        'gk_goal_kicks' : "Goal Kicks",
        'gk_pct_goal_kicks_launched' : "Launch Pct (Goal Kicks)",
        'gk_goal_kick_length_avg' : "Avg. Length of Goal Kicks",
        'gk_crosses' : "Crosses Faced",
        'gk_crosses_stopped' : "Crosses Stopped",
        'gk_crosses_stopped_pct' : "Crosses Stopped Pct",
        'gk_def_actions_outside_pen_area' : "Def. Actions Outside Pen. Area",
        'gk_def_actions_outside_pen_area_per90' : "Def. Actions Outside Pen. Area Per 90",
        'gk_avg_distance_def_actions' : "Avg. Distance of Def. Actions",
        'gk_games' : "Goalkeeper Matches",
        'gk_games_starts' : "Goalkeeper Starts",
        'gk_minutes' : "Goalkeeper Minutes",
        'gk_goals_against' : "Goals Against",
        'gk_goals_against_per90' : "Goals Against Per 90",
        'gk_shots_on_target_against' : "Shots on Target Against",
        'gk_save_pct' : "Save Percentage",
        'gk_wins' : "Wins",
        'gk_ties' : "Draws",
        'gk_losses' : "Losses",
        'gk_clean_sheets' : "Clean Sheets",
        'gk_clean_sheets_pct' : "Clean Sheet Pct",
        'gk_pens_att' : "Penalty Kicks Attempted",
        'gk_pens_allowed' : "Penalty Kicks Allowed",
        'gk_pens_saved' : "Penalty Kicks Saved",
        'gk_pens_missed' : "Penalty Kicks Missed",
        'gk_pens_save_pct' : "Penalty Kicks Save Pct"
    }

    if key in mapping:
        return mapping[key]
    else:
        return None
    
def name_to_key(name):
    mapping = {
        'Aerials Lost': 'aerials_lost',
        'Aerials Won': 'aerials_won',
        'Aerials Won Pct': 'aerials_won_pct',
        'Key Passes': 'assisted_shots',
        'Assists': 'assists',
        'Assists Per 90': 'assists_per90',
        'Avg Shot Distance': 'avg_shot_distance',
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
        'Goals Per Shot on Target': 'goals_per_shot_on_target',
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
        'Passing Compltion Pct': 'passes_pct',
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
        'Shots On Target': 'shots_on_target',
        'Shots On Target Pct': 'shots_on_target_pct',
        'Shots On Target Per 90': 'shots_on_target_per90',
        'Shots Per 90': 'shots_per90',
        'Tackles': 'tackles',
        'Tackles in the Attacking 3rd': 'tackles_att_3rd',
        'Tackles in the Defensive 3rd': 'tackles_def_3rd',
        'Tackles & Interceptions': 'tackles_interceptions',
        'Tackles in the Middle 3rd': 'tackles_mid_3rd',
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
        'xG + xAG/90': 'xg_xg_assist_per90',
        'xG per Shot' : 'xg_per_shot',
        "Average Actual Shot Distanct" : 'avg_actual_shot_distance',
        'Post-Shot Expected Goals minus Goals Allowed' : 'gk_psxg_net',
        'Saves' : 'gk_saves',
        "Free Kick Goals Against" : 'gk_free_kick_goals_against',
        "Corner Kick Goals Against" : 'gk_corner_kick_goals_against',
        "Own Goals Scored Against Goalkeeper" : 'gk_own_goals_against',
        "Post Shot Expected Goals" : 'gk_psxg',
        "Post Shot Expected Goals Per Shot On Target" : 'gk_psnpxg_per_shot_on_target_against',
        "Post Shot Expected Goals Per 90" : 'gk_psxg_net_per90',
        "Passes Completed (Launched)" : 'gk_passes_completed_launched',
        "Passes Attempted (Launched)" : 'gk_passes_launched',
        "Pass Completion Percentage (Launched)" : 'gk_passes_pct_launched',
        "Passes Attempted (GK)" : 'gk_passes',
        "Throws Attempted" : 'gk_passes_throws',
        "Launch Pct" : 'gk_pct_passes_launched',
        "Average Pass Length" : 'gk_passes_length_avg',
        "Goal Kicks" : 'gk_goal_kicks',
        "Launch Pct (Goal Kicks)" : 'gk_pct_goal_kicks_launched',
        "Avg. Length of Goal Kicks" : 'gk_goal_kick_length_avg',
        "Crosses Faced" : 'gk_crosses',
        "Crosses Stopped" : 'gk_crosses_stopped',
        "Crosses Stopped Pct" : 'gk_crosses_stopped_pct',
        "Def. Actions Outside Pen. Area" : 'gk_def_actions_outside_pen_area',
        "Def. Actions Outside Pen. Area Per 90" : 'gk_def_actions_outside_pen_area_per90',
        "Avg. Distance of Def. Actions" : 'gk_avg_distance_def_actions',
        "Goalkeeper Matches" : 'gk_games',
        "Goalkeeper Starts" : 'gk_games_starts',
        "Goalkeeper Minutes" : 'gk_minutes',
        "Goals Against" : 'gk_goals_against',
        "Goals Against Per 90" : 'gk_goals_against_per90',
        "Shots on Target Against" : 'gk_shots_on_target_against',
        "Save Percentage" : 'gk_save_pct',
        "Wins" : 'gk_wins',
        "Draws" : 'gk_ties',
        "Losses" : 'gk_losses',
        "Clean Sheets" : 'gk_clean_sheets',
        "Clean Sheet Pct" : 'gk_clean_sheets_pct',
        "Penalty Kicks Attempted" : 'gk_pens_att',
        "Penalty Kicks Allowed" : 'gk_pens_allowed',
        "Penalty Kicks Saved" : 'gk_pens_saved',
        "Penalty Kicks Missed" : 'gk_pens_missed',
        "Penalty Kicks Save Pct" : 'gk_pens_save_pct'
    }

    if name in mapping:
        return mapping[name]
    else:
        return None

def normalize(numbers, min_new=20, max_new=100):
    min_old = min(numbers)
    max_old = max(numbers)
    
    normalized_numbers = [
        min_new + ( (num - min_old) / (max_old - min_old) ) * (max_new - min_new)
        for num in numbers
    ]
    
    return normalized_numbers

def get_max_idx(x, y):
    max_product = max([a * b for a, b in zip(x, y)])
    for i in range(len(x)):
        if( (x[i] * y[i]) == max_product ):
            return i
        
def get_min_idx(x, y):
    max_product = min([a * b for a, b in zip(x, y)])
    for i in range(len(x)):
        if( (x[i] * y[i]) == max_product ):
            return i

def get_median_idx(x, y):
    products = [a * b for a, b in zip(x, y)]
    sorted_values = sorted(products)
    
    n = len(products)
    if n % 2 == 1:
        median = sorted_values[n // 2]
    else:
        median = sorted_values[(n // 2) - 1]
    
    return products.index(median)

def get_top_quartile_idx(x, y):
    products = [a * b for a, b in zip(x, y)]
    sorted_values = sorted(products, reverse=True)
    cutoff_index = len(products) // 4
    threshold_value = sorted_values[cutoff_index]
    top_25_indexes = [i for i, value in enumerate(products) if value >= threshold_value]
    
    return top_25_indexes

def get_top_n_idx(x, y, n):
    products = [a * b for a, b in zip(x, y)]
    sorted_values = sorted(products, reverse=True)
    threshold_value = sorted_values[n - 1]
    top_n_indexes = [i for i, value in enumerate(products) if value >= threshold_value]
    
    return top_n_indexes

def get_stat_top_n_idx(stat, n):
    sorted_values = sorted(stat, reverse=True)
    threshold_value = sorted_values[n - 1]
    top_indexes = [i for i, value in enumerate(stat) if value >= threshold_value]
    
    return top_indexes

def kmeans(x, y, n_clusters):
    points = np.array(list(zip(x, y)))

    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(points)

    labels = kmeans.labels_

    colors = list(mcolors.TABLEAU_COLORS.values())

    if n_clusters > len(colors):
        color_map = plt.cm.get_cmap('tab20', n_clusters)
        colors = [mcolors.rgb2hex(color_map(i)) for i in range(n_clusters)]

    point_colors = [colors[label] for label in labels]

    return point_colors