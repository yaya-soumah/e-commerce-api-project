from rest_framework.renderers import JSONRenderer
from .base import UnifiedResponseRenderer

class APIJSONRenderer(UnifiedResponseRenderer, JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        response = renderer_context.get("response")
        request = renderer_context.get("request")
        formatted = self.format_response(data, response, request)
        return super().render(formatted, accepted_media_type, renderer_context)
