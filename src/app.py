import holidays
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def holiday_list():
    list = sorted(holidays.country_holidays("DE", "HE", years=2024).items())
    return render_template('index.html', list=list)
