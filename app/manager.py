from services.sms import SMS
from app.validators.phone_validator import PhoneValidator
from app.models import User
import random
import string
import bcrypt
import json


class MeetingManager:
    def __init__(self):
        pass
    
    
    async def generate_random_password(self, n=6):
        password = ''.join(random.choices(string.ascii_uppercase + string.digits, k = n))
        return password
    
    async def create_user_credentials(self, user):
        password = await self.generate_random_password()
        client_name = f"{user.first_name} {user.middle_name} {user.last_name}"
        message = f"""
        {client_name}, Welcome to the Meeting App.
        your Credentials
        Username:{user.email} , Password:{password}
        """
        to = user.phone
        
        # check if phone number is valid 
        validate_phone = PhoneValidator(to)
        if validate_phone.validate():
            
            # update user password
            salt_key = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode("utf-8"), salt_key)
            updated = await User.filter(id=user.id).update(hash_password=hashed.decode("utf-8"), salt_key=salt_key.decode("utf-8"))
            if updated:
                sms = SMS()
                to = validate_phone.international_format()
                await sms.send(to, message, client_name)
        
        return True

    
    async def sync_users(self):
        # get all users from json file
        # create users in the database
        
        users_json = open("users.json", "r")
        
        users = json.load(users_json)
        
        for user in users:
            first_name = user["first_name"]
            middle_name = user["middle_name"]
            last_name = user["last_name"]
            email = user["email"]
            phone = user["phone"]
            
            # check if user exists in the database by email 
            user_exists = await User.filter(email=email).first()
            
            if not user_exists:
                # check if phone number is valid
                validate_phone = PhoneValidator(phone)
                
                if validate_phone.validate():
                    phone = validate_phone.international_format()
                    await User.create(
                        first_name=first_name,
                        middle_name=middle_name,
                        last_name=last_name,
                        email=email,
                        username=email,
                        phone=phone
                    )
            else:
                # check if phone number is valid
                validate_phone = PhoneValidator(phone)
                
                if validate_phone.validate():
                    phone = validate_phone.international_format()
                    await User.filter(id=user_exists.id).update(
                        first_name=first_name,
                        middle_name=middle_name,
                        last_name=last_name,
                        email=email,
                        username=email,
                        phone=phone
                    )
        return True
        
        
        
        
        