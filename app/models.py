from tkinter import Misc
from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
import enum
import datetime


class MiscFields(Model):
    is_active = fields.BooleanField(default=True)
    created = fields.DatetimeField(auto_now_add=True, null=True)
    updated = fields.DatetimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class Department(MiscFields):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, null=False, blank=False)
    description = fields.TextField(null=True, blank=True)

    class PydanticMeta:
        pass


class Committee(MiscFields):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, null=False, blank=False)
    description = fields.TextField(null=True, blank=True)
    
    class PydanticMeta:
        pass


class User(MiscFields):
    id = fields.IntField(pk=True)
    first_name = fields.CharField(max_length=100, null=False, blank=False)
    middle_name = fields.CharField(max_length=100, null=True, blank=True)
    last_name = fields.CharField(max_length=100, null=False, blank=False)
    email = fields.CharField(max_length=100, null=True, blank=True)
    phone = fields.CharField(max_length=100, null=True, blank=True)
    email = fields.CharField(max_length=100, null=True, blank=True)
    username = fields.CharField(max_length=100, null=False, blank=False)
    salt_key = fields.CharField(max_length=500, null=True, blank=True)
    hash_password = fields.CharField(max_length=500, null=True, blank=True)
    is_admin = fields.BooleanField(default=False)
    is_staff = fields.BooleanField(default=False)
    avatar = fields.CharField(max_length=100, null=True, blank=True)

    def full_name(self) -> str:
        return f"{self.fist_name} {self.middle_name} {self.last_name}".strip()

    class PydanticMeta:
        computed = ["full_name"]
        exclude = ["hash_password", "salt_key"]


User_Pydantic = pydantic_model_creator(User, name="User")
UserIn_Pydantic = pydantic_model_creator(User,
                                         name="UserIn",
                                         exclude_readonly=True)



class UserDepartment(MiscFields):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User',
                                  related_name="user_departments",
                                  on_delete=fields.CASCADE)
    department = fields.ForeignKeyField('models.Department',
                                        related_name="user_departments",
                                        on_delete=fields.CASCADE)

    class PydanticMeta:
        pass



class UserCommittee(MiscFields):
    id = fields.IntField(pk=True)
    committee = fields.ForeignKeyField('models.Committee',
                                      related_name="user_committees",
                                      on_delete=fields.CASCADE)
    user = fields.ForeignKeyField('models.User',
                                  related_name="user_committees",
                                  on_delete=fields.CASCADE)


    class PydanticMeta:
        pass



class VenueType(enum.Enum):
    HALL = "hall"
    ROOM = "room"
    GROUND = "ground"
    OTHER = "other"


class Venue(MiscFields):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, null=False, blank=False)
    description = fields.TextField(null=True, blank=True)
    venue_type = fields.CharEnumField(VenueType, default=VenueType.ROOM)
    capacity = fields.IntField(default=0)

    class PydanticMeta:
        pass


class EventType(enum.Enum):
    MEETING = "meeting"
    TRAINING = "training"
    OTHER = "other"


class Event(MiscFields):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=100, null=False, blank=False)
    description = fields.TextField(null=True, blank=True)
    event_type = fields.CharEnumField(EventType, default=EventType.MEETING)
    start_time = fields.DatetimeField(null=True, blank=True)
    end_time = fields.DatetimeField(null=True, blank=True)
    venue = fields.ForeignKeyField('models.Venue',
                                   related_name="events",
                                   on_delete=fields.CASCADE)
    author = fields.ForeignKeyField('models.User',
                                    related_name="events",
                                    on_delete=fields.CASCADE)
    

    class PydanticMeta:
        pass




class EventDepartment(MiscFields):
    id = fields.IntField(pk=True)
    event = fields.ForeignKeyField('models.Event',
                                   related_name="event_departments",
                                   on_delete=fields.CASCADE)
    department = fields.ForeignKeyField('models.Department',
                                        related_name="event_departments",
                                        on_delete=fields.CASCADE)

    class PydanticMeta:
        pass




class EventAttendee(MiscFields):
    id = fields.IntField(pk=True)
    event = fields.ForeignKeyField('models.Event',
                                   related_name="event_attendees",
                                   on_delete=fields.CASCADE)
    attendee = fields.ForeignKeyField('models.User',
                                      related_name="event_attendees",
                                      on_delete=fields.CASCADE)
    is_attending = fields.BooleanField(default=False)

    class PydanticMeta:
        pass



class EventAgenda(MiscFields):
    id = fields.IntField(pk=True)
    event = fields.ForeignKeyField('models.Event',
                                   related_name="event_agendas",
                                   on_delete=fields.CASCADE)
    title = fields.CharField(max_length=100, null=False, blank=False)
    description = fields.TextField(null=True, blank=True)
    start_time = fields.DatetimeField(null=True, blank=True)
    end_time = fields.DatetimeField(null=True, blank=True)

    class PydanticMeta:
        pass


class EventDocument(MiscFields):
    id = fields.IntField(pk=True)
    event = fields.ForeignKeyField('models.Event',
                                   related_name="event_documents",
                                   on_delete=fields.CASCADE)
    title = fields.CharField(max_length=100, null=False, blank=False)
    description = fields.TextField(null=True, blank=True)
    file = fields.TextField(null=False, blank=False)
    author = fields.ForeignKeyField('models.User',
                                    related_name="event_documents",
                                    null=True,
                                    blank=True,
                                    on_delete=fields.SET_NULL)

    class PydanticMeta:
        pass


class EventCommittee(MiscFields):
    id = fields.IntField(pk=True)
    event = fields.ForeignKeyField('models.Event',
                                   related_name="event_committees",
                                   on_delete=fields.CASCADE)
    committee = fields.ForeignKeyField('models.Committee',
                                       related_name="event_committees",
                                       on_delete=fields.CASCADE)

    class PydanticMeta:
        pass