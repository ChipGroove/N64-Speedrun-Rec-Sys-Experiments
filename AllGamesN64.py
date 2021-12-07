import json
import requests
import time

# find all official N64 Games on speedrun.com
all_games = []
data = requests.get('https://www.speedrun.com/api/v1/games?embed=categories&platform=w89rwelk&romhack=false&max=200', timeout = 10).json()

# Extract data for all official N64 Games with leaderboards on speedrun.com
while data['data']:
    for game in data['data']:
        # Set up new game entry for the dictionary
        entry = {}
        # Find name and speedrun.com internal ID
        entry['Name'] = game['names']['international']
        entry['ID'] = game['id']
        # Obtain leaderboard categories for the current game (Individual Levels excluded)
        categories = {}
        for category in game['categories']['data']:
            if category['type'] == 'per-game':
                # Obtain SRC leaderboard data
                cat_data = requests.get('https://www.speedrun.com/api/v1/leaderboards/'+game['id']+'/category/'+category['id']+'?embed=players', timeout = 60).json()
                # Set up category info
                info = {}
                info['ID'] = category['id']
                info['Players'] = []
                # Populate player information for each category on each leaderboard: players must be users on the site.
                for player in cat_data['data']['players']['data']:
                    if player['rel'] == 'user':
                        cur_player = {}
                        cur_player['Name'] = player['names']['international']
                        cur_player['ID'] = player['id']
                        info['Players'].append(cur_player)
                categories[category['name']] = info
            time.sleep(3)
        entry['Leaderboards'] = categories
        print(entry)
        all_games.append(entry)
    offset = data['pagination']['offset']
    size = data['pagination']['size']
    data = requests.get('https://www.speedrun.com/api/v1/games?embed=categories&platform=w89rwelk&romhack=false&max=200'+'&offset='+str(offset+size), timeout = 10).json()

# Save information to a JSON file
with open('all_games_N64.json', 'w') as fp:
    json.dump(all_games, fp)
