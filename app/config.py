from pydantic import BaseSettings
import jinja2
from starlette_core.templating import Jinja2Templates
from functools import lru_cache
import pendulum
import os


def format_datetime(value):
    return pendulum.parse(str(value)).to_day_datetime_string()



class Settings(BaseSettings):
    environment: str = os.getenv("ENVIRONMENT", "development")
    testing: bool = os.getenv("TESTING", 0)
    system_name: str = "Meeting"
    system_date = pendulum.now()
    secured: bool = bool(os.getenv("SECURED", False))


settings = Settings()


@lru_cache()
def get_settings() -> BaseSettings:
    return Settings()
