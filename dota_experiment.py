import dota2api
import time
from collections import defaultdict
api = dota2api.Initialise("TODO") # enter your own API key
MAX = 100
ANONYMOUS = 4294967295
PLAYERS = 10
seed = 6198860477 #Randomly selected to be relatively modern: 2023.
#issue with rounds is that the API stops working when u add too much at once, so we introduce a wait
ROUNDS = 2000
SLEEP = 6
total_anonymous = 0
total_deleted = 0
seen_ids = set() #The only purpose is to provide a sanity check
total_duplicates = 0
cluster_game_mode_stats = defaultdict(lambda: {'matches': 0, 'anonymous_players': 0})


def seq_100(start):
    anonymous_players = 0
    deleted_players = 0
    nonhuman = 0
    matches = api.get_match_history_by_seq_num(start_at_match_seq_num=start, matches_requested=MAX)
    for i in range (0, MAX-1):
        match = matches['matches'][i]
        if match ['human_players'] == PLAYERS: 
            cluster = match['cluster']
            game_mode = match['game_mode']
            cluster_game_mode_stats[(cluster, game_mode)]['matches'] += 1

            matchid = match['match_id']
            if matchid in seen_ids:
                total_duplicates += 1
            else:
                seen_ids.add(matchid)

            for j in range (0,PLAYERS):
                account_id = match['players'][j].get('account_id', None)
                
                if account_id == ANONYMOUS:
                    anonymous_players += 1
                    cluster_game_mode_stats[(cluster, game_mode)]['anonymous_players'] += 1

                if account_id is None:
                    deleted_players += 1
        else:
            nonhuman += 1
    match = matches['matches'][MAX-1]
    seed = match['match_seq_num'] #seed for next round
    return(anonymous_players,deleted_players, nonhuman, seed)


nonhuman = 0
for i in range(0,ROUNDS):
    a,d,h,e = seq_100(seed)
    total_anonymous += a
    total_deleted += d
    seed = e
    nonhuman += h
    time.sleep(SLEEP)
print("Amount of matches:", ROUNDS * 99 - nonhuman)
print("Number of anonymous players:", total_anonymous)
print("Number of deleted accounts (removed datapoints):", total_deleted)
print("Number of matches processed more than once (sanity check):", total_duplicates)
for (c,m) in cluster_game_mode_stats:
    matches = cluster_game_mode_stats[(c,m)]['matches']
    anonymous_players = cluster_game_mode_stats[(c,m)]['anonymous_players']
    average = (anonymous_players / matches)
    print((c,m), cluster_game_mode_stats[(c,m)], average)

