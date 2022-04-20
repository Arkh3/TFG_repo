from logging import raiseExceptions
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import User

# TODO: buscar en la base de datos todo
class FR_backend(BaseBackend):
    """
    Authenticate against the settings ADMIN_LOGIN and ADMIN_PASSWORD.

    Use the login name and a hash of the password. For example:

    ADMIN_LOGIN = 'administrator'
    ADMIN_PASSWORD = 'administrator'
    """
    def authenticate(self, request, email=None, password=None):
        login_valid = (settings.ADMIN_LOGIN == email)
        pwd_valid = (password == settings.ADMIN_PASSWORD)#TODO: check_password(password, settings.ADMIN_PASSWORD)
                
        if login_valid and pwd_valid:
            try:
                user = User.objects.get(email=email) #TODO: esto no funciona porque necesitamos un Manager
            except User.DoesNotExist:
                # Create a new user. There's no need to set a password
                # because only the password from settings.py is checked.
                user = User(email=email) 
                user.is_staff = True
                user.is_superuser = True
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None