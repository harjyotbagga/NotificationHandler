import enum
from datetime import datetime
from pipes import Template
from . import exceptions, email, utils
from .exporter import SENDGRID_API_KEY
from .constants import *
from .database import get_mongo_client
from .utils import FormatEmailListToString, FormatEmailStringToList

class NotificationCronEmailMethods(enum.Enum):
    ReconfigureNotificationCron = "ReconfigureNotificationCron"
    DeleteNotificationCron = "DeleteNotificationCron"

class NotificationCronEmail():
    TemplateName = "support_email_template.html"
    def __init__(self, site_id, cron_type, method, metadata={}):
        self.site_id = site_id
        self.site_name = utils.get_site_name(self.site_id)
        if self.site_name == None:
            raise exceptions.SiteDoesNotExistException(self.site_id)
        self.cron_type = cron_type
        if method not in NotificationCronEmailMethods:
            raise exceptions.InvalidNotificationCronEmailMethodException(method)
        self.method = method
        self.metadata = metadata

    def generate_email_body(self):
        date = datetime.utcnow().strftime("%Y-%m-%d")
        timestamp = datetime.utcnow().strftime("%H:%M %p")
        if self.method == NotificationCronEmailMethods.ReconfigureNotificationCron:
            email_body_text = f"Kindly reconfigure the {self.cron_type} notification cron for the site {self.site_name} (SiteID - {self.site_id}). The new configuration is as follows: {self.metadata.__str__()}"
        elif self.method == NotificationCronEmailMethods.DeleteNotificationCron:
            email_body_text = f"Kindly delete the {self.cron_type} notification cron for the site {self.site_name} (SiteID - {self.site_id})."
        email_body  = {
            "date": date,
            "timestamp": timestamp,
            "site_name": self.site_name,
            "email_body": email_body_text,
        }
        return email_body

    def get_email_recepients(self):
        db_instance = get_mongo_client()[NotificationsDatabase]
        collection = db_instance[EmailCollection]
        email_doc = collection.find_one({"type": "ITSupportTeam"})
        if email_doc == None:
            return []
        email_recepients = FormatEmailStringToList(email_doc.get("emails", ""))
        return email_recepients

    def send_email(self):
        email_body = email.render_email_template(NotificationCronEmail.TemplateName, self.generate_email_body())
        # DEV: Debug write output to file
        # email.write_debug_output(email_body)
        if self.method == NotificationCronEmailMethods.ReconfigureNotificationCron:
            subject = f"Reconfigure Notification Cron - {self.site_name} [{self.site_id}]"
        elif self.method == NotificationCronEmailMethods.DeleteNotificationCron:
            subject = f"Delete Notification Cron - {self.site_name} [{self.site_id}]"
        email_recepients = self.get_email_recepients()
        source_email = NOTIFICATION_SOURCE_EMAIL_ID
        try:
            email.send_email(source_email, email_recepients, subject, email_body)
        except exceptions.EmailNotSentException as e:
            raise exceptions.EmailNotSentException(f"Could not send email to {self.method} for site {self.site_name} (SiteID - {self.site_id}). Kindly contact the IT Support Team immediately.")