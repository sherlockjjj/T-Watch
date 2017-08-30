#!/bin/bash

# Update and install critical packages

sudo apt-get update && sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o DPkg::options::="--force-confdef" -o DPkg::options::="--force-confold" upgrade
sudo apt-get install -y zip unzip curl bzip2 python-dev build-essential git libssl1.0.0 libssl-dev \
    software-properties-common debconf-utils python-software-properties

# Update the motd message to create instructions for users when they ssh in
sudo apt-get install -y update-motd
cat > /home/ubuntu/steinsgate.message << END_HELLO


------------------------------------------------------------------------------------------------------------------------
Welcome to Steins Gate!

------------------------------------------------------------------------------------------------------------------------

END_HELLO

cat <<EOF | sudo tee /etc/update-motd.d/99-steinsgate
#!/bin/bash

cat /home/ubuntu/steinsgate.message
EOF
sudo chmod 0755 /etc/update-motd.d/99-agile-steinsgate
sudo update-motd

#
# Install Java and setup ENV
#
sudo add-apt-repository -y ppa:webupd8team/java
sudo apt-get update
echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | sudo debconf-set-selections
sudo apt-get install -y oracle-java8-installer oracle-java8-set-default

export JAVA_HOME=/usr/lib/jvm/java-8-oracle
echo "export JAVA_HOME=/usr/lib/jvm/java-8-oracle" | sudo tee -a /home/ubuntu/.bash_profile

#
# Install Miniconda
#
curl -Lko /tmp/Miniconda3-latest-Linux-x86_64.sh https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x /tmp/Miniconda3-latest-Linux-x86_64.sh
/tmp/Miniconda3-latest-Linux-x86_64.sh -b -p /home/ubuntu/anaconda

export PATH=/home/ubuntu/anaconda/bin:$PATH
echo 'export PATH=/home/ubuntu/anaconda/bin:$PATH' | sudo tee -a /home/ubuntu/.bash_profile

sudo chown -R ubuntu /home/ubuntu/anaconda
sudo chgrp -R ubuntu /home/ubuntu/anaconda

#
# Install Clone repo, install Python dependencies
#
cd /home/ubuntu
git clone https://github.com/sherlockjjj/magic_world
cd /home/ubuntu/magic_world
export PROJECT_HOME=/home/ubuntu/maigc_world
echo "export PROJECT_HOME=/home/ubuntu/magic_world" | sudo tee -a /home/ubuntu/.bash_profile
conda install python=3.5
conda install iso8601 numpy scipy scikit-learn matplotlib ipython jupyter
pip install bs4 Flask beautifulsoup4 airflow frozendict geopy kafka-python py4j pymongo pyelasticsearch requests selenium tabulate tldextract wikipedia findspark
sudo chown -R ubuntu /home/ubuntu/magic_world
sudo chgrp -R ubuntu /home/ubuntu/magic_world
cd /home/ubuntu

#
# Install Hadoop
#
curl -Lko /tmp/hadoop-2.7.3.tar.gz http://apache.osuosl.org/hadoop/common/hadoop-2.7.3/hadoop-2.7.3.tar.gz
mkdir -p /home/ubuntu/hadoop
cd /home/ubuntu/
tar -xvf /tmp/hadoop-2.7.3.tar.gz -C hadoop --strip-components=1

echo "" >> /home/ubuntu/.bash_profile
echo '# Hadoop environment setup' | sudo tee -a /home/ubuntu/.bash_profile
export HADOOP_HOME=/home/ubuntu/hadoop
echo 'export HADOOP_HOME=/home/ubuntu/hadoop' | sudo tee -a /home/ubuntu/.bash_profile
export PATH=$PATH:$HADOOP_HOME/bin
echo 'export PATH=$PATH:$HADOOP_HOME/bin' | sudo tee -a /home/ubuntu/.bash_profile
export HADOOP_CLASSPATH=$(hadoop classpath)
echo 'export HADOOP_CLASSPATH=$(hadoop classpath)' | sudo tee -a /home/ubuntu/.bash_profile
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
echo 'export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop' | sudo tee -a /home/ubuntu/.bash_profile

# Give to ubuntu
sudo chown -R ubuntu /home/ubuntu/hadoop
sudo chgrp -R ubuntu /home/ubuntu/hadoop

#
# Install Spark
#
curl -Lko /tmp/spark-2.1.0-bin-without-hadoop.tgz http://d3kbcqa49mib13.cloudfront.net/spark-2.1.0-bin-without-hadoop.tgz
mkdir -p /home/ubuntu/spark
cd /home/ubuntu
tar -xvf /tmp/spark-2.1.0-bin-without-hadoop.tgz -C spark --strip-components=1

echo "" >> /home/ubuntu/.bash_profile
echo "# Spark environment setup" | sudo tee -a /home/ubuntu/.bash_profile
export SPARK_HOME=/home/ubuntu/spark
echo 'export SPARK_HOME=/home/ubuntu/spark' | sudo tee -a /home/ubuntu/.bash_profile
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop/
echo 'export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop/' | sudo tee -a /home/ubuntu/.bash_profile
export SPARK_DIST_CLASSPATH=`$HADOOP_HOME/bin/hadoop classpath`
echo 'export SPARK_DIST_CLASSPATH=`$HADOOP_HOME/bin/hadoop classpath`' | sudo tee -a /home/ubuntu/.bash_profile
export PATH=$PATH:$SPARK_HOME/bin
echo 'export PATH=$PATH:$SPARK_HOME/bin' | sudo tee -a /home/ubuntu/.bash_profile

# Have to set spark.io.compression.codec in Spark local mode
cp /home/ubuntu/spark/conf/spark-defaults.conf.template /home/ubuntu/spark/conf/spark-defaults.conf
echo 'spark.io.compression.codec org.apache.spark.io.SnappyCompressionCodec' | sudo tee -a /home/ubuntu/spark/conf/spark-defaults.conf

# Give Spark 8GB of RAM, used Python3
echo "spark.driver.memory 25g" | sudo tee -a $SPARK_HOME/conf/spark-defaults.conf
echo "PYSPARK_PYTHON=python3" | sudo tee -a $SPARK_HOME/conf/spark-env.sh
echo "PYSPARK_DRIVER_PYTHON=python3" | sudo tee -a $SPARK_HOME/conf/spark-env.sh

# Setup log4j config to reduce logging output
cp $SPARK_HOME/conf/log4j.properties.template $SPARK_HOME/conf/log4j.properties
sed -i 's/INFO/ERROR/g' $SPARK_HOME/conf/log4j.properties

# Give to ubuntu
sudo chown -R ubuntu /home/ubuntu/spark
sudo chgrp -R ubuntu /home/ubuntu/spark

#
# Install MongoDB and dependencies
#
sudo apt-get install -y mongodb
sudo mkdir -p /data/db
sudo chown -R mongodb /data/db
sudo chgrp -R mongodb /data/db

# run MongoDB as daemon
sudo /usr/bin/mongod --fork --logpath /var/log/mongodb.log

# Get the MongoDB Java Driver
curl -Lko /home/ubuntu/magic_world/lib/mongo-java-driver-3.4.2.jar http://central.maven.org/maven2/org/mongodb/mongo-java-driver/3.4.2/mongo-java-driver-3.4.2.jar

# Install the mongo-hadoop project in the mongo-hadoop directory in the root of our project.
curl -Lko /tmp/mongo-hadoop-r2.0.2.tar.gz https://github.com/mongodb/mongo-hadoop/archive/r2.0.2.tar.gz
mkdir /home/ubuntu/mongo-hadoop
cd /home/ubuntu
tar -xvzf /tmp/mongo-hadoop-r2.0.2.tar.gz -C mongo-hadoop --strip-components=1
rm -rf /tmp/mongo-hadoop-r2.0.2.tar.gz

# Now build the mongo-hadoop-spark jars
cd /home/ubuntu/mongo-hadoop
./gradlew jar
cp /home/ubuntu/mongo-hadoop/spark/build/libs/mongo-hadoop-spark-*.jar /home/ubuntu/magic_world/lib/
cp /home/ubuntu/mongo-hadoop/build/libs/mongo-hadoop-*.jar /home/ubuntu/magic_world/lib/
cd /home/ubuntu

# Now build the pymongo_spark package
cd /home/ubuntu/mongo-hadoop/spark/src/main/python
python setup.py install
cp /home/ubuntu/mongo-hadoop/spark/src/main/python/pymongo_spark.py /home/ubuntu/magic_world/lib/
export PYTHONPATH=$PYTHONPATH:$PROJECT_HOME/lib
echo 'export PYTHONPATH=$PYTHONPATH:$PROJECT_HOME/lib' | sudo tee -a /home/ubuntu/.bash_profile
cd /home/ubuntu

rm -rf /home/ubuntu/mongo-hadoop

#
# Install ElasticSearch in the elasticsearch directory in the root of our project, and the Elasticsearch for Hadoop package
#
curl -Lko /tmp/elasticsearch-5.2.1.tar.gz https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.2.1.tar.gz
mkdir /home/ubuntu/elasticsearch
cd /home/ubuntu
tar -xvzf /tmp/elasticsearch-5.2.1.tar.gz -C elasticsearch --strip-components=1
sudo chown -R ubuntu /home/ubuntu/elasticsearch
sudo chgrp -R ubuntu /home/ubuntu/elasticsearch
sudo mkdir -p /home/ubuntu/elasticsearch/logs
sudo chown -R ubuntu /home/ubuntu/elasticsearch/logs
sudo chgrp -R ubuntu /home/ubuntu/elasticsearch/logs

# Run elasticsearch
sudo -u ubuntu /home/ubuntu/elasticsearch/bin/elasticsearch -d # re-run if you shutdown your computer

# Run a query to test - it will error but should return json
curl 'localhost:9200/agile_data_science/on_time_performance/_search?q=Origin:ATL&pretty'

# Install Elasticsearch for Hadoop
curl -Lko /tmp/elasticsearch-hadoop-5.2.1.zip http://download.elastic.co/hadoop/elasticsearch-hadoop-5.2.1.zip
unzip /tmp/elasticsearch-hadoop-5.2.1.zip
mv /home/ubuntu/elasticsearch-hadoop-5.2.1 /home/ubuntu/elasticsearch-hadoop
cp /home/ubuntu/elasticsearch-hadoop/dist/elasticsearch-hadoop-5.2.1.jar /home/ubuntu/magic_world/lib/
cp /home/ubuntu/elasticsearch-hadoop/dist/elasticsearch-spark-20_2.10-5.2.1.jar /home/ubuntu/magic_world/lib/
echo "spark.speculation false" | sudo tee -a /home/ubuntu/spark/conf/spark-defaults.conf
rm -f /tmp/elasticsearch-hadoop-5.2.1.zip
rm -rf /home/ubuntu/elasticsearch-hadoop/conf/spark-defaults.conf

#
# Spark jar setup
#

# Install and add snappy-java and lzo-java to our classpath below via spark.jars
cd /home/ubuntu/magic_world
curl -Lko lib/snappy-java-1.1.2.6.jar http://central.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.2.6/snappy-java-1.1.2.6.jar
curl -Lko lib/lzo-hadoop-1.0.5.jar http://central.maven.org/maven2/org/anarres/lzo/lzo-hadoop/1.0.0/lzo-hadoop-1.0.0.jar
cd /home/ubuntu

# Set the spark.jars path
echo "spark.jars /home/ubuntu/magic_world/lib/mongo-hadoop-spark-2.0.2.jar,/home/ubuntu/magic_world/lib/mongo-java-driver-3.4.2.jar,/home/ubuntu/magic_world/lib/mongo-hadoop-2.0.2.jar,/home/ubuntu/magic_world/lib/elasticsearch-spark-20_2.10-5.2.1.jar,/home/ubuntu/magic_world/lib/snappy-java-1.1.2.6.jar,/home/ubuntu/magic_world/lib/lzo-hadoop-1.0.5.jar" | sudo tee -a /home/ubuntu/spark/conf/spark-defaults.conf

#
# Kafka install and setup
#
curl -Lko /tmp/kafka_2.11-0.10.1.1.tgz http://www-us.apache.org/dist/kafka/0.10.1.1/kafka_2.11-0.10.1.1.tgz
mkdir -p /home/ubuntu/kafka
cd /home/ubuntu/
tar -xvzf /tmp/kafka_2.11-0.10.1.1.tgz -C kafka --strip-components=1 && rm -f /tmp/kafka_2.11-0.10.1.1.tgz
rm -f /tmp/kafka_2.11-0.10.1.1.tgz

# Give to ubuntu
sudo chown -R ubuntu /home/ubuntu/kafka
sudo chgrp -R ubuntu /home/ubuntu/kafka

# Set the log dir to kafka/logs
sed -i '/log.dirs=\/tmp\/kafka-logs/c\log.dirs=logs' /home/ubuntu/kafka/config/server.properties

# Run zookeeper (which kafka depends on), then Kafka
sudo -H -u ubuntu /home/ubuntu/kafka/bin/zookeeper-server-start.sh -daemon /home/ubuntu/kafka/config/zookeeper.properties
sudo -H -u ubuntu /home/ubuntu/kafka/bin/kafka-server-start.sh -daemon /home/ubuntu/kafka/config/server.properties

#
# Install and setup Airflow
#
pip install airflow[hive]
mkdir /home/ubuntu/airflow
mkdir /home/ubuntu/airflow/dags
mkdir /home/ubuntu/airflow/logs
mkdir /home/ubuntu/airflow/plugins
airflow initdb
airflow webserver -D
airflow scheduler -D

sudo chown -R ubuntu /home/ubuntu/airflow
sudo chgrp -R ubuntu /home/ubuntu/airflow

# Install Apache Zeppelin
curl -Lko /tmp/zeppelin-0.7.0-bin-all.tgz http://www-us.apache.org/dist/zeppelin/zeppelin-0.7.0/zeppelin-0.7.0-bin-all.tgz
mkdir zeppelin
tar -xvzf /tmp/zeppelin-0.7.0-bin-all.tgz -C zeppelin --strip-components=1

# Configure Zeppelin
cp zeppelin/conf/zeppelin-env.sh.template zeppelin/conf/zeppelin-env.sh
echo "export SPARK_HOME=$PROJECT_HOME/spark" >> zeppelin/conf/zeppelin-env.sh
echo "export SPARK_MASTER=local" >> zeppelin/conf/zeppelin-env.sh
echo "export SPARK_CLASSPATH=" >> zeppelin/conf/zeppelin-env.sh

# Jupyter server setup
jupyter-notebook --generate-config
cp /home/ubuntu/magic_world/jupyter_notebook_config.py /home/ubuntu/.jupyter/
cd /home/ubuntu/magic_world
jupyter-notebook --ip=0.0.0.0 &
cd

#
# Cleanup
#
sudo apt-get clean
sudo rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
