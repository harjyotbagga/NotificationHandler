import datetime
from pydantic import BaseModel
from typing import Dict, Optional, List

class SiteNotificationPayload(BaseModel):
    notification_name: str
    email_recipients: Optional[List[str]] = []
    metadata: Optional[Dict] = {}

    class Config:
        orm_mode = True

class EnforcementHoursPayload(BaseModel):
    enforcement_from: str
    enforcement_to: str

    class Config:
        orm_mode = True

class NotificationCronInfoPayload(BaseModel):
    notification_name: str
    timezone: Optional[str] = "UTC"
    freq: Optional[str] = None
    beat_freq: Optional[str] = None
    beat_time: Optional[str] = None

    class Config:
        orm_mode = True