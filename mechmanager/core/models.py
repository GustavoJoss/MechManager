from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Mechanic(TimeStamped):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class Vehicle(TimeStamped):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vehicles")
    plate = models.CharField("Placa", max_length=10, unique=True)
    make = models.CharField("Marca", max_length=60)
    model = models.CharField(max_length=80)
    year = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    def __str__(self):
        return f"{self.plate} - {self.make} {self.model} ({self.year})"

class Service(TimeStamped):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    default_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name} (R${self.default_price})"

class WorkOrder(TimeStamped):
    STATUS = [
        ("open", "Aberta"),
        ("in_progress", "Em execução"),
        ("done", "Concluída"),
        ("canceled", "Cancelada"),
    ]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="work_orders")
    opened_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="opened_orders")
    assigned_mechanic = models.ForeignKey(Mechanic, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS, default="open")
    opened_at = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    def __str__(self):
        return f"OS #{self.pk} - {self.vehicle.plate} [{self.get_status_display()}]"
    @property
    def total(self):
        agg = sum([wi.subtotal for wi in self.items.all()], 0)
        return round(agg, 2)

class WorkItem(TimeStamped):
    workorder = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name="items")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="work_items")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    def __str__(self):
        return f"{self.service.name} x{self.quantity} (OS #{self.workorder_id})"
    @property
    def subtotal(self):
        return round(self.quantity * self.unit_price, 2)