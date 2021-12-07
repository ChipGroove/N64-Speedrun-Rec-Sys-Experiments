import json
import random

file = open('all_games_N64.json')
data = json.load(file)

# Use Apriori Algorithm to generate candidate sets
# "Transactions" are represented as players "purchasing" categories by having a posted time in said category.

def recommend(Name):
    confidence_threshold = 0.01
    recommendations = {}
    candidates = []

    # Determine frequent itemsets which contain categories our user plays
    for freqset in significant_sets:
        if any(elem in freqset for elem in player_categories[Name]) and len(freqset) > 1:
            candidates.append(freqset)

    # Find Association rules
    for candidate in candidates:
    # Split candidate into known user categories and potential recommended categories
        L1 = [x for x in candidate if x in player_categories[Name]]
        L2 = [x for x in candidate if x not in player_categories[Name]]
        L1_freq, L1_support, L1item_freq, L1item_support = 0, 0, 0, 0
        # Determine support and confidence for each category the user doesn't play
        for item in L2:
            for transaction in transactions:
                if all(elem in transaction for elem in L1):
                    L1_freq += 1
                if all(elem in transaction for elem in L1) and item in transaction:
                    L1item_freq += 1
            L1_support = L1_freq/len(transactions)
            L1item_support = L1item_freq/len(transactions)
            confidence = L1item_support/L1_support
            if item not in recommendations.keys():
                recommendations[item] = [confidence]
            else:
                recommendations[item].append(confidence)

    # Allow max value to represent recommendation confidence
    for item in recommendations:
        if max(recommendations[item]) >= confidence_threshold:
            recommendations[item] = max(recommendations[item])
        else:
            del recommendations[item]
    
    # Convert recommendations dictionary to list ordered by confidence
    recommendations_list = list(recommendations.items())
    recommendations_list.sort(key = lambda x: x[1], reverse=True)

    # format output
    if recommendations_list == []:
        print("\nNo recommendations available for user "+Name)
    else:
        print("\nTop recommendations for user: "+Name+" (up to top 5 if available)\n")
        stop = min(5,len(recommendations_list))
        for i in range(stop):
            print(str(i+1)+": "+recommendations_list[i][0])

# Generate set of transactions by associating categories to the player's username
player_categories = {}
transactions = []
for game in data:
    for category in game['Leaderboards']:
        for player in game['Leaderboards'][category]['Players']:
            if player['Name'] in player_categories.keys():
                player_categories[player['Name']].append((game['Name'] + '; ' + category))
            else:
                player_categories[player['Name']] = [(game['Name'] + '; ' + category)]
for player in player_categories:
    transactions.append(player_categories[player])

# Use Apriori algorithm to find frequent categories
support_threshold = 0.005
significant_items = [] # List of significant items
significant_sets = [] # List of significant sets

# Create list of significant items
frequencies = {}
for set in transactions:
    for item in set:
        if item not in frequencies.keys():
            frequencies[item] = 0
        frequencies[item]+=1
for item in frequencies:
    support = frequencies[item]/len(player_categories)
    if support >= support_threshold:
        significant_items.append(item)
significant_items = sorted(significant_items)


# Create list of significant sets from significant items
for item in significant_items:
    significant_sets.append([item])

num_items = len(significant_items)

# Create Candidate sets from previous sets and evaluate
for i in range(2,num_items):
    # Find frequent sets of size i-1
    prev_sets = [x for x in significant_sets if len(x)==i-1]
    if prev_sets == []:
        break
    # Generate candidate sets
    for cur_set in prev_sets:
        # Find index of last item in set
        indices = [significant_items.index(x) for x in cur_set]
        start = max(indices) + 1
        for item in significant_items[start:]:
            candidate = []
            for x in cur_set:
                candidate.append(x)
            candidate.append(item)
            freq = 0
            for transaction in transactions:
                if all(x in transaction for x in candidate):
                    freq += 1
            if freq/len(player_categories) >= support_threshold:
                significant_sets.append(candidate)

# Generate 5 random users to make recommendations
randomlist = []
keyslist = list(player_categories)
for i in range(5):
    n = random.randint(0,len(transactions)-1)
    randomlist.append(n)
for n in randomlist:
    recommend(keyslist[n])