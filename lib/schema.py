class Schema:
    def __init__(self):
        self.countries = {
            "name": "countries",
            "primary_key" : "country_code",
            "columns": [
                {
                    "sql" : "country_code",
                    "label" : "Country Code",
                    "type" : "int",
                    "primary_key" : True,
                },
                {
                    "sql" : "country",
                    "label" : "Country",
                    "type" : "text"
                },
                {
                    "sql" : "tm_conutry_code",
                    "label" : "TM Country Code",
                    "type" : "text"
                },
                {
                    "sql" : "fapi_conutry_code",
                    "label" : "FAPI Country Code",
                    "type" : "text"
                },
                {
                    "sql" : "fbref_conutry_code",
                    "label" : "FBRef Country Code",
                    "type" : "text"
                }
            ]
        }
        self.leagues = {
            "name": "leagues",
            "primary_key" : "league_id",
            "columns": [
                {
                    "sql" : "league_id",
                    "label" : "League ID",
                    "type" : "int",
                    "primary_key" : True
                },
                {
                    "sql" : "conutry_code",
                    "label" : "Country Code",
                    "type" : "text"
                },
                {
                    "sql" : "league_name",
                    "label" : "League Name",
                    "type" : "text"
                },
                {
                    "sql" : "tm_league_id",
                    "label" : "TM League ID",
                    "type" : "text"
                },
                {
                    "sql" : "fpai_league_id",
                    "label" : "FAPI League ID",
                    "type" : "text"
                },
                {
                    "sql" : "fbref_league_id",
                    "label" : "FBRef League ID",
                    "type" : "text"
                }
            ]  
        }  
        self.players = {
            "name": "players",
            "primary_key" : "player_id",
            "columns": [
                {
                    "sql" : "player_id",
                    "label" : "Player ID",
                    "type" : "int",
                    "primary_key" : True
                },
                {
                    "sql" : "team_id",
                    "label" : "Team ID",
                    "type" : "int"
                },
                {
                    "sql" : "first_name",
                    "label" : "First Name",
                    "type" : "text"
                },
                {
                    "sql" : "last_name",
                    "label" : "Last Name",
                    "type" : "text"
                },
                {
                    "sql" : "tm_player_id",
                    "label" : "TM Player ID",
                    "type" : "text"
                },
                {
                    "sql" : "fpai_player_id",
                    "label" : "FAPI Player ID",
                    "type" : "text"
                },
                {
                    "sql" : "fbref_player_id",
                    "label" : "FBRef Player ID",
                    "type" : "text"
                }
            ]
        }
        self.teams = {
            "name": "teams",
            "primary_key" : "team_id",
            "columns": [
                {
                    "sql" : "team_id",
                    "label" : "Team ID",
                    "type" : "int",
                    "primary_key" : True
                },
                {
                    "sql" : "conutry_code",
                    "label" : "Country Code",
                    "type" : "text"
                },
                {
                    "sql" : "team_name",
                    "label" : "Team Name",
                    "type" : "text"
                },
                {
                    "sql" : "tm_team_id",
                    "label" : "TM Player ID",
                    "type" : "text"
                },
                {
                    "sql" : "fpai_team_id",
                    "label" : "FAPI Team ID",
                    "type" : "text"
                },
                {
                    "sql" : "fbref_team_id",
                    "label" : "FBRef Team ID",
                    "type" : "text"
                }
            ]
        }
        self.player_stats = {
            "name":"player_stats",
            "primary_key":"player_stats_id",
            "columns":[
                {
                    "sql":"player_stats_id",
                    "label":"Player Stats ID",
                    "type":"serial",
                    "primary_key":True,
                    "increment":True
                },
                {
                    "sql":"position",
                    "label":"Position",
                    "type":"TEXT"
                },
                {
                    "sql":"year",
                    "label":"Year",
                    "type":"TEXT"
                },
                {
                    "sql":"fbref_league_id",
                    "label":"Fbref League Id",
                    "type":"TEXT"
                },
                {
                    "sql":"league_id",
                    "label":"League Id",
                    "type":"TEXT"
                },
                {
                    "sql":"player_id",
                    "label":"Player Id",
                    "type":"TEXT"
                },
                {
                    "sql":"fbref_player_id",
                    "label":"Fbref Player Id",
                    "type":"TEXT"
                },
                {
                    "sql":"team_id",
                    "label":"Team Id",
                    "type":"TEXT"
                },
                {
                    "sql":"fbref_team_id",
                    "label":"Fbrefteam Id",
                    "type":"TEXT"
                },
                {
                    "sql":"age",
                    "label":"Age",
                    "type":"INT"
                },
                {
                    "sql":"team",
                    "label":"Team",
                    "type":"TEXT"
                },
                {
                    "sql":"country",
                    "label":"Country",
                    "type":"TEXT"
                },
                {
                    "sql":"comp_level",
                    "label":"Comp Level",
                    "type":"TEXT"
                },
                {
                    "sql":"lg_finish",
                    "label":"Lg Finish",
                    "type":"TEXT"
                },
                {
                    "sql":"minutes_90s",
                    "label":"Minutes 90s",
                    "type":"REAL"
                },
                {
                    "sql":"gk_goals_against",
                    "label":"Gk Goals Against",
                    "type":"REAL"
                },
                {
                    "sql":"gk_pens_allowed",
                    "label":"Gk Pens Allowed",
                    "type":"REAL"
                },
                {
                    "sql":"gk_free_kick_goals_against",
                    "label":"Gk Free Kick Goals Against",
                    "type":"REAL"
                },
                {
                    "sql":"gk_corner_kick_goals_against",
                    "label":"Gk Corner Kick Goals Against",
                    "type":"REAL"
                },
                {
                    "sql":"gk_own_goals_against",
                    "label":"Gk Own Goals Against",
                    "type":"REAL"
                },
                {
                    "sql":"gk_psxg",
                    "label":"Gk Psxg",
                    "type":"REAL"
                },
                {
                    "sql":"gk_psnpxg_per_shot_on_target_against",
                    "label":"Gk Psnpxg Per Shot On Target Against",
                    "type":"REAL"
                },
                {
                    "sql":"gk_psxg_net",
                    "label":"Gk Psxg Net",
                    "type":"REAL"
                },
                {
                    "sql":"gk_psxg_net_per90",
                    "label":"Gk Psxg Net Per90",
                    "type":"REAL"
                },
                {
                    "sql":"gk_passes_completed_launched",
                    "label":"Gk Passes Completed Launched",
                    "type":"REAL"
                },
                {
                    "sql":"gk_passes_launched",
                    "label":"Gk Passes Launched",
                    "type":"REAL"
                },
                {
                    "sql":"gk_passes_pct_launched",
                    "label":"Gk Passes Pct Launched",
                    "type":"REAL"
                },
                {
                    "sql":"gk_passes",
                    "label":"Gk Passes",
                    "type":"REAL"
                },
                {
                    "sql":"gk_passes_throws",
                    "label":"Gk Passes Throws",
                    "type":"REAL"
                },
                {
                    "sql":"gk_pct_passes_launched",
                    "label":"Gk Pct Passes Launched",
                    "type":"REAL"
                },
                {
                    "sql":"gk_passes_length_avg",
                    "label":"Gk Passes Length Avg",
                    "type":"REAL"
                },
                {
                    "sql":"gk_goal_kicks",
                    "label":"Gk Goal Kicks",
                    "type":"REAL"
                },
                {
                    "sql":"gk_pct_goal_kicks_launched",
                    "label":"Gk Pct Goal Kicks Launched",
                    "type":"REAL"
                },
                {
                    "sql":"gk_goal_kick_length_avg",
                    "label":"Gk Goal Kick Length Avg",
                    "type":"REAL"
                },
                {
                    "sql":"gk_crosses",
                    "label":"Gk Crosses",
                    "type":"REAL"
                },
                {
                    "sql":"gk_crosses_stopped",
                    "label":"Gk Crosses Stopped",
                    "type":"REAL"
                },
                {
                    "sql":"gk_crosses_stopped_pct",
                    "label":"Gk Crosses Stopped Pct",
                    "type":"REAL"
                },
                {
                    "sql":"gk_def_actions_outside_pen_area",
                    "label":"Gk Def Actions Outside Pen Area",
                    "type":"REAL"
                },
                {
                    "sql":"gk_def_actions_outside_pen_area_per90",
                    "label":"Gk Def Actions Outside Pen Area Per90",
                    "type":"REAL"
                },
                {
                    "sql":"gk_avg_distance_def_actions",
                    "label":"Gk Avg Distance Def Actions",
                    "type":"REAL"
                },
                {
                    "sql":"matches",
                    "label":"Matches",
                    "type":"TEXT"
                },
                {
                    "sql":"gk_games",
                    "label":"Gk Games",
                    "type":"REAL"
                },
                {
                    "sql":"gk_games_starts",
                    "label":"Gk Games Starts",
                    "type":"REAL"
                },
                {
                    "sql":"gk_minutes",
                    "label":"Gk Minutes",
                    "type":"TEXT"
                },
                {
                    "sql":"gk_goals_against_per90",
                    "label":"Gk Goals Against Per90",
                    "type":"REAL"
                },
                {
                    "sql":"gk_shots_on_target_against",
                    "label":"Gk Shots On Target Against",
                    "type":"REAL"
                },
                {
                    "sql":"gk_saves",
                    "label":"Gk Saves",
                    "type":"REAL"
                },
                {
                    "sql":"gk_save_pct",
                    "label":"Gk Save Pct",
                    "type":"REAL"
                },
                {
                    "sql":"gk_wins",
                    "label":"Gk Wins",
                    "type":"REAL"
                },
                {
                    "sql":"gk_ties",
                    "label":"Gk Ties",
                    "type":"REAL"
                },
                {
                    "sql":"gk_losses",
                    "label":"Gk Losses",
                    "type":"REAL"
                },
                {
                    "sql":"gk_clean_sheets",
                    "label":"Gk Clean Sheets",
                    "type":"REAL"
                },
                {
                    "sql":"gk_clean_sheets_pct",
                    "label":"Gk Clean Sheets Pct",
                    "type":"REAL"
                },
                {
                    "sql":"gk_pens_att",
                    "label":"Gk Pens Att",
                    "type":"REAL"
                },
                {
                    "sql":"gk_pens_saved",
                    "label":"Gk Pens Saved",
                    "type":"REAL"
                },
                {
                    "sql":"gk_pens_missed",
                    "label":"Gk Pens Missed",
                    "type":"REAL"
                },
                {
                    "sql":"gk_pens_save_pct",
                    "label":"Gk Pens Save Pct",
                    "type":"REAL"
                },
                {
                    "sql":"games",
                    "label":"Games",
                    "type":"REAL"
                },
                {
                    "sql":"games_starts",
                    "label":"Games Starts",
                    "type":"REAL"
                },
                {
                    "sql":"minutes",
                    "label":"Minutes",
                    "type":"TEXT"
                },
                {
                    "sql":"goals",
                    "label":"Goals",
                    "type":"REAL"
                },
                {
                    "sql":"assists",
                    "label":"Assists",
                    "type":"REAL"
                },
                {
                    "sql":"goals_assists",
                    "label":"Goals Assists",
                    "type":"REAL"
                },
                {
                    "sql":"goals_pens",
                    "label":"Goals Pens",
                    "type":"REAL"
                },
                {
                    "sql":"pens_made",
                    "label":"Pens Made",
                    "type":"REAL"
                },
                {
                    "sql":"pens_att",
                    "label":"Pens Att",
                    "type":"REAL"
                },
                {
                    "sql":"cards_yellow",
                    "label":"Cards Yellow",
                    "type":"REAL"
                },
                {
                    "sql":"cards_red",
                    "label":"Cards Red",
                    "type":"REAL"
                },
                {
                    "sql":"xg",
                    "label":"Xg",
                    "type":"REAL"
                },
                {
                    "sql":"npxg",
                    "label":"Npxg",
                    "type":"REAL"
                },
                {
                    "sql":"xg_assist",
                    "label":"Xg Assist",
                    "type":"REAL"
                },
                {
                    "sql":"npxg_xg_assist",
                    "label":"Npxg Xg Assist",
                    "type":"REAL"
                },
                {
                    "sql":"progressive_carries",
                    "label":"Progressive Carries",
                    "type":"REAL"
                },
                {
                    "sql":"progressive_passes",
                    "label":"Progressive Passes",
                    "type":"REAL"
                },
                {
                    "sql":"progressive_passes_received",
                    "label":"Progressive Passes Received",
                    "type":"REAL"
                },
                {
                    "sql":"goals_per90",
                    "label":"Goals Per90",
                    "type":"REAL"
                },
                {
                    "sql":"assists_per90",
                    "label":"Assists Per90",
                    "type":"REAL"
                },
                {
                    "sql":"goals_assists_per90",
                    "label":"Goals Assists Per90",
                    "type":"REAL"
                },
                {
                    "sql":"goals_pens_per90",
                    "label":"Goals Pens Per90",
                    "type":"REAL"
                },
                {
                    "sql":"goals_assists_pens_per90",
                    "label":"Goals Assists Pens Per90",
                    "type":"REAL"
                },
                {
                    "sql":"xg_per90",
                    "label":"Xg Per90",
                    "type":"REAL"
                },
                {
                    "sql":"xg_assist_per90",
                    "label":"Xg Assist Per90",
                    "type":"REAL"
                },
                {
                    "sql":"xg_xg_assist_per90",
                    "label":"Xg Xg Assist Per90",
                    "type":"REAL"
                },
                {
                    "sql":"npxg_per90",
                    "label":"Npxg Per90",
                    "type":"REAL"
                },
                {
                    "sql":"npxg_xg_assist_per90",
                    "label":"Npxg Xg Assist Per90",
                    "type":"REAL"
                },
                {
                    "sql":"passes_completed",
                    "label":"Passes Completed",
                    "type":"REAL"
                },
                {
                    "sql":"passes",
                    "label":"Passes",
                    "type":"REAL"
                },
                {
                    "sql":"passes_pct",
                    "label":"Passes Pct",
                    "type":"REAL"
                },
                {
                    "sql":"passes_total_distance",
                    "label":"Passes Total Distance",
                    "type":"REAL"
                },
                {
                    "sql":"passes_progressive_distance",
                    "label":"Passes Progressive Distance",
                    "type":"REAL"
                },
                {
                    "sql":"passes_completed_short",
                    "label":"Passes Completed Short",
                    "type":"REAL"
                },
                {
                    "sql":"passes_short",
                    "label":"Passes Short",
                    "type":"REAL"
                },
                {
                    "sql":"passes_pct_short",
                    "label":"Passes Pct Short",
                    "type":"REAL"
                },
                {
                    "sql":"passes_completed_medium",
                    "label":"Passes Completed Medium",
                    "type":"REAL"
                },
                {
                    "sql":"passes_medium",
                    "label":"Passes Medium",
                    "type":"REAL"
                },
                {
                    "sql":"passes_pct_medium",
                    "label":"Passes Pct Medium",
                    "type":"REAL"
                },
                {
                    "sql":"passes_completed_long",
                    "label":"Passes Completed Long",
                    "type":"REAL"
                },
                {
                    "sql":"passes_long",
                    "label":"Passes Long",
                    "type":"REAL"
                },
                {
                    "sql":"passes_pct_long",
                    "label":"Passes Pct Long",
                    "type":"REAL"
                },
                {
                    "sql":"pass_xa",
                    "label":"Pass Xa",
                    "type":"REAL"
                },
                {
                    "sql":"xg_assist_net",
                    "label":"Xg Assist Net",
                    "type":"REAL"
                },
                {
                    "sql":"assisted_shots",
                    "label":"Assisted Shots",
                    "type":"REAL"
                },
                {
                    "sql":"passes_into_final_third",
                    "label":"Passes Into Final Third",
                    "type":"REAL"
                },
                {
                    "sql":"passes_into_penalty_area",
                    "label":"Passes Into Penalty Area",
                    "type":"REAL"
                },
                {
                    "sql":"crosses_into_penalty_area",
                    "label":"Crosses Into Penalty Area",
                    "type":"REAL"
                },
                {
                    "sql":"passes_live",
                    "label":"Passes Live",
                    "type":"REAL"
                },
                {
                    "sql":"passes_dead",
                    "label":"Passes Dead",
                    "type":"REAL"
                },
                {
                    "sql":"passes_free_kicks",
                    "label":"Passes Free Kicks",
                    "type":"REAL"
                },
                {
                    "sql":"through_balls",
                    "label":"Through Balls",
                    "type":"REAL"
                },
                {
                    "sql":"passes_switches",
                    "label":"Passes Switches",
                    "type":"REAL"
                },
                {
                    "sql":"crosses",
                    "label":"Crosses",
                    "type":"REAL"
                },
                {
                    "sql":"throw_ins",
                    "label":"Throw Ins",
                    "type":"REAL"
                },
                {
                    "sql":"corner_kicks",
                    "label":"Corner Kicks",
                    "type":"REAL"
                },
                {
                    "sql":"corner_kicks_in",
                    "label":"Corner Kicks In",
                    "type":"REAL"
                },
                {
                    "sql":"corner_kicks_out",
                    "label":"Corner Kicks Out",
                    "type":"REAL"
                },
                {
                    "sql":"corner_kicks_straight",
                    "label":"Corner Kicks Straight",
                    "type":"REAL"
                },
                {
                    "sql":"passes_offsides",
                    "label":"Passes Offsides",
                    "type":"REAL"
                },
                {
                    "sql":"passes_blocked",
                    "label":"Passes Blocked",
                    "type":"REAL"
                },
                {
                    "sql":"tackles",
                    "label":"Tackles",
                    "type":"REAL"
                },
                {
                    "sql":"tackles_won",
                    "label":"Tackles Won",
                    "type":"REAL"
                },
                {
                    "sql":"tackles_def_3rd",
                    "label":"Tackles Def 3rd",
                    "type":"REAL"
                },
                {
                    "sql":"tackles_mid_3rd",
                    "label":"Tackles Mid 3rd",
                    "type":"REAL"
                },
                {
                    "sql":"tackles_att_3rd",
                    "label":"Tackles Att 3rd",
                    "type":"REAL"
                },
                {
                    "sql":"challenge_tackles",
                    "label":"Challenge Tackles",
                    "type":"REAL"
                },
                {
                    "sql":"challenges",
                    "label":"Challenges",
                    "type":"REAL"
                },
                {
                    "sql":"challenge_tackles_pct",
                    "label":"Challenge Tackles Pct",
                    "type":"REAL"
                },
                {
                    "sql":"challenges_lost",
                    "label":"Challenges Lost",
                    "type":"REAL"
                },
                {
                    "sql":"blocks",
                    "label":"Blocks",
                    "type":"REAL"
                },
                {
                    "sql":"blocked_shots",
                    "label":"Blocked Shots",
                    "type":"REAL"
                },
                {
                    "sql":"blocked_passes",
                    "label":"Blocked Passes",
                    "type":"REAL"
                },
                {
                    "sql":"interceptions",
                    "label":"Interceptions",
                    "type":"REAL"
                },
                {
                    "sql":"tackles_interceptions",
                    "label":"Tackles Interceptions",
                    "type":"REAL"
                },
                {
                    "sql":"clearances",
                    "label":"Clearances",
                    "type":"REAL"
                },
                {
                    "sql":"errors",
                    "label":"Errors",
                    "type":"REAL"
                },
                {
                    "sql":"touches",
                    "label":"Touches",
                    "type":"REAL"
                },
                {
                    "sql":"touches_def_pen_area",
                    "label":"Touches Def Pen Area",
                    "type":"REAL"
                },
                {
                    "sql":"touches_def_3rd",
                    "label":"Touches Def 3rd",
                    "type":"REAL"
                },
                {
                    "sql":"touches_mid_3rd",
                    "label":"Touches Mid 3rd",
                    "type":"REAL"
                },
                {
                    "sql":"touches_att_3rd",
                    "label":"Touches Att 3rd",
                    "type":"REAL"
                },
                {
                    "sql":"touches_att_pen_area",
                    "label":"Touches Att Pen Area",
                    "type":"REAL"
                },
                {
                    "sql":"touches_live_ball",
                    "label":"Touches Live Ball",
                    "type":"REAL"
                },
                {
                    "sql":"take_ons",
                    "label":"Take Ons",
                    "type":"REAL"
                },
                {
                    "sql":"take_ons_won",
                    "label":"Take Ons Won",
                    "type":"REAL"
                },
                {
                    "sql":"take_ons_won_pct",
                    "label":"Take Ons Won Pct",
                    "type":"REAL"
                },
                {
                    "sql":"take_ons_tackled",
                    "label":"Take Ons Tackled",
                    "type":"REAL"
                },
                {
                    "sql":"take_ons_tackled_pct",
                    "label":"Take Ons Tackled Pct",
                    "type":"REAL"
                },
                {
                    "sql":"carries",
                    "label":"Carries",
                    "type":"REAL"
                },
                {
                    "sql":"carries_distance",
                    "label":"Carries Distance",
                    "type":"REAL"
                },
                {
                    "sql":"carries_progressive_distance",
                    "label":"Carries Progressive Distance",
                    "type":"REAL"
                },
                {
                    "sql":"carries_into_final_third",
                    "label":"Carries Into Final Third",
                    "type":"REAL"
                },
                {
                    "sql":"carries_into_penalty_area",
                    "label":"Carries Into Penalty Area",
                    "type":"REAL"
                },
                {
                    "sql":"miscontrols",
                    "label":"Miscontrols",
                    "type":"REAL"
                },
                {
                    "sql":"dispossessed",
                    "label":"Dispossessed",
                    "type":"REAL"
                },
                {
                    "sql":"passes_received",
                    "label":"Passes Received",
                    "type":"REAL"
                },
                {
                    "sql":"minutes_per_game",
                    "label":"Minutes Per Game",
                    "type":"REAL"
                },
                {
                    "sql":"minutes_pct",
                    "label":"Minutes Pct",
                    "type":"REAL"
                },
                {
                    "sql":"minutes_per_start",
                    "label":"Minutes Per Start",
                    "type":"REAL"
                },
                {
                    "sql":"games_complete",
                    "label":"Games Complete",
                    "type":"REAL"
                },
                {
                    "sql":"games_subs",
                    "label":"Games Subs",
                    "type":"REAL"
                },
                {
                    "sql":"minutes_per_sub",
                    "label":"Minutes Per Sub",
                    "type":"REAL"
                },
                {
                    "sql":"unused_subs",
                    "label":"Unused Subs",
                    "type":"REAL"
                },
                {
                    "sql":"points_per_game",
                    "label":"Points Per Game",
                    "type":"REAL"
                },
                {
                    "sql":"on_goals_for",
                    "label":"On Goals For",
                    "type":"REAL"
                },
                {
                    "sql":"on_goals_against",
                    "label":"On Goals Against",
                    "type":"REAL"
                },
                {
                    "sql":"plus_minus",
                    "label":"Plus Minus",
                    "type":"REAL"
                },
                {
                    "sql":"plus_minus_per90",
                    "label":"Plus Minus Per90",
                    "type":"REAL"
                },
                {
                    "sql":"plus_minus_wowy",
                    "label":"Plus Minus Wowy",
                    "type":"REAL"
                },
                {
                    "sql":"on_xg_for",
                    "label":"On Xg For",
                    "type":"REAL"
                },
                {
                    "sql":"on_xg_against",
                    "label":"On Xg Against",
                    "type":"REAL"
                },
                {
                    "sql":"xg_plus_minus",
                    "label":"Xg Plus Minus",
                    "type":"REAL"
                },
                {
                    "sql":"xg_plus_minus_per90",
                    "label":"Xg Plus Minus Per90",
                    "type":"REAL"
                },
                {
                    "sql":"xg_plus_minus_wowy",
                    "label":"Xg Plus Minus Wowy",
                    "type":"REAL"
                },
                {
                    "sql":"cards_yellow_red",
                    "label":"Cards Yellow Red",
                    "type":"REAL"
                },
                {
                    "sql":"fouls",
                    "label":"Fouls",
                    "type":"REAL"
                },
                {
                    "sql":"fouled",
                    "label":"Fouled",
                    "type":"REAL"
                },
                {
                    "sql":"offsides",
                    "label":"Offsides",
                    "type":"REAL"
                },
                {
                    "sql":"pens_won",
                    "label":"Pens Won",
                    "type":"REAL"
                },
                {
                    "sql":"pens_conceded",
                    "label":"Pens Conceded",
                    "type":"REAL"
                },
                {
                    "sql":"own_goals",
                    "label":"Own Goals",
                    "type":"REAL"
                },
                {
                    "sql":"ball_recoveries",
                    "label":"Ball Recoveries",
                    "type":"REAL"
                },
                {
                    "sql":"aerials_won",
                    "label":"Aerials Won",
                    "type":"REAL"
                },
                {
                    "sql":"aerials_lost",
                    "label":"Aerials Lost",
                    "type":"REAL"
                },
                {
                    "sql":"aerials_won_pct",
                    "label":"Aerials Won Pct",
                    "type":"REAL"
                },
                {
                    "sql":"shots",
                    "label":"Shots",
                    "type":"REAL"
                },
                {
                    "sql":"shots_on_target",
                    "label":"Shots On Target",
                    "type":"REAL"
                },
                {
                    "sql":"shots_on_target_pct",
                    "label":"Shots On Target Pct",
                    "type":"REAL"
                },
                {
                    "sql":"shots_per90",
                    "label":"Shots Per90",
                    "type":"REAL"
                },
                {
                    "sql":"shots_on_target_per90",
                    "label":"Shots On Target Per90",
                    "type":"REAL"
                },
                {
                    "sql":"goals_per_shot",
                    "label":"Goals Per Shot",
                    "type":"REAL"
                },
                {
                    "sql":"goals_per_shot_on_target",
                    "label":"Goals Per Shot On Target",
                    "type":"REAL"
                },
                {
                    "sql":"average_shot_distance",
                    "label":"Average Shot Distance",
                    "type":"REAL"
                },
                {
                    "sql":"shots_free_kicks",
                    "label":"Shots Free Kicks",
                    "type":"REAL"
                },
                {
                    "sql":"npxg_per_shot",
                    "label":"Npxg Per Shot",
                    "type":"REAL"
                },
                {
                    "sql":"xg_net",
                    "label":"Xg Net",
                    "type":"REAL"
                },
                {
                    "sql":"npxg_net",
                    "label":"Npxg Net",
                    "type":"REAL"
                }
            ]
        }

    def get_schema(self, table):
        return getattr(self, table)