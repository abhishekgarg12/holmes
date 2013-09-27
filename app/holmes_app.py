import os
import json
import ast
import time

from flask import Flask, render_template

app = Flask(__name__)

TODAY = time.strftime('%d%m%Y')


def get_data():
    username = os.environ["USERNAME"]
    DB = os.path.join(r"T:\VDT\TEMP\chronos", username)
    orig = ast.literal_eval(open(DB).read())
    return orig

def get_user_data(user, date):
    data = get_data()
    filt = data[user][date]
    return filt

@app.route("/")
def index():
    data = get_data()
    return render_template("index.html", data=data, today=TODAY)

@app.route("/d3")
def d3():
    data = get_data()
    data = data['abhishek.garg'][TODAY]
    return render_template("d3.html", data = data)

def _round(inp):
    return round(inp,2)


app.jinja_env.add_extension('jinja2.ext.do')
app.jinja_env.globals.update(round = _round)
app.jinja_env.globals.update(user_data = get_user_data)

if __name__ == "__main__":
    app.run(debug=True)
