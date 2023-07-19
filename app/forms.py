from starlette_wtf import StarletteForm, CSRFProtectMiddleware, csrf_protect
from wtforms import *
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms.widgets import PasswordInput
from app import models


class LoginForm(StarletteForm):
    username = StringField("Username", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
