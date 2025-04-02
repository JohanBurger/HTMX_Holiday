# tests/test_holidays_blueprint.py
import os
from http import HTTPStatus
from unittest.mock import patch
import unittest

from flask import Flask
from bs4 import BeautifulSoup
from error_messages import ErrorMessages
from holidays_blueprint import holidays_blueprint
from pycountry import SubdivisionHierarchy


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
        self.assertIn(ErrorMessages.COUNTRY_CODE_NOT_SUPPORTED, response.data.decode())

    def test_country_code_not_supplied(self):
        response = self.client.get('/holidays')
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn(ErrorMessages.COUNTRY_CODE_NOT_SUPPLIED, response.data.decode())

    @patch('holidays_blueprint.holidays')
    @patch('holidays_blueprint.pycountry.countries.get')
    def test_region_code(self, mock_pycountry, mock_holidays):
        # Arrange
        country_code = 'AU'
        nt_code = 'NT'
        nt_name = 'Northern Territory'
        vic_code = 'VIC'
        vic_name = 'Victoria'

        mock_holidays.list_supported_countries.return_value = {country_code: [nt_code, vic_code]}
        mock_pycountry.subdivisions.get(f'{country_code}-{nt_code}').return_value = SubdivisionHierarchy(code=f'{country_code}-{nt_code}', country_code=country_code, name=nt_name, parent_code=None, type='Territory')
        mock_pycountry.subdivisions.get(f'{country_code}-{vic_code}').return_value = SubdivisionHierarchy(code=f'{country_code}-{vic_code}', country_code=country_code, name=vic_name, parent_code=None, type='State')

        # Act
        response = self.client.get('/holidays?country=AU')

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.OK)
        soup = BeautifulSoup(response.data, 'html.parser')
        region_selector = soup.find('select', {'id': 'region'})
        options = region_selector.find_all('option')
        self.assertEqual(len(options), 3)
        option_values = {option['value']: option.text for option in options[1:]}
        self.assertIn(nt_code, option_values)
        self.assertEqual(option_values[nt_code].strip(), nt_name)
        self.assertIn(vic_code, option_values)
        self.assertEqual(option_values[vic_code].strip(), vic_name)

    @patch('holidays_blueprint.holidays')
    @patch('holidays_blueprint.pycountry.countries.get')
    def test_region_code_not_found(self, mock_pycountry, mock_holidays):
        # Arrange
        country_code = 'AU'
        nt_code = 'NT'
        nt_name = 'Northern Territory'
        vic_code = 'VIC'
        vic_name = 'Victoria'

        mock_holidays.list_supported_countries.return_value = {country_code: [nt_code, vic_code]}
        mock_pycountry.subdivisions.get(f'{country_code}-{nt_code}').return_value = SubdivisionHierarchy(code=f'{country_code}-{nt_code}', country_code=country_code, name=nt_name, parent_code=None, type='Territory')
        mock_pycountry.subdivisions.get(f'{country_code}-{vic_code}').return_value = SubdivisionHierarchy(code=f'{country_code}-{vic_code}', country_code=country_code, name=vic_name, parent_code=None, type='State')

        # Act
        response = self.client.get('/holidays?country=AU&region=XX')

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertIn(ErrorMessages.REGION_CODE_NOT_SUPPORTED, response.data.decode())
