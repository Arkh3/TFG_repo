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
<<<<<<< HEAD:FaceRecognitionDeployment/fr_project/fr_project/urls.py

urlpatterns = [
    path('admin/', admin.site.urls),
]
=======
from FaceRecognitionAuth.views import registro_1, registro_2, user_logged
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registro1/', registro_1),
    path('registro2/', registro_2),
    path('user_logged/', user_logged),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
>>>>>>> 1b7dd5ab541f1aac775929f59ea334595065833d:FaceRecognitionDeployment/DjangoProject/FaceRecognitionAuth/urls.py
