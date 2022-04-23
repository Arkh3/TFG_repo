from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from.models import User
from .forms import LoginForm 
from django.http import HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout

# Create your views here.
from .forms import LoginForm, RegisterForm

@require_http_methods(["GET", "POST"])
def login1(request):
    if request.method == "GET":
        return render(request, "login1.html", {"form": LoginForm()})
    
@require_http_methods(["GET", "POST"])
def login2(request):
    if request.method == "GET":
        return render(request, "login2.html", {"form": LoginForm()})
    
    form = LoginForm(request.POST)
    
    if not form.is_valid():
        return HttpResponseBadRequest(f"Error en los datos del formulario: {form.errors}")

    # Toma los datos limpios del formulario
    email = form.cleaned_data['email']
    password = form.cleaned_data['password']

    # Realiza la autenticación
    user = authenticate(request, email=email, password=password)
    if user is not None:
        login(request, user)  # Registra el usuario en la sesión
        return redirect('/welcome/')
    else:
        return render(request, "error.html")

@require_http_methods(["GET", "POST"]) #Adaptarlo luego un poco a como lo tengo en GIW
def register(request):

    def checkPassword(pwd):
        hasLetters = False
        hasNumbers = False

        for char in pwd:
            if char.isalpha():
                hasLetters = True
            elif char.isnumeric():
                hasNumbers = True
            else:
                return False

        if len(pwd) < 8 or not hasLetters or not hasNumbers:
            return False

        return True

    if request.method == "GET":
        return render(request, "registro2.html", {"form": RegisterForm()})

    form = RegisterForm(request.POST)

    if not form.is_valid():
        return HttpResponseBadRequest(f"Error en los datos del formulario: {form.errors}")

    # Toma los datos limpios del formulario
    email = form.cleaned_data['email']
    pwd1 = form.cleaned_data['pass1']
    pwd2 = form.cleaned_data['pass2']

    #TODO: hacer esto bien 
    aceptaTerminosYCondiciones = True

    if not aceptaTerminosYCondiciones:
        return HttpResponseBadRequest(f"Error en los datos: para crear un usuario debes aceptar los términos y condiciones")

    if User.objects.filter(email=email).exists():
        return HttpResponseBadRequest(f"Error en los datos: ese correo ya está en uso")

    if not checkPassword(pwd1):
        return HttpResponseBadRequest(f"Error en los datos: la contraseña tiene que cumplir ciertos criterios (len >= 8 y solo puede tener letras y números).")

    if pwd1 != pwd2:
        return HttpResponseBadRequest(f"Error en los datos: las contraseñas deben ser iguales")

    # TODO maybe: mandarle un correo para confirmarle (y que tenga una campo en la bbdd que sea is_verified)
    
    user = User.objects.create_user(email, email, pwd1)
    user.save()

    user = authenticate(request, email=email, password=pwd1)

    if User is None:
        return HttpResponseBadRequest(f"Error NO SE HA GUARDADO BIEN EL USUARIO")

    login(request, user)
    return redirect('/welcome/')

    
def welcome(request):
    if request.user.is_authenticated:
        return render(request, "welcome.html")
    else:
        return redirect('/')

def logoutUser(request):
    logout(request)  # Elimina el usuario de la sesión
    return redirect('/')

