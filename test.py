
import time
from datetime import datetime, timedelta

time_obj = [5, 3, 0]
converted_time = datetime(2000, 1, time_obj[0], time_obj[1], time_obj[2])
time_now = time.gmtime()
time_now = datetime(2000, 1, time_now.tm_wday, time_now.tm_hour, time_now.tm_min)
if converted_time < time_now:
    print('that time is in the past')
else:
    time_diff = converted_time - time_now + timedelta(minutes=15)
    print(f'in {time_diff.days} days, {int(time_diff.seconds/3600)} hours, {int((time_diff.seconds%3600)/60)} minutes')