#start zookeeper
kafka/bin/zookeeper-server-start.sh kafka/config/zookeeper.properties
#start another window
#start kafka service
kafka/bin/kafka-server-start.sh kafka/config/server.properties
#start another window
#create topic
kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic twitterstream
