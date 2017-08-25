"""
A consumer class that could receive Kafka messages
and store the messages in json lines 

"""
from kafka import KafkaConsumer
import time
from utils import *

class myConsumer():
    """
    KafkaConumser Wrapper to store kafka stream output
    """
    def __init__(self, topic, path=None):
        self.topic = topic
        self.path = path

    def _consume(self, consumer, time_interval=5):
        """
        Collect streams within the last 5 seconds
        """
        start = time.time()
        print time.time()
        for message in consumer:
            if time.time() > start + time_interval:
                break
            msg = message.value.decode('utf-8')
            #print msg
            self.results.append(msg)

    def consume_stream(self):
        """
        Create a consumer to consume current Kafka stream with the given topic
        and store to a local folder
        """
        consumer = KafkaConsumer(self.topic)
        print "collecting ..."
        self._consume(consumer)
        consumer.close()
        print "after collecting ..."
        pass

    def reset(self):
        self.results = []

    def run(self):
        self.reset()
        self.count = 0
        while self.count < 10:
            print "Repeat {}".format(self.count)
            path = self.path.format(self.topic, self.count)
            self.reset()
            print "Before collect {}".format(len(self.results))
            self.consume_stream()
            print "Collected {} streams".format(len(self.results))
            write_json_lines_file(self.results, path)
            self.count += 1



if __name__ == "__main__":
    path = 'kafka_files/{0}_{1}.jsonl'
    topic = 'twitterstream'
    mc = myConsumer(topic, path)
    mc.run()
