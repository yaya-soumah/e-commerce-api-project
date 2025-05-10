from rest_framework.response import Response
from rest_framework import status

class APIResponse(Response):
    def __init__(self, data=None, message=None, status_code=None, errors=None, meta=None, **kwargs):
        formatted_data = {
            "status": "success" if status_code is None or status_code < 400 else "error",
            "data": data,
            "message": message,
            "error":errors if status_code >= 400 else None,
            "meta": meta or {}
        }

        # Handle errors
        if formatted_data["status"] == "error" and data:
            formatted_data["message"] = message or ("Validation failed" if status_code == 400 else "An error occurred")
            formatted_data["errors"] = data
            formatted_data["data"] = None

        # Handle 204 No Content
        if status_code == status.HTTP_204_NO_CONTENT:
            formatted_data["data"] = None            

        if  status_code == status.HTTP_200_OK or \
            status_code == status.HTTP_201_CREATED or \
            status_code == status.HTTP_204_NO_CONTENT:
            formatted_data["message"] = message or "Operation successful"


        super().__init__(
            data=formatted_data,
            status=status_code,
            **kwargs
        )