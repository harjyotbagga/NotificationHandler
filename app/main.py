from fastapi import FastAPI, Header, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from . import service, completer, responses, auth, schemas, exceptions

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_PREFIX = "/notification-handler"

@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    return responses.ResponseModel("Park Loyalty", True, "Park Loyalty Notification Handler Service.")


@app.get(BASE_PREFIX + "/", status_code=status.HTTP_200_OK)
async def read_root():
    return responses.ResponseModel("Park Loyalty", True, "Park Loyalty Notification Handler Entrypoint.")


@app.get(BASE_PREFIX + "/url_list", status_code=status.HTTP_200_OK)
def get_all_urls():
    url_list = [{"path": route.path, "name": route.name} for route in app.routes]
    return responses.ResponseModel(url_list, True, "All URLs")


@app.get(BASE_PREFIX + "/get_notification_list", status_code=status.HTTP_200_OK)
def get_notification_list(auth = Depends(auth.verifyEDITAuthenticationAndAuthorizationRequest)):
    try:
        notification_list = service.GetNotificationList({})
        return responses.ResponseModel(notification_list, True, "Notification List")
    except Exception as e:
        return responses.HTTPExceptionResponse(status_code=500, message=str(e))


@app.get(BASE_PREFIX + "/get_site_notification_list", status_code=status.HTTP_200_OK)
def get_site_notification_list(auth = Depends(auth.verifyEDITAuthenticationAndAuthorizationRequest)):
    try:
        site_id = auth.get("metadata", {}).get("site_id")
        notification_list = service.GetSiteNotificationList(site_id)
        return responses.ResponseModel(notification_list, True, "Site Notification List")
    except Exception as e:
        return responses.HTTPExceptionResponse(status_code=500, message=str(e))


@app.post(BASE_PREFIX + "/create_notification", status_code=status.HTTP_201_CREATED)
def create_notification(payload: schemas.SiteNotificationPayload, auth = Depends(auth.verifyEDITAuthenticationAndAuthorizationRequest)):
    try:
        encoded_payload = completer.general_completer_user(payload, auth["metadata"])
    except Exception as e:
        return responses.ErrorResponseModel("Error at completion!", False, str(e))
    try:
        service.CreateNotification(encoded_payload)
        return responses.ResponseModel("", True, "Site Notification Created Successfully")
    except exceptions.InvalidNotificationException as e:
        return responses.HTTPExceptionResponse(status_code=400, message=str(e))
    except exceptions.DuplicateNotificationException as e:
        return responses.HTTPExceptionResponse(status_code=400, message=str(e))
    except Exception as e:
        return responses.HTTPExceptionResponse(status_code=500, message=str(e))

@app.post(BASE_PREFIX + "/update_notification", status_code=status.HTTP_200_OK)
def update_notification(payload: schemas.SiteNotificationPayload, auth = Depends(auth.verifyEDITAuthenticationAndAuthorizationRequest)):
    try:
        encoded_payload = completer.general_completer_user(payload, auth["metadata"])
    except Exception as e:
        return responses.ErrorResponseModel("Error at completion!", False, str(e))
    try:
        service.UpdateNotification(encoded_payload)
        return responses.ResponseModel("", True, "Site Notification Updated Successfully")
    except exceptions.InvalidNotificationException as e:
        return responses.HTTPExceptionResponse(status_code=400, message=str(e))
    except Exception as e:
        return responses.HTTPExceptionResponse(status_code=500, message=str(e))

@app.post(BASE_PREFIX + "/delete_notification", status_code=status.HTTP_200_OK)
def delete_notification(payload: schemas.SiteNotificationPayload, auth = Depends(auth.verifyEDITAuthenticationAndAuthorizationRequest)):
    try:
        encoded_payload = completer.general_completer_user(payload, auth["metadata"])
    except Exception as e:
        return responses.ErrorResponseModel("Error at completion!", False, str(e))
    try:
        service.DeleteNotification(encoded_payload)
        return responses.ResponseModel("", True, "Site Notification Deleted Successfully")
    except exceptions.InvalidNotificationException as e:
        return responses.HTTPExceptionResponse(status_code=400, message=str(e))
    except Exception as e:
        return responses.HTTPExceptionResponse(status_code=500, message=str(e))

@app.get(BASE_PREFIX + "/get_notification_info", status_code=status.HTTP_200_OK)
def get_notification_info(notification_name: str, auth = Depends(auth.verifyEDITAuthenticationAndAuthorizationRequest)):
    try:
        site_id = auth.get("metadata", {}).get("site_id")
        notification = service.GetNotificationInfo(site_id, notification_name)
        return responses.ResponseModel(notification, True, "Site Notification Retreived Successfully")
    except exceptions.InvalidNotificationException as e:
        return responses.HTTPExceptionResponse(status_code=400, message=str(e))
    except Exception as e:
        return responses.HTTPExceptionResponse(status_code=500, message=str(e))

@app.get(BASE_PREFIX + "/get_enforcement_hours", status_code=status.HTTP_200_OK)
def get_enforcement_hours(auth = Depends(auth.verifyEDITAuthenticationAndAuthorizationRequest)):
    try:
        site_id = auth.get("metadata", {}).get("site_id")
        enforcement_hours = service.GetEnforcementHours(site_id)
        if enforcement_hours == {}:
            return responses.ResponseModel(enforcement_hours, True, f"Enforcement Hours are not set for site {site_id}")
        return responses.ResponseModel(enforcement_hours, True, "Enforcement Hours Retreived Successfully")
    except Exception as e:
        return responses.HTTPExceptionResponse(status_code=500, message=str(e))

@app.post(BASE_PREFIX + "/set_enforcement_hours", status_code=status.HTTP_200_OK)
def set_enforcement_hours(payload: schemas.EnforcementHoursPayload, auth = Depends(auth.verifyEDITAuthenticationAndAuthorizationRequest)):
    try:
        try:
            encoded_payload = completer.general_completer_user(payload, auth["metadata"])
        except Exception as e:
            return responses.ErrorResponseModel("Error at completion!", False, str(e))
        service.SetEnforcementHours(encoded_payload)
        return responses.ResponseModel("", True, "Enforcement Hours Updated Successfully.")
    except exceptions.InvalidEnforcementHoursException as e:
        return responses.HTTPExceptionResponse(status_code=400, message=str(e))
    except Exception as e:
        return responses.HTTPExceptionResponse(status_code=500, message=str(e))

@app.post(BASE_PREFIX + "/delete_enforcement_hours", status_code=status.HTTP_200_OK)
def delete_enforcement_hours(auth = Depends(auth.verifyEDITAuthenticationAndAuthorizationRequest)):
    try:
        try:
            encoded_payload = completer.general_completer_user({}, auth["metadata"])
        except Exception as e:
            return responses.ErrorResponseModel("Error at completion!", False, str(e))
        enforcement_hours = service.DeleteEnforcementHours(encoded_payload)
        return responses.ResponseModel(enforcement_hours, True, "Enforcement Hours Deleted Successfully.")
    except Exception as e:
        return responses.HTTPExceptionResponse(status_code=500, message=str(e))

@app.get(BASE_PREFIX + "/get_timezone_list", status_code=status.HTTP_200_OK)
def get_timezone_list(auth = Depends(auth.verifyEDITAuthenticationAndAuthorizationRequest)):
    try:
        timezone_list = service.GetTimezoneList()
        return responses.ResponseModel(timezone_list, True, "Notification Timezone List Retreived Successfully")
    except Exception as e:
        return responses.HTTPExceptionResponse(status_code=500, message=str(e))

@app.get(BASE_PREFIX + "/get_notification_cron_info", status_code=status.HTTP_200_OK)
def get_notification_cron_info(notification_name: str, auth = Depends(auth.verifyEDITAuthenticationAndAuthorizationRequest)):
    try:
        site_id = auth.get("metadata", {}).get("site_id")
        notification_cron_info = service.GetNotificationCronInfo(site_id, notification_name)
        if notification_cron_info == {}:
            return responses.ResponseModel(notification_cron_info, True, f"{notification_name} is not configured for {site_id} currently.")
        return responses.ResponseModel(notification_cron_info, True, "Notification Cron Info Retreived Successfully")
    except exceptions.InvalidNotificationException as e:
        return responses.HTTPExceptionResponse(status_code=400, message=str(e))
    except Exception as e:
        return responses.HTTPExceptionResponse(status_code=500, message=str(e))

@app.post(BASE_PREFIX + "/set_notification_cron_info", status_code=status.HTTP_200_OK)
def set_notification_cron_info(payload: schemas.NotificationCronInfoPayload, auth = Depends(auth.verifyEDITAuthenticationAndAuthorizationRequest)):
    try:
        try:
            encoded_payload = completer.general_completer_user(payload, auth["metadata"])
        except Exception as e:
            return responses.ErrorResponseModel("Error at completion!", False, str(e))
        service.SetNotificationCronInfo(encoded_payload)
        return responses.ResponseModel("", True, "Notification Cron Info Updated Successfully.")
    except exceptions.InvalidTimezoneException as e:
        return responses.HTTPExceptionResponse(status_code=400, message=str(e))
    except exceptions.InvalidDayFreqException as e:
        return responses.HTTPExceptionResponse(status_code=400, message=str(e))
    except exceptions.InvalidBeatFreqFormatException as e:
        return responses.HTTPExceptionResponse(status_code=400, message=str(e))
    except exceptions.InvalidBeatTimeFormatException as e:
        return responses.HTTPExceptionResponse(status_code=400, message=str(e))
    except Exception as e:
        return responses.HTTPExceptionResponse(status_code=500, message=str(e))

@app.post(BASE_PREFIX + "/delete_notification_cron_info", status_code=status.HTTP_200_OK)
def delete_notification_cron_info(payload: schemas.NotificationCronInfoPayload, auth = Depends(auth.verifyEDITAuthenticationAndAuthorizationRequest)):
    try:
        try:
            encoded_payload = completer.general_completer_user(payload, auth["metadata"])
        except Exception as e:
            return responses.ErrorResponseModel("Error at completion!", False, str(e))
        service.DeleteNotificationCronInfo(encoded_payload)
        return responses.ResponseModel("", True, "Notification Cron Info Deleted Successfully.")
    except exceptions.NotConfigurableNotificationsCronsException as e:
        return responses.HTTPExceptionResponse(status_code=400, message=str(e))
    except exceptions.NotificationCronDoesNotExistException as e:
        return responses.HTTPExceptionResponse(status_code=400, message=str(e))
    except Exception as e:
        return responses.HTTPExceptionResponse(status_code=500, message=str(e))
