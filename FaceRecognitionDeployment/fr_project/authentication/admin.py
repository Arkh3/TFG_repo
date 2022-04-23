from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.

#TODO: PUEDe heredar de from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
class CustomUserAdmin(UserAdmin):
    list_display = ("email",)
    list_filter = ("is_staff", "is_superuser", "groups")
    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )


#TODO: a lo mejor tengo que hacer admin.site.unregister(User) y luego admin.site.register(User, UserAdmin)
admin.site.register(User, CustomUserAdmin)