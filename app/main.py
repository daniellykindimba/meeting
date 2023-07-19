from fastapi import FastAPI, Depends, Response, Request
import logging
import jwt
from . import models
from .database import DATABASE_URL
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect
from fastapi.responses import RedirectResponse
from starlette_wtf import CSRFProtectMiddleware
from datetime import timedelta
from api.main import api
from app.login_manager import manager
from app.forms import *
from .config import Settings, get_settings
from starlette.middleware import Middleware
from starlette_wtf import CSRFProtectMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.authentication import (
    AuthCredentials, AuthenticationBackend, BaseUser
)
from starlette.middleware.authentication import AuthenticationMiddleware

from tortoise.contrib.fastapi import register_tortoise
from starlette_graphene3 import GraphQLApp, make_graphiql_handler
from app.g_schema import schema
from starlette.middleware.cors import CORSMiddleware
from app.login_manager import JWT_SECRET
# models.Base.metadata.create_all(engine)

log = logging.getLogger("uvicorn")

# oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")

description = """
Insurance BI API helps you do awesome stuff. 🚀

## Events

You can **read events**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
"""

class InsuranceBiUser(BaseUser):
    def __init__(self, payload: str) -> None:
        self.payload = payload
    
    @property
    def id(self) -> int:
        return self.payload["id"]
    
    @property
    def first_name(self) -> str:
        return self.payload['first_name']
    
    @property
    def middle_name(self) -> str:
        return self.payload['middle_name']
    
    @property
    def last_name(self) -> str:
        return self.payload['last_name']
    
    @property
    def email(self) -> str:
        return self.payload['email']
    
    @property
    def sub(self) -> str:
        return self.payload['sub']
    
    @property
    def exp(self) -> int:
        return self.payload['exp']
    
    
    @property
    def username(self) -> str:
        return self.payload['username']

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.payload['username']


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, request: Request):
        if "Authorization" not in request.headers:
            return
        authorization = request.headers["Authorization"]
        if not authorization:
            return
        scheme, _, param = authorization.partition(" ")
        if not authorization or scheme.lower() != "bearer":
            return
        try:
            payload = jwt.decode(param, JWT_SECRET, algorithms=["HS256"])
            user = payload
        except jwt.PyJWTError:
            return
        return AuthCredentials(["authenticated"]), InsuranceBiUser(user)




app = FastAPI(title="Meeting API",
              middleware=[
                  Middleware(AuthenticationMiddleware, backend=BasicAuthBackend()),
                  Middleware(SessionMiddleware,
                             secret_key='theloveofgodisgreatandpurebi'),
                  Middleware(CORSMiddleware, allow_origins=['*'], 
                             allow_methods=["GET", "OPTIONS", "POST"],
                             allow_headers=["*"]),
                  Middleware(CSRFProtectMiddleware,
                             csrf_secret='theloveofgodisgreatandpurebi')
              ])

register_tortoise(
    app,
    db_url=DATABASE_URL,
    modules={"models": ["app.models", "aerich.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

app.mount("/api", api)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/graphql", GraphQLApp(schema, on_get=make_graphiql_handler()))

manager.useRequest(app)


def object_as_dict(obj):
    return {
        c.key: getattr(obj, c.key)
        for c in inspect(obj).mapper.column_attrs
    }


@manager.user_loader
async def query_user(username: str):
    user = await models.User.filter(username=str(username).strip().lower()
                                    ).first()
    return user


@app.get("/logout", include_in_schema=False)
async def logout(request: Request,
                 response: Response,
                 settings: Settings = Depends(get_settings)):
    access_token = manager.create_access_token(data={},
                                               expires=timedelta(seconds=1))
    resp = RedirectResponse(url="/login")
    manager.set_cookie(resp, access_token)
    response.delete_cookie("access_token")
    return resp
