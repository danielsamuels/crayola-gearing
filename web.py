
from raven.contrib.flask import Sentry

from run import Runner

from flask import Flask, send_file
app = Flask(__name__)
app.debug = True
app.config['SENTRY_DSN'] = 'https://bbe540f965174d2da70ffacd097c59db:6345ee5cc988477489f817f54eed054e@app.getsentry.com/32482'
sentry = Sentry(app)


@app.route("/")
def run():
    data = Runner()
    csv = data.output_csv()

    response = send_file(csv)
    response.headers["Content-Disposition"] = "attachment; filename=data.csv"
    return response

if __name__ == "__main__":
    app.run()
