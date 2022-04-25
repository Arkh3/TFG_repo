from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from.models import User
from django.http import HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
import os
# Create your views here.
from .forms import RegisterForm, LoginEmailForm, LoginForm

@require_http_methods(["GET", "POST"])
def login0(request):
    if request.method == "GET":
        if not request.user.is_authenticated:
            if 'email' in request.session:
                request.session.pop("email")
            return render(request, "login0.html", {"form": LoginEmailForm()})
        else:
            return redirect('/welcome/')

    form = LoginEmailForm(request.POST)

    if not form.is_valid():
        return HttpResponseBadRequest(f"Error en los datos del formulario00: {form.errors}")

    # Toma los datos limpios del formulario
    email = form.cleaned_data['email']

    if not User.objects.filter(email=email).exists():
        return HttpResponseBadRequest(f"El usuario no existe")

    request.session['email'] = email

    user = User.objects.get(email=email)

    if user.recognizer is not None:
        return redirect('/login1/')
    else:
        return redirect('/login2/')


@require_http_methods(["GET", "POST"])
def login1(request):
    if request.method == "GET":
        if 'email' in request.session:
              # Checkee que existe el reconocedor
            email = request.session['email']

            user = User.objects.get(email=email)

            if user.recognizer is not None:
                return render(request, "login1.html", {'email': request.session['email']})
            else:
                #TODO: Si no existe el reconocedor que se ponga en rojo y le de una explicación de que tiene que activar el reconocimiento facial en los ajustes una vez iniciado sesión
                return render(request, "login1.html", {'email': request.session['email']})
        else:
            return redirect("/")

    #TODO: hacer que:
  
    # Esto debería ser authentification(email, imagenes): Si le da a click que coga unas imágenes de algún directorio y que las valide contra el reconocedor existente
    # Realiza la autenticación
    #user = authenticate(request, email=email, imagenes=imagenes)
    #if user is not None:
    #    login(request, user) # Registra el usuario en la sesión
    #    return redirect('/welcome/')
    #else:
    #    return render(request, "error.html")
    #
    

@require_http_methods(["GET", "POST"])
def login2(request):
    if request.method == "GET":
        if 'email' in request.session:
            return render(request, "login2.html", {'email': request.session['email']})
        else:
            return redirect("/")
    
    form = LoginForm(request.POST)
    
    if not form.is_valid():
        return HttpResponseBadRequest(f"Error en los datos del formulario: {form.errors}")

    ## Toma los datos limpios del formulario
    email = form.cleaned_data['email']
    password = form.cleaned_data['password']
#
    # Realiza la autenticación
    user = authenticate(request, email=email, password=password)
    if user is not None:
        login(request, user) # Registra el usuario en la sesión
        return redirect('/welcome/')
    else:
        return render(request, "error.html")


@require_http_methods(["GET", "POST"])
def register1(request):

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
        return render(request, "registro1.html", {"form": RegisterForm()})

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

    # TODO maybe: mandarle un correo para confirmarle (y que tenga una campo en la bbdd que sea is_verified) (el usuario tiene una funcion de send emaill creo mirar en models.py)

    User.objects.create_user(email, pwd1)

    user = authenticate(request, email=email, password=pwd1)

    if user is None:
        return HttpResponseBadRequest(f"Error NO SE HA GUARDADO BIEN EL USUARIO")
    
    #TODO: mover el login a register2 al final
    login(request, user)
    request.session['email'] = email
    return redirect('/register2/')

# TODO: que register1 le pase a register2 el email (si no esta el email, register2 debería redireccionar a register1)
# TODO: register dos debería tener dos botones: omitir el paso y finalizar
@require_http_methods(["GET", "POST"])
def register2(request):
    if request.method == "GET":
        return render(request, "registro2.html", {})
        
    email = request.session['email']

    user = User.objects.get(email=email)

    recognizerPath = os.path.join(settings.RECOGNIZERS_PATH, str(user.id))

    user.recognizer = recognizerPath
    user.save()

    return render(request, "welcome.html")
    # TODO: Crear el reconocedor en elpath recognizerPath


def welcome(request):
    if 'email' in request.session:
        request.session.pop("email")

    if request.user.is_authenticated:
        return render(request, "welcome.html")
    else:
        return redirect('/')


def logoutUser(request):
    logout(request)  # Elimina el usuario de la sesión
    return redirect('/')

