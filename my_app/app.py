from flask import Flask, render_template, url_for

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def home():
    return 'Welcome to Twitter Master'

@app.route('/send')
def send():
    return "<a href=%s>file</a>" % url_for('static', filename='../kafka_files/twitterstream_0.jsonl')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
