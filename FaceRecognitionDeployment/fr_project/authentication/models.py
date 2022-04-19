from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

#TODO: probar a usar AbstractBaseUser porque solo tiene tres campos y podemos poner justo los que necesitemos (password, last logging y is active)
class User(AbstractUser):
    pass