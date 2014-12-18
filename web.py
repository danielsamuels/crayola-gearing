from raven.contrib.flask import Sentry

from run import Runner

from flask import Flask, send_file
app = Flask(__name__)
app.debug = True
app.config['SENTRY_DSN'] = 'https://bbe540f965174d2da70ffacd097c59db:6345ee5cc988477489f817f54eed054e@app.getsentry.com/32482'
sentry = Sentry(app)


@app.route("/")
def mains():
    return send_file('output-mains.csv', mimetype='text/csv; charset=utf-8')

@app.route("/alts")
def alts():
    return send_file('output-alts.csv', mimetype='text/csv; charset=utf-8')

if __name__ == "__main__":
    app.run()
