# N64-Speedrun-Rec-Sys-Experiments
Messing around with different implementations of Recommender Systems for N64 Speedruns.
All data used in the following project was collected using the API from speedrun.com. Data was accessed and collected using Scrapy, and the relevant information was stored in all_games_N64.JSON. The information in the dataset was last updated on November 18, 2021. If you wish, you may execute the file AllGamesN64.py in your own workspace, and an updated JSON will be created for your use.

Further information about the API, for your own interest, is available here:

https://github.com/speedruncomorg/api/blob/master/version1/README.md

There are three recommender systems to play around with in this project:
1. FrequentItemsetRecommender.py: This implementation uses the Apriori algorithm to filter games and categories down to categories which frequently appear together on users profiles. Recommendations are made based on this information.
2. ClusterRecommender.py: This system applies k-means clustering to recommend games to users. Given the user for which we want to recommend games, each game they play is an attribute. Each user in the dataset is given a "document vector" in the form of a boolean model, assigning 1s if the players play the same game as the given user and 0s otherwise. An implementation of k-means clustering groups the users together, and recommendations of games for the user are taken from the set of games that players from the same cluster play.
3. PersonalizedPageRankRecommender: This system represents the game as a network. The network is formulated as an adjacency matrix of games, where a connection is made if a there exists a player which plays both games. Any games with no crossover are assigned a vector of all 1s. Random walks are made from each game the user plays and the set of destinations forms the candidates for recommendation. Random choice recommends the games from these candidates.

Have fun!
