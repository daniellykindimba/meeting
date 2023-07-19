import graphene
from app import models
from app.middlewares.authentication import login_required
from app.nodes import *
from tortoise.queryset import (
    Q,
)
import pendulum
import random

"""
    Querying
"""


class Query(graphene.ObjectType):
    me = graphene.Field(UserObject)

    @login_required
    async def resolve_me(self, info, **kwargs):
        return await models.User.get(id=info.context["request"].user.id)

    users = graphene.Field(
        UserPaginatedObject,
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )
    user = graphene.Field(UserObject, id=graphene.Int(required=True))

    @login_required
    async def resolve_users(self, info, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size

        s = models.User.all()

        # get total count
        total_count = await s.count()

        return UserPaginatedObject(
            total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all().order_by("-created"),
        )

    @login_required
    async def resolve_user(self, info, **kwargs):
        id = kwargs.get("id")
        return await models.User.get(id=id)

    departments = graphene.Field(
        DepartmentPaginatedObject,
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )

    department = graphene.Field(DepartmentObject, id=graphene.Int(required=True))

    @login_required
    async def resolve_departments(self, info, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size

        s = models.Department.all()

        # get total count
        total_count = await s.count()

        return DepartmentPaginatedObject(
            total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all(),
        )

    @login_required
    async def resolve_department(self, info, **kwargs):
        id = kwargs.get("id")
        return await models.Department.get(id=id)

    venues = graphene.Field(
        VenuePaginatedObject,
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )

    venue = graphene.Field(VenueObject, id=graphene.Int(required=True))

    @login_required
    async def resolve_venues(self, info, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size

        s = models.Venue.all()

        # get total count
        total_count = await s.count()

        return VenuePaginatedObject(
            total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all(),
        )

    @login_required
    async def resolve_venue(self, info, **kwargs):
        id = kwargs.get("id")
        return await models.Venue.get(id=id)

    events = graphene.Field(
        EventPaginatedObject,
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )

    event = graphene.Field(EventObject, id=graphene.Int(required=True))

    @login_required
    async def resolve_events(self, info, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size

        s = models.Event.all()

        # get total count
        total_count = await s.count()

        return EventPaginatedObject(
            total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all(),
        )

    @login_required
    async def resolve_event(self, info, **kwargs):
        id = kwargs.get("id")
        return await models.Event.get(id=id)

    event_attendees = graphene.Field(
        EventAttendeePaginatedObject,
        id=graphene.Int(required=True, description="Event ID"),
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )

    event_attendee = graphene.Field(EventAttendeeObject, id=graphene.Int(required=True))

    @login_required
    async def resolve_event_attendees(self, info, **kwargs):
        print("=======kwargs: ", kwargs)
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size

        s = models.EventAttendee.filter(event_id=kwargs.get("id"))

        # get total count
        total_count = await s.count()

        return EventAttendeePaginatedObject(
            total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all(),
        )

    @login_required
    async def resolve_event_attendee(self, info, **kwargs):
        id = kwargs.get("id")
        return await models.EventAttendee.get(id=id)

    event_documents = graphene.Field(
        EventDocumentPaginatedObject,
        event_id=graphene.Int(required=True, description="Event ID"),
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )

    event_document = graphene.Field(EventDocumentObject, id=graphene.Int(required=True))

    @login_required
    async def resolve_event_documents(self, info, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size

        s = models.EventDocument.filter(
            event_id=kwargs.get("event_id")
        )

        # get total count
        total_count = await s.count()

        return EventDocumentPaginatedObject(
            total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all().order_by("-created"),
        )

    @login_required
    async def resolve_event_document(self, info, **kwargs):
        id = kwargs.get("id")
        return await models.EventDocument.get(id=id)

    event_agendas = graphene.Field(
        EventAgendaPaginatedObject,
        event_id=graphene.Int(required=True, description="Event ID"),
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )

    event_agenda = graphene.Field(EventAgendaObject, id=graphene.Int(required=True))

    @login_required
    async def resolve_event_agendas(self, info, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size

        s = models.EventAgenda.filter(
            event_id=kwargs.get("event_id")
        )

        # get total count
        total_count = await s.count()

        return EventAgendaPaginatedObject(
            total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all(),
        )

    @login_required
    async def resolve_event_agenda(self, info, **kwargs):
        id = kwargs.get("id")
        return await models.EventAgenda.get(id=id)

    event_types = graphene.Field(DataObject)

    @login_required
    async def resolve_event_types(self, info, **kwargs):
        datas = [e.value for e in models.EventType]
        return DataObject(data=datas)

    venue_types = graphene.Field(DataObject)

    @login_required
    async def resolve_venue_types(self, info, **kwargs):
        datas = [e.value for e in models.VenueType]
        return DataObject(data=datas)

    department_users = graphene.Field(
        UserDepartmentPaginatedObject,
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )

    department_user = graphene.Field(
        UserDepartmentObject, id=graphene.Int(required=True)
    )

    @login_required
    async def resolve_department_users(self, info, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size

        s = models.UserDepartment.all()

        # get total count
        total_count = await s.count()

        return UserDepartmentPaginatedObject(
            total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all(),
        )

    @login_required
    async def resolve_department_user(self, info, **kwargs):
        id = kwargs.get("id")
        return await models.UserDepartment.get(id=id)

    event_attendees_to_add = graphene.Field(
        UserPaginatedObject,
        event_id=graphene.Int(required=True),
        department_ids=graphene.List(graphene.Int, required=False),
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )

    @login_required
    async def resolve_event_attendees_to_add(self, info, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size

        # check if event exists
        event = await models.Event.get(id=kwargs.get("event_id"))
        if not event:
            raise Exception("Event not found")

        # get all event attendees
        event_attendees = await models.EventAttendee.filter(event=event).all()
        event_attendees_ids = [e.attendee_id for e in event_attendees]

        # get departments users
        department_users = await models.UserDepartment.filter(
            department_id__in=kwargs.get("department_ids")
        )

        # get all users except the ones already added
        if len(department_users) > 0:
            s = models.User.filter(
                id__in=[e.user_id for e in department_users]
            ).all()
        else:
            s = models.User.filter(~Q(id__in=event_attendees_ids)).all()

        # get total count
        total_count = await s.count()

        return UserPaginatedObject(
            total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all(),
        )

    event_attendees_to_add_by_departments = graphene.Field(
        UserPaginatedObject,
        event_id=graphene.Int(required=True),
        department_ids=graphene.List(graphene.Int, required=True),
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )

    @login_required
    async def resolve_event_attendees_to_add_by_departments(self, info, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size

        # check if event exists
        event = await models.Event.get(id=kwargs.get("event_id"))

        if not event:
            raise Exception("Event not found")

        # get all event attendees
        event_attendees = await models.EventAttendee.filter(event=event).all()

        event_attendees_ids = [e.attendee.id for e in event_attendees]

        # get all users by department except the ones already added
        department_users = await models.UserDepartment.filter(
            department__in=kwargs.get("department_ids")
        ).all()
        department_users_ids = [e.user.id for e in department_users]

        s = models.User.filter(
            Q(id__in=department_users_ids) & ~Q(id__in=event_attendees_ids)
        ).all()

        # get total count
        total_count = await s.count()

        return UserPaginatedObject(
            total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all(),
        )

    my_events = graphene.Field(
        EventPaginatedObject,
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )

    @login_required
    async def resolve_my_events(self, info, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size
        # get all events where user is an attendee
        user = await models.User.get(id=info.context["request"].user.id)

        # get all event attendees
        event_attendees = await models.EventAttendee.filter(attendee=user).all()

        event_attendees_ids = [e.event_id for e in event_attendees]

        # get all events created by user
        events = await models.Event.filter(author=user).all()

        event_ids = [e.id for e in events]

        # combine both lists
        event_ids = event_ids + event_attendees_ids

        # get all events
        s = models.Event.filter(id__in=event_ids).all()

        # get total count
        total_count = await s.count()

        return EventPaginatedObject(
            total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all(),
        )

    user_events = graphene.Field(
        EventPaginatedObject,
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )

    @login_required
    async def resolve_user_events(self, info, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size

        # get all events where user is an author
        user = await models.User.get(id=info.context["request"].user.id)

        # get all events created by user
        s = models.Event.filter(author=user).all()

        # get total count
        total_count = await s.count()

        return EventPaginatedObject(
            total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all(),
        )

    user_events_subscribed = graphene.Field(
        EventPaginatedObject,
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )

    @login_required
    async def resolve_user_events_subscribed(self, info, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size

        # get all events where user is an attendee
        user = await models.User.get(id=info.context["request"].user.id)

        # get all event attendees
        attendees = await models.EventAttendee.filter(attendee=user).all()

        event_ids = [e.event.id for e in attendees]

        # get all events
        s = models.Event.filter(id__in=event_ids).all()

        # get total count
        total_count = await s.count()

        return EventPaginatedObject(
            total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all(),
        )
