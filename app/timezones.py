import pytz
import datetime

timezones = list(set(pytz.all_timezones))
sorted_timezones = []

for tz in timezones:
    curr_time = datetime.datetime.now(pytz.timezone(tz))
    offset = curr_time.utcoffset().total_seconds()/60/60
    hours = int(offset)
    minutes = int((offset - hours) * 60)
    offset_str = f"{hours:02d}:{minutes:02d}"
    tz_info = {
        "timezone": tz,
        "offset_str": offset_str,
        "offset": offset
    }
    sorted_timezones.append(tz_info)

sorted_timezones=sorted(sorted_timezones, key=lambda x: (x["offset"], x["timezone"]))

tz1 = pytz.timezone("Asia/Kolkata")
print(tz1)

try:
    tz2 = pytz.timezone("ABC")
    print(tz2)
except pytz.exceptions.UnknownTimeZoneError as e:
    print("Unknown Timezone Error: " + str(e))
