from holidays_blueprint import holidays_blueprint
from flask import Flask

app = Flask(__name__)
app.register_blueprint(holidays_blueprint)
app.run

@app.after_request
def add_header(response):
    response.cache_control.max_age = 600
    response.cache_control.public = True
    return response
