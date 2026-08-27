from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config.settings import settings
from app.core.security.csrf import validate_csrf_token


class CSRFMiddleware(BaseHTTPMiddleware):

    
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}
    
    async def dispatch(self, request: Request, call_next) -> Response:
   
        if not settings.CSRF_ENABLED:
            return await call_next(request)

        if request.method in self.SAFE_METHODS:
            return await call_next(request)
        
  
        validate_csrf_token(request)
        

        response = await call_next(request)
        return response