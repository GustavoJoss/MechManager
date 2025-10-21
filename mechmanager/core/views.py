from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST

from .forms import (
    SignUpForm,
    VehicleForm,
    WorkOrderForm,
    WorkItemFormSet,
)
from .models import Vehicle, WorkOrder


# -------------------- PÚBLICO --------------------

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


# -------------------- ÁREA DO USUÁRIO --------------------

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


# -------------------- PERMISSÃO: SUPERUSER --------------------

def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)


# -------------------- CRUD NA UI (apenas superuser) --------------------

@superuser_required
def vehicle_create(request):
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Veículo cadastrado com sucesso.")
            return redirect("user_area")
    else:
        form = VehicleForm()
    # sempre retorna algo (GET ou POST inválido)
    return render(request, "vehicle_form.html", {"form": form})


@superuser_required
def workorder_create(request):
    if request.method == "POST":
        form = WorkOrderForm(request.POST)
        formset = WorkItemFormSet(request.POST)          # monta o formset sem instance
        if form.is_valid() and formset.is_valid():
            wo = form.save(commit=False)
            wo.opened_by = request.user
            wo.save()
            formset.instance = wo                        # agora liga os itens à OS criada
            formset.save()
            messages.success(request, "Ordem de serviço criada com sucesso.")
            return redirect("user_area")
    else:
        form = WorkOrderForm()
        formset = WorkItemFormSet()
    # sempre retorna algo (GET ou POST inválido)
    return render(request, "workorder_form.html", {"form": form, "formset": formset})


# -------------------- AÇÕES DO CLIENTE --------------------

@login_required
@require_POST
def confirm_workorder(request, pk):
    wo = get_object_or_404(WorkOrder, pk=pk)
    # dono do veículo pode confirmar; superuser também
    if request.user.is_superuser or wo.vehicle.owner_id == request.user.id:
        wo.customer_confirmed = True                     # nome do campo correto
        wo.save(update_fields=["customer_confirmed"])
        messages.success(request, "Serviço confirmado com sucesso!")
    else:
        messages.error(request, "Você não tem permissão para confirmar esta OS.")
    return redirect("user_area")
