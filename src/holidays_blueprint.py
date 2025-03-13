import calendar
from datetime import datetime
from http import HTTPMethod, HTTPStatus
from typing import List, Optional, Tuple

import holidays
from flask import Blueprint, abort, request, render_template, make_response
import pycountry

holidays_blueprint = Blueprint('holidays_blueprint', __name__)
_COUNTRY_ARG = 'country'
_REGION_ARG = 'region'
_YEAR_ARG = 'year'
NONE_REGION = "None"


@holidays_blueprint.route('/', methods=[HTTPMethod.GET])
def holiday_list():
    supported_countries = sorted(holidays.registry.COUNTRIES.items())
    countries = [(country[1], _get_country_name(country[1])) for _, country in supported_countries]
    return render_template('index.html', countries=countries)

@holidays_blueprint.route('/holidays', methods=[HTTPMethod.GET])
def get_holidays():
    country_code = _validate_country_code(request.args.get(_COUNTRY_ARG))
    regions = _get_regions_for_country(country_code)
    region_code = _validate_region_code(request.args.get(_REGION_ARG), regions)
    year = _parse_year(request.args.get(_YEAR_ARG))

    holiday_days = sorted(holidays.country_holidays(country_code, region_code, year).items())
    holiday_model = [(calendar.day_name[day.weekday()], day, name) for day, name in holiday_days]

    country_name = _get_country_name(country_code)
    heading = f"Holidays in {_get_region_name(country_code, region_code)}, {country_name} for {year}" if region_code else f"National holidays in {country_name} for {year}"

    return render_template('region_selector.html',
                           regions=regions, selected_region=region_code, year=year,
                           heading=heading, holidays=holiday_model)

@holidays_blueprint.route('/liveness', methods=[HTTPMethod.GET])
def liveness():
    response = make_response("OK", HTTPStatus.OK)
    return response

def _validate_country_code(country_code: Optional[str]) -> str:
    if not country_code:
        abort(HTTPStatus.BAD_REQUEST, description="Country code not supplied")
    country_code = country_code.upper()
    if country_code not in holidays.list_supported_countries(True):
        abort(HTTPStatus.NOT_FOUND, description="Country code not supported")
    return country_code


def _get_country_name(country_code: str) -> str:
    country_info = pycountry.countries.get(alpha_2=country_code)
    return getattr(country_info, 'common_name', country_info.name) if country_info else country_code


def _validate_region_code(region_code: Optional[str], regions: List[Tuple[str, str]]) -> Optional[str]:
    if not regions and region_code:
        abort(HTTPStatus.BAD_REQUEST, description="Region code supplied for country without regions")
    if not region_code or region_code == NONE_REGION:
        return None
    region_code = region_code.upper()
    if region_code not in [region[0] for region in regions]:
        abort(HTTPStatus.NOT_FOUND, description="Region code not supported")
    return region_code


def _get_region_name(country_code: str, region_code: Optional[str]) -> str:
    if not region_code:
        return NONE_REGION
    region = pycountry.subdivisions.get(code=f'{country_code}-{region_code}')
    return region.name if region else region_code


def _get_regions_for_country(country_code: str) -> List[Tuple[str, str]]:
    region_codes = sorted(holidays.list_supported_countries(True).get(country_code, []))
    return [(region_code, _get_region_name(country_code, region_code)) for region_code in region_codes]


def _parse_year(year_str: Optional[str]) -> int:
    if not year_str:
        return datetime.now().year
    try:
        return int(year_str)
    except ValueError:
        abort(HTTPStatus.BAD_REQUEST, description="Year must be a number")