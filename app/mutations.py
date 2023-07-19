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

        if not user.is_active:
            message = "Authentication Failed, Your account has been deactivated"
            return AuthMutation(success=False, message=message)

        hashed = bcrypt.hashpw(
            kwargs.get("password").encode("utf-8"), user.salt_key.encode("utf-8")
        )

        # check if user.hash_password is string or bytes and convert to string
        hash_password = user.hash_password
        if isinstance(hash_password, bytes):
            hash_password = hash_password.decode("utf-8")

        if not any(
            (
                hash_password == hashed.decode("utf-8"),
                str(user.hash_password) == hashed.decode("utf-8"),
            )
        ):
            message = "Authentication Failed, Invalid Password"
            return AuthMutation(success=False, message=message)

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
                success=False, message="Department already exists"
            )
        department = await models.Department.create(**kwargs)
        return CreateDepartmentMutation(
            success=True,
            message="Department created successfully",
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
            required=True, description="Department Description"
        )

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if department already exists
        department = await models.Department.filter(id=kwargs.get("id")).first()
        if not department:
            return UpdateDepartmentMutation(
                success=False, message="Department does not exist"
            )
        department = await models.Department.filter(id=kwargs.get("id")).update(
            **kwargs
        )
        return UpdateDepartmentMutation(
            success=True,
            message="Department updated successfully",
            department=department,
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
                success=False, message="Department does not exist"
            )
        department = await models.Department.filter(id=kwargs.get("id")).delete()
        return DeleteDepartmentMutation(
            success=True,
            message="Department deleted successfully",
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
        description = graphene.String(required=True)
        capacity = graphene.Int(required=True)
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
        description = graphene.String(required=True, description="Venue Description")
        capacity = graphene.Int(required=True, description="Venue Capacity")

    @login_required
    async def mutate(self, info, *args, **kwargs):
        # check if venue already exists
        venue = await models.Venue.filter(id=kwargs.get("id")).first()
        if not venue:
            return UpdateVenueMutation(success=False, message="Venue does not exist")
        venue = await models.Venue.filter(id=kwargs.get("id")).update(**kwargs)
        return UpdateVenueMutation(
            success=True, message="Venue updated successfully", venue=venue
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
        title = graphene.String()
        description = graphene.String()
        event_type = graphene.String()
        start_time = graphene.String()
        end_time = graphene.String()
        venue_id = graphene.Int()

    @login_required
    async def mutate(self, info, *args, **kwargs):
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
        start_time = graphene.DateTime()
        end_time = graphene.DateTime()
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
            start_time__gte=kwargs.get("start_time"),
            end_time__lte=kwargs.get("end_time"),
        ).first()

        if event:
            return UpdateEventMutation(
                success=False, message="Venue is not available for the event time"
            )

        event = await models.Event.filter(id=kwargs.get("id")).update(**kwargs)
        return UpdateEventMutation(
            success=True, message="Event updated successfully", event=event
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
        event_id = graphene.Int(required=True)
        title = graphene.String(required=True)
        description = graphene.String(required=True)

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
        )

        return CreateEventAgendaMutation(
            success=True,
            message="Event Agenda created successfully",
            event_agenda=event_agenda,
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
            event_agenda=event_agenda,
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
        file = kwargs.get("file")['file']
        # process file of type starlette.datastructures.UploadFile
        file = MinioUploader().upload(file)

        kwargs["file"] = file

        # create event document
        event_document = await models.EventDocument.create(
            event_id=kwargs.get("event_id"),
            title=kwargs.get("title"),
            description=kwargs.get("description"),
            file=kwargs.get("file"),
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
