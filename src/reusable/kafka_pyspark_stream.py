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
from pyspark.streaming.kafka import KafkaUtils, OffsetRange, TopicAndPartition
def txt_to_feature(text):
    words = re.sub("[^a-zA-Z]", " ", text).lower().split()
    clean_words = [ps.stem(w) for w in words if not w in stops]
    return( " ".join(clean_words))

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
    #stream = KafkaUtils.createStream(ssc, 'cdh57-01-node-01.moffatt.me:2181', 'spark-streaming', {TOPIC:1})

    # parsed = stream.map(lambda v: json.loads(v[1]))
    object_stream = stream.map(lambda x: json.loads(x[1]))
    output = object_stream.map(lambda x: json.loads(x)['text'])
    print ("Streaming ...")

    count_stream = stream.map(txt_to_feature) \
                         .map(lambda string: len(str))

    output.pprint()
    ssc.start()
    ssc.awaitTermination()



if __name__ == '__main__':
    main()
