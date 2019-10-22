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
maxBadAttempts = 3
abortFlag = 0
maxAbort = 2

# Starting points for the data
season = 2017
gameType = 1
gameNumber = 0


with open(DATA_PATH, "a") as f:

    # When the number of bad attempts reaches the maximum a total
    # of `maxAbort` times in a row, then exit the while loop
    while abortFlag < maxAbort:

        gameNumber += 1
        gameId = str(season) + "{:02d}".format(gameType) + "{:04d}".format(gameNumber)

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
                    str(data['teams']['away']['teamStats']['teamSkaterStats']['takeaways'] - data['teams']['away']['teamStats']['teamSkaterStats']['giveaways']),
                    str(data['teams']['home']['team']['id']),
                    str(data['teams']['home']['team']['name']),
                    str(data['teams']['home']['teamStats']['teamSkaterStats']['goals']),
                    str(data['teams']['home']['teamStats']['teamSkaterStats']['shots']),
                    str(data['teams']['home']['teamStats']['teamSkaterStats']['takeaways'] - data['teams']['home']['teamStats']['teamSkaterStats']['giveaways'])
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
                else:
                    gameType = 1
                    season += 1
                    print("--- Going to next season: {}".format(season))

                # Increment number of times reached maxBadAttempts
                abortFlag += 1

