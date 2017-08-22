import json
import tweepy
from kafka import SimpleProducer, KafkaClient
from tweepy import OAuthHandler, Stream, API
from tweepy.streaming import StreamListener
from configparser import ConfigParser

class TstreamListener(StreamListener):
    def __init__(self, api):
        self.api = api
        super(StreamListener, self).__init__()
        client = KafkaClient("localhost:9092")
        self.producer = SimpleProducer(client, async=True, \
                      batch_send_every_n = 1000, batch_send_every_t=10)

    def on_status(self, status):
        """
        Called whenever new data arrives from live stream
        """

        msg = status.text.encode('utf-8')
        try:
            self.producer.send_messages(b'twitterstream', msg)
        except Exception as e:
            print e
            return False
        return True

    def on_error(self, status_code):
        print "Error received in kafka producer"
        return True #don't kill the stream

    def on_timeout(self):
        return True

if __name__ == '__main__':

    #authenticate
    config = ConfigParser()
    config.read('.config/.credentials')
    consumer_key = config.get('auth', 'consumer_key')
    consumer_secret = config.get('auth', 'consumer_secret')
    access_token = config.get('auth', 'access_token')
    access_token_secret = config.get('auth', 'access_token_secret')

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth)

    stream = Stream(auth, listener=TstreamListener(api))

    stream.filter(track=['basketball'], locations=[-122.75,36.8,-121.75,37.8], languages=['en'])
