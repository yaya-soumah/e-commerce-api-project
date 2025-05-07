import logging
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

class ResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        logger.info("ResponseMiddleware initialized")

    def __call__(self, request):
        logger.info(f"Processing request: {request.method} {request.path}")
        response = self.get_response(request)
        
        # Log response type for debugging
        logger.debug(f"Response type: {type(response)}")
        
        # Only process DRF Response objects
        if not isinstance(response, Response):
            logger.debug(f"Skipping non-DRF response: {response}")
            return response

        # Initialize response structure
        formatted_response = {
            "status": "success" if response.status_code < 400 else "error",
            "data": None,
            "message": None,
            "meta": {}
        }

        # Handle response data
        try:
            data = response.data if hasattr(response, 'data') else None
            logger.debug(f"Raw response data: {data}")

            if formatted_response["status"] == "error" and data:
                formatted_response["message"] = "Validation failed" if response.status_code == 400 else "An error occurred"
                formatted_response["meta"]["errors"] = data
            elif response.status_code == 204:
                formatted_response["message"] = "Operation successful"
            elif isinstance(data, dict) and "detail" in data:
                formatted_response["message"] = data.pop("detail", None)
                formatted_response["data"] = data
            elif isinstance(data, dict) and "count" in data:
                # Handle paginated response
                count = data.pop("count", None)
                pagesize = request.GET.get("pagesize", 10)
                formatted_response["meta"] = {
                    "count": count,
                    "next": data.pop("next", None),
                    "previous": data.pop("previous", None),
                    "pagenum": request.GET.get("pagenum", None),
                    "pagesize": pagesize,
                    "total_pages": (count + int(pagesize) - 1) // int(pagesize) if count and pagesize else None
                }
                formatted_response["data"] = data.get("results", data)
            else:
                formatted_response["data"] = data

        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            formatted_response["status"] = "error"
            formatted_response["message"] = "Response formatting failed"
            formatted_response["meta"]["errors"] = {"detail": str(e)}

        # Create new Response object with renderer properties
        new_response = Response(
            data=formatted_response,
            status=response.status_code,
            headers=dict(response.items())
        )
        # Copy renderer properties from original response
        if hasattr(response, 'accepted_renderer'):
            new_response.accepted_renderer = response.accepted_renderer
        if hasattr(response, 'accepted_media_type'):
            new_response.accepted_media_type = response.accepted_media_type
        if hasattr(response, 'renderer_context'):
            new_response.renderer_context = response.renderer_context
        
        # Render the response to set content
        try:
            new_response.render()
            logger.debug(f"Rendered response content: {new_response.rendered_content}")
        except Exception as e:
            logger.error(f"Error rendering response: {str(e)}")
            # Fallback to original response if rendering fails
            return response
            
        logger.debug(f"New formatted response: {new_response.data}")
        return new_response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        logger.error(f"Exception: {str(exc)}")
        formatted_response = {
            "status": "error",
            "data": None,
            "message": str(exc),
            "meta": {"errors": response.data}
        }
        new_response = Response(
            data=formatted_response,
            status=response.status_code,
            headers=dict(response.items())
        )
        # Copy renderer properties
        if hasattr(response, 'accepted_renderer'):
            new_response.accepted_renderer = response.accepted_renderer
        if hasattr(response, 'accepted_media_type'):
            new_response.accepted_media_type = response.accepted_media_type
        if hasattr(response, 'renderer_context'):
            new_response.renderer_context = response.renderer_context
        # Render the response
        try:
            new_response.render()
            logger.debug(f"Rendered exception response content: {new_response.rendered_content}")
        except Exception as e:
            logger.error(f"Error rendering exception response: {str(e)}")
            return response
        return new_response
    return response