import time
from datetime import datetime

def getGuestTime():
    curr_datetime = datetime.now()
    dt_string = curr_datetime.strftime("%d/%m/%Y")
    ti_string = curr_datetime.strftime("%H:%M:%S")
    return "{0} {1}".format(dt_string, ti_string)

def getGuestTimezone():
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    utc_offset = - (time.altzone if is_dst else time.timezone)/3600
    if utc_offset > 0:
        marker = "+"
    else:
        marker = "-"
    tzone = "UTC{0}{1}".format(marker, utc_offset)
    return tzone
