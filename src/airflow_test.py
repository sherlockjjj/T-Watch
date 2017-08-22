import sys, os, re

from airflow import DAG
from airflow.operators.bash_operators import BashOperator
from datetime import datetime, timedelta
import iso8601

project_home = os.environ['PROJECT_HOME']

default_args = {
    'owner': 'airflow',
    'depends_on_past': false,
    'start_date': iso8601.parse_date('2016-12-01'),
    'email': ['yfangfh15@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

#timedelta 1 is run daily
dag = DAG(
    'agile_data_science_airflow_test',
    default_args=default_args,
    schedule_interval=timedelta(1)
)

#run a simple pyspark script
# ds is the built variable that contains the date the Airflow uses to run the command
pyspark_local_task_one = BashOperator(
    task_id = "pyspark_local_task_one",
    bash_command = """spark-submit \
    --master {{ params.master }}
    {{ params.base_path}} / {{ params.filename }} {{ ds }} {{ params.bash_path }}""",
    params = {
      "master": "local[8]",
      "filename": "ch02/pyspark_local_task_one.py",
      "base_path": "{}/".format(project_home)
    },
    dag=dag
)

#run another script that depends on the previous one
pyspark_local_task_two = BashOperator(
    task_id = "pyspark_local_task_two",
    bash_command = """spark-submit \
    --master {{ params.master }}
    {{ params.base_path}} / {{ params.filename }} {{ ds }} {{ params.bash_path }}""",
    params = {
      "master": "local[8]",
      "filename": "ch02/pyspark_local_task_two.py",
      "base_path": "{}/".format(project_home)
    },
    dag=dag
)

#set dependency
pyspark_local_task_two.set_upstream(pyspark_local_task_one)
