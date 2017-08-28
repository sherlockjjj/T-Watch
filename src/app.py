from flask import Flask, render_template, request
import json
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient()
collection = client.streams.tweets

@app.route('/')
def hello():
    return render_template('base.html')

@app.route('/summary',methods=['GET','POST'])
def summary():
    total_counts = collection.count()
    negative_counts = collection.find({'prediction': 0}).count()
    positive_counts = collection.find({'prediction': 1}).count()
    return render_template('result.html',total=total_counts, positive=positive_counts, negative=negative_counts) 

@app.route('/table', methods=['GET', 'POST'])
def table():
    neg_tweets = collection.find({'prediction': 0})
    return render_template('table.html', tweets=list(neg_tweets))
        
if __name__ == '__main__':
    app.run(debug=True)
