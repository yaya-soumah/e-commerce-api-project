from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
import logging

logger = logging.getLogger(__name__)

class BearerAuthentication(TokenAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request):        
        try:
            auth = super().authenticate(request)   
            if auth is None:
                return None         
            user, token = auth            
            return user, token
        except AuthenticationFailed as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise