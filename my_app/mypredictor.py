import re, os, sys, time
from stat import ST_CTIME
import pymongo
from pymongo import MongoClient
import findspark
findspark.init()
import pyspark
from pyspark.sql.functions import col, udf
import pymongo_spark
pymongo_spark.activate()
from pyspark.sql.types import *
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, HashingTF, IDF, CountVectorizer, IDFModel, StopWordsRemover
from pyspark.ml.classification import RandomForestClassifier, RandomForestClassificationModel
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
from pyspark.ml.feature import HashingTF, Tokenizer

class myPredictor():
    def __init__(self):
        print ("Configuring Path ... \n")
        self._add_path()
        print ("Loading Saved Models ...\n")
        self._load_models()

        self.ads_filter = udf(filter_ads, BooleanType())
        self.pp_udf = udf(preprocess, ArrayType(StringType()))
        self.remover = StopWordsRemover(inputCol="Words", outputCol="filtered")

        print ("Checking ... \n")
        get_collection_count()

    def _add_path(self):
        self.input_path = '../kafka_files/twitterstream_{}.jsonl'
        self.output_path = '../predictions/prediction_{}.jsonl'
        self.params_path = '../tmp/{}'

    def _load_models(self):
        hf_path = self.params_path.format('hf')
        idf_path = self.params_path.format('idfmodel')
        rf_path = self.params_path.format('rf')

        self.hashingTF = HashingTF.load(hf_path)
        self.idfmodel = IDFModel.load(idf_path)
        self.rf = RandomForestClassificationModel.load(rf_path)

    def add_input_files(self, sorted_files):
        """
        sorted_files: tuple (time, path)
        """
        self.input_files = [path for _, path in sorted_files]

    def predict_one(self, path, num):
        df = spark.read.json(path, columnNameOfCorruptRecord='Text')
        ads_free = df.filter(self.ads_filter(df.Text))
        words = ads_free.withColumn('Words', self.pp_udf(ads_free.Text))
        removed = self.remover.transform(words)
        featureized = self.hashingTF.transform(removed)
        result = self.idfmodel.transform(featureized)
        prediction = self.rf.transform(result)
        output_path = self.output_path.format(num)
        prediction.write.json(output_path, mode='overwrite')
        prediction.write.format("com.mongodb.spark.sql.DefaultSource").mode("append").save()
        return output_path

    def predict(self):
        count = 0
        for path in self.input_files:
            time.sleep(2)
            output = self.predict_one(path, count)
            get_collection_count()
            self.client.test.events.insert_many(spark.read.json(output))
#             except:
#                 print('Something Wrong with path {}'.format(path))
            count += 1

#utils functions
def filter_ads(text):
    return 'https' not in text

def preprocess(text):
    words = re.sub("[^a-zA-Z]", " ", text).lower().split()
    return words

def find_input_files():
    paths = []
    for file in os.listdir("../kafka_files"):
        if file.endswith(".jsonl"):
            paths.append(os.path.join("../kafka_files/", file))
    entries = [(os.stat(path)[ST_CTIME], path) for path in paths]
    sorted_entries = sorted(entries)
    return sorted_entries

def get_collection_count():
    print ("number of collections is {}".format(client.test.events.count()))

#             .config("spark.mongodb.input.database", db) \
#             .config("spark.mongodb.input.collectionn", collection) \
#             .config("spark.mongodb.output.database", db) \
#             .config("spark.mongodb.output.collection", collection) \
if __name__ == "__main__":
    client = MongoClient()
    db = client.test
    collection = db.events
    spark = pyspark.sql.SparkSession.builder \
            .master("local[4]") \
            .appName('Testing Prediction Pipeline') \
            .config("spark.mongodb.input.uri", "mongodb://127.0.0.1/test.coll") \
            .config("spark.mongodb.output.uri", "mongodb://127.0.0.1/test.coll") \
            .getOrCreate()

    #get input stream files sorted by timestamp
    sorted_files = find_input_files()
    
    #make prediction and store the output to ../predictions/
    pred = myPredictor()
    pred.add_input_files(sorted_files)
    pred.predict()

    #close client connection
    client.close()
