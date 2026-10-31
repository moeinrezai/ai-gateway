# Global IP-based limits
GLOBAL_IP_LIMIT = 100  # requests
GLOBAL_IP_WINDOW = 60  # seconds (1 minute)

# Authentication endpoints (stricter, per endpoint)
LOGIN_IP_LIMIT = 5  # requests
REGISTER_IP_LIMIT = 3  # requests
AUTH_IP_WINDOW = 60  # seconds

# AI endpoints
AI_IP_LIMIT = 20  # requests
AI_IP_WINDOW = 60  # seconds


USER_AI_LIMIT = 100  # requests per hour
USER_AI_WINDOW = 3600  # seconds
