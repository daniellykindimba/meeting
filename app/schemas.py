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
    
    analytics = graphene.Field(DataObject)
    
    @login_required
    async def resolve_analytics(self, info, *args, **kwargs):
        return DataObject(
            data={
                "total_users": await models.User.all().count(),
                "total_events": await models.Event.all().count(),
                "total_departments": await models.Department.all().count(),
                "total_committees": await models.Committee.all().count(),
                "total_venues": await models.Venue.all().count(),
            }
        )


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

        s = models.User.filter(
            Q(first_name__icontains=key) |
            Q(middle_name__icontains=key) |
            Q(last_name__icontains=key) |
            Q(email__icontains=key) | 
            Q(phone__icontains=key)
        ).order_by("-created")

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
            results=await s.offset(offset).limit(size).all().order_by("-created"),
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
            results=await s.offset(offset).limit(size).all().order_by("-created"),
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
        event_type=graphene.String(required=False),
    )

    event = graphene.Field(EventObject, id=graphene.Int(required=True))

    @login_required
    async def resolve_events(self, info, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size

        s = models.Event.all()
        if kwargs.get("event_type"):
            s = s.filter(event_type=kwargs.get("event_type"))

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
    
    
    event_documents_managers = graphene.Field(
        EventAttendeePaginatedObject,
        id=graphene.Int(required=True, description="Event ID"),
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )
    
    @login_required
    async def resolve_event_documents_managers(self, info, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size

        s = models.EventAttendee.filter(event_id=kwargs.get("id"), can_upload=True).filter(
            Q(attendee__first_name__icontains=key) | 
            Q(attendee__middle_name__icontains=key) | 
            Q(attendee__last_name__icontains=key) | 
            Q(attendee__email__icontains=key) | 
            Q(attendee__username__icontains=key)
        )

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
    
    
    not_event_documents_managers = graphene.Field(
        EventAttendeePaginatedObject,
        id=graphene.Int(required=True, description="Event ID"),
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )
    
    @login_required
    async def resolve_not_event_documents_managers(self, info, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size

        s = models.EventAttendee.filter(event_id=kwargs.get("id"), can_upload=False).filter(
            Q(attendee__first_name__icontains=key) | 
            Q(attendee__middle_name__icontains=key) | 
            Q(attendee__last_name__icontains=key) | 
            Q(attendee__email__icontains=key) | 
            Q(attendee__username__icontains=key)
        )

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
        
    
    
    event_minutes_managers = graphene.Field(
        EventAttendeePaginatedObject,
        id=graphene.Int(required=True, description="Event ID"),
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )
    
    @login_required
    async def resolve_event_minutes_managers(self, info, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size

        s = models.EventAttendee.filter(event_id=kwargs.get("id"), manage_minutes=True).filter(
            Q(attendee__first_name__icontains=key) | 
            Q(attendee__middle_name__icontains=key) | 
            Q(attendee__last_name__icontains=key) | 
            Q(attendee__email__icontains=key) | 
            Q(attendee__username__icontains=key)
        )

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
    
    
    event_agendas_managers = graphene.Field(
        EventAttendeePaginatedObject,
        id=graphene.Int(required=True, description="Event ID"),
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )
    
    
    @login_required
    async def resolve_evenet_agendas_managers(self, info, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size

        s = models.EventAttendee.filter(event_id=kwargs.get("id"), manage_agendas=True).filter(
            Q(attendee__first_name__icontains=key) | 
            Q(attendee__middle_name__icontains=key) | 
            Q(attendee__last_name__icontains=key) | 
            Q(attendee__email__icontains=key) | 
            Q(attendee__username__icontains=key)
        )

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
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size

        s = models.EventAttendee.filter(event_id=kwargs.get("id")).filter(
            Q(attendee__first_name__icontains=key) | 
            Q(attendee__middle_name__icontains=key) | 
            Q(attendee__last_name__icontains=key) | 
            Q(attendee__email__icontains=key) | 
            Q(attendee__username__icontains=key)
        )

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
        ).filter(
            Q(title__icontains=key) | 
            Q(description__icontains=key)
        )

        # get total count
        total_count = await s.count()

        return EventAgendaPaginatedObject(
            total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all().order_by("index"),
        )

    @login_required
    async def resolve_event_agenda(self, info, **kwargs):
        id = kwargs.get("id")
        return await models.EventAgenda.get(id=id)


    creation_financial_years = graphene.Field(DataObject)
    
    @login_required
    async def resolve_creation_financial_years(self, info, *args, **kwargs):
        c_date = pendulum.now()
        years = []
        if c_date.month >= 7:
            years.append(f"{c_date.year + 1}/{c_date.year + 2}")
            years.append(f"{c_date.year}/{c_date.year + 1}")
        else:
            years.append(f"{c_date.year}/{c_date.year + 1}")
            years.append(f"{c_date.year - 1}/{c_date.year}")
        
        return DataObject(data=years)
    
    
    financial_years = graphene.Field(DataObject)
    
    @login_required
    async def resolve_financial_years(self, info, *args, **kwargs):
        all_events = await models.Event.all()
        unique_years = set(
            event.financial_year for event in all_events if event.financial_year is not None)
        unique_years_list = list(unique_years)
        return DataObject(data=unique_years_list)

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
            department_id__in=kwargs.get("department_ids", [])
        )

        # get all users except the ones already added
        if len(department_users) > 0:
            s = models.User.filter(
                id__in=[e.user_id for e in department_users]
            ).filter(
                Q(first_name__icontains=key) |
                Q(middle_name__icontains=key) | 
                Q(last_name__icontains=key) |
                Q(email__icontains=key) |
                Q(phone__icontains=key)
            ).all()
        else:
            s = models.User.filter(~Q(id__in=event_attendees_ids)).filter(
                Q(first_name__icontains=key) |
                Q(middle_name__icontains=key) | 
                Q(last_name__icontains=key) |
                Q(email__icontains=key) |
                Q(phone__icontains=key)).all()

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
        ).filter(
             Q(first_name__icontains=key) |
                Q(middle_name__icontains=key) | 
                Q(last_name__icontains=key) |
                Q(email__icontains=key) |
                Q(phone__icontains=key)).all()

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
        event_type=graphene.String(required=False),
        financial_year=graphene.String(required=False),
        committee_id=graphene.Int(required=False),
        department_id=graphene.Int(required=False)
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
        
        # get event type 
        event_type = kwargs.get("event_type")
        # check if event type is not none
        if event_type:
            s = s.filter(event_type=event_type)
        
        committee_id = kwargs.get("committee_id")
        if committee_id:
            committee_events = [
                ec.event_id for ec in await models.EventCommittee.filter(
                    committee_id=committee_id)
            ]
            s = s.filter(id__in=committee_events)
        
        department_id = kwargs.get("department_id")
        if department_id:
            department_events = [
                ed.event_id for ed in await models.EventDepartment.filter(
                    department_id=department_id)
            ]
            s = s.filter(id__in=department_events)
        
        financial_year = kwargs.get("financial_year")
        if financial_year:
            fy_splitted = str(financial_year).split("/")
            fy_start_string = f"01/07/{fy_splitted[0]}"
            fy_start = pendulum.parse(fy_start_string, strict=False)
            fy_end = pendulum.parse(fy_start_string, strict=False).add(months=12).subtract(days=1)
            s = s.filter(start_time__gt=fy_start, start_time__lt=fy_end)

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
    
    
    timeline = graphene.Field(
        TimelinePaginatedObject,
        fetch_date=graphene.String(required=True),
        mode=graphene.String(required=True),
    )
    
    @login_required
    async def resolve_timeline(self, info, *args, **kwargs):
        fetch_date = pendulum.parse(kwargs.get("fetch_date"), strict=False)
        
        event_attendees = await models.EventAttendee.filter(
            attendee_id=info.context["request"].user.id
        ).all()
        
        # get list of event ids
        events_ids = [e.event_id for e in event_attendees]
        
        # get all events created by user
        event_author = await models.Event.filter(
            author_id=info.context["request"].user.id,
            start_time__year=fetch_date.year, 
            start_time__month=fetch_date.month
        ).all()
        
        # get list of event ids
        events_author_ids = [e.id for e in event_author]
        
        # combine both lists
        events_ids = events_ids + events_author_ids
        
        # get all events
        events = await models.Event.filter(
            id__in=events_ids, start_time__year=fetch_date.year, 
            start_time__month=fetch_date.month
        ).all()
        
        datas = []
        
        for event in events:
            datas.append({
                "type": "success",
                "content": event.title,
                "description": event.description,
                "id": event.id,
                "date": event.start_time.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return TimelinePaginatedObject(
            data=datas)
    
    
    my_todays_events = graphene.Field(
        EventPaginatedObject,
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )
    
    @login_required
    async def resolve_my_todays_events(self, info, *args, **kwargs):
        # get all events where current user is an attendee
        events_ids = [e.event_id for e in await models.EventAttendee.filter(
            attendee_id=info.context['request'].user.id)] + [
                e.id for e in await Event.filter(
                author_id=info.context['request'].user.id)
            ]
        
        # filter unique events
        events_ids = list(set(events_ids))
        
        # get all events order by start time in wqhich start time is starting from today
        c_date = pendulum.now()
        events = await models.Event.filter(
            id__in=events_ids
        ).filter(
            start_time__lt=c_date, 
            end_time__gt=c_date).order_by("-start_time")
        
        # only 4
        events = events[:10]
        
        return EventPaginatedObject(
            total=len(events),
            page=1,
            pages=1,
            has_next=False,
            has_prev=False,
            results=events,
        )
           
    
    
    my_documents = graphene.Field(
        EventDocumentPaginatedObject
    )
    
    @login_required
    async def resolve_my_documents(self, info, *args, **kwargs):
        # get all events where current user is an attendee
        events_attendee = await models.EventAttendee.filter(
            attendee_id=info.context['request'].user.id).all()
        
        events_ids = [e.event_id for e in events_attendee] + [
            e.id for e in await Event.filter(
                author_id=info.context['request'].user.id
            )
        ]
        
        # get all events documents order by created 
        documents = await models.EventDocument.filter(
            event_id__in=events_ids).order_by("-created").all()
        
        return EventDocumentPaginatedObject(
            total=len(documents),
            page=1,
            pages=1,
            has_next=False,
            has_prev=False,
            results=documents)
    
    
    committees = graphene.Field(
        CommitteePaginatedObject,
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )
    
    committee = graphene.Field(CommitteeObject, id=graphene.Int(required=True))
    
    
    @login_required
    async def resolve_committees(self, info, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size
        
        s = models.Committee.filter(
            Q(name__icontains=key) |
            Q(description__icontains=key)
        ).order_by("-created")
        
        total_count = await s.count()
        
        return CommitteePaginatedObject(
            total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all(),
        )
    
    
    committee_members = graphene.Field(
        userCommitteePaginatedObject,
        id=graphene.Int(required=True, description="Committee ID"),
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )
    
    @login_required
    async def resolve_committee_members(self, info, *args, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size
        
        s = models.UserCommittee.filter(
            committee_id=kwargs.get("id")
        ).order_by("-created")
        
        total_count = await s.count()
        
        return userCommitteePaginatedObject(
            total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all(),
        )
    
    committee_member = graphene.Field(
        userCommitteeObject, id=graphene.Int(required=True)
    )
    
    @login_required
    async def resolve_committee_member(self, info, *args, **kwargs):
        return await models.UserCommittee.get(id=kwargs.get("id"))


    not_committee_members = graphene.Field(
        UserPaginatedObject,
        id=graphene.Int(required=True, description="Committee ID"),
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )
    
    @login_required
    async def resolve_not_committee_members(self, info, *args, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size
        
        committee = await models.Committee.get(id=kwargs.get("id"))
        
        # get all committee members
        committee_members = [
            u.user_id for u in await models.UserCommittee.filter(
                committee_id=committee.id
            ).all()
        ]
        
        s = models.User.filter(
            ~Q(id__in=committee_members)
        ).filter(
            Q(first_name__icontains=key) |
            Q(middle_name__icontains=key) |
            Q(last_name__icontains=key) |
            Q(email__icontains=key) |
            Q(phone__icontains=key)
        ).order_by("-created")
        
        total_count = await s.count()
        
        return UserPaginatedObject(
             total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all(),
        )
            
        
    
    
    committee_departments = graphene.Field(
        CommitteeDepartmentPaginatedObject,
        id=graphene.Int(required=True, description="Committee ID"),
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )
    
    @login_required
    async def resolve_committee_departments(self, info, *args, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size
        
        s = models.CommitteeDepartment.filter(
            committee_id=kwargs.get("id")
        ).order_by("-created")
        
        total_count = await s.count()
        
        return CommitteeDepartmentPaginatedObject(
            total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all(),
        )
    
    committee_department = graphene.Field(
        CommitteeDepartmentObject, id=graphene.Int(required=True)
    )
    
    @login_required
    async def resolve_committee_department(self, info, *args, **kwargs):
        return await models.CommitteeDepartment.get(id=kwargs.get("id"))

    
    not_committee_departments = graphene.Field(
        DepartmentPaginatedObject,
        id=graphene.Int(required=True, description="Committee ID"),
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )
    
    @login_required
    async def resolve_not_committee_departments(self, info, *args, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        page = kwargs.get("page") if kwargs.get("page") else 1
        size = kwargs.get("page_size") if kwargs.get("page_size") else 25

        offset = (page - 1) * size
        
        committee = await models.Committee.get(id=kwargs.get("id"))
        
        # get all committee members
        committee_departments = [
            u.department_id for u in await models.CommitteeDepartment.filter(
                committee_id=committee.id
            ).all()
        ]
        
        s = models.Department.filter(
            ~Q(id__in=committee_departments)
        ).filter(
            Q(name__icontains=key) |
            Q(description__icontains=key)
        ).order_by("-created")
        
        total_count = await s.count()
        
        return DepartmentPaginatedObject(
             total=total_count,
            page=page,
            pages=total_count // size,
            has_next=total_count > offset + size,
            has_prev=page > 1,
            results=await s.offset(offset).limit(size).all(),
        )
    
    
    event_committees = graphene.Field(
        EventCommitteePaginatedObject,
        id=graphene.Int(required=True, description="Event ID"),
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )
    
    @login_required
    async def resolve_event_committees(self, info, *args, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        
        s = models.EventCommittee.filter(
            event_id=kwargs.get("id")
        ).order_by("-created")
        
        total_count = await s.count()
        
        return EventCommitteePaginatedObject(
            total=total_count,
            page=1,
            pages=1,
            has_next=False,
            has_prev=False,
            results=await s.all(),
        )
    
    event_committee = graphene.Field(
        EventCommitteeObject, id=graphene.Int(required=True)
    )
    
    @login_required
    async def resolve_event_committee(self, info, *args, **kwargs):
        return await models.EventCommittee.get(id=kwargs.get("id"))

    event_committees_to_add = graphene.Field(
        CommitteePaginatedObject,
        id=graphene.Int(required=True, description="Event ID"),
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )
    
    @login_required
    async def resolve_event_committees_to_add(self, info, *args, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        
        # get all event committees
        event_committees = [
            e.committee_id for e in await models.EventCommittee.filter(
                event_id=kwargs.get("id")
            ).all()
        ]
        
        s = models.Committee.filter(
            ~Q(id__in=event_committees)
        ).filter(
            Q(name__icontains=key) |
            Q(description__icontains=key)
        ).order_by("-created")
        
        total_count = await s.count()
        
        return CommitteePaginatedObject(
             total=total_count,
            page=1,
            pages=1,
            has_next=False,
            has_prev=False,
            results=await s.all(),
        )
    
    
    user_event_document_note = graphene.Field(
        EventUserDocumentNoteObject,
        id=graphene.Int(required=True, description="Event Document ID")
    )
    
    @login_required
    async def resolve_user_event_document_note(self, info, *args, **kwargs):
        # check if event_document exists
        event_document = await models.EventDocument.get(id=kwargs.get("id"))
        if not event_document:
            raise Exception("Event Document not found")
        
        return await models.EventUserDocumentNote.get(
            event_document_id=kwargs.get("id"), 
            user_id=info.context['request'].user.id)

    event_minutes = graphene.Field(
        EventMinutePaginatedObject,
        event_id=graphene.Int(required=True, description="Event ID"),
        key=graphene.String(required=False),
        sort=graphene.String(required=False),
        where=graphene.JSONString(required=False),
        page=graphene.Int(required=False),
        page_size=graphene.Int(required=False),
    )
    
    @login_required
    async def resolve_event_minutes(self, info, *args, **kwargs):
        key = kwargs.get("key") if kwargs.get("key") else ""
        
        s = models.EventMinute.filter(
            event_id=kwargs.get("event_id")
        ).order_by("index")
        
        total_count = await s.count()
        
        return EventMinutePaginatedObject(
            total=total_count,
            page=1,
            pages=1,
            has_next=False,
            has_prev=False,
            results=await s.all(),
        )


    
    
        
    
