from datetime import datetime
from fastapi.encoders import jsonable_encoder

def general_completer_user(payload, metadata):
    encoded_payload = jsonable_encoder(payload)
    dateTimeObj = datetime.now()

    encoded_payload["event_initiator_role"] = metadata["role"]
    encoded_payload["event_initiator_id"] = metadata["user_id"]
    encoded_payload["site_id"] = metadata["site_id"]
    encoded_payload["timestamp"] = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    return encoded_payload