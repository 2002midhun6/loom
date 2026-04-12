import re
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from . models import *


class Authentication_check:
    def email_validator(self,email):
        if not re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?$', email):
            return 'Email should be valid!'
        return None
    def username_validator(self, username):
        if len(username) < 4:
            return 'Username must be at least 4 characters long'
        if len(username) > 30:
            return 'Username cannot be more than 30 characters'
        
        
        if not re.match(r'^[a-zA-Z0-9._]+$', username):
            return 'Username can only contain letters, numbers, underscore (_) and dot (.)'
        
        
        if username[0] in '._' or username[-1] in '._':
            return 'Username cannot start or end with dot (.) or underscore (_)'
        
        return None       
    def first_name_validator(self,first_name):
        if not re.match(r'^[a-zA-Z]+(?:[\'-][a-zA-Z]+)*$', first_name):
            return 'First name should contain only letters (hyphen and apostrophe allowed)'
        return None
        
    def last_name_validator(self,last_name):
        if not re.match(r'^[a-zA-Z]+(?:[\'-][a-zA-Z]+)*$', last_name):
            return 'Last name should contain only letters (hyphen and apostrophe allowed)'
        return None
    
    def pass_validator(self,password):
        try:
            validate_password(password)
        except ValidationError as e:
            return e.messages
        return None
    def password_mismatch(self,password, confirm_password):
        if password != confirm_password:
            return 'Passwords do not match'
        return None
    
        
        


       

