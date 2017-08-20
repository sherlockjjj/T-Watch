from pymongo import MongoClient
from utils import *

if __name__ == '__main__':
    filename = '../tmp/tesla_tweets.jsonl'
    client = MongoClient()
    db = client.tweets_test
    collection = db.tweets
    ary = read_json_lines_file(filename)
    # print ary[0]
    print "before insert the count is {}".format(collection.count())
    collection.insert_many(ary)
    print "after insert the count is {}".format(collection.count())
    client.close()
