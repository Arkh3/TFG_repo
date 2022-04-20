from django.shortcuts import render, redirect
from .forms import LoginForm 
from django.http import HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
# Create your views here.

def inicio(request):
    if request.method == "GET":
        return render(request, "base.html", {})

#TODO: @require_http_methods(["GET", "POST"])
def userLogin(request):

    if request.method == "GET":
        form = LoginForm()   
        return render(request, "login.html", {'login_form': form})

    elif request.method == "POST":
        # Carga el formulario desde los datos de la petición y lo valida
        form = LoginForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest(f"Error en los datos del formulario: {form.errors}")

        # Toma los datos limpios del formulario
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        # Realiza la autenticación
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Registra el usuario en la sesión
            return redirect('/inicio/')
        else:
            return render(request, "error_login.html")


def logoutUser(request):
    logout(request)  # Elimina el usuario de la sesión
    return redirect('/inicio/')