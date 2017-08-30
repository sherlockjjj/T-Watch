from flask import Flask, render_template, request
import json, ast
from pymongo import MongoClient
from utils import team_dict
from datetime import datetime
from collections import Counter
import plotly 
import plotly.plotly as py
import plotly.graph_objs as go
import operator 

app = Flask(__name__)

client = MongoClient()
collection = client.streams.nba

#setting up plotly
with open('/home/ubuntu/.plotly/.credentials') as f:
    file = ast.literal_eval(f.read())
plotly.tools.set_credentials_file(username=file['username'], api_key=file['api_key'])

@app.route('/')
def hello():
    return render_template('base.html')

@app.route('/summary',methods=['GET','POST'])
def summary():
    total_counts = collection.count()
    negative_counts = collection.find({'prediction': 0}).count()
    positive_counts = collection.find({'prediction': 1}).count()
    return render_template('result.html',total=total_counts, positive=positive_counts, negative=negative_counts) 

@app.route('/topics', methods=['GET', 'POST'])
def topics():
    return render_template('topics.html', teams=list(team_dict.keys()))
    
@app.route('/negative', methods=['GET', 'POST'])
def find_negative():
    neg_tweets = collection.find({'prediction': 0}).sort('created_at', -1).limit(40)
    return render_template('table.html', tweets_count=neg_tweets.count(), topic='Negative', tweets=list(neg_tweets))

@app.route('/positive', methods=['GET', 'POST'])
def find_positive():
    pos_tweets = collection.find({'prediction': 1}).sort('created_at', -1).limit(40)
    return render_template('table.html', tweets_count=pos_tweets.count(), topic='Positive', tweets=list(pos_tweets))

@app.route('/team=<team>')
def find_team(team):
    team = " ".join(team.split("%20"))
    team_tweets = collection.find({'teams': team}).sort('created_at', -1).limit(40)
    return render_template('table.html', tweets_count=team_tweets.count(), topic=team, tweets=list(team_tweets))

@app.route('/search')
@app.route('/search/')
def search():
    #search parameters
    topics = request.args.get('topic')
    followers = request.args.get('followers')
    return render_template('search.html')

#not working right now
@app.route('/team=<topic>/followers=<followers>')  
def find_team_with_followers(team, followers):
    team = " ".join(team.split("%20"))
    team_tweets = collection.find({'teams': topic, 'followers': {'gte': int(followers)}}).sort('created_at', -1).limit(40)
    return render_template('table.html', tweets_count=team_tweets.count(), topic=team, tweets=list(team_tweets))

@app.route('/topic_counts_chart')
def topic_counts_chart():
    topic_counts = collection.find()
    topic_counts = list(map(lambda x: x['teams'], topic_counts))
    d = dict(Counter(topic_counts))    
    sorted_x = sorted(d.items(), key=operator.itemgetter(1))
    x = []
    y = []
    for a, b in sorted_x:
        x.append(a)
        y.append(b)
    #plot 
    data = [go.Bar(
            x=x,
            y=y
    )]
    url = py.plot(data, filename='basic-bar')
    url += '.embed'
    return render_template('chart.html', chart_url=url)

@app.route('/topic_counts_chart.json')
def topic_counts_json():
    topic_counts = collection.find()
    topic_counts = list(map(lambda x: x['teams'], topic_counts))
    d = dict(Counter(topic_counts))
    d_list = [{'topic': k, 'counts': v} for k,v in d.items()]
    return json.dumps(d_list, ensure_ascii=False)

if __name__ == '__main__':
    app.run(debug=True)
