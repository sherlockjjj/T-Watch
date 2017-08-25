import json
import sys, os, re, ast
import findspark
# Add the streaming package and initialize
findspark.add_packages(["org.apache.spark:spark-streaming-kafka-0-8_2.11:2.2.0"])
findspark.init()
import pyspark
import pyspark.streaming
from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

def main():
    PERIOD=10
    BROKERS='localhost:9092'
    TOPIC= 'twitterstream'
    duration=100
    conf = SparkConf().set("spark.default.paralleism", 1)
    sc = SparkContext(appName='Streamer', conf=conf)
    #create a streaming context with batch interval 10 sec
    ssc = StreamingContext(sc, PERIOD)
    #ssc.checkpoint("checkpoint")
    stream = KafkaUtils.createDirectStream(
      ssc,
      [TOPIC],
      {
        "metadata.broker.list": BROKERS,
      }
    )

    tweets = stream.map(lambda x: json.loads(x[1])).map(lambda x: json.loads(x))
    text = tweets.map(lambda x: x['text'])

    print ("Streaming ...")
    text.pprint()
    ssc.start()
    ssc.awaitTermination()

if __name__ == '__main__':
    main()
