from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from .models import User
from django.http import HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
import os, base64
from .faceRecognition import parseImage
from .forms import RegisterForm, LoginEmailForm, LoginPwdForm, ResetPwdForm
from django.http import JsonResponse
import math

# Create your views here.

# TODO: arreglar el spaninglish
# TODO: comentar bien el código para que esté bien especificado
# TODO: hacer que tomar las imágenes vaya más rápido plz (haciendo requests de 5 en 5 fotos maybe) (tambien se puede hacer en login y en register)
# TODO: revisar el reconocimiento facial al final cuando el resto esté acabado
# TODO: hacer que los mensajes de error (tipo: el usuario ya existe) aparezcan en el propio html y no te lleven a otro

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
        return HttpResponseBadRequest(f"Error en los datos del formulario: {form.errors}")

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
            user.cleanUserFolder()

            hasRecon = user.recognizer is not None
            return render(request, "login1.html", {'email': email, 'hasRecon': hasRecon})
        else:
            return redirect("/")

    #TODO: esto debería poder hacerse desde cualquier máquina pero no se puede hacer desde dos máquinas simultaneamlente
    elif request.method == "POST":
        if 'email' not in request.session:
            return JsonResponse({"allPhotos": False, "noEmail":True}, status=400)

        email = request.session['email']
        user = User.objects.get(email=email)

        processedImagesPath = user.get_tmp_processed_imgs_path()
        foundFace = processImage(user, request, processedImagesPath)
        numRequest, numFaces = user.setAndGetMetadata(newFace = foundFace)

        print(str(numFaces) + "/" + str(numRequest))

        if numFaces >= settings.NEEDED_IMGS_FOR_LOGIN:
            user2 = authenticate(request, email=request.session['email'], images=processedImagesPath)
            user.cleanUserFolder()
            if user2 is not None:
                login(request, user2)
                return JsonResponse({"allPhotos": True, "facesProgress":math.trunc((numFaces/settings.NEEDED_IMGS_FOR_REGISTER)*100)}, status=200)
            else:
                return JsonResponse({"allPhotos": False, "noEmail":False}, status=400)
            
        elif numRequest > settings.MAX_IMG_REQUESTS:
            user.cleanUserFolder()
            return JsonResponse({"allPhotos": False, "noEmail":False}, status=400)

        else:
            return JsonResponse({"allPhotos": False}, status=200) 


@require_http_methods(["GET", "POST"])
def login2(request):
    if request.method == "GET":
        if 'email' in request.session:
            return render(request, "login2.html", {'email': request.session['email'], 'form':LoginPwdForm()})
        else:
            return redirect("/")
    
     ## Toma los datos limpios del formulario
    form = LoginPwdForm(request.POST)
    
    if not form.is_valid():
        return HttpResponseBadRequest(f"Error en los datos del formulario: {form.errors}")

    password = form.cleaned_data['password']

    ## Realiza la autenticación
    user = authenticate(request, email=request.session['email'], password=password)

    if user is not None:
        login(request, user)
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

    ## Toma los datos del formulario
    form = RegisterForm(request.POST)

    if not form.is_valid():
        return HttpResponseBadRequest(f"Error en los datos del formulario: {form.errors}")

    email = form.cleaned_data['email']
    email = email.lower()
    pwd1 = form.cleaned_data['pass1']
    pwd2 = form.cleaned_data['pass2']

    if User.objects.filter(email=email).exists():
        return HttpResponseBadRequest(f"Error en los datos: ese correo ya está en uso")
    
    if not checkPassword(pwd1, pwd2):
        return HttpResponseBadRequest(f"Error en los datos: la contraseña tiene que cumplir ciertos criterios (len >= 8 y solo puede tener letras y números).")

    # TODO: mandarle un correo de confirmación (y que tenga una campo en la bbdd que sea is_verified)

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

        processedImagesPath = user.get_tmp_processed_imgs_path()
        foundFace = processImage(user, request, processedImagesPath)
        numRequest, numFaces = user.setAndGetMetadata(newFace = foundFace)

        print(str(numFaces) + "/" + str(numRequest))

        if numFaces == settings.NEEDED_IMGS_FOR_REGISTER:
            user.createRecognizer()
            return JsonResponse({"allPhotos": True, "facesProgress":math.trunc((numFaces/settings.NEEDED_IMGS_FOR_REGISTER)*100)}, status=200)

        elif numRequest > settings.MAX_IMG_REQUESTS:
            user.cleanUserFolder()
            return JsonResponse({"allPhotos": False}, status=400)

        else:
            return JsonResponse({"allPhotos": False, "facesProgress":math.trunc(((numFaces+1)/settings.NEEDED_IMGS_FOR_REGISTER)*100)}, status=200)


@require_http_methods(["GET"])
def welcome(request):
    if request.method == "GET":
        if 'email' in request.session:
            request.session.pop("email")

        if request.user.is_authenticated:

            user = User.objects.get(email=request.user)

            aux = user.recognizer is not None
            return render(request, "welcome.html", {"hasRecognizer":aux})
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
            return HttpResponseBadRequest(f"Error en los datos del formulario: {form.errors}")

        # Toma los datos limpios del formulario
        password_old = form.cleaned_data['password0']
        password_new_1 = form.cleaned_data['password1']
        password_new_2 = form.cleaned_data['password2']

        user = authenticate(request, email=email, password=password_old)

        if user is not None:
            if checkPassword(password_new_1, password_new_2):
                User.objects.changePassword(email, password_new_1)
                user = authenticate(request, email=email, password=password_new_1)
                login(request, user) 
                return redirect("/welcome/")
            else:
                return HttpResponseBadRequest("La nueva contraseña no cumple los requisitos")

        else:
            return HttpResponseBadRequest("La contraseña actual no es la correcta")


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
            return HttpResponseBadRequest(f"Error en los datos del formulario: {form.errors}")

        password = form.cleaned_data['password']

        ## Realiza la autenticación
        user = authenticate(request, email=request.user, password=password)

        if user is not None:
            request.session['registering'] = False
            return redirect('/register_fr/')
        else:
            return HttpResponseBadRequest('Contraseña actual errónea.')


########################### AUX FUNCTIONS ######################################


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