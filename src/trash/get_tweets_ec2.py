import tweepy
from utils import *
from pymongo import MongoClient
from tweepy import OAuthHandler, Stream, API
from tweepy.streaming import StreamListener
import boto
import os
from configparser import ConfigParser
config = ConfigParser()
config.read('.config/.credentials')
consumer_key = config.get('auth', 'consumer_key')
consumer_secret = config.get('auth', 'consumer_secret')
access_token = config.get('auth', 'access_token')
access_token_secret = config.get('auth', 'access_token_secret')

def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            print "Limit is reached"
            time.sleep(15 * 60)

def get_timeline():
    public_tweets = api.home_timeline()
    for tweet in public_tweets:
        print tweet.text

def find_friends(username):
    user = api.get_user(username)
    for friend in user.friends():
         print friend.screen_name

def grab_tweets(topic, max_tweets=1000):
    path = '../tmp/{}.jsonl'.format(topic)
    searched_tweets = []
    count = 0
    print "Grabbing Tweets ..."
    for status in limit_handled(tweepy.Cursor(api.search, q=topic,lang='en',
                     result_type='recent').items(max_tweets)):
        count += 1
        searched_tweets.append(status._json)
        if count % 100 == 0:
            print "Getting {} tweets".format(count)
    return searched_tweets

class MyStreamListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_status(self, status):
        print status.text

    def on_error(self, status_code):
        if status_code == 420:
            #disconnect the stream
            return False

if __name__ == '__main__':
    #authenticate
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth)
    searched_topics = ['fitbit']
    topic_list = ['tesla', 'uber', 'airbnb', 'alibaba', 'xiaomi', 'spacex', 'gopro', 'amazon', 'salesforce']
    topic = 'tesla'
    for topics in topic_list:
        searched_tweets = grab_tweets(topic, max_tweets=1500)
        write_json_lines_file(searched_tweets, path)
        time.sleep(15 * 60)
    # l = MyStreamListener()
    # stream = Stream(auth, l)
    # stream.filter(track=['basketball'])
