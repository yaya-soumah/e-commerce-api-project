from rest_framework.renderers import JSONRenderer
from rest_framework import status

class APIJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        response = renderer_context.get("response")
        request = renderer_context.get("request", {})
        
        # Initialize response structure
        formatted_data = {
            "status": "success",
            "data": data,
            "message": None,
            "errors": None,
            "meta": {}
        } 

        status_code = response.status_code if response else 200
        if status_code >= 400:
            formatted_data["status"] = "error"
            formatted_data["message"] = "Validation failed" if status_code == 400 else "An error occurred"
            formatted_data["errors"] = data
            formatted_data["data"] = None
        elif status_code == status.HTTP_204_NO_CONTENT:
            formatted_data["data"] = None            

        if  status_code == status.HTTP_200_OK or \
            status_code == status.HTTP_201_CREATED or \
            status_code == status.HTTP_204_NO_CONTENT:
            formatted_data["message"] = "Operation successful"      
        
        if isinstance(data,dict):            
            if  "count" in data:
                pagesize = request.GET.get("pagesize", 10)
                formatted_data["meta"] = {
                "count": data.get("count", None),
                "next": data.get("next", None),
                "previous": data.get("previous", None),
                "pagenum": request.GET.get("pagenum", None),
                "pagesize": pagesize,
                "total_pages": (
                    (data["count"] + int(pagesize) - 1) // int(pagesize)
                    if data.get("count") and pagesize
                    else None
                )
                }            
                formatted_data["data"] = data.get("results", data)
            elif "message" in data:
                formatted_data["message"]=data.pop("message","") 
                formatted_data["meta"]=data.pop("meta",{}) 
                formatted_data["data"] = data                
     
        
        # Handle detail messages (e.g., authentication errors)
            elif  "detail" in data:
                formatted_data["message"] = data.pop("detail", "")
                if formatted_data["status"] == "success":
                    formatted_data["data"] = data
        
        

        return super().render(formatted_data, accepted_media_type, renderer_context)