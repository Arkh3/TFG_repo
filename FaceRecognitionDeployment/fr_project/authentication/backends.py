from logging import raiseExceptions
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import User

class FR_backend(BaseBackend):
    
    def authenticate(self, request, email=None, password=None):

        try:
            user = User.objects.get(email=email)

            if not user.check_password(password):
                return None
            
            return user

        except User.DoesNotExist:
            return None


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None