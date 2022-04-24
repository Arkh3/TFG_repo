from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .userManager import UserManager
from django.core.mail import send_mail
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

    

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)