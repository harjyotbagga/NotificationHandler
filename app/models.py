import enum
import re
from wsgiref import validate
import pytz
import datetime
from . import exceptions
from .database import get_mongo_client
from .constants import NotificationsDatabase, NotificationListCollection

class CronType(enum.Enum):
    NonConfigurableCron = "non_configurable"
    PeriodicCron = "periodic"
    ScheduledCron = "schedule"

class CronDayFreq(enum.Enum):
    daily = "daily"
    weekday = "weekday"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

class Cron():
    def __init__(self, timezone, freq) -> None:
        self.timezone = timezone
        self.freq = freq
        self.validate_timezone(self.timezone)
        self.validate_freq(self.freq)

    def validate_timezone(self, timezone_name: str):
        try:
            pytz.timezone(timezone_name)
        except pytz.exceptions.UnknownTimeZoneError:
            raise exceptions.InvalidTimezoneException(timezone_name)

    def validate_freq(self, freq: str):
        if not CronDayFreq.has_value(freq):
            raise exceptions.InvalidDayFreqException(freq)

class PeriodicCron(Cron):
    def __init__(self, beat_freq, timezone, freq) -> None:
        super().__init__(timezone or "UTC", freq or "daily")
        self.beat_freq = beat_freq or 15
        self.validate_beat_freq(self.beat_freq)

    def validate_beat_freq(self, beat_freq):
        if not (isinstance(beat_freq, int) and beat_freq > 0):
            raise exceptions.InvalidBeatFreqFormatException(beat_freq)

class ScheduledCron(Cron):
    def __init__(self, beat_time, timezone, freq) -> None:
        super().__init__(timezone or "UTC", freq or "daily")
        self.beat_time = beat_time or "06:00"
        self.validate_beat_time(self.beat_time)

    def validate_beat_time(self, beat_time: str):
        tz_regex_pattern = r"^(?:2[0-3]|[01][0-9]):[0-5][0-9]$"
        tz_regex = re.compile(tz_regex_pattern)
        if not bool(re.fullmatch(tz_regex, beat_time)):
            raise exceptions.InvalidBeatTimeFormatException(beat_time)

def get_valid_notifications():
    valid_notifications = [
        NoPermitUploadNotification.NotificationName,
        NoScofflawUploadNotification.NotificationName,
        DailyCitationNotification.NotificationName,
        CitationCountNotification.NotificationName,
        SiteExportNotification.NotificationName,
        HighLatencyNotification.NotificationName,
        NoTransactionNotification.NotificationName,
    ]
    return valid_notifications

def get_notification_class(notification_name: str):
    notification_class_dict = {
        NoPermitUploadNotification.NotificationName: NoPermitUploadNotification,
        NoScofflawUploadNotification.NotificationName: NoScofflawUploadNotification,
        DailyCitationNotification.NotificationName: DailyCitationNotification,
        CitationCountNotification.NotificationName: CitationCountNotification,
        SiteExportNotification.NotificationName: SiteExportNotification,
        HighLatencyNotification.NotificationName: HighLatencyNotification,
        NoTransactionNotification.NotificationName: NoTransactionNotification,
    }
    notification_class = notification_class_dict.get(notification_name, None)
    if notification_class is None:
        raise exceptions.InvalidNotificationException(notification_name)
    return notification_class

class SiteNotification():
    NotificationMetadataKeys = {}
    def __init__(self, site_id, email_recipients) -> None:
        self.site_id = site_id
        self.email_recipients = email_recipients
        self.notification_name = "Site Notification"
        self.created_at = datetime.datetime.utcnow()
        self.metadata = {}   

    @staticmethod
    def FormatEmailListForDatabase(email_list: list):
        if len(email_list) == 0:
            return ""
        email_str = ",".join(email_list)
        return email_str

    @staticmethod
    def FormatEmailStringForResponse(email_str: str):
        if email_str == "":
            return []
        email_list = email_str.split(",")
        return email_list

    def DoesNotificationExist(self) -> bool:
        db_instance = get_mongo_client()[self.site_id]
        collection = db_instance[NotificationListCollection]
        doc = collection.find_one({
            "entity_details": {"$elemMatch": {"notification_name": self.notification_name}}
            })
        if doc is None:
            return False
        return True

    def CreateNotification(self):
        new_notification = self.__dict__
        new_notification["email"] = self.FormatEmailListForDatabase(new_notification.get("email", []))
        db_instance = get_mongo_client()[self.site_id]
        collection = db_instance[NotificationListCollection]
        doc = collection.find_one({"entity_type": "NotificationList"})
        if doc is None:
            new_notification_list = {
                "entity_type": "NotificationList",
                "entity_details": [new_notification],
                "created_at": self.created_at,
                "site_id": self.site_id
            }
            collection.insert_one(new_notification_list)
            return
        
        notification_list = doc.get("entity_details", [])
        for notification in notification_list:
            if notification.get("notification_name") == self.notification_name:
                raise exceptions.DuplicateNotificationException(self.site_id, self.notification_name)
        notification_list.append(new_notification)
        collection.update_one({"entity_type": "NotificationList"}, {"$set": {"entity_details": notification_list}})
        return

    def GetNotificationInfo(self):
        db_instance = get_mongo_client()[self.site_id]
        collection = db_instance[NotificationListCollection]
        doc = collection.find_one({
            "entity_details": {"$elemMatch": {"notification_name": self.notification_name}}
            })
        if doc is None:
            raise exceptions.NotificationDoesNotExistException(self.site_id, self.notification_name)
        notification_list = doc.get("entity_details", [])
        for notification in notification_list:
            if notification.get("notification_name") == self.notification_name:
                notification["email"] = self.FormatEmailStringForResponse(notification.get("email", ""))
                return notification
        raise exceptions.NotificationDoesNotExistException(self.site_id, self.notification_name)

    def UpdateNotification(self):
        notification = self.__dict__
        notification["email"] = self.FormatEmailListForDatabase(notification.get("email", []))
        db_instance = get_mongo_client()[self.site_id]
        collection = db_instance[NotificationListCollection]
        doc = collection.find_one({"entity_type": "NotificationList"})
        if doc is None:
            raise exceptions.NotificationDoesNotExistException(self.site_id, self.notification_name)
        notification_list = doc.get("entity_details", [])
        notification_exists = False
        for idx, notification_doc in enumerate(notification_list):
            if notification_doc.get("notification_name") == self.notification_name:
                notification_list[idx] = notification
                notification_exists = True
                break
        if not notification_exists:
            raise exceptions.NotificationDoesNotExistException(self.site_id, self.notification_name)
        collection.update_one({"entity_type": "NotificationList"}, {"$set": {"entity_details": notification_list}})
        return

    def DeleteNotification(self):
        db_instance = get_mongo_client()[self.site_id]
        collection = db_instance[NotificationListCollection]
        doc = collection.find_one({"entity_type": "NotificationList"})
        if doc is None:
            raise exceptions.NotificationDoesNotExistException(self.site_id, self.notification_name)
        notification_list = doc.get("entity_details", [])
        notification_exists = False
        for idx, notification_doc in enumerate(notification_list):
            if notification_doc.get("notification_name") == self.notification_name:
                notification_exists = True
                break
        if not notification_exists:
            raise exceptions.NotificationDoesNotExistException(self.site_id, self.notification_name)
        else:
            notification_list.pop(idx)
            collection.update_one({"entity_type": "NotificationList"}, {"$set": {"entity_details": notification_list}})
        return

    @property
    def __dict__(self) -> dict:
        return {
            "notification_name": self.notification_name,
            "email": self.email_recipients,
            "created_at": self.created_at,
            "metadata": self.metadata
        }
    def __repr__(self) -> str:
        return "SiteNotification(site_id, notification_name, subject, email_recipients, email_body)"
    def __str__(self) -> str:
        return f"SiteNotification({self.site_id}, {self.notification_name})"

class NoPermitUploadNotification(SiteNotification):
    NotificationName = "No Permit Uploaded Notification"
    NotificationCronName = "PermitNotificationsCron"
    NotificationCronType = CronType.ScheduledCron
    isCronConfigurable = True
    def __init__(self, site_id, email_recipients=[], metadata={}) -> None:
        super().__init__(site_id, email_recipients)
        self.notification_name = "No Permit Uploaded Notification"
        self.set_default_beat_values(metadata)

    def set_default_beat_values(self, metadata) -> None:
        self.metadata = {}
    
class NoScofflawUploadNotification(SiteNotification):
    NotificationName = "No Scofflaw Uploaded Notification"
    NotificationCronName = "ScofflawNotificationsCron"
    NotificationCronType = CronType.ScheduledCron
    isCronConfigurable = True
    def __init__(self, site_id, email_recipients=[], metadata={}) -> None:
        super().__init__(site_id, email_recipients)
        self.notification_name = "No Scofflaw Uploaded Notification"
        self.set_default_beat_values(metadata)

    def set_default_beat_values(self, metadata) -> None:
        self.metadata = {}

class DailyCitationNotification(SiteNotification):
    NotificationName = "Daily Citation Notification"
    NotificationCronName = "DailyCitationNotificationsCron"
    NotificationCronType = CronType.ScheduledCron
    isCronConfigurable = True
    def __init__(self, site_id, email_recipients=[], metadata={}) -> None:
        super().__init__(site_id, email_recipients)
        self.notification_name = "Daily Citation Notification"
        self.set_default_beat_values(metadata)

    def set_default_beat_values(self, metadata) -> None:
        self.metadata = {}

class CitationCountNotification(SiteNotification):
    NotificationName = "Citation Count Notification"
    NotificationCronName = "CitationCountNotificationsCron"
    NotificationCronType = CronType.ScheduledCron
    isCronConfigurable = True
    def __init__(self, site_id, email_recipients=[], metadata={}) -> None:
        super().__init__(site_id, email_recipients)
        self.notification_name = "Citation Count Notification"
        self.set_default_beat_values(metadata)

    def set_default_beat_values(self, metadata) -> None:
        self.metadata = {}

class SiteExportNotification(SiteNotification):
    NotificationName = "Site Export Notification"
    NotificationCronName = None
    NotificationCronType = CronType.NonConfigurableCron
    isCronConfigurable = False
    def __init__(self, site_id, email_recipients=[], metadata={}) -> None:
        super().__init__(site_id, email_recipients)
        self.notification_name = "Site Export Notification"
        self.set_default_beat_values(metadata)

    def set_default_beat_values(self, metadata) -> None:
        self.metadata = {}

class HighLatencyNotification(SiteNotification):
    NotificationName = "Integration Latency Notification"
    NotificationCronName = "IntegrationLatencyNotificationsCron"
    NotificationCronType = CronType.PeriodicCron
    isCronConfigurable = True
    NotificationMetadataKeys = {
        "num_of_transactions": {
            "title": "Number of Transactions",
            "description": "The number of high latency transactions that need to be there for a High Latency Report to be sent.",
            "default_value": 10
        },
        "latency_threshold": {
            "title": "Latency Threshold",
            "description": "The Latency Threshold Value that is considered high for a transactions in seconds.",
            "default_value": 200
        },
        "latency_duration_threshold": {
            "title": "Latency Duration Threshold",
            "description": "The duration / interval for which High Latency Transactions are considered in minutes.",
            "default_value": 15
        }
    }
    def __init__(self, site_id, email_recipients=[], metadata={}) -> None:
        super().__init__(site_id, email_recipients)
        self.notification_name = "Integration Latency Notification"
        self.set_default_beat_values(metadata)

    def set_default_beat_values(self, metadata) -> None:
        self.metadata = {
            "num_of_transactions": metadata.get("num_of_transactions", 10),
            "latency_threshold": metadata.get("latency_threshold", 200),
            "latency_duration_threshold": metadata.get("latency_duration_threshold", 15),
        }

class NoTransactionNotification(SiteNotification):
    NotificationName = "No Transaction Notification"
    NotificationCronName = "NoTransactionNotificationsCron"
    NotificationCronType = CronType.PeriodicCron
    isCronConfigurable = True
    NotificationMetadataKeys = {
        "no_transaction_threshold": {
            "title": "No Transaction Threshold",
            "description": "The threshold interval to be considered for checking if transactions exist in minutes.",
            "default_value": 15
        },
    }
    def __init__(self, site_id, email_recipients=[], metadata={}) -> None:
        super().__init__(site_id, email_recipients)
        self.notification_name = "No Transaction Notification"
        self.set_default_beat_values(metadata)

    def set_default_beat_values(self, metadata) -> None:
        self.metadata = {
            "no_transaction_threshold": metadata.get("no_transaction_threshold", 15),
        }