import json
import re
import os
import time

start_time = time.time()
print('--- executing tweets_cleaned.py ---')
input_dir = "tweet_input/tweets.txt"
output_dir = "tweet_output/f1.txt"

unicode_count = 0
# Initializing the list of clean tweets
output_data = []

with open(input_dir) as input_file:
    for line in input_file:
        tweet = json.loads(line)
        try:
            # Extracing the relevant data (tweet and text and timestamp) from the Twitter JSON message
            original_text = tweet['text']
            timestamp = tweet['created_at']
            
            # Removing the non-ASCII unicode characters 
            no_unicode_text = original_text.encode('ascii','ignore')
            
            # Tracking the number of tweets that contain unicode characters
            unicode_count += no_unicode_text != original_text
            
            # Replacing the whitespcae characters with space 
            no_whitespace_text = re.sub('\s', ' ', no_unicode_text)
            
            clean_text = no_whitespace_text
            clean_tweet = clean_text+" (timestamp: "+timestamp+")"
            
            # Adding the clean tweet to the list of clean tweets
            output_data.append(clean_tweet)
        except:
            # Skipping any artifacts in the input file
            output_data.append("--- WARNING: THIS LINE IS NOT A TWEET ---")
        
output_data.append(str(unicode_count)+" tweets contained unicode.")
print("--- tweets processed in %s seconds ---" % round((time.time() - start_time),2))
with open(output_dir,'w') as output_file:
    print ("--- writing to /%s ---"% output_dir)
    output_file.write(os.linesep.join(output_data))