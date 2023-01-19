from datetime import datetime


class SiteDoesNotExistException(Exception):
    def __init__(self, site_id) -> None:
        self.message = f"{site_id} does not exist. Please check the site ID or contact the admin."
        super().__init__(self.message)

class InvalidNotificationException(Exception):
    def __init__(self, invalid_notification_name) -> None:
        self.message = f"{invalid_notification_name} is not a valid notification."
        super().__init__(self.message)

class DuplicateNotificationException(Exception):
    def __init__(self, site_id, notification_name) -> None:
        self.message = f"{notification_name} is already setup for {site_id}. Please update the existing notification."
        super().__init__(self.message)

class NotificationDoesNotExistException(Exception):
    def __init__(self, site_id, notification_name) -> None:
        self.message = f"{notification_name} is not setup for {site_id}. Please create a new notification."
        super().__init__(self.message)

class NotificationCronDoesNotExistException(Exception):
    def __init__(self, site_id, notification_name) -> None:
        self.message = f"{notification_name} is not been configured for {site_id}. Please configure the cron."
        super().__init__(self.message)

class InvalidEnforcementHoursException(Exception):
    def __init__(self) -> None:
        self.message = "The enforcement hours sent are invalid. Kindly check the enforcement hours sent."
        super().__init__(self.message)

class NotConfigurableNotificationsCronsException(Exception):
    def __init__(self, notification_name) -> None:
        self.message = f"{notification_name}'s cron is not configurable. If you think this is a mistake, kindly contact the admin."
        super().__init__(self.message)

class InvalidTimezoneException(Exception):
    def __init__(self, tz_name) -> None:
        self.message = f"{tz_name} is an invalid Timezone. Kindly select a valid timezone."
        super().__init__(self.message)

class InvalidDayFreqException(Exception):
    def __init__(self, freq) -> None:
        self.message = f"{freq} is an invalid freq value. Kindly send a valid freq value."
        super().__init__(self.message)

class InvalidBeatTimeFormatException(Exception):
    def __init__(self, beat_time) -> None:
        self.message = f"{beat_time} has an invalid format. Kindly send a valid beat_time value."
        super().__init__(self.message)

class InvalidBeatFreqFormatException(Exception):
    def __init__(self, beat_freq) -> None:
        self.message = f"{beat_freq} has an invalid format. Kindly send a valid beat_freq value."
        super().__init__(self.message)

class InvalidNotificationCronEmailMethodException(Exception):
    def __init__(self, method) -> None:
        self.message = f"{method} is an invalid method. Kindly send a valid method."
        super().__init__(self.message)

class EmailNotSentException(Exception):
    def __init__(self, message) -> None:
        curr_timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self.message = f"Could not send Email Successfully. Timestamp: {curr_timestamp}. Error: {message}"
        super().__init__(self.message)