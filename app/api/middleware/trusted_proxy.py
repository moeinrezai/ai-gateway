from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config.settings import settings


class TrustedProxyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        
        direct_ip = request.client.host if request.client else "127.0.0.1"
        
       
        if direct_ip in settings.trusted_proxies_list:
            
            forwarded_for = request.headers.get("X-Forwarded-For")
            
            if forwarded_for:
              
                real_ip = forwarded_for.split(",")[0].strip()
                request.state.client_ip = real_ip
            else:
               
                request.state.client_ip = direct_ip
        else:
            
            request.state.client_ip = direct_ip

    
        response = await call_next(request)
        return response