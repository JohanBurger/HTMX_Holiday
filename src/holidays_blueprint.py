import calendar
from datetime import datetime

import holidays
from flask import Blueprint, abort, request, render_template

holidays_blueprint = Blueprint('holidays_blueprint', __name__)
_COUNTRY_ARG = 'country'
_REGION_ARG = 'region'
_YEAR_ARG = 'year'


@holidays_blueprint.route('/')
def holiday_list():
    supported_countries = sorted(holidays.registry.COUNTRIES.items())
    countries = [(country[1], country[0]) for _, country in supported_countries]
    print(countries)
    return render_template('index.html', countries=countries)


@holidays_blueprint.route('/holidays')
def get_holidays():
    country = _parse_country()

    regions = sorted(holidays.list_supported_countries(True)[country])
    region = _parse_region_for(regions)

    year = _parse_year()

    holiday_days = sorted(holidays.country_holidays(country, region, year).items())

    holiday_model =[(calendar.day_name[day.weekday()], day, name) for day, name in holiday_days]
    if region is None:
        heading = f"National holidays in {country} for {year}"
    else:
        heading = f"Holidays in {region}, {country} for {year}"

    return render_template('region_selector.html',
                           regions=regions, selected_region=region, year=year, heading=heading, holidays=holiday_model)


def _parse_country():
    country = request.args.get(_COUNTRY_ARG)
    if country is None:
        abort(400, description="Country code not supplied")
    supported_countries = holidays.list_supported_countries(True)
    if country not in supported_countries:
        abort(404, description="Country code not supported")
    return country.upper()


def _parse_region_for(regions):
    region = request.args.get(_REGION_ARG)
    if regions is None and region is not None:
        abort(400, description="Region code supplied for country without regions")
    if region is None or region == "None":
        print("No region specified")
        return None
    if region not in regions:
        abort(404, description="Region code not supported")
    return region.upper()


def _parse_year():
    year = request.args.get(_YEAR_ARG)
    if year is None:
        return datetime.now().year
    try:
        year = int(year)
    except ValueError:
        abort(400, description="Year must be a number")
    return year