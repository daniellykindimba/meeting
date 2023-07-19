from fastapi import FastAPI, Depends, status, Response, HTTPException, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse
import logging
import os
import jwt
from functools import lru_cache
from pydantic import BaseSettings
from app import models
from app import schemas
from app.database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from sqlalchemy import inspect
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi_login import LoginManager
from fastapi.responses import RedirectResponse
from starlette_wtf import StarletteForm, CSRFProtectMiddleware, csrf_protect
from datetime import timedelta
from app import forms
from app.login_manager import manager
import pendulum


log = logging.getLogger("uvicorn")

templates = Jinja2Templates(directory="templates")
