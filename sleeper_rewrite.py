#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 16:42:38 2019

@author: corey
"""

from sleeper_wrapper import League
from sleeper_wrapper import Players
from sleeper_wrapper import Stats
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#####
# Get the player data
#####


league_id = 438058453903077376

league = League(league_id)
stats = Stats()
players = Players()


all_rules = {
    'pass_2pt': 2.0, # Passing 2 point conversions
    'pass_int': -2.0, # Passing interceptions
    'pass_lng': 0, # Long pass
    'off_snp': 68.0, # Total snaps
    'gs': 1.0, # Game started
    'cmp_pct': 66.7, # Completion percentage
    'pass_fd': 6.0, # Passing first downs
    'gp': 1.0, # Game played
    'pass_sack': 1.0, # Times sacked passing
    'tm_off_snp': 68.0, # Teams total offensive snaps
    'wind_speed': 6.0, # Wind speed
    'gms_active': 1.0, # Active during game
    'pass_cmp': 18.0, # Completions
    'pts_half_ppr': 10.4, # Points in half ppr
    'pass_rtg': 80.17, # Passer rating (?)
    'pass_sack_yds': 8.0, # Yards lost to sacks
    'tm_def_snp': 70.0, # Teams total defensive snaps
    'rush_ypa': -1.0, # Rushing yards per attempt
    'temperature': 84.0, # Temperature during the game
    'pass_att': 27.0, # Pass attempts
    'pass_inc': 9.0, # Pass incompletions
    'pass_ypa': 6.1, # Pass yards per attempt
    'rush_att': 2.0, # Passing attempts
    'rush_lng': -1.0, # Long rush
    'tm_st_snp': 19.0, # Teams total special team snaps
    'rush_yd': -2.0, # Rush yards
    'pass_int_td': 1.0, # Touchdowns from interceptions thrown
    'pass_yd': 166.0, # Passing yards
    'pass_td': 1.0, # Passing touchdowns
    'pts_ppr': 10.44, # Points in ppr
    'humidity': 79.0, # Humidity during the game
    'pts_std': 10.44, # Points in standard
    'pass_ypc': 9.2, # Passing yards per completions
    'rec_yd': 55.0, # Receiving yards
    'bonus_rush_rec_yd_100': 1.0, # If they have more than 100 rushing/receiving yards
    'rec_ypt': 7.9, # Yards per target
    'rec_pct': 85.7, # Catch percentage
    'rec_ypr': 9.2, # Yards per reception
    'rec_20_29': 1.0, # Receptions between 20 and 29 yards
    'rec_0_4': 2.0, # Receptions between 0 and 4 yards
    'rush_fd': 2.0, # Rushing first downs
    'rec': 6.0, # Receptions
    'rec_5_9': 3.0, # Receptions between 5 and 9 yards
    'rush_att': 18.0, # Rushing attempts
    'td': 1.0, # Rushing touchdowns
    'rec_td': 1.0, # Receiving touchdowns
    'rush_lng': 18.0, # Long rush
    'rec_lng': 27.0, # Long reception
    'rec_tgt': 7.0, # Receiving targets
    'rec_fd': 1.0, # Receiving first downs
    'bonus_rec_rb': 6.0, # Receptions as a running back
    'bonus_rec_wr': 8.0,
    'bonus_rec_te': 4.0,
    'rec_2pt': 2.0,
    'rush_2pt': 1.0,
    }
league_rules = league._league['scoring_settings']
league_roster = league._league['roster_positions']
taxi_spots = league._league['settings']['taxi_slots']

# Add values after the position to differentiate them
# league_roster_dict = {i:league_roster.count(i) for i in league_roster}
league_roster_list = []
for i in range(len(league_roster)+taxi_spots):
    added = False
    n = 1
    while not added:
        # Exception for taxi spots because they are not included by default
        if i >= len(league_roster):
            position_name = 'BN' + ' ' + str(n)
        else:
            position_name = league_roster[i] + ' ' + str(n)
            
        if position_name in league_roster_list:
            n += 1
        else:
            league_roster_list.append(position_name)
            added = True

users = league.get_users()
rosters = league.get_rosters()

base_df = pd.DataFrame()

# Get owner ids
owner_id_list = []
owner_name_list = []
owner_roster_list = []
for user in users:
    owner_id_list.append(user['user_id'])
    owner_name_list.append(user['display_name'])
    for roster in rosters:
        # Save which roster id corresponds to an owner
        if user['user_id'] == roster['owner_id']:
            owner_roster_list.append(roster['roster_id'])
            
# Find owner for roster
roster_to_owner = {owner_roster_list[i]:owner_name_list[i] for i in range(len(owner_roster_list))}
roster_to_owner_sorted = {k: v for k, v in sorted(roster_to_owner.items(), key=lambda item: item[0])}
owners_sorted = list(roster_to_owner_sorted.values())

#standings = league.get_standings(rosters, users)

# A number of arrays will be created where the row specifies the owner and the 
# column specifies the week

points_arr = np.zeros((len(owner_roster_list), 17))
matchup_arr = np.zeros((len(owner_roster_list), 17))
win_arr = np.zeros((len(owner_roster_list), 17))
overall_win_arr = np.zeros((len(owner_roster_list), 17))
potential_points_arr = np.zeros((len(owner_roster_list), 17))
sleeper_points_arr = np.zeros((len(owner_roster_list), 17))

all_players = players.get_all_players()
# print('test')
weekly_matchup_list = np.array([])
weeks = 2
for week in range(weeks):
    weekly_matchup = league.get_matchups(week)
    week_stats = stats.get_week_stats('regular', 2019, week)
    
    # Using 
    weekly_scores = []
    weekly_wins = []
    
    for team in weekly_matchup:
        sleeper_points = team['points']
        sleeper_points_arr[team['roster_id']-1, week-1] = sleeper_points
        
        team_roster_id = team['roster_id']
        team_points = team['points'] # Sleeper's reported points
        team_players = team['players']
        team_starters = team['starters'] 
        team_matchup_id = team['matchup_id'] # Matchup id keeps track of who plays who
        
        matchup_arr[team['roster_id']-1, week-1] = team_matchup_id
        
        team_roster_info_df = pd.DataFrame({'Name': ['']*len(team_players),
                                           'Position': ['']*len(team_players),
                                           'Points': [0.0]*len(team_players),
                                           'Starter': [False]*len(team_players)},
                                           index = team_players)

        for player in team_players:
            # Going to loop through every player to get their info to add to the DataFrame
            if player in week_stats:
                # Get every player's position and points to calculate max points for
                player_name = all_players[player]['full_name']
                player_position = all_players[player]['position']
                
                # Calculate the player's points directly
                player_points = 0
                player_stats = week_stats[player]
                for stat in player_stats:
                    # Loop through all of the stats for the player, then multiply
                    # them by the corresponding rule and continuously add them
                    if stat in league_rules:
                        # Only check the stats that are important (i.e. don't care about snaps)
                        player_points += player_stats[stat]*round(league_rules[stat],6)
                
            else:
            # If the player was not active this week don't try to find their stats
                player_name = all_players[player]['full_name']
                player_position = all_players[player]['position']
                player_points = 0.0
            
            if player in team_starters:
                # Could also just have this as 
                # team_roster_info_df.at[player, 'Starter'] = True
                # below but this reads better I think
                player_starter = True
            else:
                player_starter = False
                
            # Now add them to the team_roster_info dataframe for potential points
            team_roster_info_df.at[player, 'Name'] = player_name
            team_roster_info_df.at[player, 'Position'] = player_position
            team_roster_info_df.at[player, 'Points'] = player_points
            team_roster_info_df.at[player, 'Starter'] = player_starter
        
        
        team_points = team_roster_info_df.loc[team_roster_info_df['Starter'] == True]['Points'].sum()
        points_arr[team['roster_id']-1, week-1] = team_points
        
        ############## Potential points calculation
        team_potential_points_df = pd.DataFrame({'Name': ['']*len(league_roster_list),
                                        'Position': ['']*len(league_roster_list),
                                        'Points': [0.0]*len(league_roster_list),
                                        'Starter': [False]*len(league_roster_list),
                                        'ID': ['']*len(league_roster_list)},
                                        index = league_roster_list)
        for position in league_roster_list:
            # These positions have the number after them, so split that off 
            # and then take the number to use for indexing
            
            raw_position = position.split(' ')[0]
            position_num = int(position.split(' ')[1]) - 1
            potential_points_starter = True
            if 'FLEX' in position and 'SUPER' not in position:
                # FLEX positions
                positions = ['RB', 'WR', 'TE']
            elif 'FLEX' in position and 'SUPER' in position:
                # SUPER FLEX positions
                positions = ['QB', 'RB', 'WR', 'TE']
            elif 'BN' in position:
                # Bench positions
                positions = ['QB', 'RB', 'WR', 'TE', 'K']
                potential_points_starter = False
            else:
                # Singleton positions
                positions = [raw_position]
                   
            # Now create a dataframe with all viable positions and then sort it
            # and take the top value that isn't already being used
            position_df = team_roster_info_df.loc[team_roster_info_df['Position'].isin(positions)]
            added = False
            while not added:
                if position_num >= len(team_roster_info_df):
                    # Because not everyone has a full roster only do this when
                    # they still have players
                    break
                    
                # Need to look through the players
                best_player = position_df.sort_values(by=['Points'], ascending=False).iloc[position_num]
                best_player_id = position_df.sort_values(by=['Points'], ascending=False).index[position_num]
                
                if best_player_id not in team_potential_points_df['ID'].values:
                    # If the player's id is not already added then we can add them to the dataframe
                    team_potential_points_df.at[position, 'Name'] = best_player['Name']
                    team_potential_points_df.at[position, 'Position'] = best_player['Position']
                    team_potential_points_df.at[position, 'Points'] = best_player['Points']
                    team_potential_points_df.at[position, 'Starter'] = potential_points_starter
                    team_potential_points_df.at[position, 'ID'] = best_player_id
                    added = True
                position_num += 1
        
        # Now that we have a dataframe that has the correct optimal lineup we 
        # can calculate the potential points
        team_potential_points = team_potential_points_df.loc[team_potential_points_df['Starter'] == True]['Points'].sum()
        potential_points_arr[team['roster_id']-1, week-1] = team_potential_points


###########################
points_df = pd.DataFrame(points_arr, index = owners_sorted)
potential_points_df = pd.DataFrame(potential_points_arr, index = owners_sorted)
summed_potential_points = pd.DataFrame(potential_points_df.sum(axis=1)).sort_values(by=0, ascending = False)

##########################
# for week in range(weeks):
#     # i represents the current team
#     for i in range(len(matchup_arr)):
        




