#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 16:42:38 2019

@author: corey
"""

from sleeper_wrapper import League
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

league_id = 438058453903077376

league = League(league_id)

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


#standings = league.get_standings(rosters, users)

# A number of arrays will be created where the row specifies the owner and the 
# column specifies the week

score_arr = np.zeros((len(owner_roster_list), 16))
win_arr = np.zeros((len(owner_roster_list), 16))
overall_win_arr = np.zeros((len(owner_roster_list), 16))

weekly_matchup_list = np.array()
for week in range(1, 2):
    weekly_matchup = league.get_matchups(week)
    
    # Using 
    weekly_scores = []
    weekly_wins = []
    for team in weekly_matchup:
        
        
        
        
        
        
        
        
        
        