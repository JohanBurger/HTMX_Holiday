import calendar
from datetime import datetime

import holidays
from flask import Flask, render_template, request, abort

app = Flask(__name__)


@app.route('/')
def holiday_list():
    supported_countries = sorted(holidays.registry.COUNTRIES.items())
    countries = [(country[1], country[0]) for _, country in supported_countries]
    return render_template('index.html', countries=countries)


__COUNTRY_ARG = 'country'
__REGION_ARG = 'region'
__YEAR_ARG = 'year'


@app.route('/holidays')
def get_holidays():
    region = None
    year = datetime.today().year
    print(request.args.get(__COUNTRY_ARG))
    if request.args.get(__COUNTRY_ARG) is None:
        abort(404, description="Country code not found")
    country= request.args.get(__COUNTRY_ARG).upper()

    if request.args.get(__REGION_ARG) is not None:
        region = request.args.get(__REGION_ARG).upper()
        # TODO validate region

    if request.args.get(__YEAR_ARG) is not None:
        print(f"year:{request.args.get(__YEAR_ARG)}")

    supported_countries = holidays.list_supported_countries(True)
    if country not in supported_countries:
        # TODO: return render_template('error.html')
        abort(404, description=f"Country code {country} not found")

    regions = sorted(supported_countries[country])

    if region is None:
        holiday_days = holidays.country_holidays(country, years=2024).items()
    else:
        print(f"Here: country:{country}, region:{region}, year:{year}")
        holiday_days = holidays.country_holidays(country, region, years=2024).items()
    holiday_model =[(calendar.day_name[day.weekday()], day, name) for day, name in holiday_days]
    return render_template('region_selector.html',
                           regions=regions, selected_region=region, year=year, holidays=holiday_model)
