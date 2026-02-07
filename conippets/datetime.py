from datetime import datetime, UTC, timedelta

now = datetime.now
# return timestamp + utcoffset
fromtimestamp = datetime.fromtimestamp
timestamp = datetime.timestamp
fromisoformat = datetime.fromisoformat

def utcnow():
    return now(UTC)

def utcfromtimestamp(t):
    return fromtimestamp(t, UTC)

def localtime(hours=8):
    utc_time = utcnow()
    time_delta = timedelta(hours=hours)
    my_time = utc_time + time_delta
    return my_time
