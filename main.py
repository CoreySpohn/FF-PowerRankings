# -*- coding: utf-8 -*-
import requests
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import os
scriptDir = os.path.dirname(__file__)


league = 'LOF'
year = 2018
if league == 'MAE':
    # Mechanical Aerospace Engineering
    leagueID = 1514235

elif league == 'LOF':
    # League of Futons
    leagueID = 707792

elif league == 'HRN':
    # Herndon League
    leagueID = 1395395
    
teamIDs = list(pd.read_csv(league+str(year)+'Owners.csv',header=None).values.tolist()[0])
firstWeek = 1
lastWeek = 16
playoffStartWeek = 14
weeks = list(range(firstWeek,lastWeek+1))
path = league + str(year) + 'ROS.csv'
ROSPath = os.path.join(scriptDir, path)

# Power ranking values
numOfRecentWeeks = 4 # Number of recent weeks to use for power rankings
winsWeight = 50
overallWinsWeight = 300
recentOverallWinsWeight = 250
pointsScoredWeight = 200
recentPointsScoredWeight = 150
ROSWeight = 5

scores = {}
for week in weeks:
    r = requests.get('http://games.espn.com/ffl/api/v2/scoreboard', 
                     params={'leagueId': leagueID, 'seasonId': year, 'matchupPeriodId': week})
    scores[week] = r.json()

###############################################################################
# Examples of using the scores json file
# Location of score: scores[i]['scoreboard']['matchups'][j]['teams'][k]['score']
    # i keys: 1:16 (weeks in the season)
    # j index: 0:4 (teams/2)
    # k index: 0:1 (The two teams, unless there's a bye in the playoffs)

# Location of winner: scores[i]['scoreboard']['matchups'][j]['winner']
    # If this returns 'home' then the winner is
    # scores[i]['scoreboard']['matchups'][j]['teams'][0]
    # If it returns 'away' then the winner is
    # scores[i]['scoreboard']['matchups'][j]['teams'][1]
###############################################################################

df = []
for key in scores:
    temp = scores[key]['scoreboard']['matchups']
    for match in temp:
        if match['bye']==False:
            # 'Home' team in the matchup
            if match['winner'] == 'home':
                home = 1
                away = 0
            else:
                home = 0
                away = 1
            
            df.append([key, 
                   match['teams'][0]['team']['teamAbbrev'],
                   match['teams'][0]['team']['teamId'],
                   match['teams'][1]['team']['teamId'],
                   home,
                   match['teams'][0]['score']-match['teams'][1]['score'],
                   match['teams'][0]['score'],
                   match['teams'][1]['score']])
            df.append([key, 
                   match['teams'][1]['team']['teamAbbrev'],
                   match['teams'][1]['team']['teamId'],
                   match['teams'][0]['team']['teamId'],
                   away,
                   match['teams'][1]['score']-match['teams'][0]['score'],
                   match['teams'][1]['score'],
                   match['teams'][0]['score']])
        else:
            # Byes in the playoffs count as a win with 0 Points against
            df.append([key, match['teams'][0]['team']['teamAbbrev'],
                       match['teams'][0]['team']['teamId'],
                       match['teams'][0]['team']['teamId'],
                       1,
                       0,
                       match['teams'][0]['score'],
                       0])

# Renamce the columns
df = pd.DataFrame(df, columns=['Week', 'Team Abbrev', 'Team ID', 'Opponnent ID', 'Win', 'Point Differential', 'Points For', 'Points Against'])

# Add owner names
owners = []
opponnents = []
for i in range(0,len(df)):
    ID = df['Team ID'][i]
    opponnentID = df['Opponnent ID'][i]
    owners.append(teamIDs[ID-1])
    opponnents.append(teamIDs[opponnentID-1])
df['Team Owner'] = owners
df['Opponnent'] = opponnents


# Overall wins calculation
totalWins = []
for week in weeks:
    # Create a temp dataframe for the current week
    weekdf = df.loc[df['Week'] == week]
    for i in range(len(weekdf)*(week-1),len(weekdf)*(week-1)+len(weekdf)):
        # Basically the range is 0-9 for week 1, 10-19 week 2, etc but works if your league has more/less than 10
        pfi = weekdf['Points For'][i] # Points for of current team
        wins = 0
        for j in range(len(weekdf)*(week-1),len(weekdf)*(week-1)+len(weekdf)):
            pfj = weekdf['Points For'][j] # Points For of comparison team
            if pfi > pfj:
                wins += 1
        totalWins.append(wins)
df['Overall Wins'] = totalWins


# Reorder the columns
df = pd.DataFrame(df, columns=['Week', 'Team Owner', 'Team Abbrev', 'Team ID', 'Opponnent', 'Opponnent ID', 'Win', 'Point Differential', 'Overall Wins', 'Points For', 'Points Against'])

# Running total of points
totPtsFor = []
avgPtsFor = []
totPtsAga = []
avgPtsAga = []
recTotPtsFor = []
recAvgPtsFor = []
recTotPtsAga = []
recAvgPtsAga = []
totOverallWins = []
recOverallWins = []
totWins = []
recWins = []

for i in range(0,len(df)):
    # Create a temp dataframe of current size
    tempdf = df[0:i+1]
    owner = tempdf['Team Owner'][i]
    week = tempdf['Week'][i]
    persondf = tempdf.loc[tempdf['Team Owner'] == owner]
    
    # Calculate total points values
    tempTotPtsFor = sum(persondf['Points For'])
    tempAvgPtsFor = tempTotPtsFor/week
    tempTotPtsAga = sum(persondf['Points Against'])
    tempAvgPtsAga = tempTotPtsAga/week
    
    # Calculate recent points values
    tempRecTotPtsFor = sum(persondf.tail(numOfRecentWeeks)['Points For'])
    tempRecAvgPtsFor = tempRecTotPtsFor/min(week,numOfRecentWeeks)
    tempRecTotPtsAga = sum(persondf.tail(numOfRecentWeeks)['Points Against'])
    tempRecAvgPtsAga = tempRecTotPtsAga/min(week,numOfRecentWeeks)
    
    # Store the values
    totPtsFor.append(tempTotPtsFor)
    avgPtsFor.append(tempAvgPtsFor)
    totPtsAga.append(tempTotPtsAga)
    avgPtsAga.append(tempAvgPtsAga)
    
    recTotPtsFor.append(tempRecTotPtsFor)
    recAvgPtsFor.append(tempRecAvgPtsFor)
    recTotPtsAga.append(tempRecTotPtsAga)
    recAvgPtsAga.append(tempRecAvgPtsAga)
    
    # Cumulative overall wins
    totOverallWins.append(sum(persondf['Overall Wins']))
    recOverallWins.append(sum(persondf.tail(numOfRecentWeeks)['Overall Wins']))
    
    # Cumulative wins
    totWins.append(sum(persondf['Win']))
    recWins.append(sum(persondf.tail(numOfRecentWeeks)['Win']))

# Add the values to the dataframe
df['Total Points For'] = totPtsFor
df['Average Points For'] = avgPtsFor
df['Total Points Against'] = totPtsAga
df['Average Points Against'] = avgPtsAga

df['Recent Points For'] = recTotPtsFor
df['Recent Average Points For'] = recAvgPtsFor
df['Recent Points Against'] = recTotPtsAga
df['Recent Average Points Against'] = recAvgPtsAga

df['Total Overall Wins'] = totOverallWins
df['Recent Overall Wins'] = recOverallWins

df['Total Wins'] = totWins
df['Recent Wins'] = recWins

# Rest of season roster strength
rosStrCsv = pd.read_csv(ROSPath)
rosStrList = []
for i in range(0,len(df)):
    week = df['Week'][i]
    teamID = df['Team ID'][i]
    tempRosStr = rosStrCsv[str(week)][teamID-1]
    rosStrList.append(tempRosStr)
df['Roster Strength'] = rosStrList

# Power ranking
powerLevel = []
for i in range(0,len(df)):
    week = df['Week'][i]
    wins = winsWeight*df['Total Wins'][i]/week
    overallWins = overallWinsWeight*df['Total Overall Wins'][i]/(week*(len(teamIDs)-1))
    recentOverallWins = (min(numOfRecentWeeks,week)/numOfRecentWeeks)*recentOverallWinsWeight*df['Recent Overall Wins'][i]/(min(numOfRecentWeeks,week)*9)
    
    weekdf = df.loc[df['Week']==week]
    avgPointsScored = np.mean(weekdf['Average Points For'])
    pointsScored = pointsScoredWeight*(df['Average Points For'][i]/avgPointsScored)**2
    avgRecPointsScored = np.mean(weekdf['Recent Average Points For'])
    recentPointsScored = (min(numOfRecentWeeks,week)/numOfRecentWeeks)*recentPointsScoredWeight*(df['Recent Average Points For'][i]/avgRecPointsScored)**2
    
    rosStr = ROSWeight*(11-df['Roster Strength'][i])
    powerLevel.append(wins+overallWins+recentOverallWins+pointsScored+recentPointsScored+rosStr)
    
df['Power Level'] = powerLevel

# Power Rank calculation
powerRanks = []
for week in weeks:
    # Create a temp dataframe for the current week
    weekdf = df.loc[df['Week'] == week]
    for i in range(len(weekdf)*(week-1),len(weekdf)*(week-1)+len(weekdf)):
        # Basically the range is 0-9 for week 1, 10-19 week 2, etc but works if your league has more/less than 10
        pLi = weekdf['Power Level'][i] # Power Level for of current team
        powerRank = 1
        for j in range(len(weekdf)*(week-1),len(weekdf)*(week-1)+len(weekdf)):
            pLj = weekdf['Power Level'][j] # Power Level of comparison team
            if pLi < pLj:
                powerRank += 1
        powerRanks.append(powerRank)
df['Power Rank'] = powerRanks

# Playoff seeding
# Rules: Top 4 teams in the standings with points for as tie break
# 5th seed is the team with the highest points for remaining
# 6th seed is the team with the highest power level remaining
# Get the teams that will be in the playoffs, sort them by total wins and then total points for
seedList = []
for week in weeks:
    if week < playoffStartWeek:
        weekdf = df.loc[df['Week'] == week].sort_values(['Total Wins','Total Points For'], ascending=[False, False])
        playoffTeams = list(weekdf.head(4).iloc[:,1]) # Get just the names of the top teams by ESPN's metric
        fifth = weekdf.loc[~df['Team Owner'].isin(playoffTeams)].sort_values('Total Points For', ascending=False).head(1).iloc[0,1]
        playoffTeams.append(str(fifth)) # Get the team with the most remaining points for
        sixth = weekdf.loc[~df['Team Owner'].isin(playoffTeams)].sort_values('Power Level', ascending=False).head(1).iloc[0,1]
        playoffTeams.append(str(sixth)) # Get the team with the highest power level remaining
        
        consolationTeams = list(weekdf.loc[~weekdf['Team Owner'].isin(playoffTeams)].sort_values(['Total Wins','Total Points For'], ascending=[False, False])['Team Owner'])
        seeding = playoffTeams + consolationTeams
        
        weekdf = df.loc[df['Week'] == week] # remake it so that it isn't sorted
        for owner in weekdf['Team Owner']:
            seedList.append(seeding.index(owner)+1)
        
    else:
        # Don't change the seeds in the playoffs
        weekdf = df.loc[df['Week'] == week] # remake it so that it isn't still sorted
        for owner in weekdf['Team Owner']:
            seedList.append(seeding.index(owner)+1)
df['Playoff Seed'] = seedList

# Determine how the playoffs went
# Seeds 1 and 2 get a bye
# Quarterfinal 1: Seed 3 plays seed 6
# Quarterfinal 2: Seed 4 plays seed 5
# Semi-final 1: Winner of QF2 plays seed 1
# Semi-final 2: Winner of QF1 plays seed 2
# Semi-final winners: Play for championship
# QF losers play the last 2 weeks, the person with more total points after 2 weeks gets 5th
# SF losers play the last week, person with more points gets 3rd
playoffWeeks = list(range(playoffStartWeek, lastWeek+1))
playoffdf = df.loc[df['Week'].isin(playoffWeeks)]


################
## Some stats ##
################
# Highest scoring week
#highPtsId = df['Points For'].idxmax()
#print('Highest score: ')
#print(df['Team Owner'][highPtsId])
#print('scored')
#print(df['Points For'][highPtsId])
#print('points week')
#print(df['Week'][highPtsId])
#
## Lowest scoring week
#lowPtsId = df['Points For'].idxmin()
#print('\nLowest score: ')
#print(df['Team Owner'][lowPtsId])
#print('scored')
#print(df['Points For'][lowPtsId])
#print('points week')
#print(df['Week'][lowPtsId])

# Highest
largeFont = 20
mediumFont = 15
smallFont = 12

# Power Level Graph
fig0 = plt.figure(0)
for name in teamIDs:
    persondf = df.loc[df['Team Owner'] == name]
    plt.plot(persondf['Week'], persondf['Power Level'])
plt.legend(teamIDs, loc='upper left', bbox_to_anchor=(1, 1), fontsize=14)
plt.xlabel('Week', fontsize=20)
plt.ylabel('Power Level', fontsize=20)
plt.xticks(weeks)

#fig0.savefig('Power Level.png',format='png', dpi=720, bbox_inches='tight', pad_inches=0.1)


# Points For
fig1 = plt.figure(1)
for name in teamIDs:
    persondf = df.loc[df['Team Owner'] == name]
    plt.plot(persondf['Week'], persondf['Average Points For'])

plt.legend(teamIDs, loc='upper left', bbox_to_anchor=(1, 1), fontsize=14)
plt.xlabel('Week', fontsize=20)
plt.ylabel('Average Points For', fontsize=20)
plt.xticks(weeks)    
#fig1.savefig('Points For.png',format='png', dpi=720, bbox_inches='tight', pad_inches=0.1)


# Worst stretch
i = df['Recent Points Against'].idxmax() # Get line of most points against
owner = df['Team Owner'][i] # Get that persons name
recentWeeks = list(range(df['Week'][i]-numOfRecentWeeks+1,df['Week'][i]+1)) 
persondf = tempdf.loc[tempdf['Team Owner'] == owner] # Create temp dataframe of only that person
persondf = persondf.loc[persondf['Week'].isin(recentWeeks)] # Trim dataframe to only include the desired weeks

getFuckedPerson = [] # Create lists for the graph of opponnent, number of points and which week
getFuckedPoints = []
getFuckedWeeks = []
for i in range(0,len(persondf)):
    getFuckedPerson.append(persondf.iloc[i]['Opponnent'])
    getFuckedPoints.append(persondf.iloc[i]['Points Against'])
    getFuckedWeeks.append(persondf.iloc[i]['Week'])

# Get the rest of the leagues values
recentLeaguedf = df.loc[df['Week'].isin(recentWeeks)].loc[df['Team Owner'] != owner]
leaguePointsAgainst = []
for week in recentWeeks:
    leaguePointsAgainst.append(np.mean(recentLeaguedf.loc[recentLeaguedf['Week'] == week]['Points Against']))
fig2 = plt.figure(2)
ax = fig2.add_subplot(111)
plt.xlabel('Week')
plt.ylabel('Points Against')
plt.title(owner + ' got fucked', fontsize=20)
plt.xticks(recentWeeks)
plt.plot(getFuckedWeeks,getFuckedPoints)
plt.plot(getFuckedWeeks,leaguePointsAgainst)
plt.legend([owner, 'League Average'], loc='upper left', bbox_to_anchor=(1, 0.6), fontsize=14)
for i, txt in enumerate(getFuckedPerson):
    ax.annotate(txt, xy = (getFuckedWeeks[i],getFuckedPoints[i]), fontsize=14)
plt.show()
#fig2.savefig('Get fucked.png',format='png', dpi=720, bbox_inches='tight', pad_inches=0.1)


# Points scored for each playoff team
fig3 = plt.figure(3)
playoffWeeks = list(range(playoffStartWeek,lastWeek+1))
playoffdf = df.loc[df['Week'].isin(playoffWeeks)].loc[df['Team Owner'].isin(playoffTeams)]
for name in playoffTeams:
    persondf = playoffdf.loc[df['Team Owner'] == name]
    plt.plot(persondf['Week'], persondf['Points For'])

plt.legend(playoffTeams, loc='upper left', bbox_to_anchor=(1, 1), fontsize=14)
plt.xlabel('Week', fontsize=20)
plt.ylabel('Playoff Points', fontsize=20)
plt.xticks(playoffWeeks)
#fig3.savefig('Points For.png',format='png', dpi=720, bbox_inches='tight', pad_inches=0.1)


# Playoff seed plot
fig4 = plt.figure(4)
for name in teamIDs:
    persondf = df.loc[df['Team Owner'] == name].loc[df['Week'].isin(list(range(1,playoffStartWeek)))]
    plt.plot(persondf['Week'], persondf['Playoff Seed'])
plt.legend(teamIDs, loc='upper left', bbox_to_anchor=(1, 1), fontsize=14)
plt.xlabel('Week', fontsize=20)
plt.ylabel('Playoff Seed', fontsize=20)
plt.ylim(len(teamIDs)+1,0)
plt.yticks(list(range(1,11)))
plt.xticks(list(range(1,playoffStartWeek)))