import graphene
from app import models
from app.graphene_custom_fields import JSON
from settings import settings
from app.models import *
import pendulum
import math

class DataObject(graphene.ObjectType):
    data = JSON()


class TimelinePaginatedObject(graphene.ObjectType):
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
    departments = graphene.List(lambda: DepartmentObject)
    committees = graphene.List(lambda: CommitteeObject)
    
    async def resolve_departments(self, info, **kwargs):
        # get user departments 
        user_departments = [ud.department_id for ud in await UserDepartment.filter(user=self.id).all()]
        return await Department.filter(id__in=user_departments).all()

    async def resolve_committees(self, info, **kwargs):
        # get user committees 
        user_committees = [uc.committee_id for uc in await UserCommittee.filter(user=self.id).all()]
        return await Committee.filter(id__in=user_committees).all()

    async def resolve_can_edit(self, info, *args, **kwargs):
        try:
            if self.id == info.context['request'].user.id and self.is_admin:
                return True
        except:
            pass
        return False
    
    async def resolve_can_delete(self, info, *args, **kwargs):
        try:
            if self.id == info.context['request'].user.id and self.is_admin:
                return True
        except:
            pass
        return False
    
    async def resolve_can_manage(self, info, *args, **kwargs):
        try:
            if self.id == info.context['request'].user.id and self.is_admin:
                return True
        except:
            pass
        return False


class UserPaginatedObject(MiscPaginatedObject):
    results = graphene.List(UserObject)



class DepartmentObject(MiscFieldObject):
    name = graphene.String()
    description = graphene.String()
    
    async def resolve_can_edit(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return False
    
    async def resolve_can_delete(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return False
    
    async def resolve_can_manage(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return False


class DepartmentPaginatedObject(MiscPaginatedObject):
    results = graphene.List(DepartmentObject)


class UserDepartmentObject(MiscFieldObject):
    user = graphene.Field(UserObject)
    department = graphene.Field(DepartmentObject)
    
    async def resolve_can_edit(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return False
    
    async def resolve_can_delete(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return False
    
    async def resolve_can_manage(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return False

class UserDepartmentPaginatedObject(MiscPaginatedObject):
    results = graphene.List(UserDepartmentObject)


class VenueObject(MiscFieldObject):
    name = graphene.String()
    description = graphene.String()
    capacity = graphene.Int()
    venue_type = graphene.String()

    async def resolve_venue_type(self, info, **kwargs):
        return self.venue_type.name
    
    async def resolve_can_edit(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return False
    
    async def resolve_can_delete(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return False
    
    async def resolve_can_manage(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return False


class VenuePaginatedObject(MiscPaginatedObject):
    results = graphene.List(VenueObject)



class EventObject(MiscFieldObject):
    id = graphene.Int()
    title = graphene.String()
    description = graphene.String()
    event_type = graphene.String()
    event_type_value = graphene.String()
    start_time = graphene.DateTime()
    end_time = graphene.DateTime()
    venue = graphene.Field(VenueObject)
    author = graphene.Field(UserObject)
    attendees = graphene.List(lambda: UserObject)
    quarter = graphene.String()
    financial_year = graphene.String()
    manage_documents = graphene.Boolean()
    manage_agendas = graphene.Boolean()
    manage_minutes = graphene.Boolean()
    
    async def resolve_quarter(self, info, *args, **kwargs):
        sd = pendulum.parse(str(self.start_time), strict=False)
        years = []
        if sd.month >= 7:
            years = [sd.year, int(sd.year) + 1]
            start_date = pendulum.parse(f"07/01/{years[0]}", strict=False)
            end_date = start_date.add(months=12).subtract(days=1)
            # create date range for the financial year
            date_range = pendulum.period(start_date, end_date).range('days')
            date_range = list(date_range)
            # get all teh dates in the date range
            dates = [str(d.date()) for d in date_range]
            # split the dates into 4 quarters of 3 months each
            splitted_dates = []
            for d in dates:
                three_month_dates = []
                
                
                
            return f"Q1"
        else:
            years = [int(sd.year) - 1, sd.year]
            start_date = pendulum.parse(f"07/01/{years[0]}", strict=False)
            end_date = start_date.add(months=12).subtract(days=1)
            # create date range for the financial year
            date_range = pendulum.period(start_date, end_date).range('days')
            date_range = list(date_range)
            # create group of 3 months from the date range
            quarter_date_range = [date_range[i:i + 3] for i in range(0, len(date_range), 3)]
            # check if teh sd is in which group of 3 months and return the index
            for i, qdr in enumerate(quarter_date_range):
                if sd in qdr:
                    q = f"Q{i + 1}"
                    print("Q", q)
                    return q
        
    
    async def resolve_attendees(self, info, **kwargs):
        event_attendees = [ea.attendee_id for ea in await EventAttendee.filter(event=self.id).all()]
        return await User.filter(id__in=event_attendees).all()
    
    async def resolve_event_type(self, info, **kwargs):
        try:
            return self.event_type.name
        except:
            return None
    
    async def resolve_event_type_value(self, info, **kwargs):
        try:
            return self.event_type.value
        except:
            return None
    
    async def resolve_can_edit(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return info.context['request'].user.id == self.author_id
    
    async def resolve_can_delete(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return info.context['request'].user.id == self.author_id
    
    async def resolve_can_manage(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return info.context['request'].user.id == self.author_id
    
    async def resolve_manage_documents(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        attendee = await EventAttendee.filter(attendee_id=info.context['request'].user.id, event_id=self.id, can_upload=True).exists()
        return attendee or info.context['request'].user.id == self.author_id

    async def resolve_manage_agendas(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        attendee = await EventAttendee.filter(attendee_id=info.context['request'].user.id, event_id=self.id, manage_agendas=True).exists()
        return attendee or info.context['request'].user.id == self.author_id
    
    async def resolve_manage_minutes(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        attendee = await EventAttendee.filter(attendee_id=info.context['request'].user.id, event_id=self.id, manage_minutes=True).exists()
        return attendee or info.context['request'].user.id == self.author_id
        


class EventPaginatedObject(MiscPaginatedObject):
    results = graphene.List(EventObject)



class EventDepartmentObject(MiscFieldObject):
    event = graphene.Field(EventObject)
    department = graphene.Field(DepartmentObject)
    
    async def resolve_can_edit(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        event_obj = await Event.get(id=self.event_id)
        if event_obj:
            return info.context['request'].user.id == event_obj.author_id
        return False
    
    
    async def resolve_can_delete(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        event_obj = await Event.get(id=self.event_id)
        if event_obj:
            return info.context['request'].user.id == event_obj.author_id
        return False
    
    async def resolve_can_manage(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        event_obj = await Event.get(id=self.event_id)
        if event_obj:
            return info.context['request'].user.id == event_obj.author_id
        return False


class EventDepartmentPaginatedObject(MiscPaginatedObject):
    results = graphene.List(EventDepartmentObject)


class EventAttendeeObject(MiscFieldObject):
    event = graphene.Field(EventObject)
    attendee = graphene.Field(UserObject)
    is_attending = graphene.Boolean()
    
    async def resolve_can_edit(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        event_obj = await Event.get(id=self.event_id)
        if event_obj:
            return info.context['request'].user.id == event_obj.author_id
        return False
    
    async def resolve_can_delete(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        event_obj = await Event.get(id=self.event_id)
        if event_obj:
            return info.context['request'].user.id == event_obj.author_id
        return False
    
    async def resolve_can_manage(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        event_obj = await Event.get(id=self.event_id)
        if event_obj:
            return info.context['request'].user.id == event_obj.author_id
        return False


class EventAttendeePaginatedObject(MiscPaginatedObject):
    results = graphene.List(EventAttendeeObject)


class EventAgendaObject(MiscFieldObject):
    event = graphene.Field(EventObject)
    title = graphene.String()
    description = graphene.String()
    start_time = graphene.DateTime()
    end_time = graphene.DateTime()
    index = graphene.Int()
    
    async def resolve_can_edit(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        event_obj = await Event.get(id=self.event_id)
        if event_obj:
            return info.context['request'].user.id == event_obj.author_id
        return False
    
    async def resolve_can_delete(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        event_obj = await Event.get(id=self.event_id)
        if event_obj:
            return info.context['request'].user.id == event_obj.author_id
        return False
    
    async def resolve_can_manage(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        event_obj = await Event.get(id=self.event_id)
        if event_obj:
            return info.context['request'].user.id == event_obj.author_id
        return False


class EventAgendaPaginatedObject(MiscPaginatedObject):
    results = graphene.List(EventAgendaObject)


class EventDocumentObject(MiscFieldObject):
    event = graphene.Field(EventObject)
    title = graphene.String()
    description = graphene.String()
    file = graphene.String()
    author = graphene.Field(UserObject)
    note = graphene.Field(lambda: EventUserDocumentNoteObject)
    departments = graphene.List(lambda: DepartmentObject)
    
    async def resolve_departments(self, info, **kwargs):
        deps = await EventDocumentDepartment.filter(event_document_id=self.id).all()
        return await Department.filter(id__in=[d.department_id for d in deps]).all()

    async def resolve_file(self, info, **kwargs):
        return f"{settings.MINIO_SERVER}{self.file}"

    async def resolve_note(self, info, **kwargs):
       return await EventUserDocumentNote.filter(
           event_document_id=self.id, 
           user_id=info.context['request'].user.id
        ).first()

    async def resolve_can_edit(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        event_obj = await Event.get(id=self.event_id)
        return info.context['request'].user.id == event_obj.author_id
    
    async def resolve_can_delete(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        event_obj = await Event.get(id=self.event_id)
        return info.context['request'].user.id == event_obj.author_id
    
    async def resolve_can_manage(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        event_obj = await Event.get(id=self.event_id)
        return info.context['request'].user.id == event_obj.author_id

class EventDocumentPaginatedObject(MiscPaginatedObject):
    results = graphene.List(EventDocumentObject)




class CommitteeObject(MiscFieldObject):
    name = graphene.String()
    description = graphene.String()
    
    async def resolve_can_edit(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return False
    
    async def resolve_can_delete(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return False
    
    async def resolve_can_manage(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return False


class CommitteePaginatedObject(MiscPaginatedObject):
    results = graphene.List(CommitteeObject)


class userCommitteeObject(MiscFieldObject):
    user = graphene.Field(UserObject)
    committee = graphene.Field(CommitteeObject)
    
    async def resolve_can_edit(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return False
    
    async def resolve_can_delete(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return False
    
    async def resolve_can_manage(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return False


class userCommitteePaginatedObject(MiscPaginatedObject):
    results = graphene.List(userCommitteeObject)


class CommitteeDepartmentObject(MiscFieldObject):
    committee = graphene.Field(CommitteeObject)
    department = graphene.Field(DepartmentObject)
    
    async def resolve_can_edit(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return False
    
    async def resolve_can_delete(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return False
    
    async def resolve_can_manage(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        return False


class CommitteeDepartmentPaginatedObject(MiscPaginatedObject):
    results = graphene.List(CommitteeDepartmentObject)


class EventUserDocumentNoteObject(MiscFieldObject):
    event = graphene.Field(EventObject)
    user = graphene.Field(UserObject)
    event_document = graphene.Field(EventDocumentObject)
    note = graphene.String()
    
    async def resolve_can_edit(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
    
        if self.user_id == info.context['request'].user.id:
            return True
        
        event_obj = await Event.get(id=self.event_id)
        if event_obj:
            return info.context['request'].user.id == event_obj.author_id
        
        return False
    
    async def resolve_can_delete(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
    
        if self.user_id == info.context['request'].user.id:
            return True
        
        event_obj = await Event.get(id=self.event_id)
        if event_obj:
            return info.context['request'].user.id == event_obj.author_id
        
        return False
    
    async def resolve_can_manage(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
    
        if self.user_id == info.context['request'].user.id:
            return True
        
        event_obj = await Event.get(id=self.event_id)
        if event_obj:
            return info.context['request'].user.id == event_obj.author_id
        
        return False


class EventUserDocumentNotePaginatedObject(MiscPaginatedObject):
    results = graphene.List(EventUserDocumentNoteObject)


class EventCommitteeObject(MiscFieldObject):
    event = graphene.Field(EventObject)
    committee = graphene.Field(CommitteeObject)
    
    async def resolve_can_edit(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        
        event_obj = await Event.get(id=self.event_id)
        if event_obj:
            return info.context['request'].user.id == event_obj.author_id
        
        return False
    
    async def resolve_can_delete(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        
        event_obj = await Event.get(id=self.event_id)
        if event_obj:
            return info.context['request'].user.id == event_obj.author_id
        
        return False
    
    async def resolve_can_manage(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        
        event_obj = await Event.get(id=self.event_id)
        if event_obj:
            return info.context['request'].user.id == event_obj.author_id
        
        return False


class EventCommitteePaginatedObject(MiscPaginatedObject):
    results = graphene.List(EventCommitteeObject)


class EventMinuteObject(MiscFieldObject):
    event = graphene.Field(EventObject)
    content = graphene.String()
    author = graphene.Field(UserObject)
    index = graphene.Int()
    
    async def resolve_can_edit(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        
        event_obj = await Event.get(id=self.event_id)
        if event_obj:
            return info.context['request'].user.id == event_obj.author_id
    
        if self.author_id == info.context['request'].user.id:
            return True
        
        return False
    
    async def resolve_can_delete(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        
        event_obj = await Event.get(id=self.event_id)
        if event_obj:
            return info.context['request'].user.id == event_obj.author_id
    
        if self.author_id == info.context['request'].user.id:
            return True
        
        return False
    
    async def resolve_can_manage(self, info, *args, **kwargs):
        user = await User.get(id=info.context['request'].user.id)
        if user and user.is_admin:
            return True
        
        event_obj = await Event.get(id=self.event_id)
        if event_obj:
            return info.context['request'].user.id == event_obj.author_id
    
        if self.author_id == info.context['request'].user.id:
            return True
        
        return False


class EventMinutePaginatedObject(MiscPaginatedObject):
    results = graphene.List(EventMinuteObject)

    

