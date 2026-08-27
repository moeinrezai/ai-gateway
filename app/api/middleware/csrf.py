from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config.settings import settings
from app.core.security.csrf import validate_csrf_token


class CSRFMiddleware(BaseHTTPMiddleware):
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}
    
   
    EXEMPT_PATHS = {
        "/api/v1/auth/login",
        "/api/v1/auth/register",
    }
    
    async def dispatch(self, request: Request, call_next) -> Response:
      
        if not settings.CSRF_ENABLED:
            return await call_next(request)
        
    
        if request.method in self.SAFE_METHODS:
            return await call_next(request)
        
    
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        

        validate_csrf_token(request)
        
  
        response = await call_next(request)
        return response