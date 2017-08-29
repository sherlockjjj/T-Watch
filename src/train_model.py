"""
Author:
Joseph Fang

Description:
The original script was used to train model for a labeled sentiment twitter dataset of over 1 million tweets
When in production, we use this in the airflow that could be executed daily/weekly to update model
base_path could be the path for training data
"""
from utils import preprocess
import sys, os, re
import datetime, iso8601

def main(base_path):
    
    APP_NAME = 'train_model'
    try :
        sc and spark
    except NameError as e:
        import findspark
        findspark.init() 
        import pyspark
        spark = pyspark.sql.SparkSession.builder \
            .master("local[4]") \
            .appName('train model') \
            .getOrCreate()
    
    PROJECT_HOWE = "/home/ubuntu/capstone/"
    
    #loading data as the desired format
    from pyspark.sql.types import *
    from pyspark.sql.functions import col, udf
    schema = StructType([
            StructField('NewIndex' , IntegerType(), False),
            StructField('Index' , IntegerType(), False),
            StructField('ItemID' , IntegerType(), False),
            StructField('Sentiment' , IntegerType(), False),
            StructField('SentimentSource' , StringType(), False),
            StructField('SentimentText' , StringType(), False),
    ])
    
    filename = PROJECT_HOME + "nokaggle-Sentiment-Analysis-Dataset.csv"
    users = spark.read.csv(filename, header=True, schema=schema)
    
    
    #model training stages 
    from pyspark.ml import Pipeline
    from pyspark.ml.feature import HashingTF, IDF, IDFModel, StopWordsRemover
    from pyspark.ml.classification import RandomForestClassifier
    from pyspark.ml.evaluation import BinaryClassificationEvaluator
    from pyspark.ml.tuning import CrossValidator, ParamGridBuilder, TrainValidationSplit
    
    pp_udf = udf(preprocess, ArrayType(StringType()))
    words = users.withColumn('Words', pp_udf(users.SentimentText))
    
    #remove stop words
    remover = StopWordsRemover(inputCol="Words", outputCol="filtered")
    removed = remover.transform(words)

    #rename column and select columns
    filtered = removed.select('ItemID', col('Sentiment').alias('label'), 'SentimentText', 'Words', 'filtered')

    #perform term frequency
    hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures", numFeatures=200)
    featurized = hashingTF.transform(filled_featurized)

    #perform idf
    featurized.cache()
    idf = IDF(inputCol="rawFeatures", outputCol="features")
    model = idf.fit(featurized)
    result = model.transform(featurized)

    #save idf and idf model
    idf_path = PROJECT_HOME + 'tmp/idf'
    idf.save(idf_path)
    idfmodel_path = PROJECT_HOME + 'tmp/idfmodel'
    model.save(idfmodel_path)
    #load via following
    #loadedModel = IDFModel.load(idfmodel_path)

    #fit single rf model
    rf = RandomForestClassifier(numTrees=100, labelCol="label", seed=42)
    rf_model = rf.fit(result)

    #Prepare Train Test Split
    train, test = result.randomSplit([0.8, 0.2], seed=42)

    # Configure an ML pipeline, which consists of tree stages: hashingTF, idf and RandomForestClassifier.
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
    
    #cv score
    print (cvModel.avgMetrics)
    #test score
    evaluator = BinaryClassificationEvaluator()
    print ("Test Score is {}".format(evaluator.evaluate(cvModel.transform(test))))
    cvModel.getEstimatorParamMaps()

    #save model
    cv_path = PROJECT_HOME + 'tmp/cv'
    cvModel.bestModel.save(cv_path)
if __name__ == "__main__":
    main(sys.argv[1])
