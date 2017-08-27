import json, os
import boto
import findspark
# Add the streaming package and initialize
findspark.add_packages(["org.apache.spark:spark-streaming-kafka-0-8_2.11:2.2.0"])
findspark.init()
import pyspark
from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import pymongo_spark
pymongo_spark.activate()
from pymongo import MongoClient
from configparser import ConfigParser
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from mypredictor import myStreamPredictor
from pyspark.sql import Row

def predict_store(time, rdd):
    """
    predict and store incoming streams
    """
    print("========= %s =========" % str(time))
    # Convert RDD[String] to RDD[Row] to DataFrame
    rowRdd = rdd.map(lambda w: Row(**w))
    df = spark.createDataFrame(rowRdd, ['id', 'screen_name','text'])
    prediction = pred.predict(df)
    prediction.show()
    cols = ['id', 'screen_name', 'text', 'prediction']
    convert_dict = lambda x: {d:x[d] for d in cols}
    pred_rdd = prediction.rdd.map(convert_dict)
    pred_rdd.saveToMongoDB('mongodb://localhost:27017/streams.tweets')

if __name__ == "__main__":
    #authenticate
    config = ConfigParser()
    config.read('../.config/.credentials')
    region = config.get('aws', 'region')
    AWS_ACCESS_KEY_ID = config.get('aws', 'AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config.get('aws', 'AWS_SECRET_ACCESS_KEY')
    os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
    os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY

    #setting up environment
    PERIOD=10
    BROKERS='localhost:9092'
    TOPIC= 'twitterstream'
    duration=100
    try:
        sc
    except:    
        conf = SparkConf().set("spark.default.paralleism", 1)
        spark = pyspark.sql.SparkSession.builder \
                                        .master("local[4]") \
                                        .appName('Streamer') \
                                        .config(conf=conf)  \
                                        .getOrCreate()
        sc = spark.sparkContext
        #create a streaming context with batch interval 10 sec

    #initialize predictor
    pred = myStreamPredictor() 
    
    client = MongoClient()
    collection = client.streams.tweets
    collection.drop()
    client.close()
    
    #a new ssc needs to be started after a previous ssc is stopped
    ssc = StreamingContext(sc, PERIOD)

    #create stream receivers
    stream = KafkaUtils.createDirectStream(
              ssc,
              [TOPIC],
              {
                "metadata.broker.list": BROKERS,
              }
    )
    tweets = stream.map(lambda x: json.loads(x[1])).map(lambda x: json.loads(x))
    #filter commercials
    filtered_tweets = tweets.filter(lambda x: 'https' not in x['text'])

    # DataFrame operations inside your streaming program
    text = filtered_tweets.map(lambda x: {'id': x['id'], 'screen_name': x['user']['screen_name'], 'text': x['text']})
    text.foreachRDD(predict_store)
    ssc.start()
    
    import time
    time.sleep(5*60)
    ssc.stop(stopSparkContext=False, stopGraceFully=True)
    client = MongoClient()
    print (client.streams.tweets.count())
    client.close()
    
    

    
    