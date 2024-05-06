import zoneinfo
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from flask import Blueprint

timezone_blueprint = Blueprint('timezone_blueprint', __name__)


@timezone_blueprint.route('/tz')
def test():
    # dt = datetime(2020, 10, 31, 12, tzinfo=ZoneInfo("America/Los_Angeles"))
    zones = zoneinfo.available_timezones()
    # return zones
    # tz_info = dt.tzinfo
    # return tz_info.tzname("America/Los_Angeles")
    return "Not working yet"