from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST, require_http_methods

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


@require_http_methods(["GET", "POST"]) #Adaptarlo luego un poco a como lo tengo en GIW
def register(request):
    if request.method == "GET":
        return render(request, "registro2.html", {"form": RegisterForm()})
    
def welcome(request):
    if True: #TODO: si el usuario tiene una sesión ( creo que viene en las request)
        return render(request, "welcome.html")
    else:
        return redirect('/inicio/')