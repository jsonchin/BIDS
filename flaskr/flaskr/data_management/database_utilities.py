import datetime
import pytz

def get_current_time():
    return str(datetime.datetime.now(pytz.timezone('US/Pacific')))[:19]