from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from.models import User
from django.http import HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
import os, base64
# Create your views here.
from .forms import RegisterForm, LoginEmailForm, LoginPwdForm

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

    user = authenticate(request, email=email, password=pwd1)

    if user is None:
        return HttpResponseBadRequest(f"Error NO SE HA GUARDADO BIEN EL USUARIO")
    
    #TODO: mover el login a register2 al final
    login(request, user)
    request.session['email'] = email
    return redirect('/register2/')


# TODO: register un boton que evoluciona: omitir el paso > bloqueo > finalizar
@require_http_methods(["GET", "POST"])
def register2(request):
    if request.method == "GET":
        if 'email' in request.session:
            return render(request, "registro2.html", {'email':request.session['email']})
        else:
            return redirect('register1')
      
    email = request.session['email']

    user = User.objects.get(email=email)

    recognizerPath = os.path.join(settings.RECOGNIZERS_PATH, str(user.id))

    user.recognizer = recognizerPath
    user.save()

    return redirect("/welcome/")
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


def upload_register(request):
    if request.method == "POST":
              
        user = User.objects.get(email=request.session['email'])

        # TODO: ese 10 tambien hay que cambiarlo en el javascript ( linea 77)
        for i in range(10):
            base64_img = request.POST['fotos['+str(i)+'][]']

            data_img = base64.decodebytes(base64_img.encode('ascii'))
            
            tmp_path =  user.get_tmp_imgs_path()

            id = len(os.listdir(tmp_path)) + 1
            
            f = open(os.path.join(tmp_path, str(id) + ".png"), 'wb')
            f.write(data_img)
            f.close()

        #TODO: createRecognizer(request.session['email']) # que cojalas imagenes de user.get_tmp_imgs_path(), las vaya codificando y borrando y cuando haya codificado y borrado todas que cree el reconocedor
        
        #TODO: register2 debería comprobar si existe ya un reconocedor para la persona ( en caso de que exista debería poner, reconocedor creado con éxito! y poner finalizar)
        return redirect('/register2/')


#MANDÁNDOLE 50 IMÁGENES Y QUE EL UPLOAD_REGISTER PARSEE 30 IMÁGENES Y DE ERROR SI EN LAS 50 IMAGENES NO HA CONSEGUIDO ENCONTRAR 30 BUENAS

#CHECKEA CUANTAS IMAGENES HAY (DEBERIA HABER 0 AL PRINCIPIO Y 30 AL FINAL)

#COGE LA IMAGEN Y LA PARSEA, VE SI HAY UNA CARA Y HACE EL ENCODING Y LA GUARDA EN ALGUN FICHERO CON LO DE PICKLE

#BORRA LA IMAGEN (O NO SE GUARDA DIRECTAMENTE)

#UNA VEZ ACABE EL REGISTRO DEBERÍA LIMPIARSE LA CARPETA DE TMP


##############
#OTRA FORMA DE HACERLO SERÍA 