import sys, os, re

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

from datetime import datetime, timedelta
import iso8601

PROJECT_HOME = os.environ["PROJECT_HOME"]
EMAIL = os.environ["MY_EMAIL"]
default_args = {
  'owner': 'airflow',
  'depends_on_past': False,
  'start_date': iso8601.parse_date("2017-08-28"),
  'email': [EMAIL],
  'email_on_failure': True,
  'email_on_retry': True,
  'retries': 3,
  'retry_delay': timedelta(7),
}

training_dag = DAG(
  'weekly_model_training',
  default_args=default_args
)

# Save two commands for all our PySpark tasks
pyspark_bash_command = """
spark-submit --master {{ params.master }} \
  {{ params.base_path }}/{{ params.filename }} \
  {{ params.base_path }}
"""
pyspark_date_bash_command = """
spark-submit --master {{ params.master }} \
  {{ params.base_path }}/{{ params.filename }} \
  {{ ds }} {{ params.base_path }}
"""

# Gather the training data for our classifier
train_model_operator = BashOperator(
  task_id = "train_model",
  bash_command = pyspark_bash_command,
  params = {
    "master": "local[8]",
    "filename": "src/train_model.py",
    "base_path": "{}/".format(PROJECT_HOME)
  },
  dag=training_dag
)

# The model training depends on the feature extraction
train_classifier_model_operator.set_upstream(extract_features_operator)

daily_prediction_dag = DAG(
  'daily_report',
  default_args=default_args,
  schedule_interval=timedelta(1)
)

# Fetch prediction requests from MongoDB
fetch_prediction_requests_operator = BashOperator(
  task_id = "pyspark_fetch_prediction_requests",
  bash_command = pyspark_date_bash_command,
  params = {
    "master": "local[8]",
    "filename": "fetch_prediction_requests.py",
    "base_path": "{}/".format(PROJECT_HOME)
  },
  dag=daily_prediction_dag
)

# Make the actual predictions for today
make_predictions_operator = BashOperator(
  task_id = "pyspark_make_predictions",
  bash_command = pyspark_date_bash_command,
  params = {
    "master": "local[8]",
    "filename": "spark-stream.py",
    "base_path": "{}/".format(PROJECT_HOME)
  },
  dag=daily_prediction_dag
)

# Load today's predictions 
load_prediction_results_operator = BashOperator(
  task_id = "pyspark_load_prediction_results",
  bash_command = pyspark_date_bash_command,
  params = {
    "master": "local[8]",
    "filename": "app.py",
    "base_path": "{}/".format(PROJECT_HOME)
  },
  dag=daily_prediction_dag
)

# Set downstream dependencies for daily_prediction_dag
fetch_prediction_requests_operator.set_downstream(make_predictions_operator)
make_predictions_operator.set_downstream(load_prediction_results_operator)
