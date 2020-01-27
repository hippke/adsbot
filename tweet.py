# Read file, tweet, and delete file
from twython import Twython
import os

max_tweets_per_run = 2
path = "tweets/"
twitter = Twython(
    os.environ.get("consumer_key"),
    os.environ.get("consumer_secret"),
    os.environ.get("access_token"),
    os.environ.get("access_token_secret"),
)
counter = 0
if os.path.exists(path):
    print('Path exists:', path)
    for file in os.listdir(path):
        filehandle = open(path+file, "r")
        tweet = filehandle.readline()
        print('Tweeting', path+file, tweet)
        twitter.update_status(status=tweet)
        
        filehandle.close()
        os.remove(path+file)
        counter += 1
        if counter >= max_tweets_per_run:
            print('max_tweets_per_run reached, aborting:', max_tweets_per_run)
            break
