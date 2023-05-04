from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import HttpResponseRedirect, render, redirect
from django.urls import reverse
from .models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

def index(request):
    
    # get all users just to list them in the index page after login
    users = User.objects.all()
    
    return render(request, 'index.html', {
                    "users": users,
                })

@csrf_exempt
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect("/admin")  # redirect to Django admin site
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")
    
@csrf_exempt
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index") )
    else:
        return render(request, "register.html")
    

    
    
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))