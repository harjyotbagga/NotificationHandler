from fastapi import HTTPException

def InternalResponseModel(status, response, metadata):
    return {
        "status": status,
        "response": response,
        "metadata": metadata
    }

def ResponseModel(data, status, message):
    return {
        "data": data,
        "status": True,
        "message": message,
    }

def ErrorResponseModel(error, status, message):
    return {"error": error, "status": status, "message": message}

def HTTPExceptionResponse(status_code :int,  message: str):
    raise HTTPException(status_code=status_code,detail=message)