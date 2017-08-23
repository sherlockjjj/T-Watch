import pandas as pd
import re
import string
import findspark
findspark.init()
import pyspark as ps
from pyspark.sql.types import *
import re
import string
from datetime import datetime
from pyspark.sql.functions import array_contains
from pyspark.sql.functions import col
from pyspark.sql.functions import udf
from pyspark.ml.feature import Tokenizer
from pyspark.ml.feature import StopWordsRemover

def preprocess(text):
    words = re.sub("[^a-zA-Z]", " ", text).lower().split()
    return words

if __name__ == "__main__":
    spark = ps.sql.SparkSession.builder \
            .master("local[4]") \
            .appName('Model Training') \
            .getOrCreate()

    schema = StructType([
        StructField('Index' , IntegerType(), True),
        StructField('ItemID' , IntegerType(), True),
        StructField('Sentiment' , IntegerType(), True),
        StructField('SentimentSource' , StringType(), True),
        StructField('SentimentText' , StringType(), True),
    ])

    filename = "../data/cleaned-Sentiment-Analysis-Dataset.csv"
    users = spark.read.csv(filename, header=True, schema=schema)
    users.show(5)

    pp_udf = udf(preprocess, ArrayType(StringType()))
    df = users.withColumn('Words', pp_udf(users.SentimentText))
    remover = StopWordsRemover(inputCol="Words", outputCol="filtered")
    clean_df = remover.transform(df)
