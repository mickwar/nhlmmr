import numpy as np
import pandas as pd

### Calculate the rating from the beginning

### Read in data
df = pd.read_csv("data/games.csv", delimiter = ";")

### Initial ratings

# Initialize the 30 teams in 2005 to all the same rating.
# When new teams come in (e.g. Vegas in 2017), use the current average rating
# across the league as the new team's starting rating.

# Arbitrarily chosen initial rating
# Since this is a zero-sum algorithm, this -should- be the average across time,
# perhaps deviating from the initial average as teams play a different number of
# games throughout the year
INITIAL_RATING = 2000

# "Standard deviation"
SIGMA = 400

# K-factors for pre-, regular, and post-seasons
# These K-factors may seem high, but since we're using the point differential
# in computing the observed scores, we need to inflate the rating adjustments
# a bit. A win doesn't always give a 1, instead it gives something like 0.66
# if you win by 1 and 0.8 if you win by 2. Thus, the K only tells you the
# maximum rating points you can win, not what you will get. (The max rating
# change occurs if a team wins by scoring an infinite number of points over the
# other team.)
# 'New' should maybe last about 10 games? Unclear
K_FACTOR = {'New': 200, '01' : 100, '02' : 60, '03' : 40}


# Example initialization
#df.head(100)[['awayId', 'awayName']]
#df.head(100)['awayId']
#len(df.head(100)['awayId'].unique()

ratings = {}

initialTeams = df.head(100).drop_duplicates(['awayId', 'awayName'])[['awayId', 'awayName']]

for team in initialTeams.values:
    ratings[team[0]] = {'name' : team[1],
                   'initialRating' : INITIAL_RATING,
                   'ratingWins' : [],
                   'ratingShots' : [],
                   'ratingDiff' : [],
                   'season' : [],
                   'gameType' : [],
                   'gameNumber' : [],
                   'time' : []
                  }


# Use key 'time' for a standardized time object, makes for easier plotting later

# First 400 games
for i in range(400):
    game = df.values[i]
    updateRatings(ratings, game)

#for r in ratings:
#    print(ratings[r]['name'], ' '*(21 - len(ratings[r]['name'])), ratings[r]['ratingWins'][-10:])


def updateRatings(ratings, game):
    teamA = ratings[game[1]]
    teamB = ratings[game[6]]

    season = str(game[0])[0:4]
    gameType = str(game[0])[4:6]
    gameNumber = str(game[0])[6:10]
    # teamA and teamB are dictionaries of previous ratings and games played
    # game is the outcome of the latest game

    # If game has a new team, it needs to be added to ratings

    # Get ratings
    R_A = teamA['initialRating'] if len(teamA['ratingWins']) == 0 else teamA['ratingWins'][-1]
    R_B = teamB['initialRating'] if len(teamB['ratingWins']) == 0 else teamB['ratingWins'][-1]

    # Observed goals
    S_A = game[3]
    S_B = game[8]

    # Calculate expected scores
    E_A = 1 / (1 + np.exp((R_B - R_A) / SIGMA))
    E_B = 1 - E_A

    # Observed scores
    O_A = 1 / (1 + 2 ** ((S_B - S_A)))
    O_B = 1 - O_A

    # (The term "scores" for E_* and O_* relates to the logistic curve,
    # not the actual goals scored in the game)

    # Determine K-factor by gameType
    K_A = K_FACTOR['New'] if len(teamA['ratingWins']) <= 30 else K_FACTOR[gameType]
    K_B = K_FACTOR['New'] if len(teamB['ratingWins']) <= 30 else K_FACTOR[gameType]

    # Append new ratings and other info
    # Make sure to always adjust as integers
    teamA['ratingWins'].append(int(R_A + K_A * (O_A - E_A)))
    teamB['ratingWins'].append(int(R_B + K_B * (O_B - E_B)))

    teamA['season'].append(season)
    teamA['gameType'].append(gameType)
    teamA['gameNumber'].append(gameNumber)

    teamB['season'].append(season)
    teamB['gameType'].append(gameType)
    teamB['gameNumber'].append(gameNumber)

    # Do need to return anything, the appends modify the original dictionary


