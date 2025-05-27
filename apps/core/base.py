from rest_framework import status
from rest_framework.renderers import BaseRenderer


class UnifiedResponseRenderer(BaseRenderer):
    def format_response(self, data, response, request):
        formatted = {
            "status": "success",
            "data": None,
            "message": None,
            "errors": None,
            "meta": {}
        }

        if response and response.status_code >= 400:
            formatted["status"] = "error"
            formatted["message"] = self.get_error_message(response.status_code)
            formatted["errors"] = data
            return formatted

        if not isinstance(data, dict):
            formatted["data"] = data
            formatted["message"] = self.get_success_message(request, response.status_code)
            return formatted

        if "results" in data:
            formatted["data"] = data["results"]
            formatted["meta"] = {
                key: data.get(key)
                for key in ("count", "next", "previous")
                if key in data
            }
            formatted["message"] = self.get_success_message(request, response.status_code)
            return formatted

        known_keys = {"data", "message", "errors", "meta"}
        if any(key in data for key in known_keys):
            formatted["data"] = data.get("data")
            formatted["message"] = data.get("message") or self.get_success_message(request, response.status_code)
            formatted["errors"] = data.get("errors")
            formatted["meta"] = data.get("meta", {})
            return formatted

        formatted["data"] = data
        formatted["message"] = self.get_success_message(request, response.status_code)
        return formatted

    def get_error_message(self, status_code):
        return {
            400: "Validation failed",
            401: "Authentication required",
            403: "Permission denied",
            404: "Not found",
        }.get(status_code, "An error occurred")

    def get_success_message(self, request, status_code):
        method = request.method if request else "GET"
        if status_code == 201 or method == "POST":
            return "Created"
        elif method in ("PUT", "PATCH"):
            return "Updated"
        elif method == "DELETE":
            return "Deleted"
        return "Fetched"
