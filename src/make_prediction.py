#python=3.5
import re
import pymongo
import findspark
findspark.init()
import pyspark
from pyspark.sql.functions import col, udf
import pymongo_spark
pymongo_spark.activate()
from pyspark.sql.types import *
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, HashingTF, IDF, CountVectorizer, IDFModel, StopWordsRemover
from pyspark.ml.classification import RandomForestClassifier, LogisticRegression, GBTClassifier, RandomForestClassificationModel
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
from pyspark.ml.feature import HashingTF, Tokenizer
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder, ParamGridBuilder, TrainValidationSplit

def filter_ads(text):
    return 'https' not in text

def preprocess(text):
    words = re.sub("[^a-zA-Z]", " ", text).lower().split()
    return words


if __name__ == "__main__":

    spark = pyspark.sql.SparkSession.builder \
                .master("local[4]") \
                .appName('Testing Spark Mongo') \
                .getOrCreate()

    path = '../kafka_files/twitterstream_0.jsonl'
    schema = StructType([
                StructField('Text' , StringType(), False),
    ])
    df = spark.read.json(path, columnNameOfCorruptRecord='Text')

    #construct udf
    ads_filter = udf(filter_ads, BooleanType())

    ads_free = df.filter(ads_filter(df.Text))

    #remove punctuation
    pp_udf = udf(preprocess, ArrayType(StringType()))
    words = ads_free.withColumn('Words', pp_udf(ads_free.Text))

    #remove stop words
    remover = StopWordsRemover(inputCol="Words", outputCol="filtered")
    removed = remover.transform(words)

    params_path = '../tmp/{}'

    #Load trained hashing frequency and transform
    hf_path = params_path.format('hf')
    hashingTF = HashingTF.load(hf_path)
    featureized = hashingTF.transform(removed)

    #Load trained hashing frequency and transform
    idf_path = params_path.format('idfmodel')
    idfmodel = IDFModel.load(idf_path)
    result = idfmodel.transform(featureized)

    #load rf model and predict
    rf_path = params_path.format('rf')
    rf = RandomForestClassificationModel.load(rf_path)
    prediction = rf.transform(result)

    path_to_save = '../tmp/twitterstream_test_prediction.json'
    prediction.write.json(path_to_save)


    #test whether json is written
    test = spark.read.json(path_to_save)
