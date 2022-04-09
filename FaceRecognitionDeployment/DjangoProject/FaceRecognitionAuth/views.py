from django.shortcuts import render
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.http import HttpResponse

from .forms import Register1, Register2, Register3

@require_http_methods(["GET", "POST"])
def registro_1(request):
    if request.method == "GET":
        return render(request, "registro1.html", {"form": Register1()}) #Register3
 
def registro_2(request):
    if request.method == "GET":
        return render(request, "registro2.html", {
            "form": Register2(), "username" : request.GET['username'], "mail" : request.GET['mail']})
       
def user_logged(request):
    if request.method == "GET":
        form = Register2(request.GET)
        
        if not form.is_valid():
            return HttpResponseBadRequest("Error en los datos del formulario:%r}" %form.errors)
        
        formData = form.cleaned_data
        
        username = request.GET['username']
        mail = request.GET['mail']
        clave1 = formData['pass1']
        clave2 = formData['pass2']
        
        if (clave1 == clave2):
            # CREAR AQUI AL USUARIO
            mensaje = 'Bienvenido %r' %username
            return HttpResponse(mensaje)
        else:
            return render(request, "error.html", {})