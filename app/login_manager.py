from fastapi_login import LoginManager

JWT_SECRET = "d48e52f4e0a88ffab39b2b0a0a0cb5db7e7cab131a95c16f"
TOKEN_EXPIRATION_TIME = 3600

manager = LoginManager(JWT_SECRET, '/token', use_cookie=True, use_header=True)

class NotAuthenticatedException(Exception):
    pass


manager.not_authenticated_exception = NotAuthenticatedException
