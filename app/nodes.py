import graphene
from app import models
from app.graphene_custom_fields import JSON
from settings import settings
from app.models import *



class DataObject(graphene.ObjectType):
    data = JSON()



class MiscFieldObject(graphene.ObjectType):
    id = graphene.Int()
    created = graphene.DateTime()
    updated = graphene.DateTime()
    is_active = graphene.Boolean()
    can_edit = graphene.Boolean()
    can_delete = graphene.Boolean()
    can_manage = graphene.Boolean()



class MiscPaginatedObject(graphene.ObjectType):
    total = graphene.Int()
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()



class UserObject(MiscFieldObject):
    username = graphene.String()
    first_name = graphene.String()
    middle_name = graphene.String()
    last_name = graphene.String()
    email = graphene.String()
    phone = graphene.String()
    is_admin = graphene.Boolean()
    is_staff = graphene.Boolean()
    avatar = graphene.String()


class UserPaginatedObject(MiscPaginatedObject):
    results = graphene.List(UserObject)



class DepartmentObject(MiscFieldObject):
    name = graphene.String()
    description = graphene.String()


class DepartmentPaginatedObject(MiscPaginatedObject):
    results = graphene.List(DepartmentObject)


class UserDepartmentObject(MiscFieldObject):
    user = graphene.Field(UserObject)
    department = graphene.Field(DepartmentObject)

class UserDepartmentPaginatedObject(MiscPaginatedObject):
    results = graphene.List(UserDepartmentObject)



class VenueObject(MiscFieldObject):
    name = graphene.String()
    description = graphene.String()
    capacity = graphene.Int()
    venue_type = graphene.String()

    async def resolve_venue_type(self, info, **kwargs):
        return self.venue_type.name


class VenuePaginatedObject(MiscPaginatedObject):
    results = graphene.List(VenueObject)



class EventObject(MiscFieldObject):
    id = graphene.Int()
    title = graphene.String()
    description = graphene.String()
    event_type = graphene.String()
    start_time = graphene.DateTime()
    end_time = graphene.DateTime()
    venue = graphene.Field(VenueObject)
    author = graphene.Field(UserObject)


class EventPaginatedObject(MiscPaginatedObject):
    results = graphene.List(EventObject)



class EventDepartmentObject(MiscFieldObject):
    event = graphene.Field(EventObject)
    department = graphene.Field(DepartmentObject)


class EventDepartmentPaginatedObject(MiscPaginatedObject):
    results = graphene.List(EventDepartmentObject)


class EventAttendeeObject(MiscFieldObject):
    event = graphene.Field(EventObject)
    attendee = graphene.Field(UserObject)
    is_attending = graphene.Boolean()


class EventAttendeePaginatedObject(MiscPaginatedObject):
    results = graphene.List(EventAttendeeObject)


class EventAgendaObject(MiscFieldObject):
    event = graphene.Field(EventObject)
    title = graphene.String()
    description = graphene.String()
    start_time = graphene.DateTime()
    end_time = graphene.DateTime()


class EventAgendaPaginatedObject(MiscPaginatedObject):
    results = graphene.List(EventAgendaObject)


class EventDocumentObject(MiscFieldObject):
    event = graphene.Field(EventObject)
    title = graphene.String()
    description = graphene.String()
    file = graphene.String()

    async def resolve_file(self, info, **kwargs):
        return f"{settings.MINIO_SERVER}{self.file}"


class EventDocumentPaginatedObject(MiscPaginatedObject):
    results = graphene.List(EventDocumentObject)



