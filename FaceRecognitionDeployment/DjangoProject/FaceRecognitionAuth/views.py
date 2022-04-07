from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST, require_http_methods

@require_http_methods(["GET", "POST"])
def login(request):
    if request.method == "GET":
        return render(request, "login.html", {})