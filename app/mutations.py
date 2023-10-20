from datetime import timedelta

import bcrypt
import graphene
from app.nodes import *
from app.login_manager import manager
from tortoise.queryset import (
    Q,
)
from app.middlewares.authentication import login_required
from app.validators.phone_validator import PhoneValidator
from graphene_file_upload.scalars import Upload
from app.manager import MeetingManager
import pendulum


class AuthMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserObject)
    token = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    async def mutate(self, info, *args, **kwargs):
        print("kwargs", kwargs)
        user = await models.User.filter(
            Q(username=str(kwargs.get("email")).strip().lower())
            | Q(email=str(kwargs.get("email")).strip().lower())
        ).first()

        if not user:
            message = "Authentication Failed User not found"
            return AuthMutation(success=False, message=message)

        # if not user.is_active:
        #     message = "Authentication Failed, Your account has been deactivated"
        #     return AuthMutation(success=False, message=message)

        # hashed = bcrypt.hashpw(
        #     kwargs.get("password").encode("utf-8"), user.salt_key.encode("utf-8")
        # )

        # # check if user.hash_password is string or bytes and convert to string
        # hash_password = user.hash_password
        # if isinstance(hash_password, bytes):
        #     hash_password = hash_password.decode("utf-8")

        # if not any(
        #     (
        #         hash_password == hashed.decode("utf-8"),
        #         str(user.hash_password) == hashed.decode("utf-8"),
        #     )
        # ):
        #     message = "Authentication Failed, Invalid Password"
        #     return AuthMutation(success=False, message=message)

        user_dict = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "middle_name": user.middle_name,
            "last_name": user.last_name,
            "email": user.email,
            "sub": user.username,
        }

        t_expires = timedelta(seconds=90000000)
        access_token = manager.create_access_token(data=user_dict, expires=t_expires)

        return AuthMutation(
            success=True,
            message="Authentication Success",
            user=user,
            token=access_token,
        )


class CreateDepartmentMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    department = graphene.Field(DepartmentObject)

    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if department already exists
        department = await models.Department.filter(
            name__iexact=kwargs.get("name")
        ).first()
        if department:
            return CreateDepartmentMutation(
                success=False, message="Directorate already exists"
            )
        department = await models.Department.create(**kwargs)
        return CreateDepartmentMutation(
            success=True,
            message="Directorate created successfully",
            department=department,
        )


class UpdateDepartmentMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    department = graphene.Field(DepartmentObject)

    class Arguments:
        id = graphene.Int(required=True, description="Department ID")
        name = graphene.String(required=True, description="Department Name")
        description = graphene.String(
            required=True, description="Directorate Description"
        )

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if department already exists
        department = await models.Department.filter(id=kwargs.get("id")).first()
        if not department:
            return UpdateDepartmentMutation(
                success=False, message="Directorate does not exist"
            )
        
        kwargs_copy = kwargs.copy()
        try:
            kwargs_copy.pop("id")
        except:
            pass
        department = await models.Department.filter(id=kwargs.get("id")).update(
            **kwargs_copy
        )
        return UpdateDepartmentMutation(
            success=True,
            message="Directorate updated successfully",
            department=await models.Department.get(id=kwargs.get("id")),
        )


class DeleteDepartmentMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    department = graphene.Field(DepartmentObject)

    class Arguments:
        id = graphene.Int(required=True, description="Department ID")

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if department already exists
        department = await models.Department.filter(id=kwargs.get("id")).first()
        if not department:
            return DeleteDepartmentMutation(
                success=False, message="Directorate does not exist"
            )
        department = await models.Department.filter(id=kwargs.get("id")).delete()
        return DeleteDepartmentMutation(
            success=True,
            message="Directorate deleted successfully",
            department=department,
        )




class BlockDepartmentMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    department = graphene.Field(DepartmentObject)
    
    class Arguments:
        id = graphene.Int(required=True, description="Department ID")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if department already exists
        department = await models.Department.filter(id=kwargs.get("id")).first()
        if not department:
            return BlockDepartmentMutation(
                success=False, message="Directorate does not exist"
            )
        department = await models.Department.filter(id=kwargs.get("id")).update(is_active=False)
        return BlockDepartmentMutation(
            success=True,
            message="Directorate blocked successfully",
            department=department,
        )
    

class UnblockDepartmentMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    department = graphene.Field(DepartmentObject)
    
    class Arguments:
        id = graphene.Int(required=True, description="Department ID")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if department already exists
        department = await models.Department.filter(id=kwargs.get("id")).first()
        if not department:
            return UnblockDepartmentMutation(
                success=False, message="Directorate does not exist"
            )
        department = await models.Department.filter(id=kwargs.get("id")).update(is_active=True)
        return UnblockDepartmentMutation(
            success=True,
            message="Directorate unblocked successfully",
            department=department,
        )


class CreateUserMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserObject)

    class Arguments:
        first_name = graphene.String(required=True)
        middle_name = graphene.String(required=False)
        last_name = graphene.String(required=True)
        email = graphene.String(required=False)
        phone = graphene.String(required=False)
        is_admin = graphene.Boolean(required=False)
        is_staff = graphene.Boolean(required=False)
        departments_ids = graphene.List(graphene.Int)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        print("=====kwargs: ", kwargs)

        # check if user already exists by email
        user = await models.User.filter(email__iexact=kwargs.get("email")).first()
        if user:
            return CreateUserMutation(success=False, message="User already exists")

        # check if phone is valid
        phone = kwargs.get("phone")
        valid_phone = PhoneValidator(phone)
        if not valid_phone.validate():
            return CreateUserMutation(success=False, message="Invalid Phone Number")

        phone = valid_phone.international_format_plain()

        # normalize email
        email = kwargs.get("email")
        if email:
            email = email.strip().lower()

        # create user
        user = await models.User.create(
            first_name=kwargs.get("first_name"),
            middle_name=kwargs.get("middle_name"),
            last_name=kwargs.get("last_name"),
            email=email,
            phone=phone,
            username=email,
            is_admin=kwargs.get("is_admin"),
            is_staff=kwargs.get("is_staff"),
        )

        # auto create user departments
        for department in kwargs.get("departments_ids"):
            if not await models.UserDepartment.filter(
                department_id=department, user_id=user.id
            ).first():
                await models.UserDepartment.create(
                    user_id=user.id, department_id=department
                )

        return CreateUserMutation(
            success=True, message="User created successfully", user=user
        )


class UpdateUserMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserObject)

    class Arguments:
        id = graphene.Int(required=True)
        first_name = graphene.String(required=True)
        middle_name = graphene.String(required=False)
        last_name = graphene.String(required=True)
        email = graphene.String(required=False)
        phone = graphene.String(required=False)
        is_admin = graphene.Boolean(required=False)
        is_staff = graphene.Boolean(required=False)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if user already exists by email
        user = await models.User.filter(id=kwargs.get("id")).first()
        if not user:
            return CreateUserMutation(success=False, message="User does not exist")

        # check if user already exists by email except the current user
        user = (
            await models.User.filter(email__iexact=kwargs.get("email"))
            .exclude(id=user.id)
            .first()
        )
        if user:
            return CreateUserMutation(success=False, message="User already exists")

        # check if phone is valid
        phone = kwargs.get("phone")
        valid_phone = PhoneValidator(phone)
        if not valid_phone.validate():
            return CreateUserMutation(success=False, message="Invalid Phone Number")

        phone = valid_phone.international_format_plain()

        # normalize email
        email = kwargs.get("email")
        if email:
            email = email.strip().lower()

        # create user
        user = await models.User.filter(id=kwargs.get("id")).update(
            first_name=kwargs.get("first_name"),
            middle_name=kwargs.get("middle_name"),
            last_name=kwargs.get("last_name"),
            email=email,
            phone=phone,
            username=email,
            is_admin=kwargs.get("is_admin"),
            is_staff=kwargs.get("is_staff"),
        )

        return CreateUserMutation(
            success=True, message="User updated successfully", user=user
        )


class DeleteUserMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserObject)

    class Arguments:
        id = graphene.Int(required=True)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if user already exists by email
        user = await models.User.filter(id=kwargs.get("id")).first()
        if not user:
            return CreateUserMutation(success=False, message="User does not exist")

        # delete user
        user = await models.User.filter(id=kwargs.get("id")).delete()

        return CreateUserMutation(
            success=True, message="User deleted successfully", user=user
        )


class BlockUserMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserObject)

    class Arguments:
        id = graphene.Int(required=True)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if user already exists by email
        user = await models.User.filter(id=kwargs.get("id")).first()
        if not user:
            return CreateUserMutation(success=False, message="User does not exist")

        # block user
        user = await models.User.filter(id=kwargs.get("id")).update(is_active=False)

        return CreateUserMutation(
            success=True, message="User blocked successfully", user=user
        )


class UnblockUserMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserObject)

    class Arguments:
        id = graphene.Int(required=True)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if user already exists by email
        user = await models.User.filter(id=kwargs.get("id")).first()
        if not user:
            return CreateUserMutation(success=False, message="User does not exist")

        # unblock user
        user = await models.User.filter(id=kwargs.get("id")).update(is_active=True)

        return CreateUserMutation(
            success=True, message="User unblocked successfully", user=user
        )


class AddUserDepartmentMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    user_department = graphene.Field(UserDepartmentObject)

    class Arguments:
        user_id = graphene.Int(required=True)
        department_id = graphene.Int(required=True)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if user already exists by email
        user = await models.User.filter(id=kwargs.get("user_id")).first()
        if not user:
            return AddUserDepartmentMutation(
                success=False, message="User does not exist"
            )

        # check if department already exists by name
        department = await models.Department.filter(
            id=kwargs.get("department_id")
        ).first()
        if not department:
            return AddUserDepartmentMutation(
                success=False, message="Department does not exist"
            )

        # check if user department already exists
        user_department = await models.UserDepartment.filter(
            user_id=kwargs.get("user_id"), department_id=kwargs.get("department_id")
        ).first()
        if user_department:
            return AddUserDepartmentMutation(
                success=False, message="User Department already exists"
            )

        # create user department
        user_department = await models.UserDepartment.create(
            user_id=kwargs.get("user_id"), department_id=kwargs.get("department_id")
        )

        return AddUserDepartmentMutation(
            success=True,
            message="User Department created successfully",
            user_department=user_department,
        )


class RemoveUserDepartmentMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    user_department = graphene.Field(UserDepartmentObject)

    class Arguments:
        user_id = graphene.Int(required=True)
        department_id = graphene.Int(required=True)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if user already exists by email
        user = await models.User.filter(id=kwargs.get("user_id")).first()
        if not user:
            return RemoveUserDepartmentMutation(
                success=False, message="User does not exist"
            )

        # check if department already exists by name
        department = await models.Department.filter(
            id=kwargs.get("department_id")
        ).first()
        if not department:
            return RemoveUserDepartmentMutation(
                success=False, message="Department does not exist"
            )

        # check if user department already exists
        user_department = await models.UserDepartment.filter(
            user_id=kwargs.get("user_id"), department_id=kwargs.get("department_id")
        ).first()
        if not user_department:
            return RemoveUserDepartmentMutation(
                success=False, message="User Department does not exist"
            )

        # remove user department
        user_department = await models.UserDepartment.filter(
            user_id=kwargs.get("user_id"), department_id=kwargs.get("department_id")
        ).delete()

        return RemoveUserDepartmentMutation(
            success=True,
            message="User Department removed successfully",
            user_department=user_department,
        )


class CreateVenueMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    venue = graphene.Field(VenueObject)

    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=False)
        capacity = graphene.Int(required=False)
        venue_type = graphene.String(required=True)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if venue already exists
        venue = await models.Venue.filter(name__iexact=kwargs.get("name")).first()
        if venue:
            return CreateVenueMutation(success=False, message="Venue already exists")
        venue = await models.Venue.create(**kwargs)
        return CreateVenueMutation(
            success=True, message="Venue created successfully", venue=venue
        )


class UpdateVenueMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    venue = graphene.Field(VenueObject)

    class Arguments:
        id = graphene.Int(required=True, description="Venue ID")
        name = graphene.String(required=True, description="Venue Name")
        description = graphene.String(required=False, description="Venue Description")
        capacity = graphene.Int(required=True, description="Venue Capacity")
        venue_type = graphene.String(required=True)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if venue already exists
        venue = await models.Venue.filter(id=kwargs.get("id")).first()
        if not venue:
            return UpdateVenueMutation(success=False, message="Venue does not exist")
        kwargs_copy = kwargs.copy()
        try:
            kwargs_copy.pop("id")
        except:
            pass
        venue = await models.Venue.filter(id=kwargs.get("id")).update(**kwargs_copy)
        return UpdateVenueMutation(
            success=True, message="Venue updated successfully", venue=await models.Venue.get(id=kwargs.get("id"))
        )


class DeleteVenueMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    venue = graphene.Field(VenueObject)

    class Arguments:
        id = graphene.Int(required=True, description="Venue ID")

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if venue already exists
        venue = await models.Venue.filter(id=kwargs.get("id")).first()
        if not venue:
            return DeleteVenueMutation(success=False, message="Venue does not exist")
        venue = await models.Venue.filter(id=kwargs.get("id")).delete()
        return DeleteVenueMutation(
            success=True, message="Venue deleted successfully", venue=venue
        )


class BlockVenueMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    venue = graphene.Field(VenueObject)

    class Arguments:
        id = graphene.Int(required=True, description="Venue ID")

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if venue already exists
        venue = await models.Venue.filter(id=kwargs.get("id")).first()
        if not venue:
            return BlockVenueMutation(success=False, message="Venue does not exist")
        venue = await models.Venue.filter(id=kwargs.get("id")).update(is_active=False)
        return BlockVenueMutation(
            success=True, message="Venue blocked successfully", venue=venue
        )


class UnblockVenueMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    venue = graphene.Field(VenueObject)

    class Arguments:
        id = graphene.Int(required=True, description="Venue ID")

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if venue already exists
        venue = await models.Venue.filter(id=kwargs.get("id")).first()
        if not venue:
            return UnblockVenueMutation(success=False, message="Venue does not exist")
        venue = await models.Venue.filter(id=kwargs.get("id")).update(is_active=True)
        return UnblockVenueMutation(
            success=True, message="Venue unblocked successfully", venue=venue
        )


class CreateEventMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    event = graphene.Field(EventObject)

    class Arguments:
        title = graphene.String(required=True, description="Event Title")
        description = graphene.String(description="Event Description")
        event_type = graphene.String(required=True, description="Event Type")
        start_time = graphene.String(required=True, description="Event Start Time")
        end_time = graphene.String(required=False, description="Event End Time")
        duration = graphene.Int(required=False, description="Event Duration")
        duration_type = graphene.String(required=False, description="Event Duration Type")
        venue_id = graphene.Int(required=True, description="Event Venue ID")
        departments = graphene.List(graphene.Int, required=False, description="Event Departments")
        committees = graphene.List(graphene.Int, required=False, description="Event Committees")
        financial_year = graphene.String(required=False, description="Event Financial Year")

    @login_required
    async def mutate(self, info, *args, **kwargs):
        print(kwargs)
        # check if venue  exists
        venue = await models.Venue.filter(id=kwargs.get("venue_id")).first()

        if not venue:
            return CreateEventMutation(success=False, message="Venue does not exist")

        start_time = pendulum.parse(kwargs.get("start_time"), strict=False)
        end_time = pendulum.parse(kwargs.get("end_time"), strict=False)

        kwargs["start_time"] = start_time
        kwargs["end_time"] = end_time
        kwargs["author_id"] = info.context["request"].user.id

        # check if venue is available for the event time
        event = await models.Event.filter(
            venue_id=kwargs.get("venue_id"),
            start_time__gte=start_time,
            end_time__lte=end_time,
        ).first()

        if event:
            return CreateEventMutation(
                success=False, message="Venue is not available for the event time"
            )

        event = await models.Event.create(**kwargs)
        
        for department in kwargs.get("departments", []):
            if not await models.EventDepartment.filter(
                department_id=department, event_id=event.id
            ).first():
                await models.EventDepartment.create(
                    event_id=event.id, department_id=department
                )
            
            # get all department users
            department_users = await models.UserDepartment.filter(
                department_id=department
            )
            
            # adding department users to event as attendees
            for department_user in department_users:
                # check if user is already an attendee
                if not await models.EventAttendee.filter(
                    attendee_id=department_user.user_id, event_id=event.id
                ).first():
                    await models.EventAttendee.create(
                        event_id=event.id, attendee_id=department_user.user_id
                    )
            
        
        
        for committee in kwargs.get("committees", []):
            if not await models.EventCommittee.filter(
                committee_id=committee, event_id=event.id
            ).first():
                await models.EventCommittee.create(
                    event_id=event.id, committee_id=committee
                )
            
            # get all committee users
            committee_users = await models.UserCommittee.filter(
                committee_id=committee
            )
            
            for committee_user in committee_users:
                # check if user is already an attendee
                if not await models.EventAttendee.filter(
                    attendee_id=committee_user.user_id, event_id=event.id
                ).first():
                    await models.EventAttendee.create(
                        event_id=event.id, attendee_id=committee_user.user_id
                    )


        return CreateEventMutation(
            success=True, message="Event created successfully", event=event
        )


class DeleteEventMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        id = graphene.Int(required=True, description="Event ID")

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if event already exists
        event = await models.Event.filter(id=kwargs.get("id")).first()
        if not event:
            return DeleteEventMutation(success=False, message="Event does not exist")
        event = await models.Event.filter(id=kwargs.get("id")).delete()
        return DeleteEventMutation(success=True, message="Event deleted successfully")


class UpdateEventMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    event = graphene.Field(EventObject)

    class Arguments:
        id = graphene.Int(required=True, description="Event ID")
        title = graphene.String()
        description = graphene.String()
        event_type = graphene.String()
        start_time = graphene.String()
        end_time = graphene.String()
        venue_id = graphene.Int()

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if event already exists
        event = await models.Event.filter(id=kwargs.get("id")).first()
        if not event:
            return UpdateEventMutation(success=False, message="Event does not exist")

        # check if venue  exists
        venue = await models.Venue.filter(id=kwargs.get("venue_id")).first()

        if not venue:
            return UpdateEventMutation(success=False, message="Venue does not exist")

        # check if venue is available for the event time
        event = await models.Event.filter(
            venue_id=kwargs.get("venue_id"),
            start_time__gte=pendulum.parse(kwargs.get("start_time"), strict=False),
            end_time__lte=pendulum.parse(kwargs.get("end_time"), strict=False),
        ).exclude(
            id=kwargs.get("id")
        ).first()

        if event:
            return UpdateEventMutation(
                success=False, message="Venue is not available for the event time"
            )

        id = kwargs.get("id")
        kwargs.pop("id")
    
        kwargs["start_time"] = pendulum.parse(kwargs.get("start_time"), strict=False)
        kwargs["end_time"] = pendulum.parse(kwargs.get("end_time"), strict=False)
        
        event = await models.Event.filter(id=id).update(**kwargs)
        return UpdateEventMutation(
            success=True, 
            message="Event updated successfully", 
            event=await models.Event.filter(id=id).first()
        )


class AddEventDepartmentMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    event_department = graphene.Field(EventDepartmentObject)

    class Arguments:
        event_id = graphene.Int(required=True)
        department_id = graphene.Int(required=True)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if event already exists by id
        event = await models.Event.filter(id=kwargs.get("event_id")).first()
        if not event:
            return AddEventDepartmentMutation(
                success=False, message="Event does not exist"
            )

        # check if department already exists by id
        department = await models.Department.filter(
            id=kwargs.get("department_id")
        ).first()
        if not department:
            return AddEventDepartmentMutation(
                success=False, message="Department does not exist"
            )

        # check if event department already exists
        event_department = await models.EventDepartment.filter(
            event_id=kwargs.get("event_id"), department_id=kwargs.get("department_id")
        ).first()
        if event_department:
            return AddEventDepartmentMutation(
                success=False, message="Event Department already exists"
            )

        # create event department
        event_department = await models.EventDepartment.create(
            event_id=kwargs.get("event_id"), department_id=kwargs.get("department_id")
        )

        return AddEventDepartmentMutation(
            success=True,
            message="Event Department created successfully",
            event_department=event_department,
        )


class RemoveEventDepartmentMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    event_department = graphene.Field(EventDepartmentObject)

    class Arguments:
        event_id = graphene.Int(required=True)
        department_id = graphene.Int(required=True)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if event already exists by id
        event = await models.Event.filter(id=kwargs.get("event_id")).first()
        if not event:
            return RemoveEventDepartmentMutation(
                success=False, message="Event does not exist"
            )

        # check if department already exists by id
        department = await models.Department.filter(
            id=kwargs.get("department_id")
        ).first()
        if not department:
            return RemoveEventDepartmentMutation(
                success=False, message="Department does not exist"
            )

        # check if event department already exists
        event_department = await models.EventDepartment.filter(
            event_id=kwargs.get("event_id"), department_id=kwargs.get("department_id")
        ).first()
        if not event_department:
            return RemoveEventDepartmentMutation(
                success=False, message="Event Department does not exist"
            )

        # remove event department
        event_department = await models.EventDepartment.filter(
            event_id=kwargs.get("event_id"), department_id=kwargs.get("department_id")
        ).delete()

        return RemoveEventDepartmentMutation(
            success=True,
            message="Event Department removed successfully",
            event_department=event_department,
        )


class AddEventAttendeeMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    event_attendee = graphene.Field(EventAttendeeObject)

    class Arguments:
        event_id = graphene.Int(required=True)
        attendee_id = graphene.Int(required=True)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if event already exists by id
        event = await models.Event.filter(id=kwargs.get("event_id")).first()
        if not event:
            return AddEventAttendeeMutation(
                success=False, message="Event does not exist"
            )

        # check if user already exists by id
        user = await models.User.filter(id=kwargs.get("attendee_id")).first()
        if not user:
            return AddEventAttendeeMutation(
                success=False, message="User does not exist"
            )

        # check if event attendee already exists
        event_attendee = await models.EventAttendee.filter(
            event_id=kwargs.get("event_id"), attendee_id=kwargs.get("attendee_id")
        ).first()
        if event_attendee:
            return AddEventAttendeeMutation(
                success=False, message="Event Attendee already exists"
            )

        # create event attendee
        event_attendee = await models.EventAttendee.create(
            event_id=kwargs.get("event_id"), attendee_id=kwargs.get("attendee_id")
        )

        return AddEventAttendeeMutation(
            success=True,
            message="Event Attendee created successfully",
            event_attendee=event_attendee,
        )


class BulkAddEventAttendeeMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    event_attendee = graphene.Field(EventAttendeeObject)

    class Arguments:
        event_id = graphene.Int(required=True)
        attendee_ids = graphene.List(graphene.Int, required=True)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if event already exists by id
        event = await models.Event.filter(id=kwargs.get("event_id")).first()
        if not event:
            return AddEventAttendeeMutation(
                success=False, message="Event does not exist"
            )

        # check if user already exists by id
        user = await models.User.filter(id__in=kwargs.get("attendee_ids")).first()
        if not user:
            return AddEventAttendeeMutation(
                success=False, message="User does not exist"
            )

        # create event attendee
        added = []
        for attendee_id in kwargs.get("attendee_ids"):
            # check if event attendee already exists
            event_attendee = await models.EventAttendee.filter(
                event_id=kwargs.get("event_id"), attendee_id=attendee_id
            ).exists()
            if not event_attendee:
                event_attendee = await models.EventAttendee.create(
                    event_id=kwargs.get("event_id"), attendee_id=attendee_id
                )
                added.append(event_attendee.id)

        return AddEventAttendeeMutation(
            success=True,
            message="Event Attendee created successfully",
            event_attendee=await models.EventAttendee.filter(id__in=added).all(),
        )


class RemoveEventAttendeeMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    event_attendee = graphene.Field(EventAttendeeObject)

    class Arguments:
        event_id = graphene.Int(required=True)
        attendee_id = graphene.Int(required=True)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if event already exists by id
        event = await models.Event.filter(id=kwargs.get("event_id")).first()
        if not event:
            return RemoveEventAttendeeMutation(
                success=False, message="Event does not exist"
            )

        # check if event attendee already exists
        event_attendee = await models.EventAttendee.filter(
            event_id=kwargs.get("event_id"), id=kwargs.get("attendee_id")
        ).first()
        if not event_attendee:
            return RemoveEventAttendeeMutation(
                success=False, message="Event Attendee does not exist"
            )

        # remove event attendee
        event_attendee = await models.EventAttendee.filter(
            event_id=kwargs.get("event_id"), id=kwargs.get("attendee_id")
        ).delete()

        return RemoveEventAttendeeMutation(
            success=True,
            message="Event Attendee removed successfully",
            event_attendee=event_attendee,
        )


class BulkRemoveEventAttendeeMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        event_id = graphene.Int(required=True)
        attendee_ids = graphene.List(graphene.Int, required=True)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if event already exists by id
        event = await models.Event.filter(id=kwargs.get("event_id")).first()
        if not event:
            return RemoveEventAttendeeMutation(
                success=False, message="Event does not exist"
            )

        # remove event attendee
        for attendee_id in kwargs.get("attendee_ids"):
            event_attendee = await models.EventAttendee.filter(
                event_id=kwargs.get("event_id"), id=attendee_id
            ).delete()

        return RemoveEventAttendeeMutation(
            success=True,
            message="Event Attendees removed successfully",
        )


class CreateEventAgendaMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    event_agenda = graphene.Field(EventAgendaObject)

    class Arguments:
        event_id = graphene.Int(required=True, description="Event ID")
        title = graphene.String(required=True)
        description = graphene.String(required=False)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if event already exists by id
        event = await models.Event.filter(id=kwargs.get("event_id")).first()
        if not event:
            return CreateEventAgendaMutation(
                success=False, message="Event does not exist"
            )

        # check if event agenda already exists
        event_agenda = await models.EventAgenda.filter(
            event_id=kwargs.get("event_id"),
            title__iexact=kwargs.get("title"),
        ).first()
        if event_agenda:
            return CreateEventAgendaMutation(
                success=False, message="Event Agenda already exists"
            )

        # create event agenda
        event_agenda = await models.EventAgenda.create(
            event_id=kwargs.get("event_id"),
            title=kwargs.get("title"),
            description=kwargs.get("description"),
            index=await models.EventAgenda.filter(event_id=kwargs.get("event_id")).count() + 1,
        )

        return CreateEventAgendaMutation(
            success=True,
            message="Event Agenda created successfully",
            event_agenda=await models.EventAgenda.filter(id=event_agenda.id).first(),
        )


class UpdateEventAgendaMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    event_agenda = graphene.Field(EventAgendaObject)

    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String(required=True)
        description = graphene.String(required=True)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if event agenda already exists
        event_agenda = await models.EventAgenda.filter(id=kwargs.get("id")).first()
        if not event_agenda:
            return UpdateEventAgendaMutation(
                success=False, message="Event Agenda does not exist"
            )

        # update event agenda
        event_agenda = await models.EventAgenda.filter(id=kwargs.get("id")).update(
            title=kwargs.get("title"), description=kwargs.get("description")
        )

        return UpdateEventAgendaMutation(
            success=True,
            message="Event Agenda updated successfully",
            event_agenda=await models.EventAgenda.filter(id=kwargs.get("id")).first(),
        )


class DeleteEventAgendaMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        id = graphene.Int(required=True, description="Event Agenda ID")

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if event agenda already exists
        event_agenda = await models.EventAgenda.filter(id=kwargs.get("id")).first()
        if not event_agenda:
            return DeleteEventAgendaMutation(
                success=False, message="Event Agenda does not exist"
            )

        # delete event agenda
        event_agenda = await models.EventAgenda.filter(id=kwargs.get("id")).delete()

        return DeleteEventAgendaMutation(
            success=True, message="Event Agenda deleted successfully"
        )


class CreateEventDocumentMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    event_document = graphene.Field(EventDocumentObject)

    class Arguments:
        event_id = graphene.Int(required=True)
        title = graphene.String(required=True)
        description = graphene.String(required=False)
        file = Upload(required=True)
        department_id = graphene.Int(required=False)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        from services.minio import MinioUploader
        print("=====kwargs: ", kwargs)
        # check if event already exists by id
        event = await models.Event.filter(id=kwargs.get("event_id")).first()
        if not event:
            return CreateEventDocumentMutation(
                success=False, message="Event does not exist"
            )

        # check if event document already exists
        event_document = await models.EventDocument.filter(
            event_id=kwargs.get("event_id"),
            title__iexact=kwargs.get("title"),
        ).first()
        if event_document:
            return CreateEventDocumentMutation(
                success=False, message="Event Document already exists"
            )

        # graphene receive a file and save it in a temporary file
        # we need to read it and upload it to minio
        file = kwargs.get("file")
        # process file of type starlette.datastructures.UploadFile
        file = MinioUploader().upload(file)

        kwargs["file"] = file

        # create event document
        event_document = await models.EventDocument.create(
            event_id=kwargs.get("event_id"),
            title=kwargs.get("title"),
            description=kwargs.get("description"),
            file=kwargs.get("file"),
            author_id=info.context['request'].user.id
        )
        
        
        if kwargs.get("department_id"):
            department_id = kwargs.get("department_id")
            # check if EventDocumentDepartment already exists
            event_document_department = await models.EventDocumentDepartment.filter(
                event_document_id=event_document.id,
                department_id=department_id
            ).first()
            if not event_document_department:
                await models.EventDocumentDepartment.create(
                    event_document_id=event_document.id,
                    department_id=department_id
                )
            # check if event department already exists
            event_department = await models.EventDepartment.filter(
                event_id=kwargs.get("event_id"),
                department_id=department_id,
            ).first()
            if not event_department:
                await models.EventDepartment.create(
                    event_id=kwargs.get("event_id"),
                    department_id=department_id,
                )

        return CreateEventDocumentMutation(
            success=True,
            message="Event Document created successfully",
            event_document=event_document,
        )


class UpdateEventDocumentMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    event_document = graphene.Field(EventDocumentObject)

    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        file = Upload(required=True)

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if event document already exists
        event_document = await models.EventDocument.filter(id=kwargs.get("id")).first()
        if not event_document:
            return UpdateEventDocumentMutation(
                success=False, message="Event Document does not exist"
            )

        # update event document
        event_document = await models.EventDocument.filter(id=kwargs.get("id")).update(
            title=kwargs.get("title"),
            description=kwargs.get("description"),
            file=kwargs.get("file"),
        )

        return UpdateEventDocumentMutation(
            success=True,
            message="Event Document updated successfully",
            event_document=event_document,
        )


class DeleteEventDocumentMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        id = graphene.Int(required=True, description="Event Document ID")

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if event document already exists
        event_document = await models.EventDocument.filter(id=kwargs.get("id")).first()
        if not event_document:
            return DeleteEventDocumentMutation(
                success=False, message="Event Document does not exist"
            )

        # delete event document
        event_document = await models.EventDocument.filter(id=kwargs.get("id")).delete()

        return DeleteEventDocumentMutation(
            success=True, message="Event Document deleted successfully"
        )



class CreateUserCredentialsMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        user_id = graphene.Int(required=True, description="User ID")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        from app.manager import MeetingManager
        # check if user already exists
        user = await models.User.filter(id=kwargs.get("user_id")).first()
        
        if not user:
            return CreateUserCredentialsMutation(success=False, message="User does not exist")
    
        created = await MeetingManager().create_user_credentials(user)
        
        if not created:
            return CreateUserCredentialsMutation(success=False, message="User credentials not created")
        
        return CreateUserCredentialsMutation(success=True, message="User credentials created successfully")


class CreateAllUsersCredentialsMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        pass
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        from app.manager import MeetingManager
        # check if user already exists
        users = await models.User.filter(hash_password__isnull=True, salt_key__isnull=True)
        
        for user in users:
            try:
                await MeetingManager().create_user_credentials(user)
            except:
                pass
        
        return CreateAllUsersCredentialsMutation(success=True, message="User credentials created successfully")




class SyncUsersMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        from app.manager import MeetingManager
        # check if user already exists
        sync = await MeetingManager().sync_users()
        if not sync:
            return SyncUsersMutation(success=False, message="Users not synced")
        
        return SyncUsersMutation(success=True, message="Users synced successfully")



class CreateCommitteeMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    committee = graphene.Field(CommitteeObject)
    
    class Arguments:
        name = graphene.String(required=True, description="Committee Name")
        description = graphene.String(required=True, description="Committee Description")
    
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if committee already exists
        committee = await models.Committee.filter(name__iexact=kwargs.get("name")).first()
        if committee:
            return CreateCommitteeMutation(success=False, message="Committee already exists")
        committee = await models.Committee.create(**kwargs)
        return CreateCommitteeMutation(
            success=True, message="Committee created successfully", committee=committee
        )


class UpdateCommitteeMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    committee = graphene.Field(CommitteeObject)
    
    class Arguments:
        id = graphene.Int(required=True, description="Committee ID")
        name = graphene.String(required=True, description="Committee Name")
        description = graphene.String(required=True, description="Committee Description")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if committee already exists
        committee = await models.Committee.filter(id=kwargs.get("id")).first()
        if not committee:
            return UpdateCommitteeMutation(success=False, message="Committee does not exist")
        
        
        # check if name is already taken  excluding the current committee
        if await models.Committee.filter(name__iexact=kwargs.get("name")).exclude(id=kwargs.get("id")).exists():
            return UpdateCommitteeMutation(success=False, message="Committee name already taken")
        
        kwargs_copy = kwargs.copy()
        try:
            kwargs_copy.pop("id")
        except:
            pass
        committee = await models.Committee.filter(id=kwargs.get("id")).update(**kwargs_copy)
        return UpdateCommitteeMutation(
            success=True, message="Committee updated successfully", committee=await models.Committee.filter(id=kwargs.get("id")).first()
        )


class DeleteCommitteeMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        id = graphene.Int(required=True, description="Committee ID")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if committee already exists
        committee = await models.Committee.filter(id=kwargs.get("id")).first()
        if not committee:
            return DeleteCommitteeMutation(success=False, message="Committee does not exist")
        committee = await models.Committee.filter(id=kwargs.get("id")).delete()
        return DeleteCommitteeMutation(success=True, message="Committee deleted successfully")


class BlockUnblockCommitteeMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    committee = graphene.Field(CommitteeObject)
    
    class Arguments:
        id = graphene.Int(required=True, description="Committee ID")
        block = graphene.Boolean(required=True, description="Block Committee")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if committee already exists
        committee = await models.Committee.filter(id=kwargs.get("id")).first()
        if not committee:
            return BlockUnblockCommitteeMutation(success=False, message="Committee does not exist")
        committee = await models.Committee.filter(id=kwargs.get("id")).update(is_active=kwargs.get("block"))
        return BlockUnblockCommitteeMutation(success=True, message="Committee blocked successfully", committee=committee)



class BlockCommitteeMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    committee = graphene.Field(CommitteeObject)
    
    class Arguments:
        id = graphene.Int(required=True, description="Committee ID")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if committee already exists
        committee = await models.Committee.filter(id=kwargs.get("id")).first()
        if not committee:
            return BlockCommitteeMutation(success=False, message="Committee does not exist")
        committee = await models.Committee.filter(id=kwargs.get("id")).update(is_active=False)
        return BlockCommitteeMutation(success=True, message="Committee blocked successfully", committee=committee)


class UnblockCommitteeMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    committee = graphene.Field(CommitteeObject)
    
    class Arguments:
        id = graphene.Int(required=True, description="Committee ID")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if committee already exists
        committee = await models.Committee.filter(id=kwargs.get("id")).first()
        if not committee:
            return UnblockCommitteeMutation(success=False, message="Committee does not exist")
        committee = await models.Committee.filter(id=kwargs.get("id")).update(is_active=True)
        return UnblockCommitteeMutation(success=True, message="Committee unblocked successfully", committee=committee)


class AddCommitteeMemberMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    committee_member = graphene.Field(userCommitteeObject)
    
    class Arguments:
        committee_id = graphene.Int(required=True, description="Committee ID")
        user_id = graphene.Int(required=True, description="User ID")
    
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if committee already exists
        if not await models.Committee.filter(id=kwargs.get("committee_id")).exists():
            return AddCommitteeMemberMutation(success=False, message="Committee does not exist")
        
        # check if user already exists
        if not await models.User.filter(id=kwargs.get("user_id")).exists():
            return AddCommitteeMemberMutation(success=False, message="User does not exist")
        
        # check if committee member already exists
        if await models.UserCommittee.filter(committee_id=kwargs.get("committee_id"), user_id=kwargs.get("user_id")).exists():
            return AddCommitteeMemberMutation(success=False, message="Committee Member already exists")
        
        user_committee = await models.UserCommittee.create(committee_id=kwargs.get("committee_id"), user_id=kwargs.get("user_id"))
        
        return AddCommitteeMemberMutation(
            success=True, message="Committee Member created successfully", committee_member=user_committee)
    
class DeleteCommitteeMemberMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        id = graphene.Int(required=True, description="Committee Member ID")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if committee member already exists
        if not await models.UserCommittee.filter(id=kwargs.get("id")).exists():
            return DeleteCommitteeMemberMutation(success=False, message="Committee Member does not exist")
        
        user_committee = await models.UserCommittee.filter(id=kwargs.get("id")).delete()
        
        return DeleteCommitteeMemberMutation(success=True, message="Committee Member deleted successfully")



class ForgotPasswordMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        email = graphene.String(required=True, description="User Email")
    
    async def mutate(self, info, *args, **kwargs):
        # sanitize email
        email = kwargs.get("email").strip().lower()
        
        # check if user already exists
        if not await models.User.filter(email__iexact=email).exists():
            return ForgotPasswordMutation(success=False, message=f"User with email {email} does not exist")
        
        # get user 
        user = await models.User.filter(email__iexact=email).first()
        
        # check if user has a phone number
        if not user.phone:
            return ForgotPasswordMutation(success=False, message=f"User with email {email} does not have a phone number, please contact System Administrator for assistance")
        
        sent = await MeetingManager().send_user_recovery_token(user)
        
        if sent:
            return ForgotPasswordMutation(success=True, message=f"Recovery token sent to {user.phone}")
        
        return ForgotPasswordMutation(success=False, message=f"Recovery token not sent")
        


class VerifyOtpMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        email = graphene.String(required=True, description="User Email")
        otp = graphene.String(required=True, description="OTP")
    
    async def mutate(self, info, *args, **kwargs):
        # sanitize email 
        email = kwargs.get("email").strip().lower()
        # check if user already exists
        if not models.User.filter(email__iexact=email).exists():
            return VerifyOtpMutation(success=False, message=f"User with email {email} does not exist")
        
        user = await models.User.filter(email__iexact=email).first()
        
        # sanitize otp 
        otp = kwargs.get("otp").strip()
        # check if user otp is valid 
        user_otp = await models.UserOTP.filter(user_id=user.id, token=otp, is_used=False).first()
        
        if not user_otp:
            return VerifyOtpMutation(success=False, message=f"Invalid OTP or OTP already used")
        
        return VerifyOtpMutation(success=True, message=f"OTP verified successfully")


class UserChangePasswordMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        email = graphene.String(required=True, description="User Email")
        otp = graphene.String(required=True, description="OTP")
        password = graphene.String(required=True, description="New Password")
        confirm_password = graphene.String(required=True, description="Confirm Password")
    
    async def mutate(self, info, *args, **kwargs):
        print(kwargs)
        
        # sanitize email
        email = kwargs.get("email").strip().lower()
        
        # check if user exists by email 
        if not models.User.filter(email__iexact=email).exists():
            return UserChangePasswordMutation(success=False, message=f"User with email {email} does not exist")
        
        user = await models.User.filter(email__iexact=email).first()
        
        # check if user otp is valid and not used 
        user_otp = await models.UserOTP.filter(user_id=user.id, token=kwargs.get("otp"), is_used=False).first()
        
        if not user_otp:
            return UserChangePasswordMutation(success=False, message=f"Invalid OTP or OTP already used")
        
        # check if password and confirm password match
        if kwargs.get("password") != kwargs.get("confirm_password"):
            return UserChangePasswordMutation(success=False, message=f"Password and Confirm Password do not match")
        
        changed = await MeetingManager().change_user_password(user, kwargs.get("password"))
        
        if not changed:
            return UserChangePasswordMutation(success=False, message=f"Password not changed")
        
        
        # update user otp to used
        await models.UserOTP.filter(user_id=user.id, token=kwargs.get("otp")).update(is_used=True)
        
        return UserChangePasswordMutation(success=True, message=f"Password changed successfully")


class AddCommitteDepartmentMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    committee_department = graphene.Field(CommitteeDepartmentObject)
    
    class Arguments:
        committee_id = graphene.Int(required=True, description="Committee ID")
        department_id = graphene.Int(required=True, description="Department ID")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if committee exists
        if not await models.Committee.filter(id=kwargs.get("committee_id")).exists():
            return AddCommitteDepartmentMutation(success=False, message="Committee does not exist")
        
        # check if department exists
        if not await models.Department.filter(id=kwargs.get("department_id")).exists():
            return AddCommitteDepartmentMutation(success=False, message="Department does not exist")
        
        # check if committee department already exists
        if await models.CommitteeDepartment.filter(committee_id=kwargs.get("committee_id"), department_id=kwargs.get("department_id")).exists():
            return AddCommitteDepartmentMutation(success=False, message="Committee Department already exists")
        
        # create committee department
        committee_department = await models.CommitteeDepartment.create(committee_id=kwargs.get("committee_id"), department_id=kwargs.get("department_id"))
        
        return AddCommitteDepartmentMutation(success=True, message="Committee Department added successfully", committee_department=committee_department)


class RemoveCommitteDepartmentMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        committee_id = graphene.Int(required=True, description="Committee ID")
        department_id = graphene.Int(required=True, description="Department ID")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if committee exists
        if not await models.Committee.filter(id=kwargs.get("committee_id")).exists():
            return RemoveCommitteDepartmentMutation(success=False, message="Committee does not exist")
        
        # check if department exists
        if not await models.Department.filter(id=kwargs.get("department_id")).exists():
            return RemoveCommitteDepartmentMutation(success=False, message="Department does not exist")
        
        # check if committee department already exists
        if not await models.CommitteeDepartment.filter(committee_id=kwargs.get("committee_id"), department_id=kwargs.get("department_id")).exists():
            return RemoveCommitteDepartmentMutation(success=False, message="Committee Department does not exist")
        
        # delete committee department
        await models.CommitteeDepartment.filter(committee_id=kwargs.get("committee_id"), department_id=kwargs.get("department_id")).delete()
        
        return RemoveCommitteDepartmentMutation(success=True, message="Committee Department removed successfully")        



class CreateEventDocumentNoteMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    event_document_note = graphene.Field(EventUserDocumentNoteObject)
    event_document = graphene.Field(EventDocumentObject)
    
    class Arguments:
        document_id = graphene.Int(required=True, description="Document ID")
        note = graphene.String(required=True, description="Note")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if document exists
        if not await models.EventDocument.filter(id=kwargs.get("document_id")).exists():
            return CreateEventDocumentNoteMutation(success=False, message="Document does not exist")
        
        if await models.EventUserDocumentNote.filter(event_document_id=kwargs.get("document_id"), user_id=info.context['request'].user.id).exists():
            await models.EventUserDocumentNote.filter(event_document_id=kwargs.get("document_id"), user_id=info.context['request'].user.id).update(
                note=kwargs.get("note")
            )
        else:
            # create document note
            await models.EventUserDocumentNote.create(event_document_id=kwargs.get("document_id"), user_id=info.context['request'].user.id, note=kwargs.get("note"))
    
        
        return CreateEventDocumentNoteMutation(success=True, 
                                               message="Document Note added successfully", 
                                               event_document_note=await models.EventUserDocumentNote.filter(event_document_id=kwargs.get("document_id"), user_id=info.context['request'].user.id).first(),
                                               event_document=await models.EventDocument.filter(id=kwargs.get("document_id")).first())



class AddEventCommitteeMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    event_committee = graphene.Field(EventCommitteeObject)
    
    class Arguments:
        event_id = graphene.Int(required=True, description="Event ID")
        committee_id = graphene.Int(required=True, description="Committee ID")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if event exists
        if not await models.Event.filter(id=kwargs.get("event_id")).exists():
            return AddEventCommitteeMutation(success=False, message="Event does not exist")
        
        # check if committee exists
        if not await models.Committee.filter(id=kwargs.get("committee_id")).exists():
            return AddEventCommitteeMutation(success=False, message="Committee does not exist")
        
        # check if event committee already exists
        if await models.EventCommittee.filter(event_id=kwargs.get("event_id"), committee_id=kwargs.get("committee_id")).exists():
            return AddEventCommitteeMutation(success=False, message="Event Committee already exists")
        
        # create event committee
        await models.EventCommittee.create(
            event_id=kwargs.get("event_id"), 
            committee_id=kwargs.get("committee_id"))
        
        return AddEventCommitteeMutation(
            success=True, 
            message="Event Committee added successfully", 
            event_committee=await models.EventCommittee.filter(
                event_id=kwargs.get("event_id"),
                committee_id=kwargs.get("committee_id")
            ).first())



class DeleteEventCommitteeMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        event_id = graphene.Int(required=True, description="Event ID")
        committee_id = graphene.Int(required=True, description="Committee ID")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if event exists
        if not await models.Event.filter(id=kwargs.get("event_id")).exists():
            return DeleteEventCommitteeMutation(success=False, message="Event does not exist")
        
        # check if committee exists
        if not await models.Committee.filter(id=kwargs.get("committee_id")).exists():
            return DeleteEventCommitteeMutation(success=False, message="Committee does not exist")
        
        # check if event committee already exists
        if not await models.EventCommittee.filter(event_id=kwargs.get("event_id"), committee_id=kwargs.get("committee_id")).exists():
            return DeleteEventCommitteeMutation(success=False, message="Event Committee does not exist")
        
        # delete event committee
        await models.EventCommittee.filter(event_id=kwargs.get("event_id"), committee_id=kwargs.get("committee_id")).delete()
        
        return DeleteEventCommitteeMutation(success=True, message="Event Committee removed successfully")


class SendMeetingInvitationSmsAllAttendees(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        event_id = graphene.Int(required=True, description="Event ID")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        event = await models.Event.filter(id=kwargs.get("event_id")).first()
        if not event:
            return SendMeetingInvitationSmsAllAttendees(success=False, message="Event does not exist")
        
        manager = await MeetingManager().send_all_meeting_attendee_invitation(event)
        
        if not manager:
            return SendMeetingInvitationSmsAllAttendees(success=False, message="SMS not sent")
    
        return SendMeetingInvitationSmsAllAttendees(success=True, message="SMS sent successfully")


class SendMeetingInvitationAttendee(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        event_id = graphene.Int(required=True, description="Event ID")
        attendee_id = graphene.Int(required=True, description="Attendee ID")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        event = await models.Event.filter(id=kwargs.get("event_id")).first()
        attendee = await models.EventAttendee.filter(id=kwargs.get("attendee_id")).first()
        if event and attendee:
            manager = await MeetingManager().send_meeting_attendee_invitation(
                event,
                attendee
            )
            if manager:
                return SendMeetingInvitationAttendee(success=True, message="SMS sent successfully")
        return SendMeetingInvitationAttendee(success=False, message="SMS not sent")


class CreateEventMinuteMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    event_minute = graphene.Field(EventMinuteObject)
    
    class Arguments:
        event_id = graphene.Int(required=True, description="Event ID")
        content = graphene.String(required=True, description="Content")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        #check if event exists
        if not await models.Event.filter(id=kwargs.get("event_id")).exists():
            return CreateEventMinuteMutation(success=False, message="Event does not exist")
    
    
        # check if event minute by content already exists 
        if await models.EventMinute.filter(event_id=kwargs.get("event_id"), content__iexact=kwargs.get("content")).exists():
            return CreateEventMinuteMutation(success=False, message="Event Minute already exists")
    
        # create event minute
        event_minute = await models.EventMinute.create(
            event_id=kwargs.get("event_id"), 
            content=kwargs.get("content"),
            author_id=info.context['request'].user.id,
            index=await models.EventMinute.filter(event_id=kwargs.get("event_id")).count()+1
        )
    
        return CreateEventMinuteMutation(success=True, message="Event Minute created successfully", event_minute=event_minute)


class UpdateEventMinuteMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    event_minute = graphene.Field(EventMinuteObject)
    
    class Arguments:
        id = graphene.Int(required=True, description="Event Minute ID")
        content = graphene.String(required=True, description="Content")
        index = graphene.Int(required=True, description="Index")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        #check if event minute exists
        if not await models.EventMinute.filter(id=kwargs.get("id")).exists():
            return UpdateEventMinuteMutation(success=False, message="Event Minute does not exist")
        
        event_minute = await models.EventMinute.filter(id=kwargs.get("id")).first()
        
        # check if event minute already exists
        if await models.EventMinute.filter(event_id=event_minute.event_id,index=kwargs.get("index")).exclude(id=kwargs.get("id")).exists():
            return UpdateEventMinuteMutation(success=False, message="Event Minute already exists")
        
        #check if event minute already exists by content
        if await models.EventMinute.filter(event_id=event_minute.event_id,content__iexact=kwargs.get("content")).exclude(id=kwargs.get("id")).exists():
            return UpdateEventMinuteMutation(success=False, message="Event Minute already exists")
    
        kwargs_copy = kwargs.copy()
        try:
            kwargs_copy.pop("id")
        except:
            pass
        
        # update event minute
        event_minute = await models.EventMinute.filter(id=kwargs.get("id")).update(**kwargs_copy)
        
        return UpdateEventMinuteMutation(success=True, message="Event Minute updated successfully", event_minute=await models.EventMinute.filter(id=kwargs.get("id")).first())



class DeleteEventMinuteMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        id = graphene.Int(required=True, description="Event Minute ID")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        #check if event minute exists
        if not await models.EventMinute.filter(id=kwargs.get("id")).exists():
            return DeleteEventMinuteMutation(success=False, message="Event Minute does not exist")
    
        # delete event minute
        await models.EventMinute.filter(id=kwargs.get("id")).delete()
        
        return DeleteEventMinuteMutation(success=True, message="Event Minute deleted successfully")


class AddDocumentManagerMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        id = graphene.Int(required=True, description="Attendee Id")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if attendee exists
        if not await models.EventAttendee.filter(id=kwargs.get("id")).exists():
            return AddDocumentManagerMutation(success=False, message="Attendee does not exist")
        
        # update attendee can upload 
        await models.EventAttendee.filter(id=kwargs.get("id")).update(can_upload=True)
        return AddDocumentManagerMutation(success=True, message="Attendee can upload successfully")


class RemoveDocumentManagerMutation(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        id = graphene.Int(required=True, description="Attendee Id")
    
    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if attendee exists
        if not await models.EventAttendee.filter(id=kwargs.get("id")).exists():
            return RemoveDocumentManagerMutation(success=False, message="Attendee does not exist")
        
        # update attendee can upload 
        await models.EventAttendee.filter(id=kwargs.get("id")).update(can_upload=False)
        return RemoveDocumentManagerMutation(success=True, message="Attendee can upload successfully")



class Subscription(graphene.ObjectType):
    count = graphene.Int(upto=graphene.Int())

    async def subscribe_count(root, info, upto=3):
        # for i in range(upto):
        #     yield i
        #     await asyncio.sleep(1)
        pass


class Mutation(graphene.ObjectType):
    auth = AuthMutation.Field()
    register = CreateUserMutation.Field()

    create_department = CreateDepartmentMutation.Field()
    update_department = UpdateDepartmentMutation.Field()
    delete_department = DeleteDepartmentMutation.Field()
    block_department = BlockDepartmentMutation.Field()
    unblock_department = UnblockDepartmentMutation.Field()
    
    create_directorate = CreateDepartmentMutation.Field()
    update_directorate = UpdateDepartmentMutation.Field()
    delete_directorate = DeleteDepartmentMutation.Field()
    block_directorate = BlockDepartmentMutation.Field()
    unblock_directorate = UnblockDepartmentMutation.Field()

    create_user = CreateUserMutation.Field()
    update_user = UpdateUserMutation.Field()
    delete_user = DeleteUserMutation.Field()
    block_user = BlockUserMutation.Field()
    unblock_user = UnblockUserMutation.Field()

    add_user_department = AddUserDepartmentMutation.Field()
    remove_user_department = RemoveUserDepartmentMutation.Field()

    create_venue = CreateVenueMutation.Field()
    update_venue = UpdateVenueMutation.Field()
    delete_venue = DeleteVenueMutation.Field()
    block_venue = BlockVenueMutation.Field()
    unblock_venue = UnblockVenueMutation.Field()

    create_event = CreateEventMutation.Field()
    delete_event = DeleteEventMutation.Field()
    update_event = UpdateEventMutation.Field()

    add_event_department = AddEventDepartmentMutation.Field()
    remove_event_department = RemoveEventDepartmentMutation.Field()

    add_event_attendee = AddEventAttendeeMutation.Field()
    bulk_add_event_attendees = BulkAddEventAttendeeMutation.Field()
    remove_event_attendee = RemoveEventAttendeeMutation.Field()
    bulk_remove_event_attendees = BulkRemoveEventAttendeeMutation.Field()

    create_event_agenda = CreateEventAgendaMutation.Field()
    update_event_agenda = UpdateEventAgendaMutation.Field()
    delete_event_agenda = DeleteEventAgendaMutation.Field()

    create_event_document = CreateEventDocumentMutation.Field()
    update_event_document = UpdateEventDocumentMutation.Field()
    delete_event_document = DeleteEventDocumentMutation.Field()
    
    create_user_credentials = CreateUserCredentialsMutation.Field()
    create_all_user_credentials = CreateAllUsersCredentialsMutation.Field()
    sync_users = SyncUsersMutation.Field()
    
    create_committee = CreateCommitteeMutation.Field()
    update_committee = UpdateCommitteeMutation.Field()
    delete_committee = DeleteCommitteeMutation.Field()
    block_unblock_committee = BlockUnblockCommitteeMutation.Field()
    block_committee = BlockCommitteeMutation.Field()
    unblock_committee = UnblockCommitteeMutation.Field()
    
    add_committee_member = AddCommitteeMemberMutation.Field()
    delete_committee_member = DeleteCommitteeMemberMutation.Field()
    
    forgot_password = ForgotPasswordMutation.Field()
    verify_otp = VerifyOtpMutation.Field()
    user_change_password = UserChangePasswordMutation.Field()
    
    add_committee_department = AddCommitteDepartmentMutation.Field()
    remove_committee_department = RemoveCommitteDepartmentMutation.Field()
    
    create_document_user_note = CreateEventDocumentNoteMutation.Field()
    
    add_event_committee = AddEventCommitteeMutation.Field()
    delete_event_committee = DeleteEventCommitteeMutation.Field()
    
    send_meeting_invitation_sms_all_attendees = SendMeetingInvitationSmsAllAttendees.Field()
    send_meeting_invitation_attendee = SendMeetingInvitationAttendee.Field()
    
    create_event_minute = CreateEventMinuteMutation.Field()
    update_event_minute = UpdateEventMinuteMutation.Field()
    add_document_manager = AddDocumentManagerMutation.Field()
    remove_document_manager = RemoveDocumentManagerMutation.Field()
