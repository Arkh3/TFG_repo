from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from.models import User
from django.http import HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
import os, base64
from .faceRecognition import parseImage
# Create your views here.
from .forms import RegisterForm, LoginEmailForm, LoginPwdForm
from django.http import JsonResponse
import math


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

            hasRecon = user.recognizer is not None
            #TODO: Si no existe el reconocedor que se ponga en rojo y le de una explicación de que tiene que activar el reconocimiento facial en los ajustes una vez iniciado sesión
            return render(request, "login1.html", {'email': request.session['email'], 'hasRecon': hasRecon})
        else:
            return redirect("/")

    # TODO: las imágenes deberían ser las de la webcam
    imagesPath = "/code/authentication/testImagesLogin2"

    user = authenticate(request, email=request.session['email'], images=imagesPath)

    if user is not None:
        login(request, user) # Registra el usuario en la sesión
        return redirect('/welcome/')
    else:
        return HttpResponseBadRequest(f"Error: reconocimiento facial fallido incorrecta")


@require_http_methods(["GET", "POST"])
def login2(request):
    if request.method == "GET":
        if 'email' in request.session:
            return render(request, "login2.html", {'email': request.session['email'], 'form':LoginPwdForm()})
        else:
            return redirect("/")
    
    form = LoginPwdForm(request.POST)
    
    if not form.is_valid():
        return HttpResponseBadRequest(f"Error en los datos del formulario: {form.errors}")

    ## Toma los datos limpios del formulario
    password = form.cleaned_data['password']
#
    # Realiza la autenticación
    user = authenticate(request, email=request.session['email'], password=password)

    if user is not None:
        login(request, user) # Registra el usuario en la sesión
        return redirect('/welcome/')
    else:
        return HttpResponseBadRequest(f"Error: contraseña incorrecta")


# TODO: añadir los terminos y condiciones (enlace)
@require_http_methods(["GET", "POST"])
def register1(request):

    if request.method == "GET":

        if 'email' in request.session:
            request.session.pop("email")
        
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
    
    #TODO: descomentar esto al acabar el proyecto
    #if not checkPassword(pwd1):
    #    return HttpResponseBadRequest(f"Error en los datos: la contraseña tiene que cumplir ciertos criterios (len >= 8 y solo puede tener letras y números).")

    if pwd1 != pwd2:
        return HttpResponseBadRequest(f"Error en los datos: las contraseñas deben ser iguales")

    # TODO maybe: mandarle un correo para confirmarle (y que tenga una campo en la bbdd que sea is_verified) (el usuario tiene una funcion de send emaill creo mirar en models.py)

    User.objects.create_user(email, pwd1)


    # TODO: el email hay que pasarlo todo a minusculas, si no falla
    user = authenticate(request, email=email, password=pwd1)

    userPath = os.path.join(settings.USERS_DIRECTORY, str(user.id))
    if not os.path.isdir(userPath):
        os.mkdir(userPath)
        
    login(request, user)

    if user is None:
        return HttpResponseBadRequest(f"Error NO SE HA GUARDADO BIEN EL USUARIO")
    
    request.session['registering'] = True
    request.session['repeat'] = False
    request.session['email'] = email
    return redirect('/register2/')


#TODO: hay que mejorar cuando se crean y se borran las carpetas y archivos de usuarios
@require_http_methods(["GET", "POST"])
def register2(request):
    if request.method == "GET":
        if 'registering' in request.session and request.session['registering'] and request.user.is_authenticated:
            request.session.pop("registering")
            return render(request, "registro2.html", {'email':request.session['email']})
        else:
            return redirect('register1')
    
    elif request.method == "POST" and  request.user.is_authenticated:
 
        #A lo mejor se puede mandar requests de 5 en 5 fotos

        # SI ESTO SIGUE DANDO PROBLEMAS HACER QUE EL JAVASCRIPT MANDE 50 IMÁGENES Y QUE CUANDO LAS MANDE
        # DEVUELVA UN PARAMETRO EN EL REQUEST DE TIPO DONE=True y  QUE CUANDO LLEGUE ESE PARÁMETRO SE PROCESEN TODAS LAS IMÁGENES
        # Y SE LE RETORNE A LA PETICION AJAX SI HA SIDO SUCCESSFULL O NO
        # no podria hacerse el porcentaje de caras que llevamos pero se puede poner un gif de loading o processando o algo asi

        email = request.user
        user = User.objects.get(email=email)
        tmp_path =  user.get_tmp_raw_imgs_path()
        tmpImagesPath = user.get_tmp_processed_imgs_path()

        base64_img = request.POST['foto']
        data_img = base64.decodebytes(base64_img.encode('ascii'))
        id = len(os.listdir(tmp_path)) + 1
        f = open(os.path.join(tmp_path, str(id) + ".png"), 'wb')
        f.write(data_img)
        f.close()

        foundFace = parseImage(tmp_path, tmpImagesPath)
        numRequest, numFaces = user.setAndGetMetadata(newFace = foundFace)
        print(str(numFaces)+"/" + str(numRequest)) # TODO: QUITAR EL PRINT

        if numFaces == settings.NEEDED_IMGS_FOR_REGISTER:
            user.createRecognizer()
            return JsonResponse({"allPhotos": True, "facesProgress":math.trunc((numFaces/settings.NEEDED_IMGS_FOR_REGISTER)*100)}, status=200)

        elif numRequest > settings.MAX_IMG_REQUESTS:
            user.cleanUserFolder()
            return JsonResponse({"allPhotos": False}, status=400)

        else:
            return JsonResponse({"allPhotos": False, "facesProgress":math.trunc((numFaces/settings.NEEDED_IMGS_FOR_REGISTER)*100)}, status=200) # EN VEZ DE NUMFACES PUEDO PASARLE EL PORCENTAJE DE FOTOS QUE NECESITO


@require_http_methods(["GET"])
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


########################### AUX FUNCTIONS ######################################


# TODO: maybe poner toda la logica de la contraseña aqui
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