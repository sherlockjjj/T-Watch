#capstone/src 
#command specifiy streaming time in mins
import json, os
import time, sys
from datetime import datetime 
from utils import tag_dict
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

def predict_store(time, rdd):
    """
    predict and store incoming streams
    """
    print("========= %s =========" % str(time))
    if not rdd.isEmpty():
        # Convert RDD[String] to RDD[Row] to DataFrame
        cols = ['id', 'screen_name', 'text', 'followers', 'created_at', 'teams']
        rowRdd = rdd.map(lambda w: Row(id=w['id'], screen_name=w['screen_name'], \
                                       text=w['text'], followers=w['followers'], created_at=w['created_at'], teams=w['teams']))
        
        df = spark.createDataFrame(rowRdd)
        #make prediction use saved model
        prediction = pred.predict(df)
        prediction.select('text', 'teams','prediction').show()

        #save as jsonl.gz
        path = '/home/ubuntu/capstone/stream_data/{}'.format(os.environ['Today'])
        #hadoop doesn't support colon in file naming 
        convert_time = time.strftime('%H-%M-%S')
        despath = os.path.join(path, "{}.jsonl.gz".format(convert_time))
        prediction.toJSON().saveAsTextFile(despath, 'org.apache.hadoop.io.compress.GzipCodec')

        #save to mongodb for publishing
        new_cols = ['id', 'screen_name', 'text', 'followers','created_at','teams', 'prediction']
        convert_dict = lambda x: {d:x[d] for d in new_cols}
        pred_rdd = prediction.rdd.map(convert_dict)
        pred_rdd.saveToMongoDB('mongodb://localhost:27017/streams.nba')

def save_raw(time, rdd):
    if not rdd.isEmpty():
        rdd.saveToMongoDB('mongodb://localhost:27017/streams.rawnba')

def find_teams(text):
    teams = set()
    for tag in tag_dict.keys():
        if tag in text:
            teams.add(tag_dict[tag])
    if teams:
        return (" ").join(teams) 
    return "Some Team" 

if __name__ == "__main__":
    #setting up environment
    APP_NAME = 'NBA Streamer'
    os.environ['Today'] = datetime.now().strftime('%Y-%m-%d')
    PERIOD=20
    BROKERS='localhost:9092'
    TOPIC= 'twitterstream'
    duration=100
    try:
        sc
    except:    
        conf = SparkConf().set("spark.default.paralleism", 1)
        spark = pyspark.sql.SparkSession.builder \
                                        .master("local[4]") \
                                        .appName(APP_NAME) \
                                        .config(conf=conf)  \
                                        .getOrCreate()
        sc = spark.sparkContext
        #create a streaming context with batch interval 10 sec

    #initialize predictor
    pred = myStreamPredictor() 
    
    client = MongoClient()
    collection = client.streams.nba
    #collection.drop()
    print ("Before stream count is {}".format(collection.count()))
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
    features = filtered_tweets.map(lambda x: {'id': x['id'], 'screen_name': x['user']['screen_name'], 'text': x['text'], 'followers': x['user']['followers_count'], 'created_at': x['created_at'], 'teams': find_teams(x['text'])})
    
    #tweets.pprint()
    features.pprint()
    
    #store raw tweets
    tweets.foreachRDD(save_raw)
    
    #predict and store feature extracted tweets
    features.foreachRDD(predict_store)
    ssc.start()
    
    try:
        stream_time = int(sys.argv[1])
    except: 
        stream_time = 5
        
    time.sleep(stream_time*60)
    
    ssc.stop(stopSparkContext=False, stopGraceFully=True)
    
    
    
    

    
    