# https://gitlab.com/dword4/nhlapi
# https://gitlab.com/dword4/nhlapi/blob/master/stats-api.md

# Game ID explanation
# The first 4 digits identify the season of the game (ie. 2017 for the 2017-2018
# season). The next 2 digits give the type of game, where 01 = preseason,
# 02 = regular season, 03 = playoffs, 04 = all-star. The final 4 digits identify
# the specific game number. For regular season and preseason games, this ranges
# from 0001 to the number of games played. (1271 for seasons with 31 teams (2017
# and onwards) and 1230 for seasons with 30 teams). For playoff games, the 2nd
# digit of the specific number gives the round of the playoffs, the 3rd digit
# specifies the matchup, and the 4th digit specifies the game (out of 7).


import requests
import json
import os.path

# Endpoint
ENDPOINT = "https://statsapi.web.nhl.com/api/v1/game/{ID}/boxscore"
DATA_PATH = "data/games.csv"


if not os.path.exists(DATA_PATH):
    with open(DATA_PATH, "a") as f:
        f.write("gameId;awayId;awayName;awayGoals;awayShots;awayTakeGiveDiff;homeId;homeName;homeGoals;homeShots;homeTakeGiveDiff")


# Consecutive bad attempts
badAttempts = 0
maxBadAttempts = 5
abortFlag = 0
maxAbort = 3

# Starting points for the data
season = 2005       # The year after the lock-out, first year of Crosby
gameType = 1
gameNumber = 0

playoffsRound = 4   # goes 1 to 4
playoffsMatchUp = 1 # goes 1 to 8, depending on round (i.e., 2 ^ (4 - Round))
                    # gameNumber will max at 7

with open(DATA_PATH, "a") as f:

    # When the number of bad attempts reaches the maximum a total
    # of `maxAbort` times in a row, then exit the while loop
    while abortFlag < maxAbort:

        gameNumber += 1

        # Pre-season and regular season
        if gameType == 1 or gameType == 2:
            gameId = str(season) + "{:02d}".format(gameType) + "{:04d}".format(gameNumber)

        # Playoffs
        if gameType == 3:
            gameId = str(season) + "{:02d}".format(gameType) + \
                "0" + str(playoffsRound) + str(playoffsMatchUp) + str(gameNumber)

        print("Fetching data for game Id: {}".format(gameId))
        resp = requests.get(ENDPOINT.format(ID = gameId))
        data = json.loads(resp.content)

        # Got a good request
        # Using data["officials"] as a proxy for whether the game has been played
        if resp.ok and data["officials"]:
            print("--- Success") 

            # In case something is wrong with the data retrieved
            try:

                # Organize the data I want and append to data file
                line = "\n" + ";".join([
                    gameId,
                    str(data['teams']['away']['team']['id']),
                    str(data['teams']['away']['team']['name']),
                    str(data['teams']['away']['teamStats']['teamSkaterStats']['goals']),
                    str(data['teams']['away']['teamStats']['teamSkaterStats']['shots']),
                    str(data['teams']['away']['teamStats']['teamSkaterStats']['takeaways'] - \
                        data['teams']['away']['teamStats']['teamSkaterStats']['giveaways']),
                    str(data['teams']['home']['team']['id']),
                    str(data['teams']['home']['team']['name']),
                    str(data['teams']['home']['teamStats']['teamSkaterStats']['goals']),
                    str(data['teams']['home']['teamStats']['teamSkaterStats']['shots']),
                    str(data['teams']['home']['teamStats']['teamSkaterStats']['takeaways'] - \
                        data['teams']['home']['teamStats']['teamSkaterStats']['giveaways'])
                    ])

                f.write(line)

                # Reset all attempt markers
                badAttempts = 0
                abortFlag = 0

            except:
                print("--- Error: something went wrong with processing the requests")
                badAttempts += 1

        else:
            # Something's missing or we need to move to the next iteration
            print("--- Failed") 
            badAttempts += 1

            if badAttempts < maxBadAttempts:
                pass

            else:
                # Increment gameType or Season
                badAttempts = 0
                gameNumber = 0

                if gameType == 1:
                    print("--- Going from pre-season to regular season")
                    gameType = 2

                elif gameType == 2:
                    print("--- Going from regular season to playoffs")
                    gameType = 3
                    playoffsRound = 1
                    playoffsMatchUp = 1

                elif gameType == 3:
                    # Need to increment through the playoff rounds before changing gameType
                    # Check if need to go to next match up
                    if playoffsMatchUp < 2 ** (4 - playoffsRound):
                        playoffsMatchUp += 1
                        continue

                    # Check if need to go to next round
                    if playoffsRound < 4:
                        playoffsRound += 1
                        playoffsMatchUp = 1
                        continue

                    # If neither, then go to next season (this will only
                    # be run if no `continue` has been executed)
                    season += 1
                    gameType = 1
                    playoffsRound = 1
                    playoffsMatchUp = 1
                    print("--- Going to next season: {}".format(season))

                # Increment number of times reached maxBadAttempts
                abortFlag += 1

