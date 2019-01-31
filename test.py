# -*- coding: utf-8 -*-
import requests
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

# Cornell League
leagueID = 1514235
seasonId = 2018

firstWeek = 1
lastWeek = 16

scores = {}
for week in range(1, 17):
    r = requests.get('http://games.espn.com/ffl/api/v2/scoreboard', 
                     params={'leagueId': leagueID, 'seasonId': seasonId, 'matchupPeriodId': week})
    scores[week] = r.json()
    

#print(scores[1]['scoreboard']['matchups'][0]['teams'][0]['score'])

# Location of score: scores[i]['scoreboard']['matchups'][j]['teams'][k]['score']
    # i keys: 1:16 (weeks in the season)
    # j index: 0:4 (teams/2)
    # k index: 0:1 (The two teams, unless there's a bye in the playoffs)

# Location of winner: scores[i]['scoreboard']['matchups'][j]['winner']
    # If this returns 'home' then the winner is
    # scores[i]['scoreboard']['matchups'][j]['teams'][0]
    # If it returns 'away' then the winner is
    # scores[i]['scoreboard']['matchups'][j]['teams'][1]

df = []
for key in scores:
    temp = scores[key]['scoreboard']['matchups']
    for match in temp:
        if len(match['teams'])==2:
            df.append([key, 
                   match['teams'][0]['team']['teamAbbrev'],
                   match['teams'][1]['team']['teamAbbrev'],
                   match['teams'][0]['team']['teamId'],
                   match['teams'][1]['team']['teamId'],
                   match['teams'][0]['score'],
                   match['teams'][1]['score']])
        else:
            df.append([key, match['teams'][0]['team']['teamAbbrev'],
                       'BYE',
                       match['teams'][0]['team']['teamId'],
                       0,
                       match['teams'][0]['score'],
                       float('nan')])

# 
df = pd.DataFrame(df, columns=['Week', 'HomeAbbrev', 'AwayAbbrev', 'HomeID', 'AwayID', 'HomeScore', 'AwayScore'])

# Rename the columns to not be home and away
df = (df[['Week', 'HomeAbbrev', 'HomeID', 'HomeScore']]
      .rename(columns={'HomeAbbrev': 'Team Abbrev', 'HomeID': 'Team ID', 'HomeScore': 'Score'})
      .append(df[['Week', 'AwayAbbrev', 'AwayID', 'AwayScore']]
             .rename(columns={'AwayAbbrev': 'Team Abbrev', 'AwayID': 'Team ID', 'AwayScore': 'Score'}))
     )

# Sort by week and then reindex
df = df.sort_index(ascending=True)
df = df.reset_index(drop=False)

# Retain the matchup so that points against can be calculated
df = df[['index', 'Week', 'Team Abbrev', 'Team ID', 'Score']].rename(columns={'index': 'Matchup'})

## Calculating the overall wins
#for week in weeks:
#    
