from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .userManager import UserManager
from django.core.mail import send_mail
from django.conf import settings
import os
import shutil
from .faceRecognition import createRecognizer

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(_("email address"), 
                                    unique=True,
                                    error_messages={
                                        "unique": _("A user with that email already exists."),
                                    },)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # -------------- Face recoginition ---------------------

    recognizer = models.CharField(
        _("recognizer"),
        max_length=4096,
        unique=True,
        null =True,
        blank=True,
        default=None,
    )

    # ------------------------------------------------------

    def createRecognizer(self):
        recognizerPath =  self.get_recognizer_path()
        createRecognizer(self.get_tmp_processed_imgs_path(), recognizerPath)
        self.recognizer = recognizerPath
        self.save()
        self.cleanUserFolder()


    def clean(self):
        super().clean()
        self.email = self.email.lower()


    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
        

    def get_tmp_raw_imgs_path(self):
        ret = os.path.join(settings.USERS_DIRECTORY, str(self.id), "rawImages")
        
        if not os.path.isdir(ret):
            os.mkdir(ret)
            
        return ret


    def get_tmp_processed_imgs_path(self):
        ret = os.path.join(settings.USERS_DIRECTORY, str(self.id), "processedImages")
        
        if not os.path.isdir(ret):
            os.mkdir(ret)
            
        return ret


    def get_recognizer_path(self):
        ret = os.path.join(settings.USERS_DIRECTORY, str(self.id), "recognizer.fr") 
        return ret


    def get_metadata_path(self):
        return os.path.join(settings.USERS_DIRECTORY, str(self.id), "metadata.mt") 


    def setAndGetMetadata(self, newRequest = True, newFace = False):
        metadataPath = self.get_metadata_path()
        
        if not os.path.isfile(metadataPath):
            file = open(metadataPath, 'w')
            file.write("0\n")
            file.write("0\n")
            file.close
        
        file = open(metadataPath, 'r')
        numRequests = int(file.readline())
        numFaces = int(file.readline())
        file.close
        
        if newRequest:
            numRequests += 1
        
        if newFace:
            numFaces += 1

        file = open(metadataPath, 'w')
        file.write(str(numRequests) + '\n')
        file.write(str(numFaces) + '\n')
        file.close

        return numRequests, numFaces


    def cleanUserFolder(self):
        if os.path.isdir(self.get_tmp_raw_imgs_path()):
            shutil.rmtree(self.get_tmp_raw_imgs_path())
        if os.path.isdir(self.get_tmp_processed_imgs_path()):
            shutil.rmtree(self.get_tmp_processed_imgs_path())
        if os.path.isfile(self.get_metadata_path()):
            os.remove(self.get_metadata_path())