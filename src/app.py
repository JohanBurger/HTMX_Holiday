import calendar

import holidays
from flask import Flask, render_template, request, abort

app = Flask(__name__)


@app.route('/')
def holiday_list():
    supported_countries = sorted(holidays.registry.COUNTRIES.items())
    countries = [(country[1], country[0]) for _, country in supported_countries]
    return render_template('index.html', countries=countries)


@app.route('/holidays')
def get_holidays():
    for arg in request.args:
        print(arg)
    country = request.args.get('country').upper()
    region = None #request.args.get('region').upper
    year = 2024#request.args.get('year')

    print(f"country:{country}, region:{region}, year:{year}")

    supported_countries = holidays.list_supported_countries(True)
    if country not in supported_countries:
        # TODO: return render_template('error.html')
        abort(404, description=f"Country code {country} not found")

    regions = sorted(supported_countries[country])
    if regions is not None:
        region = regions[0]

    # if region not in regions:
    #     abort(404, description=f"Region code {region} not found")

    holiday_days = holidays.country_holidays(country, region, 2024).items()
    holiday_model =[(calendar.day_name[day.weekday()], day, name) for day, name in holiday_days]
    return render_template('region_selector.html', regions=regions, year=year, holidays=holiday_model)
