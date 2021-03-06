"""fr_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from authentication import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login0, name='login0'),
    path('login_fr/', views.login_fr, name='login_fr'),
    path('login_pwd/', views.login_pwd, name='login_pwd'),
    path('register1/', views.register1, name='register1'),
    path('register_fr/', views.register_fr, name='register_fr'),
    path('welcome/', views.welcome, name='welcome'),
    path('logout/', views.logoutUser, name='logout'),
    path('deleteRec/', views.deleteRec, name='deleteRec'),
    path('resetPass/', views.resetPass, name='resetPass'),
    path('confirmCreateRecognizer/', views.confirmCreateRecognizer, name='confirmCreateRecognizer'),
    path('termsAndServices/', views.termsAndServices, name='termsAndServices'),
]   + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
