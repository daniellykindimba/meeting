import jwt
import uuid
import datetime
from starlette.requests import Request
from starlette.authentication import (
    AuthenticationBackend, AuthCredentials, BaseUser
)
from app.login_manager import JWT_SECRET


def login_required(resolver):
    async def wrapper_func(source, info, **kwargs):
        request = info.context["request"]
        if "Authorization" not in request.headers:
            raise Exception("Not authenticated")
        authorization = request.headers["Authorization"]
        if not authorization:
            raise Exception("Not authenticated")
        scheme, _, param = authorization.partition(" ")
        if not authorization or scheme.lower() != "bearer":
            raise Exception("Not authenticated")
        if request.user.is_authenticated:
            result = await resolver(source, info, **kwargs)
            return result
        else:
            raise Exception("Not authenticated")
    return wrapper_func


async def check_user_in_db(user_id: str, received_token: str):
    token_in_db = await TokenBase.find_by_user_id(user_id)
    if token_in_db and token_in_db["token"] == received_token:
        return True
    return False


class AuthenticatedUser(BaseUser):
    def __init__(self, user_id: str = None, expires: float = 0.0):
        self.current_user_id = user_id
        self.expires = expires
        self.req_id = uuid.uuid4().hex

    @property
    def is_authenticated(self) -> bool:
        return True


class UnAuthenticatedUser(BaseUser):
    def __init__(self):
        self.req_id = uuid.uuid4().hex

    @property
    def is_authenticated(self) -> bool:
        return False


# authenticates each request and provides an unique reuest id to each
class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        ret_value = None
        if "Authorization" in request.cookies.keys() and request.cookies["Authorization"]:
            token = request.cookies["Authorization"].encode()
            decoded_token = jwt.decode(token, "secret", algorithms=['HS256'])
            match_token = await check_user_in_db(decoded_token["id"], token.decode())
            now = datetime.datetime.now()
            if match_token and now.timestamp() < decoded_token["expire"]:
                ret_value = AuthenticatedUser(
                    user_id=decoded_token["id"], expires=decoded_token["expire"]
                )
                await token_db.set_token(
                    ret_value.req_id,
                    token,
                    decoded_token["expire"]
                )
            else:
                ret_value = UnAuthenticatedUser()

        else:
            ret_value = UnAuthenticatedUser()
        return AuthCredentials(["authenticated"]), ret_value