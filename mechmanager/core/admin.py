from django.contrib import admin
from decimal import Decimal
from import_export import resources, fields
from import_export.widgets import DecimalWidget
from .models import Mechanic, Vehicle, Service, WorkOrder, WorkItem
from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import DecimalWidget
from import_export.admin import ImportExportModelAdmin
from decimal import Decimal
from .models import Service, Mechanic, Vehicle, WorkOrder, WorkItem

class ServiceResource(resources.ModelResource):
    # colunas do CSV (extras, não existem no model)
    category = fields.Field(attribute=None, column_name="category")
    price_min_brl = fields.Field(attribute=None, column_name="price_min_brl", widget=DecimalWidget())
    price_max_brl = fields.Field(attribute=None, column_name="price_max_brl", widget=DecimalWidget())
    estimated_hours = fields.Field(attribute=None, column_name="estimated_hours", widget=DecimalWidget())

    class Meta:
        model = Service
        import_id_fields = ("name",)
        # ➜ Inclua também os campos extras na whitelist:
        fields = (
            "name",
            "default_price",
            "estimated_minutes",
            "is_active",
            "description",
            "category",          # extra do CSV
            "price_min_brl",     # extra do CSV
            "price_max_brl",     # extra do CSV
            "estimated_hours",   # extra do CSV
        )

    def before_import_row(self, row, **kwargs):
        # horas -> minutos
        try:
            hours = Decimal(str(row.get("estimated_hours") or "0"))
        except Exception:
            hours = Decimal("0")
        row["estimated_minutes"] = int(hours * 60)

        # preço padrão: média entre min e max (troque se quiser usar o min)
        try:
            pmin = Decimal(str(row.get("price_min_brl") or "0"))
            pmax = Decimal(str(row.get("price_max_brl") or "0"))
        except Exception:
            pmin = pmax = Decimal("0")
        row["default_price"] = (pmin + pmax) / Decimal("2") if pmax > 0 else pmin

        # guardar categoria na descrição (opcional)
        cat = (row.get("category") or "").strip()
        row["description"] = cat
        row["is_active"] = True

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
    resource_classes = ServiceResource  # importa/exporta via CSV
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
