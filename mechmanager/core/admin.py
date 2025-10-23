from django.contrib import admin
from .models import Mechanic, Vehicle, Service, WorkOrder, WorkItem

# Configuração da tela de Mecânicos no admin
@admin.register(Mechanic)
class MechanicAdmin(admin.ModelAdmin):
    list_display = ("name", "specialty", "is_active", "created_at")  # colunas que aparecem
    list_filter = ("is_active",)
    search_fields = ("name", "specialty")

# Tela de Veículos no admin
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("plate", "owner", "make", "model", "year")
    search_fields = ("plate", "owner__username", "make", "model")
    list_filter = ("year", "make")

# Tela de Serviços no admin
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "default_price", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)

# Permite editar itens (WorkItem) dentro da OS diretamente no admin
class WorkItemInline(admin.TabularInline):
    model = WorkItem
    extra = 1
    fk_name = "workorder"

# Tela principal das Ordens de Serviço (WorkOrder)
@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "vehicle", "assigned_mechanic", "status", "opened_at", "closed_at", "total")
    readonly_fields = ("title",)  # título é gerado automaticamente
    list_filter = ("status", "assigned_mechanic", "opened_at")
    search_fields = ("title", "vehicle__plate", "vehicle__owner__username", "notes")
    inlines = [WorkItemInline]  # mostra os itens da OS dentro da própria OS
