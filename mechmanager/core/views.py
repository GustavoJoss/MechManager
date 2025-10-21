from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from .models import Vehicle, WorkOrder

from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

def home(request):
    return render(request, "home.html")

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)
            return redirect("user_area")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})

@login_required
def user_area(request):
    vehicles = Vehicle.objects.filter(owner=request.user).order_by("-created_at")[:5]
    orders = WorkOrder.objects.filter(vehicle__owner=request.user).order_by("-created_at")[:5]
    context = {
        "vehicles": vehicles,
        "orders": orders,
        "username": request.user.username, 
    }
    return render(request, "user_area.html", context)

@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "Você saiu da sua conta.")
    return redirect("home")
