# tests/test_holidays_blueprint.py
import os
from http import HTTPStatus
from unittest.mock import patch

import pytest
from flask import Flask
from bs4 import BeautifulSoup
from holidays_blueprint import holidays_blueprint

@pytest.fixture
def app():
    template_folder = os.path.join(os.path.dirname(__file__), '..', 'src', 'templates')
    app = Flask(__name__, template_folder=template_folder)
    app.register_blueprint(holidays_blueprint)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_liveness(client):
    response = client.get('/liveness')
    assert response.status_code == HTTPStatus.OK
    assert b'OK' in response.data

@patch('holidays_blueprint.holidays')
@patch('holidays_blueprint.pycountry.countries.get')
@pytest.mark.parametrize("country_code, country_name", [
    ('AU', 'Australia'),
    ('DE', 'Germany'),
    ('ZA', 'South Africa')
])
def test_holiday_list(mock_pycountry, mock_holidays, client, country_code, country_name):
    # Set up the mock behavior for holidays
    mock_holidays.registry.COUNTRIES.items.return_value = [
        ('australia', ('Australia', 'AU', 'AUS')),
        ('germany', ('Germany', 'DE', 'DEU')),
        ('south_africa', ('SouthAfrica', 'ZA', 'ZAF'))
    ]

    # Set up the mock behavior for pycountry
    mock_pycountry.side_effect = lambda alpha_2: {
        'AU': type('Country', (object,), {'name': 'Australia'}),
        'DE': type('Country', (object,), {'name': 'Germany'}),
        'ZA': type('Country', (object,), {'name': 'South Africa'})
    }.get(alpha_2)

    response = client.get('/')
    assert response.status_code == HTTPStatus.OK

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(response.data, 'html.parser')
    country_selector = soup.find('select', {'id': 'country'})
    options = country_selector.find_all('option')

    # Verify the dropdown contains the expected country
    option_values = {option['value']: option.text for option in options[1:]}
    assert country_code in option_values
    assert option_values[country_code] == country_name