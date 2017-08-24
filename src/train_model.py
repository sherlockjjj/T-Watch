#PYTHON=3.5
import pandas as pd
import re
import string
from datetime import datetime
import findspark
findspark.init()
import pyspark as ps
from pyspark.sql.types import *
from pyspark.sql.functions import array_contains, col, udf, when, coalesce, array
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, HashingTF, IDF, CountVectorizer, IDFModel, StopWordsRemover
from pyspark.ml.classification import RandomForestClassifier, LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import HashingTF, Tokenizer
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder, ParamGridBuilder, TrainValidationSplit


def preprocess(text):
    words = re.sub("[^a-zA-Z]", " ", text).lower().split()
    return words

if __name__ == "__main__":
    spark = ps.sql.SparkSession.builder \
            .master("local[4]") \
            .appName('Model Training') \
            .getOrCreate()

    schema = StructType([
            StructField('NewIndex' , IntegerType(), False),
            StructField('Index' , IntegerType(), False),
            StructField('ItemID' , IntegerType(), False),
            StructField('Sentiment' , IntegerType(), False),
            StructField('SentimentSource' , StringType(), False),
            StructField('SentimentText' , StringType(), False),
        ])

    filename = "../data/nokaggle-Sentiment-Analysis-Dataset.csv"
    users = spark.read.csv(filename, header=True, schema=schema)
    #users.printSchema()
    #users.show(5)

    pp_udf = udf(preprocess, ArrayType(StringType()))
    words = users.withColumn('Words', pp_udf(users.SentimentText))
    #words.printSchema()
    #remove stop words
    remover = StopWordsRemover(inputCol="Words", outputCol="filtered")
    removed = remover.transform(words)

    #rename column and select columns
    filtered = removed.select('ItemID', col('Sentiment').alias('label'), 'SentimentText', 'Words', 'filtered')

    #perform term frequency
    hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures", numFeatures=200)
    featurized = hashingTF.transform(filled_featurized)
    #featurized.select('rawFeatures').show(truncate=False)

    #perform idf
    featurized.cache()
    idf = IDF(inputCol="rawFeatures", outputCol="features")
    model = idf.fit(featurized)
    result = model.transform(featurized)
    #result.limit(10).select('features').show(truncate=False)

    #save idf and idf model
    idf_path = '../tmp/idf'
    idf.save(idf_path)
    idfmodel_path = '../tmp/idfmodel'
    model.save(idfmodel_path)
    #load via following
    #loadedModel = IDFModel.load(idfmodel_path)

    #fit single rf model
    rf = RandomForestClassifier(numTrees=100, labelCol="label", seed=42)
    rf_model = rf.fit(result)

    #Prepare Train Test Split
    train, test = result.randomSplit([0.8, 0.2], seed=42)

    # Configure an ML pipeline, which consists of tree stages: hashingTF, idf and RandomForestClassifier.
    #remover = StopWordsRemover(inputCol="Words", outputCol="filtered")
    #hashingTF = HashingTF(inputCol=tokenizer.getOutputCol(), outputCol="features")
    rf = RandomForestClassifier(labelCol="label", seed=42)
    pipeline = Pipeline(stages=[rf])

    #grid search
    paramGrid = ParamGridBuilder().addGrid(rf.numTrees, [100]).addGrid(rf.maxDepth, [5]).build()

    crossval = CrossValidator(estimator=pipeline,
                              estimatorParamMaps=paramGrid,
                              evaluator=BinaryClassificationEvaluator(),
                              numFolds=3)  # use 3+ folds in practice

    # Run cross-validation, and choose the best set of parameters.
    cvModel = crossval.fit(train)

    # Make predictions on test documents. cvModel uses the best model found (lrModel).
    prediction = cvModel.transform(test)
    selected = prediction.select("SentimentText", "probability", "prediction")
    # selected.printSchema()
    # selected.show(5)

    #cv score
    print (cvModel.avgMetrics)
    #test score
    evaluator = BinaryClassificationEvaluator()
    print ("Test Score is {}".format(evaluator.evaluate(cvModel.transform(test))))
    cvModel.getEstimatorParamMaps()

    #save model
    cv_path = '../tmp/cv'
    cvModel.bestModel.save(cv_path)
