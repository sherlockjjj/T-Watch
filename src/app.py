from flask import Flask, render_template, request
import json
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient()
collection = client.streams.tweets

# Process elasticsearch hits and return flights records
def process_search(results):
    records = []
    if results['hits'] and results['hits']['hits']:
        total = results['hits']['total']
        hits = results['hits']['hits']
        for hit in hits:
            record = hit['_source']
            records.append(record)
    return records, total

# Calculate offsets for fetching lists of flights from MongoDB
def get_navigation_offsets(offset1, offset2, increment):
    offsets = {}
    offsets['Next'] = {'top_offset': offset2 + increment, 'bottom_offset': offset1 + increment}
    offsets['Previous'] = {'top_offset': max(offset2 - increment, 0),\
                           'bottom_offset': max(offset1 - increment, 0)} 
    return offsets

# Strip the existing start and end parameters from the query string
def strip_place(url):
    try:
        p = re.match('(.+)&start=.+&end=.+', url).group(1)
    except AttributeError as e:
        return url
    return p

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
    start = request.args.get('start') or 0
    start = int(start)
    end = request.args.get('end') or 20
    end = int(end)
    width = end - start
    nav_offsets = get_navigation_offsets(start, end, 20):
    neg_tweets = collection.find({'prediction': 0}).skip(start).limit(width)
    return render_template('table.html', tweets=list(neg_tweets))
        
if __name__ == '__main__':
    app.run(debug=True)
