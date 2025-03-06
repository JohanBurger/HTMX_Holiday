# tests/test_holidays_blueprint.py
import pytest
from flask import Flask
from holidays_blueprint import holidays_blueprint

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(holidays_blueprint)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_liveness(client):
    response = client.get('/liveness')
    assert response.status_code == 200
    assert b'OK' in response.data
