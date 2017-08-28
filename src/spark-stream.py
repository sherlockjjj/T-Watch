#capstone/src 
#command specifiy streaming time in mins
import json, os
import time, sys
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
from mypredictor import myStreamPredictor
from pyspark.sql import Row
import os
from datetime import datetime 

def predict_store(time, rdd):
    """
    predict and store incoming streams
    """
    print("========= %s =========" % str(time))
    # Convert RDD[String] to RDD[Row] to DataFrame
    rowRdd = rdd.map(lambda w: Row(**w))
    df = spark.createDataFrame(rowRdd, ['id', 'screen_name','text'])
    
    #make prediction use saved model
    prediction = pred.predict(df)
    prediction.show()
    
    #save as jsonl.gz
    path = '/home/ubuntu/capstone/stream_data/{}'.format(os.environ['Today'])
    #hadoop doesn't support colon in file naming 
    convert_time = time.strftime('%H-%M-%S')
    despath = os.path.join(path, "{}.jsonl.gz".format(convert_time))
    prediction.toJSON().saveAsTextFile(despath, 'org.apache.hadoop.io.compress.GzipCodec')
    
    #save to mongodb for publishing
    cols = ['id', 'screen_name', 'text', 'prediction']
    convert_dict = lambda x: {d:x[d] for d in cols}
    pred_rdd = prediction.rdd.map(convert_dict)
    pred_rdd.saveToMongoDB('mongodb://localhost:27017/streams.tweets')

if __name__ == "__main__":
    #setting up environment
    os.environ['Today'] = datetime.now().strftime('%Y-%m-%d')
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
    print ("Before stream count is {}".format(collection.count()))
        #collection.drop()
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
    
    try:
        stream_time = int(sys.argv[1])
    except: 
        stream_time = 5
        
    time.sleep(stream_time*60)
    
    ssc.stop(stopSparkContext=False, stopGraceFully=True)
    
    #print after stream collection count
    client = MongoClient()
    print ("After Stream Count is {}".format(client.streams.tweets.count()))
    client.close()
    
    
    
    

    
    