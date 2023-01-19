import site
import pymongo
from pytz import timezone
from .database import get_mongo_client
from .constants import *
from . import exceptions, models, utils, notify

def GetNotificationList(filters: dict):
    db_instance = get_mongo_client()[NotificationsDatabase]
    collection = db_instance[NotificationListCollection]
    notification_documents = collection.find(filters)
    notification_list = []
    for notification_document in notification_documents:
        notification = {}
        notification["notification_name"] = notification_document.get("notification_name", "")
        Notification = models.get_notification_class(notification["notification_name"])
        notification["notification_cron_name"] = Notification.NotificationCronName
        notification["cron_type"] = Notification.NotificationCronType
        notification["is_cron_configurable"] = Notification.isCronConfigurable
        notification["metadata_keys"] = Notification.NotificationMetadataKeys
        notification_list.append(notification)
    return notification_list

def GetSiteNotificationList(site_id: str):
    db_instance = get_mongo_client()[site_id]
    collection = db_instance[NotificationListCollection]
    notification_list = list(collection.find({}, {"_id": 0}))
    if notification_list:
        return notification_list[0].get("entity_details", [])
    return notification_list

def CreateNotification(payload: dict):
    notification_name = payload.get("notification_name", "")
    Notification = models.get_notification_class(notification_name)
    notification = Notification(
        site_id=payload.get("site_id", ""),
        email_recipients=payload.get("email_recipients", []),
        metadata=payload.get("metadata", {})
    )
    notification.CreateNotification()
    return

def UpdateNotification(payload: dict):
    notification_name = payload.get("notification_name", "")
    Notification = models.get_notification_class(notification_name)
    notification = Notification(
        site_id=payload.get("site_id", ""),
        email_recipients=payload.get("email_recipients", []),
        metadata=payload.get("metadata", {})
    )
    notification.UpdateNotification()
    return

def DeleteNotification(payload: dict):
    notification_name = payload.get("notification_name", "")
    Notification = models.get_notification_class(notification_name)
    notification = Notification(
        site_id=payload.get("site_id", "")
    )
    notification.DeleteNotification()
    return

def GetNotificationInfo(site_id: str, notification_name: str):
    Notification = models.get_notification_class(notification_name)
    notification = Notification(
        site_id=site_id
    )
    return notification.GetNotificationInfo()

def GetEnforcementHours(site_id: str):
    db_instance = get_mongo_client()[site_id]
    collection = db_instance[ConfigurationListCollection]
    enforcement_config = collection.find_one({"config_type": "enforcement_hours"})
    if enforcement_config is None:
        return {}
    return enforcement_config.get("metadata", {})

def SetEnforcementHours(payload: dict):
    site_id = payload.get("site_id")
    db_instance = get_mongo_client()[site_id]
    collection = db_instance[ConfigurationListCollection]
    utils.validate_enforcement_hours(payload.get("enforcement_from", ""), payload.get("enforcement_to", ""))
    enforcement_config = {
        "config_type": "enforcement_hours",
        "metadata": {
            "enforcement_from": payload.get("enforcement_from", "00:00"),
            "enforcement_to": payload.get("enforcement_to", "23:59")
        }
    }
    collection.update_one({"config_type": "enforcement_hours"}, {"$set": enforcement_config}, upsert=True)
    return

def DeleteEnforcementHours(payload: dict):
    site_id = payload.get("site_id")
    db_instance = get_mongo_client()[site_id]
    collection = db_instance[ConfigurationListCollection]
    collection.delete_one({"config_type": "enforcement_hours"})
    return

def GetTimezoneList():
    db_instance = get_mongo_client()[NotificationsDatabase]
    collection = db_instance[TimezoneListCollection]
    timezone_docs = list(collection.find({}, {"_id": 0}))
    return timezone_docs

def SetTimezoneList():
    db_instance = get_mongo_client()[NotificationsDatabase]
    collection = db_instance[TimezoneListCollection]
    timezone_docs = utils.get_timezone_docs()
    requests = []
    for timezone_doc in timezone_docs:
        timezone_doc["offset"] = timezone_doc["offset_str"]
        timezone_doc.pop("offset_str")
        requests.append(
                pymongo.UpdateOne(
                    {"timezone": timezone_doc["timezone"]}, {"$setOnInsert": timezone_doc}, upsert=True
                )
            )
    collection.bulk_write(requests) 

def GetNotificationCronInfo(site_id: str, notification_name: str):
    db_instance = get_mongo_client()[ParkLoyaltyDatabase]
    collection = db_instance[CronInfoCollection]
    notification = models.get_notification_class(notification_name)
    if not notification.isCronConfigurable:
        raise exceptions.NotConfigurableNotificationsCronsException(notification_name)
    notification_cron_name = notification.NotificationCronName
    notification_cron_info = collection.find_one({
        "cron_type": notification_cron_name, 
        "sites": {"$in": [site_id]}
    }, {"_id": 0})
    if notification_cron_info is None:
        return {}
    return notification_cron_info.get("mapping", {}).get(site_id, {})

def SetNotificationCronInfo(payload: dict):
    notification_name = payload.get("notification_name")
    site_id = payload.get("site_id")
    notification = models.get_notification_class(notification_name)
    if not notification.isCronConfigurable:
        raise exceptions.NotConfigurableNotificationsCronsException(notification_name)
    notification_cron_name = notification.NotificationCronName
    notification_cron_type = notification.NotificationCronType
    cron_setting = {}
    if notification_cron_type == models.CronType.PeriodicCron:
        cron = models.PeriodicCron(
            beat_freq=payload.get("beat_freq"),
            timezone=payload.get("timezone"),
            freq=payload.get("freq")
        )
        cron_setting = cron.__dict__
    elif notification_cron_type == models.CronType.ScheduledCron:
        cron = models.ScheduledCron(
            beat_time=payload.get("beat_time"),
            timezone=payload.get("timezone"),
            freq=payload.get("freq")
        )
        cron_setting = cron.__dict__
    else:
        raise exceptions.NotConfigurableNotificationsCronsException(notification_name)
    
    db_instance = get_mongo_client()[ParkLoyaltyDatabase]
    collection = db_instance[CronInfoCollection]
    notification_cron_info = collection.find_one({
        "cron_type": notification_cron_name,
    }, {"_id": 0})
    if notification_cron_info is None:
        notification_cron_info = {}
    active_sites = notification_cron_info.get("sites", [])
    mapping = notification_cron_info.get("mapping", {})
    if site_id not in active_sites:
        active_sites.append(site_id)
    mapping[site_id] = cron_setting
    notification_cron_info["cron_type"] = notification_cron_name
    notification_cron_info["sites"] = active_sites
    notification_cron_info["mapping"] = mapping
    try:
        email = notify.NotificationCronEmail(
            site_id, 
            notification_cron_name, 
            notify.NotificationCronEmailMethods.ReconfigureNotificationCron, 
            metadata=cron_setting
        )
        email.send_email()
    except exceptions.EmailNotSentException as e: 
        raise e
    except Exception as e:
        raise e
    collection.update_one({"cron_type": notification_cron_name}, {"$set": notification_cron_info}, upsert=True)
    return

def DeleteNotificationCronInfo(payload: dict):
    notification_name = payload.get("notification_name")
    site_id = payload.get("site_id")
    notification = models.get_notification_class(notification_name)
    if not notification.isCronConfigurable:
        raise exceptions.NotConfigurableNotificationsCronsException(notification_name)
    notification_cron_name = notification.NotificationCronName
    
    db_instance = get_mongo_client()[ParkLoyaltyDatabase]
    collection = db_instance[CronInfoCollection]
    notification_cron_info = collection.find_one({
        "cron_type": notification_cron_name,
        "sites": {"$in": [site_id]}
    }, {"_id": 0})
    if notification_cron_info is None:
        raise exceptions.NotificationCronDoesNotExistException(site_id, notification_name)
    active_sites = notification_cron_info.get("sites", [])
    mapping = notification_cron_info.get("mapping", {})
    for idx, active_site_id in enumerate(active_sites):
        if site_id == active_site_id:
            del active_sites[idx]
            break
    mapping.pop(site_id)
    notification_cron_info["cron_type"] = notification_cron_name
    notification_cron_info["sites"] = active_sites
    notification_cron_info["mapping"] = mapping
    
    try:
        email = notify.NotificationCronEmail(
            site_id, 
            notification_cron_name, 
            notify.NotificationCronEmailMethods.DeleteNotificationCron, 
        )
        email.send_email()
    except exceptions.EmailNotSentException as e: 
        raise e
    except Exception as e:
        raise e
    collection.update_one({"cron_type": notification_cron_name}, {"$set": notification_cron_info}, upsert=True)
    return
