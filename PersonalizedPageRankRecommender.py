import json
import numpy as np
import collections

file = open('all_games_N64.json')
data = json.load(file)

# return a list of all players from the data
def find_players(data):
    players = []
    for game in data:
        for category in game["Leaderboards"]:
            for player in game["Leaderboards"][category]["Players"]:
                players.append(player["Name"])
    return list(set(players))

# create a weighted adjacency matrix for the games in the data
# games are adjacent if there exists a player who plays both games
# loops omitted
def make_network(data):
    adj = [[0 for i in range(len(data))] for i in range(len(data))]
    for i in range(len(data)):
        for j in range(i+1,len(data)):
            # get first games users
            boards_a = [list(data)[i]["Leaderboards"][category]["Players"] for category in data[i]["Leaderboards"]]
            users_a = set([player["Name"] for leaderboard in boards_a for player in leaderboard])
            # get second games users
            boards_b = [list(data)[j]["Leaderboards"][category]["Players"] for category in data[j]["Leaderboards"]]
            users_b = set([player["Name"] for leaderboard in boards_b for player in leaderboard])
            # establish connection if any overlap
            for player in list(users_a & users_b):
                adj[i][j] += 1
                adj[j][i] += 1
        # fill row with 1s if there was no overlap
        if all([adj[i][j] == 0] for j in range(len(adj[i]))):
            adj[i] = [1 for j in range(len(adj[i]))] 
    return adj

def random_walk(matrix, start_node, stop_chance):
    teleport_chance = 0.85
    # Randomly walk until stop
    walk = [start_node]
    flag = np.random.random()
    while flag > stop_chance:
        # Chance to teleport to a random node
        teleport = np.random.random()
        if teleport < teleport_chance:
            next_locations = matrix[walk[-1]]
            choices = []
            for i in range(len(next_locations)):
                choices.append([i for k in range(next_locations[i])])
            choices = [x for l in choices for x in l]
            walk.append(np.random.choice(choices))
        else:
            walk.append(np.random.randint(len(matrix)))
        flag = np.random.random()
    # Determine index of destination and return
    return walk[-1]

def recommend(user_games):
    # Get start indices from user games
    start_nodes = []
    for game in user_games:
        start_nodes.append(all_games.index(game))
    # Make 1000 walks from each start node, record result from each
    results = []
    for node in start_nodes:
        for i in range(1000):
            results.append(random_walk(network,node,0.1))
    frequencies = collections.Counter(results)
    candidates = frequencies.most_common()
    # Recommend top 5 candidates not in user games
    recommended = []
    i = 0
    while len(recommended) < 5:
        if all_games[candidates[i][0]] not in user_games:
            recommended.append(all_games[candidates[i][0]])
        i += 1
    return recommended

def get_user_games(user):
    # Get user games
    user_games = []
    for game in data:
        for category in game["Leaderboards"]:
            for player in game["Leaderboards"][category]["Players"]:
                if player["Name"] == user and game["Name"] not in user_games:
                    user_games.append(game["Name"])
    return user_games
    
players = find_players(data)
network = make_network(data)
all_games = [game["Name"] for game in data]
# Generate 5 random users to recommend games
# Format output
randomlist = [players[i] for i in list(np.random.randint(len(players),size=5))]
for player in randomlist:
    recommended_games = recommend(get_user_games(player))
    print("\nGames we think you'll like, "+player+":\n")
    for i in range(len(recommended_games)):
        print(recommended_games[i])