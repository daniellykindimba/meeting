from pydantic import BaseModel
import datetime


class Region(BaseModel):
    id: int
    name: str
    is_active: bool
    created: datetime.datetime
    updated: datetime.datetime

    class Config:
        orm_mode = True


class District(BaseModel):
    id: int
    name: str
    region_id: int
    is_active: bool
    created: datetime.datetime
    updated: datetime.datetime

    class Config:
        orm_mode = True


class UserRegister(BaseModel):
    full_name: str
    email: str
    password: str
    password_confirm: str


class FilterUserProfile(BaseModel):
    id: int
    region_id: int
    district_id: int
    latitude: str
    longitude: str
    location: str
    is_active: bool
    created: datetime.datetime
    updated: datetime.datetime

    class Config:
        orm_mode = True


class FilterUser(BaseModel):
    id: int
    first_name: str
    middle_name: str
    last_name: str
    email: str
    username: str
    is_active: bool
    created: datetime.datetime
    updated: datetime.datetime

    class Config:
        orm_mode = True


class User(BaseModel):
    first_name: str
    middle_name: str
    last_name: str
    username: str
    email: str
    hash_password: str

    class Config:
        orm_mode = True