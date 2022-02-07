from django.http import HttpResponse
from django.shortcuts import render
#from django.views.decorators.http import require_GET
#from django.template import loader


def saludo(request): # Primera vista
    return HttpResponse("Hola mundo :)")

#@require_GET
def login(request): # Segunda vista    
    return render(request, "login.html", {"my_text": "Estas en login bruh"})