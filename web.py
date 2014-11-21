from run import Runner

from flask import Flask, make_response, send_file
app = Flask(__name__)
app.debug = True

@app.route("/")
def run():
    data = Runner()
    csv = data.output_csv()

    response = send_file(csv)
    response.headers["Content-Disposition"] = "attachment; filename=data.csv"
    return response

if __name__ == "__main__":
    app.run()
