from flask import Flask
from flask import render_template, request
import json
import time
from pymongo import MongoClient

app = Flask(__name__)

@app.route('/')
def hello():
    return json.dumps('Hello!')

@app.route('/summary',methods=['GET','POST'])
def summary():
    client = MongoClient()
    collection = client.streams.tweets
    ids = set()
    total_counts = 0
    positive_counts = 0
    negative_counts = 0
    for t in collection.find():
        if t['id'] not in ids:
            ids.add(t['id'])
            total_counts += 1
            if t['prediction'] == 1:
                positive_counts += 1
            else:
                negative_counts += 1
    client.close()
    return render_template('result.html',total=total_counts, positive=positive_counts, negative=negative_counts) 

if __name__ == '__main__':
    app.run(debug=True)
