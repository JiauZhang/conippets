import datetime as datetime_

timedelta = datetime_.timedelta
utcnow = datetime_.datetime.utcnow
fromtimestamp = datetime_.datetime.fromtimestamp
timestamp = datetime_.datetime.timestamp

del datetime_

def localtime(hours=8):
    utc_time = utcnow()
    time_delta = timedelta(hours=hours)
    my_time = utc_time + time_delta
    return my_time