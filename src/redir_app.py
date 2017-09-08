#testing on redirecting console outputs to web app
import flask
import subprocess
import time

app = flask.Flask(__name__)
@app.route('/')
def hello():
    return 'Hello World'

@app.route('/index')
def index():
    def inner():
        proc = subprocess.Popen(
            'python src/spark-stream.py',             #call something with a lot of output so we can see it
            shell=True,
	    stdout=subprocess.PIPE
        )

        for line in iter(proc.stdout.readline,''):
            time.sleep(10)                           # Don't need this just shows the text streaming
            yield line.rstrip() + '<br/>\n'

    return flask.Response(inner(), mimetype='text/html')

if __name__ == "__main__":
    app.run(debug=True)
