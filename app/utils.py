import pytz
import datetime
import pymongo
from .database import get_mongo_client
from .exceptions import InvalidEnforcementHoursException, InvalidTimezoneException
from .constants import *

def validate_enforcement_hours(enforcement_from, enforcement_to):
    enforcement_from_list = enforcement_from.split(":")
    enforcement_to_list = enforcement_to.split(":")
    if len(enforcement_from_list) != 2 or len(enforcement_to_list) != 2:
        raise InvalidEnforcementHoursException()
    if not all(x.isdigit() for x in enforcement_from_list) or not all(x.isdigit() for x in enforcement_to_list):
        raise InvalidEnforcementHoursException()
    if int(enforcement_from_list[0]) > 23 or int(enforcement_from_list[1]) > 59 or int(enforcement_to_list[0]) > 23 or int(enforcement_to_list[1]) > 59:
        raise InvalidEnforcementHoursException()
    if int(enforcement_from_list[0]) > int(enforcement_to_list[0]):
        raise InvalidEnforcementHoursException()
    if int(enforcement_from_list[0]) == int(enforcement_to_list[0]) and int(enforcement_from_list[1]) > int(enforcement_to_list[1]):
        raise InvalidEnforcementHoursException()
    return True

def get_timezone_docs():
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
    return sorted(sorted_timezones, key=lambda x: (x["offset"], x["timezone"]))

def get_site_name(site_id: str):
    db_instance = get_mongo_client()[SitesDatabase]
    collection = db_instance[SiteListCollection]
    site_doc = collection.find_one({"site_id": site_id, "enable": True})
    if site_doc is None:
        return None
    return site_doc.get("site_name", "")

def FormatEmailListToString(email_list: list):
    if len(email_list) == 0:
        return ""
    email_str = ",".join(email_list)
    return email_str

def FormatEmailStringToList(email_str: str):
    if email_str == "":
        return []
    email_list = email_str.split(",")
    return email_list