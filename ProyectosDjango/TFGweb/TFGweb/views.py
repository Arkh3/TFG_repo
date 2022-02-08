from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .forms import LoginForm

@require_http_methods(["GET", "POST"])
def inicio(request):
    if request.method == "GET":
        return render(request, "base.html", {})

    # if request.method == "POST":

@require_http_methods(["GET", "POST"])
def loginfunct(request): 
    """Muestra el formulario (GET) o recibe los datos y realiza la autenticacion (POST)"""
    if request.method == "GET":
        form = LoginForm()   
        return render(request, "login.html", {'login_form': form})

    # if request.method == "POST":

    # Carga el formulario desde los datos de la petición y lo valida
    form = LoginForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest(f"Error en los datos del formulario: {form.errors}")

    # Toma los datos limpios del formulario
    username = form.cleaned_data['username']
    password = form.cleaned_data['password']

    # Realiza la autenticación
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)  # Registra el usuario en la sesión
        return redirect('/inicio/')
    else:
        return render(request, "error_login.html")


@require_GET
def logoutfunct(request):
    """Elimina al usuario de la sesión actual"""
    logout(request)  # Elimina el usuario de la sesión
    return redirect('/inicio/')