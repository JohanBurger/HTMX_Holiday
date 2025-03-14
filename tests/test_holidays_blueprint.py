# tests/test_holidays_blueprint.py
import os
from http import HTTPStatus
from unittest.mock import patch
import unittest

from flask import Flask
from bs4 import BeautifulSoup
from holidays_blueprint import holidays_blueprint


class HolidaysBlueprintTestCase(unittest.TestCase):
    def setUp(self):
        template_folder = os.path.join(os.path.dirname(__file__), '..', 'src', 'templates')
        self.app = Flask(__name__, template_folder=template_folder)
        self.app.register_blueprint(holidays_blueprint)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_liveness(self):
        response = self.client.get('/liveness')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b'OK', response.data)

    @patch('holidays_blueprint.holidays')
    @patch('holidays_blueprint.pycountry.countries.get')
    def test_country_list(self, mock_pycountry, mock_holidays):
        mock_holidays.registry.COUNTRIES.items.return_value = [
            ('australia', ('Australia', 'AU', 'AUS')),
            ('germany', ('Germany', 'DE', 'DEU')),
            ('south_africa', ('SouthAfrica', 'ZA', 'ZAF'))
        ]
        mock_pycountry.side_effect = lambda alpha_2: {
            'AU': type('Country', (object,), {'name': 'Australia'}),
            'DE': type('Country', (object,), {'name': 'Germany'}),
            'ZA': type('Country', (object,), {'name': 'South Africa'})
        }.get(alpha_2)

        test_cases = [
            ('AU', 'Australia'),
            ('DE', 'Germany'),
            ('ZA', 'South Africa')
        ]
        for country_code, country_name in test_cases:
            with self.subTest(country_code=country_code, country_name=country_name):
                response = self.client.get('/')
                self.assertEqual(response.status_code, HTTPStatus.OK)

                soup = BeautifulSoup(response.data, 'html.parser')
                country_selector = soup.find('select', {'id': 'country'})
                options = country_selector.find_all('option')

                option_values = {option['value']: option.text for option in options[1:]}
                self.assertIn(country_code, option_values)
                self.assertEqual(option_values[country_code], country_name)

    def test_country_code_not_found(self):
        country_code = 'XX'
        response = self.client.get(f'/holidays?country={country_code}')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertIn('Country code not supported', response.data.decode())

    def test_country_code_not_supplied(self):
        response = self.client.get('/holidays')
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn('Country code not supplied', response.data.decode())
