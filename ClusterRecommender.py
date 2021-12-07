import json
import math
import numpy as np
from numpy.random.mtrand import rand
from sklearn.metrics import silhouette_score

file = open('all_games_N64.json')
data = json.load(file)

# Use k-means clustering to recommend games
# Recommendations are made based on games in which similar users play
# Personalizes data to user

def recommend(user):
    recommendations = []

    # Obtain similarity vectors for each player
    players = generate_similarity_vectors(user)

    # Choose k using silhoutte method based on players
    silhouettes = []
    initial_assignment = []
    for k in [i+2 for i in range(9)]:
        # initialize k points
        initials = [0 for i in range(k)]
        clusters = [[] for i in range(k)]
        centroid_distances = []
        for i in range(k):
            randpoint = np.random.random_sample(len(players[user]))
            initials[i] = randpoint.tolist()
        # assign players to cluster: clusters contains list of names of similar players
        for player in players:
            distances = [math.dist(players[player],i) for i in initials]
            cluster = distances.index(min(distances))
            centroid_distances.append(min(distances))
            clusters[cluster].append(player)
        # check for any empty clusters, if one is empty, replace it with the data point with the highest error from largest cluster (furthest from centroid)
        while any([len(cluster)==0 for cluster in clusters]):
            empty_index = clusters.index([])
            largest_cluster = clusters[[len(x) for x in clusters].index(max([len(x) for x in clusters]))]
            largest_cluster_distances = [centroid_distances[i] for i in [list(players).index(player) for player in largest_cluster]]
            worst_point_index = largest_cluster_distances.index(max(largest_cluster_distances))
            clusters[empty_index].append(largest_cluster[worst_point_index])
            largest_cluster.remove(largest_cluster[worst_point_index])
        # turn clusters into lists of points with label array from model
        points = []
        labels = []
        i = 0
        for cluster in clusters:
            for player in cluster:
                points.append(players[player])
                labels.append(i)
            i += 1
        # compute silhouette score
        score = silhouette_score(points, labels, metric='euclidean')
        silhouettes.append(score)
        # update assignment if new highest silhouette score
        if silhouettes[k-2] == max(silhouettes):
            initial_assignment = [initials,points,labels]
    # Apply k-means clustering with chosen initial assignment
    final_assignment = k_means(initial_assignment[0],initial_assignment[1],initial_assignment[2])
    final_labels = final_assignment[1]
    # Use final labels to extract user cluster
    user_cluster = final_labels[list(players).index(user)]
    similar_players = [list(players)[i] for i in range(len(final_labels)) if final_labels[i] == user_cluster]
    candidate_games = []
    for game in data:
        for category in game['Leaderboards']:
            for player in game['Leaderboards'][category]['Players']:
                if player["Name"] in similar_players and player["Name"] is not user:
                    candidate_games.append(game["Name"])
    # Take up to 5 random games from similar games, note games have higher chances of appearing if more similar players play it
    if len(candidate_games) < 5:
        recommendations = candidate_games
    else:
        while len(recommendations) < 5:
            rand_val = np.random.randint(len(candidate_games))
            if candidate_games[rand_val] not in recommendations:
                recommendations.append(candidate_games[rand_val])
    return recommendations


def k_means(centroids, points, labels):
    k = len(centroids)
    threshold = 0.001
    origin = [0 for i in range(len(centroids[0]))]

    # compute initial centroid travel from origin
    travel = [math.dist(centroids[i],origin) for i in range(len(centroids))]

    # repeat new assignments until centroids dont move
    old_centroids = [origin for i in range(k)]
    new_centroids = [centroids[i] for i in range(k)]
    while sum(travel) > threshold:
        # create new centroids
        for i in range(k):
            old_centroids[i] = new_centroids[i]
            cur_cluster = [points[j] for j in range(len(points)) if labels[j]==i]
            if len(cur_cluster) > 1:
                cur_centroid = [sum(x)/len(x) for x in zip(*cur_cluster)]
            else:
                cur_centroid = cur_cluster[0]
            new_centroids[i] = cur_centroid
        # reassign labels
        distances = []
        for i in range(len(points)):
            cur_distances = [math.dist(points[i], j) for j in new_centroids]
            distances += cur_distances
            labels[i] = cur_distances.index(min(cur_distances))
        # check for missing labels
        while any([i not in labels for i in range(k)]):
            empty_cluster = [i not in labels for i in range(k)].index(True)
            worst_point_index = distances.index(max(distances))
            labels[worst_point_index] = empty_cluster
            distances[worst_point_index] = 0
        # determine centroid travel
        for i in range(k):
            travel[i] = math.dist(old_centroids[i],new_centroids[i])
    return [new_centroids, labels]

# Determine a vector of category presence for each player in games the specific user plays
# A match in games is assigned 1, a mismatch is assigned 0.
def generate_similarity_vectors(user):
    user_games = []
    for game in data:
        for category in game['Leaderboards']:
            for player in game['Leaderboards'][category]['Players']:
                if user == player["Name"] and game not in user_games:
                    user_games.append(game)
    # Get the names of all players
    players = {}
    for game in data:
        for category in game["Leaderboards"]:
            for player in game["Leaderboards"][category]["Players"]:
                if player["Name"] not in players.keys():
                    players[player["Name"]] = [0 for i in range(len(user_games))]
    # Make a vector for each player
    for cur_player in players:
        i = 0
        for game in user_games:
            for category in game["Leaderboards"]:
                for player in game["Leaderboards"][category]["Players"]:
                    if cur_player == player["Name"]:
                        players[cur_player][i] += 1
            i += 1
    return players

# Get all players
all_players = []
for game in data:
    for category in game["Leaderboards"]:
        for player in game["Leaderboards"][category]["Players"]:
            if player["Name"] not in all_players:
                all_players.append(player["Name"])
# Format output
randomlist = [all_players[i] for i in list(np.random.randint(len(all_players),size=5))]
for player in randomlist:
    recommended_games = recommend(player)
    print("\nGames we think you'll like, "+player+":\n")
    for i in range(len(recommended_games)):
        print(recommended_games[i])
