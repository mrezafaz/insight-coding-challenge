import json
import scipy as sp
import os
import time

# This function removes edges formed with a expired hashtag (expired hashtags are hashtags that belong to tweets older than 60 seconds)
def remove_edges(graph, expired_hashtag):
    # Finding hashtags that are connected to the expired hashtag
    connected_hashtags = graph[expired_hashtag]
    # Removing the expired hashtag from the list of values of each connected hashtag key
    for hashtag in connected_hashtags:
        graph[hashtag].remove(expired_hashtag)
    # Removing the expired hashtag key and values
    del graph[expired_hashtag]
    return graph

start_time = time.time()
print('--- executing average_degree.py ---')
input_dir = "tweet_input/tweets.txt"
output_dir = "tweet_output/f2.txt"

# Initializing the twitter hashtag graph
graph = {}
# Initializing a master dictionary for keeping the hashtags of all analyzed tweets
hashtags_dict = {}
# Initializing the list of rolling average degree
output_data = []

with open(input_dir) as input_file:
    for line in input_file:
        tweet = json.loads(line)
        
        try:
            # Extracting the tweet timestamp from the Twitter JSON message
            timestamp = int(tweet['timestamp_ms'])/1000
        except:
            # Skipping any artifacts in the input file
            output_data.append("--- WARNING: THIS LINE IS NOT A TWEET ---")
            continue
        
        try:
            # Extracting the tweet hashtags from the Twitter JSON message
            hashtags = sp.unique(['#'+hashtag['text'].lower() for hashtag in tweet['entities']['hashtags']])
            # Cleaning the tweet hashtags
            hashtags = [hashtag.encode('ascii','ignore') for hashtag in hashtags]
            # Creating a dictionary where the tweet timestamp is assigned to each hashtag in the tweet
            new_hashtags_dict = dict([(hashtag, timestamp) for hashtag in hashtags])
        except:
            # Creating an empty dictionary when the tweet has no hashtags
            new_hashtags_dict = {}
        
        # Identifying expired hashtags (expired hashtags are hashtags that belong to tweets older than 60 seconds)
        expired_hashtags = [hashtag*((timestamp - hashtags_dict.get(hashtag, timestamp)) > 60) for hashtag in hashtags_dict.keys()]
        expired_hashtags =  filter(None, expired_hashtags)
        
        
        for hashtag in expired_hashtags:
            # Removing the expired hastags from the master dictionary
            del hashtags_dict[hashtag]
            # Removing the edges formed with expired hashtags
            graph = remove_edges(graph, hashtag)
        
        # Updating the master hashtag dictionary with the hashtag dictionary of current tweet
        hashtags_dict.update(new_hashtags_dict)
        
        # Modifying the twitter hashtag graph with incoming tweet
        for hashtag in new_hashtags_dict.keys():
            graph[hashtag] = list(sp.unique(graph.get(hashtag,[]) + new_hashtags_dict.keys()))
            graph[hashtag].remove(hashtag)
        
        # Calculating the degree of each node in the graph
        degrees = [len(graph[node]) for node in graph.keys()]
        
        # Calculating the average degree of the graph
        try:
            avg_degree = str(round(1.0*sum(degrees)/sp.count_nonzero(degrees),2))
        except:
            # Setting the average degree to zero when there is no node (hashtag) in the graph
            avg_degree = str(0)
        
        # Adding the calculated average degree to the list of rolling average degree 
        output_data.append(avg_degree)

print("--- tweets processed in %s seconds ---" % round((time.time() - start_time),2))


with open(output_dir,'w') as output_file:
    print ("--- writing to /%s ---"% output_dir)
    output_file.write(os.linesep.join(output_data))