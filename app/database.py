from pymongo import MongoClient
import datetime
from .exporter import MONGO_DB_LINK, MONGO_TRANSACTIONAL_DB_LINK

# Mongo DB Client
# Warning: use get_mongo_client method to get client access
_Mongo_Client = MongoClient(MONGO_DB_LINK)
_Transactional_Client = MongoClient(MONGO_TRANSACTIONAL_DB_LINK)

DATA_MAX_DAYS = 5

DatasetSummaryData = "DatasetSummaryData"

PaymentData = "PaymentData"
PermitData = "PermitData"
TimingData = "TimingData"
ScofflawData = "ScofflawData"

TYPE_CONFIG = {
    ScofflawData: {"timestamp_key": 'received_timestamp'},
    PaymentData: {"timestamp_key": 'received_timestamp'},
    PermitData: {"timestamp_key": 'received_timestamp'},
    TimingData: {"timestamp_key": 'mark_start_timestamp'},
}

def get_mongo_client(collection=None, from_ts=None, real_time_data=None):
    if TYPE_CONFIG.get(collection):
       if real_time_data:
           return _Transactional_Client
       if real_time_data is None and from_ts:
           ref_time = datetime.datetime.today() - datetime.timedelta(days=DATA_MAX_DAYS)
           from_ts = from_ts.replace(tzinfo=None)
           if from_ts >= ref_time:
               return _Transactional_Client
    return _Mongo_Client