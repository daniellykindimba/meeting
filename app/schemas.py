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
    
    
    timeline = graphene.Field(
        TimelinePaginatedObject,
        fetch_date=graphene.String(required=True),
        mode=graphene.String(required=True),
    )
    
    @login_required
    async def resolve_timeline(self, info, *args, **kwargs):
        print("=======kwargs: ", kwargs)
        fetch_date = pendulum.parse(kwargs.get("fetch_date"), strict=False)
        
        event_attendees = await models.EventAttendee.filter(attendee_id=info.context["request"].user.id).all()
        
        # get list of event ids
        events_ids = [e.event_id for e in event_attendees]
        
        # get all events created by user
        event_author = await models.Event.filter(author_id=info.context["request"].user.id,start_time__year=fetch_date.year, start_time__month=fetch_date.month).all()
        
        # get list of event ids
        events_author_ids = [e.id for e in event_author]
        
        # combine both lists
        events_ids = events_ids + events_author_ids
        
        # get all events
        events = await models.Event.filter(id__in=events_ids, start_time__year=fetch_date.year, start_time__month=fetch_date.month).all()
        
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
        EventPaginatedObject
    )
    
    @login_required
    async def resolve_my_todays_events(self, info, *args, **kwargs):
        # get all events where current user is an attendee
        events = [e.event_id for e in await models.EventAttendee.filter(
            attendee_id=info.context['request'].user.id)] + [e.id for e in await Event.filter(
                author_id=info.context['request'].user.id)]
        
        # filter unique events
        events = list(set(events))
        
        # get all events order by start time
        events = await models.Event.filter(
            id__in=events).order_by("start_time").all()
        
        # only 4
        events = events[:4]
        
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
        
        events_ids = [e.event_id for e in events_attendee] + [e.id for e in await Event.filter(author_id=info.context['request'].user.id)]
        
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
    
    committee_member = graphene.Field(userCommitteeObject, id=graphene.Int(required=True))
    
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
        committee_members = [u.user_id for u in await models.UserCommittee.filter(committee_id=committee.id).all()]
        
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
            
        
    
    
    
    
