#demo for daily streaming data sent to S3
import boto
from configparser import ConfigParser
from boto.s3.key import Key
from datetime import datetime
import os

if __name__ == "__main__":
    #authenticate
    config = ConfigParser()
    config.read('/home/ubuntu/capstone/.config/.credentials')
    region = config.get('aws', 'region')
    AWS_ACCESS_KEY_ID = config.get('aws', 'AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config.get('aws', 'AWS_SECRET_ACCESS_KEY')
    os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
    os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY

    today = datetime.now().strftime('%Y-%m-%d')
    path = '/home/ubuntu/capstone/stream_data/{}'.format(today)

    #create connection to s3
    conn = boto.connect_s3()
    bucket = conn.get_bucket('tweets-basketball')

    k = Key(bucket)
    k.key = today
    files = []
    for f in os.listdir(path):
        tmp = os.path.join(path, f)
        k.set_contents_from_filename(os.path.join(tmp, 'part-0000.gz'))
