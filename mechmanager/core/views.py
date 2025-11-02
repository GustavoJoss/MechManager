from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.db.models import Prefetch

from .forms import (
    SignUpForm,
    VehicleForm,
    WorkOrderForm,
    WorkItemFormSet,
)
from .models import Vehicle, WorkOrder, WorkItem


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
@login_required
def user_area(request):
    vehicles = (
        Vehicle.objects
        .filter(owner=request.user)
        .order_by("-created_at")[:5]
    )

    orders = (
        WorkOrder.objects
        .filter(vehicle__owner=request.user, customer_confirmed=False)
        .select_related("vehicle", "vehicle__owner", "assigned_mechanic")
        .prefetch_related(Prefetch("items", queryset=WorkItem.objects.select_related("service")))
        .order_by("-created_at")[:5]
    )

    def humanize(minutes: int) -> str:
        h, m = divmod(int(minutes or 0), 60)
        if h and m:  return f"{h}h {m}min"
        if h:       return f"{h}h"
        return f"{m}min"

    # anota os valores prontos para o template
    for wo in orders:
        mins = wo.total_estimated_minutes()
        wo.total_minutes = mins
        wo.total_hours = round(mins / 60, 1)
        wo.total_human = humanize(mins)

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
            formset.instance = wo                        # liga os itens à OS criada
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


@login_required
def confirmar_os_json(request, pk):
    wo = get_object_or_404(WorkOrder, pk=pk)
    
     # Dono do veículo (ou superuser) pode confirmar
    if not (request.user.is_superuser or wo.vehicle.owner_id == request.user.id):
        return HttpResponseForbidden("Sem permissão")

    # Marca como confirmado pelo cliente
    wo.customer_confirmed = True

    # Opcional: mover status de 'open' para 'in_progress'
    if wo.status == "open":
        wo.status = "in_progress"

    wo.save(update_fields=["customer_confirmed", "status"])

    return JsonResponse({"ok": True})


@login_required
def workorder_detail(request, pk: int):
    os_obj = get_object_or_404(
        WorkOrder.objects.select_related("vehicle", "vehicle__owner")
                         .prefetch_related("items__service"),
        pk=pk
    )

    # Permissão: dono do veículo ou superuser
    if not request.user.is_superuser and os_obj.vehicle.owner_id != request.user.id:
        return HttpResponseForbidden("Você não tem permissão para ver esta Ordem de Serviço")

    itens = []
    for it in os_obj.items.all():
        itens.append({
            "service": str(it.service),
            "quantity": int(it.quantity or 0),
            "unit_price": float(it.unit_price or 0),
            "total": float(it.subtotal),
            "estimated_minutes": it.line_estimated_minutes(),
        })

    created = getattr(os_obj, "created_at", None)
    total_minutes = os_obj.total_estimated_minutes()

    data = {
        "id": os_obj.id,
        "title": os_obj.title or "",                 # era description, corrigido para title
        "notes": os_obj.notes or "",                 # para mostrar nas observações
        "customer": (os_obj.vehicle.owner.get_full_name() or os_obj.vehicle.owner.username),
        "vehicle": {
            "plate": os_obj.vehicle.plate,
            "make": getattr(os_obj.vehicle, "make", ""),
            "model": getattr(os_obj.vehicle, "model", ""),
            "year": getattr(os_obj.vehicle, "year", ""),
        },
        "total": float(os_obj.total),
        "estimated_total_minutes": total_minutes,
        "estimated_total_hours": round(total_minutes / 60, 1),
        "created_at": created.isoformat() if created else None,
        "items": itens,
    }
    return JsonResponse(data, status=200)
