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
        max_length=4096, # TODO: a lo mejor queremos hacer mas pequeño el campo hehe
        unique=True,
        null =True,
        blank=True,
        default=None,
    )

    # ------------------------------------------------------

    #TODO: crear un reconocedor con 30 imagenes

    #TODO: reemplazar el reconocedor: borrar el actual y crear otro nuevo con el reconocedor de 30 imágenes

    #TODO: pasarle 5 imágenes y que valide las 5 y diga si es el o no

    def createRecognizer(self):
        recognizerPath =  self.get_recognizer_path()
        createRecognizer(self.get_tmp_processed_imgs_path(), recognizerPath)
        self.recognizer = recognizerPath
        self.save()
        self.cleanUserFolder()


    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)


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

        shutil.rmtree(self.get_tmp_raw_imgs_path())
        shutil.rmtree(self.get_tmp_processed_imgs_path())
        os.remove(self.get_metadata_path())