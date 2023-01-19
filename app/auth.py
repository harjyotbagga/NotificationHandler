#============================================================================================
# API OPERTIONS FOR AUTH.
#============================================================================================
from urllib import response
from .exporter import AUTH_STATUS_LINK
from .responses import HTTPExceptionResponse
from fastapi import FastAPI, Request ,HTTPException, Depends, Request
import requests
import json

ScopeGet = "get"
ScopeCreate = "create"
ScopeEdit = "edit"
ScopeDelete = "delete"

def checkAuth(token, endpoint_name, scope_type):
    try:
        payload = json.dumps({
            "endpoint_name": endpoint_name,
            "scope_type": scope_type
        })
        auth_response = requests.post(AUTH_STATUS_LINK, headers={"Content-Type": "application/json", "token": token}, data=payload)
        return auth_response.json()

    except Exception as e:
        print(e)
        raise Exception("Error! Auth Module Offline")

def verifyGETAuthenticationAndAuthorizationRequest(request: Request):
    return verifyAuthenticationAndAuthorizationRequest(request, ScopeGet)
    
def verifyCREATEAuthenticationAndAuthorizationRequest(request: Request):
    return verifyAuthenticationAndAuthorizationRequest(request, ScopeCreate)

def verifyEDITAuthenticationAndAuthorizationRequest(request: Request):
    return verifyAuthenticationAndAuthorizationRequest(request, ScopeEdit)

def verifyDELETEAuthenticationAndAuthorizationRequest(request: Request):
    return verifyAuthenticationAndAuthorizationRequest(request, ScopeDelete)

def verifyAuthenticationAndAuthorizationRequest(request: Request, scope_type: str):
    token = request.headers.get('token', None)
    if token is None:
        if "Authorization" in request.headers:        
            token = request.headers["authorization"].split("Bearer")[-1].strip()
        elif not token:
            raise HTTPExceptionResponse(
                status_code=401,
                message="Token not provided",
            )

    endpoint_name = request.url.path
    auth_response = checkAuth(token, endpoint_name, scope_type)
    if auth_response["token_active"] == False:
        raise HTTPExceptionResponse(status_code=401, message="Token authentication failure")
    if auth_response["status"] == False:
        raise HTTPExceptionResponse(status_code=401, message="You are not authorised to access this route.")
    return auth_response