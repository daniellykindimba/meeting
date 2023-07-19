from phonenumbers import carrier
import phonenumbers
from phonenumbers.phonenumberutil import number_type


class PhoneValidator:
    is_valid = True
    national_formatted_phone_number = None
    international_formatted_phone_number = None

    def __init__(self, phone, code="TZ"):
        self.phone = phone
        self.code = code

    def validate(self):
        '''Validating Phone Number, 
        the function returns a boolean, 
        :return: True if phone is valid
        :return: False if Phone is not valid
        '''

        try:
            z = phonenumbers.parse(self.phone, self.code)
            ro_number_international = phonenumbers.format_number(
                z, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            is_mobile = carrier._is_mobile(
                number_type(phonenumbers.parse(ro_number_international)))
            if not phonenumbers.is_possible_number(z):
                self.is_valid = False
            if not is_mobile:
                self.is_valid = False
        except:
            self.is_valid = False
        return self.is_valid

    def getCarrierName(self):
        '''A function for retrieving the carrier name of the mobile phone number
        supplied. i.e. Tigo, Voda e.t.c 
        '''

        ro_number = phonenumbers.parse(self.phone, self.code)
        name = carrier.name_for_number(ro_number, "en")
        return name

    def national_format(self):
        '''A function for formatting the mobile phone number in National Standard'''

        phone_parse = phonenumbers.parse(self.phone, self.code)
        self.national_formatted_phone_number = phonenumbers.format_number(
            phone_parse, phonenumbers.PhoneNumberFormat.NATIONAL)
        return str(self.national_formatted_phone_number).replace(" ",
                                                                 "").replace(
                                                                     "+", "")

    def international_format_plain(self):
        '''A function for formatting the mobile phone number in International Standard without plus(+) sign'''

        phone_parse = phonenumbers.parse(self.phone, self.code)
        self.international_formatted_phone_number = phonenumbers.format_number(
            phone_parse, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        return str(self.international_formatted_phone_number).replace(" ", "")

    def international_format(self):
        '''A function for formatting the mobile phone number in International Standard without plus(+) sign'''
        phone_parse = phonenumbers.parse(self.phone, self.code)
        self.international_formatted_phone_number = phonenumbers.format_number(
            phone_parse, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        return str(self.international_formatted_phone_number).replace(
            " ", "").replace("+", "")
