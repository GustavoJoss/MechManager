from django.contrib import admin
from .models import Mechanic, Vehicle, Service, WorkOrder, WorkItem

@admin.register(Mechanic)
class MechanicAdmin(admin.ModelAdmin):
    list_display = ("name", "specialty", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "specialty")

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("plate", "owner", "make", "model", "year")
    search_fields = ("plate", "owner__username", "make", "model")
    list_filter = ("year", "make")

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "default_price", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)

class WorkItemInline(admin.TabularInline):
    model = WorkItem
    extra = 1
    fk_name = "workorder"  # opcional; ajuda a evitar ambiguidade

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "vehicle", "assigned_mechanic", "status", "opened_at", "closed_at", "total")
    readonly_fields = ("title",)
    list_filter = ("status", "assigned_mechanic", "opened_at")
    search_fields = ("title", "vehicle__plate", "vehicle__owner__username", "notes")
    inlines = [WorkItemInline]
