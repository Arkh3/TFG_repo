from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from .models import User
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
import os, base64
from .faceRecognition import parseImage
from .forms import RegisterForm, LoginEmailForm, LoginPwdForm, ResetPwdForm
from django.http import JsonResponse
import math
from django.contrib import messages

# Create your views here.

# TODO: hacer que tomar las imágenes vaya más rápido plz (haciendo requests de 5 en 5 fotos maybe) (tambien se puede hacer en login y en register)
# TODO: revisar el reconocimiento facial al final cuando el resto esté acabado
# TODO: añadir terminos y condiciones en termsAndServices.html

@require_http_methods(["GET", "POST"])
def login0(request):

    if request.method == "GET":

        ## Si el usuario está autenticado le envía a /welcome
        if not request.user.is_authenticated:
            if 'email' in request.session:
                request.session.pop("email")
            return render(request, "login0.html", {"form": LoginEmailForm()})

        else:
            return redirect('/welcome/')


    ## Toma los datos limpios del formulario
    form = LoginEmailForm(request.POST)

    if not form.is_valid():
        messages.error(request,'Error en los datos del formulario.')
        return redirect('/')

    email = form.cleaned_data['email']

    ## Se asegura que el usuario existe
    if not User.objects.filter(email=email).exists():
        messages.error(request,'Ese usuario no existe')
        return redirect('/')

    ## Guarda en el request el email para los pasos posteriores
    request.session['email'] = email

    ## Si el usuario tiene reconocedor le envía a login_fr
    # en caso contrario a login_pwd
    user = User.objects.get(email=email)

    if user.recognizer is not None:
        return redirect('/login_fr/')
    else:
        return redirect('/login_pwd/')


@require_http_methods(["GET", "POST"])
def login_fr(request):
    if request.method == "GET":
        if 'email' in request.session:
            ## Comprueba si existe el reconocedor
            email = request.session['email']

            user = User.objects.get(email=email)
            user.cleanUserFolder()

            hasRecon = user.recognizer is not None
            return render(request, "login_fr.html", {'email': email, 'hasRecon': hasRecon})
        else:
            return redirect("/")

    #TODO: esto debería poder hacerse desde cualquier máquina pero no se puede hacer desde dos máquinas simultaneamlente
    elif request.method == "POST":
        if 'email' not in request.session:
            return JsonResponse({"allPhotos": False, "noEmail":True}, status=400)

        email = request.session['email']
        user = User.objects.get(email=email)

        ## Procesa la imagen
        processedImagesPath = user.get_tmp_processed_imgs_path()
        foundFace = processImage(user, request, processedImagesPath)
        numRequest, numFaces = user.setAndGetMetadata(newFace = foundFace)

        #print(str(numFaces) + "/" + str(numRequest))

        ## Si el número de imágenes parseadas es el correcto
        if numFaces >= settings.NEEDED_IMGS_FOR_LOGIN:
            user2 = authenticate(request, email=request.session['email'], images=processedImagesPath)
            user.cleanUserFolder()
            if user2 is not None:
                login(request, user2)
                return JsonResponse({"allPhotos": True, "facesProgress":math.trunc((numFaces/settings.NEEDED_IMGS_FOR_REGISTER)*100)}, status=200)
            else:
                return JsonResponse({"allPhotos": False, "noEmail":False}, status=400)

        ## Si el número de imágenes enviadas ya ha llegado al máximo
        elif numRequest > settings.MAX_IMG_REQUESTS:
            user.cleanUserFolder()
            return JsonResponse({"allPhotos": False, "noEmail":False}, status=400)

        ## En caso contrario se siguen necesitando más imágenes
        else:
            return JsonResponse({"allPhotos": False}, status=200) 

 
@require_http_methods(["GET", "POST"])
def login_pwd(request):
    if request.method == "GET":
        if 'email' in request.session:
            return render(request, "login_pwd.html", {'email': request.session['email'], 'form':LoginPwdForm()})
        else:
            return redirect("/")
    
    ## Toma los datos limpios del formulario
    form = LoginPwdForm(request.POST)
    
    if not form.is_valid():
        messages.error(request,'Error en los datos del formulario.')
        return redirect('/login_pwd')

    password = form.cleaned_data['password']

    ## Realiza la autenticación
    user = authenticate(request, email=request.session['email'], password=password)

    if user is not None:
        login(request, user)
        return redirect('/welcome/')
    else:
        messages.error(request,'Contraseña incorrecta.')
        return redirect('/login_pwd')


@require_http_methods(["GET", "POST"])
def register1(request):

    if request.method == "GET":
        if 'email' in request.session:
            request.session.pop("email")
        
        return render(request, "registro1.html", {"form": RegisterForm()})

    ## Toma los datos limpios del formulario
    form = RegisterForm(request.POST)

    if not form.is_valid():
        messages.error(request,'Error en los datos del formulario.')
        return redirect('/register1')

    email = form.cleaned_data['email']
    email = email.lower()
    pwd1 = form.cleaned_data['pass1']
    pwd2 = form.cleaned_data['pass2']

    ## Comprueba si ya se ha usado ese correo
    if User.objects.filter(email=email).exists():
        messages.error(request,'Error en los datos: ese correo ya está en uso.')
        return redirect('/register1')
    
    ## Comprueba restricciones sobre las contraseñas 
    if not checkPassword(pwd1, pwd2):
        messages.error(request,'Error en los datos: la contraseña tiene que cumplir ciertos criterios (len >= 8 y solo puede tener letras y números) y las contraseñas deben ser iguales.')
        return redirect('/register1')

    # TODO: mandarle un correo de confirmación (y que tenga una campo en la bbdd que sea is_verified)

    ## Registra una sesión del usuario
    User.objects.create_user(email, pwd1)
    user = authenticate(request, email=email, password=pwd1)
    login(request, user)
    
    request.session['registering'] = True
    return redirect('/register_fr/')


@require_http_methods(["GET", "POST"])
def register_fr(request):
    
    if request.method == "GET":
        if request.user.is_authenticated:
            if 'registering' in request.session:
                aux = request.session['registering']
                request.session.pop("registering")

                ## Borra el reconocedor en caso de existir uno
                email = request.user
                user = User.objects.get(email=email)
                user.cleanUserFolder()
                recogPath = user.recognizer 
                
                if recogPath is not None:
                    os.remove(recogPath)
                    user.recognizer = None
                    user.save()

                return render(request, "registro_fr.html", {'email':request.user, 'registering': aux})
            else:
                return redirect('welcome')
        else:
            return redirect('register1')
    
    elif request.user.is_authenticated:
        
        email = request.user
        user = User.objects.get(email=email)

        ## Procesa la imagen
        processedImagesPath = user.get_tmp_processed_imgs_path()
        foundFace = processImage(user, request, processedImagesPath)
        numRequest, numFaces = user.setAndGetMetadata(newFace = foundFace)

        #print(str(numFaces) + "/" + str(numRequest))

        ## Si el número de imágenes parseadas es el correcto 
        if numFaces == settings.NEEDED_IMGS_FOR_REGISTER:
            user.createRecognizer()
            return JsonResponse({"allPhotos": True, "facesProgress":math.trunc((numFaces/settings.NEEDED_IMGS_FOR_REGISTER)*100)}, status=200)

        ## Si el número de imágenes enviadas ya ha llegado al máximo
        elif numRequest > settings.MAX_IMG_REQUESTS:
            user.cleanUserFolder()
            return JsonResponse({"allPhotos": False}, status=400)

        ## En caso contrario se siguen necesitando más imágenes
        else:
            return JsonResponse({"allPhotos": False, "facesProgress":math.trunc(((numFaces+1)/settings.NEEDED_IMGS_FOR_REGISTER)*100)}, status=200)


@require_http_methods(["GET"])
def welcome(request):
    if request.method == "GET":
        if 'email' in request.session:
            request.session.pop("email")

        ## Si el usuario esta authenticated
        if request.user.is_authenticated:
            user = User.objects.get(email=request.user)

            aux = user.recognizer is not None
            return render(request, "welcome.html", {"hasRecognizer":aux})
        
        ## En caso contrario enviar a inicio de sesión
        else:
            return redirect('/')
    

@require_http_methods(["GET", "POST"])
def deleteRec(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            user = User.objects.get(email=request.user)
            return render(request, "deleteRec.html", {})

    if request.user.is_authenticated:
        email = request.user
        user = User.objects.get(email=email)
        recogPath = user.recognizer 
        
        if recogPath is not None:
            os.remove(recogPath)
            user.recognizer = None
            user.save()
        return JsonResponse({"a": True}, status=200)
    else:
        return JsonResponse({"b": True}, status=400)


@require_http_methods(["GET"])
def logoutUser(request):
    logout(request)  # Elimina el usuario de la sesión
    return redirect('/')


@require_http_methods(["GET", "POST"])
def resetPass(request):
    if request.method == "GET":
        if request.user.is_authenticated:    
            return render(request, "resetPass.html", {"form": ResetPwdForm()})
        else:
            return redirect("/")
    
    elif request.method == "POST" and request.user.is_authenticated:
        email = request.user

        form = ResetPwdForm(request.POST)

        if not form.is_valid():
            messages.error(request,'Error en los datos del formulario.')
            return redirect('/resetPass')

        ## Toma los datos limpios del formulario
        password_old = form.cleaned_data['password0']
        password_new_1 = form.cleaned_data['password1']
        password_new_2 = form.cleaned_data['password2']

        ## Comprueba que la contraseña actual es la correcta
        user = authenticate(request, email=email, password=password_old)

        if user is not None:
            ## Comprueba las nuevas contraseñas
            if checkPassword(password_new_1, password_new_2):
                User.objects.changePassword(email, password_new_1)
                user = authenticate(request, email=email, password=password_new_1)
                login(request, user) 
                return redirect("/welcome/")
            else:
                messages.error(request,'Las contraseñas deben ser iguales y la nueva contraseña no cumple los requisitos: len >= 8 y solo puede tener letras y números.')
                return redirect('/resetPass')

        else:
            messages.error(request,'La contraseña actual no es la correcta.')
            return redirect('/resetPass')


@require_http_methods(["GET", "POST"])
def confirmCreateRecognizer(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return render(request, "confirmCreateRecognizer.html", {'form': LoginPwdForm()})

    elif request.method == "POST" and request.user.is_authenticated:
        email = request.user

        ## Toma los datos limpios del formulario
        form = LoginPwdForm(request.POST)
        
        if not form.is_valid():
            messages.error(request,'Error en los datos del formulario.')
            return redirect('/confirmCreateRecognizer')

        password = form.cleaned_data['password']

        ## Comprueba que la contraseña sea correcta
        user = authenticate(request, email=request.user, password=password)

        if user is not None:
            request.session['registering'] = False
            return redirect('/register_fr/')
        else:
            messages.error(request,'La contraseña actual no es la correcta.')
            return redirect('/confirmCreateRecognizer')


@require_http_methods(["GET"])
def termsAndServices(request):
    if request.method == "GET":
        return render(request, "termsAndServices.html",{})

########################### AUX FUNCTIONS ######################################

## Restricciones: len >= 8, letras+numeros, que sean iguales
def checkPassword(pwd1, pwd2):
    hasLetters = False
    hasNumbers = False

    if pwd1 != pwd2:
        return False

    for char in pwd1:
        if char.isalpha():
            hasLetters = True
        elif char.isnumeric():
            hasNumbers = True
        else:
            return False

    if len(pwd1) < 8 or not hasLetters or not hasNumbers:
        return False

    return True


def processImage(user, request, processedImagesPath):
    tmp_path =  user.get_tmp_raw_imgs_path()
    base64_img = request.POST['foto']
    data_img = base64.decodebytes(base64_img.encode('ascii'))
    id = len(os.listdir(tmp_path)) + 1
    raw_image_path = os.path.join(tmp_path, str(id) + ".png")
    f = open(raw_image_path, 'wb')
    f.write(data_img)
    f.close()

    foundFace = parseImage(raw_image_path, processedImagesPath)

    return foundFace