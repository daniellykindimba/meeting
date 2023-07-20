from fastapi import FastAPI,Depends, status, Response, Request
from app import models
from app import pydantic_models as schemas
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from datetime import timedelta
from app.login_manager import manager, TOKEN_EXPIRATION_TIME
from app.forms import *
from app.config import Settings, get_settings
import bcrypt

# oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")

description = """
FlashApp API helps you do awesome stuff. 🚀

## Events

You can **read events**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
"""

api = FastAPI(title="Meeting API")


@api.post("/token")
async def token_generator(
        request: Request,
        response: Response,
        settings: Settings = Depends(get_settings),
        form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await models.User.filter(
        username=str(form_data.username).strip().lower()).first()
    if not user:
        raise InvalidCredentialsException

    hashed = bcrypt.hashpw(form_data.password.encode("utf-8"),
                           user.salt_key.encode("utf-8"))
    if not bcrypt.checkpw(form_data.password.encode("utf-8"), hashed):
        raise InvalidCredentialsException
    else:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "middle_name": user.middle_name,
            "last_name": user.last_name,
            "email": user.email,
            "sub": user.username
        }
        access_token = manager.create_access_token(
            data=user_dict, expires=timedelta(hours=TOKEN_EXPIRATION_TIME))
        manager.set_cookie(response, access_token)
        return {'token': access_token}


@api.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: schemas.UserRegister,
                   settings: Settings = Depends(get_settings)):
    salt_key = bcrypt.gensalt()
    hashed = bcrypt.hashpw(request.password.encode('utf-8'), salt_key)
    new_user = await models.User.create(
        first_name=str(request.full_name).split(" ")[0],
        middle_name=str(request.full_name).split(" ")[1],
        last_name=" ".join(str(request.full_name).split(" ")[3:]),
        email=request.email,
        username=request.email,
        phone=request.phone,
        salt_key=salt_key.decode("utf-8"),
        hash_password=hashed.decode("utf-8"))
    return new_user