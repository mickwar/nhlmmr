import numpy as np

### Calculate the rating from the beginning

### Read in data

### Initial ratings

# Initialize the 30 teams in 2005 to all the same rating.
# When new teams come in (e.g. Vegas in 2017), use the current average rating
# across the league as the new team's starting rating.

# Arbitrarily chosen initial rating
# Since this is a zero-sum algorithm, this -should- be the average across time,
# perhaps deviating from the initial average as teams play a different number of
# games throughout the year
INITIAL_RATING = 2000

# K-factors for pre-, regular, and post-seasons
# So for every new season, there is higher volatility.
K_FACTOR_PRE = 32
K_FACTOR_REG = 16
K_FACTOR_POST = 8

# As dictionary
K_FACTOR = {'01' : 32, '02' : 16, '03' : 8}

ratings = {}

# Example initialization
ID = '6'
name = 'Boston Bruins'

ratings[ID] = {'name' : name,
               'ratingWins' : [INITIAL_RATING],
               'ratingShots' : [INITIAL_RATING],
               'ratingDiff' : [INITIAL_RATING],
               'season' : [],
               'gameType' : [],
               'gameNumber' : [],
               'time' : []
              }

# Use key 'time' for a standardized time object, makes for easier plotting later

# How to append
ratings['6']['ratingWins'].append(1300)
ratings['6']['time'].append(1)

def updateRatings(teamA, teamB, game):
    # teamA and teamB are dictionaries of previous ratings and games played
    # game is the outcome of the latest game

    # Calculate expected scores
    E_A = 1 / (1 + np.exp((teamB['ratingWins'] - teamA['ratingWins']) / (SIGMA * point_diff)))

    # Determine K-factor by gameType

    # Append new ratings and other info

    # Don't think I need to return anything, the appends should modify the
    # original dictionary


