from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django import forms
import re

# pega o modelo de usuário padrão do Django
User = settings.AUTH_USER_MODEL


# modelo base com datas automáticas
class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True  # não cria tabela, só serve pra herança


# modelo de mecânico
class Mechanic(TimeStamped):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# modelo de veículo, ligado a um dono (usuário)
class Vehicle(TimeStamped):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vehicles")
    plate = models.CharField("Placa", max_length=10, unique=True)
    make = models.CharField("Marca", max_length=60)
    model = models.CharField(max_length=80)
    year = models.PositiveIntegerField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.plate} - {self.make} {self.model} ({self.year})"


# modelo de serviço (ex: troca de óleo, alinhamento)
class Service(TimeStamped):
    name = models.CharField("Serviço", max_length=100)
    description = models.TextField("Descrição", blank=True)
    default_price = models.DecimalField(
        "Preço padrão",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal("0.00"),
    )
    estimated_minutes = models.PositiveIntegerField(
        "Tempo padrão (min)",
        default=0,
        help_text="Tempo estimado do serviço em minutos",
    )
    is_active = models.BooleanField("Ativo", default=True)

    def __str__(self):
        return f"{self.name} (R${self.default_price})"


# modelo de ordem de serviço (OS)
class WorkOrder(TimeStamped):
    STATUS = [
        ("open", "Aberta"),
        ("in_progress", "Em execução"),
        ("done", "Concluída"),
        ("canceled", "Cancelada"),
    ]

    title = models.CharField("Título da OS", max_length=100, blank=True, default="")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="work_orders")
    opened_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="opened_orders"
    )
    assigned_mechanic = models.ForeignKey(
        Mechanic, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    status = models.CharField("Status", max_length=20, choices=STATUS, default="open")
    opened_at = models.DateTimeField("Abertura", default=timezone.now)
    closed_at = models.DateTimeField("Fechamento", null=True, blank=True)
    notes = models.TextField("Notas", blank=True)
    customer_confirmed = models.BooleanField("Confirmada pelo cliente", default=False)

    def __str__(self):
        return self.title or f"OS #{self.pk} - {self.vehicle.plate} [{self.get_status_display()}]"

    # soma o total dos serviços
    @property
    def total(self) -> Decimal:
        total = sum((wi.subtotal for wi in self.items.all()), Decimal("0.00"))
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # soma o tempo estimado total da OS (em minutos)
    def total_estimated_minutes(self) -> int:
        return sum(
            (it.quantity or 0) * (getattr(it.service, "estimated_minutes", 0) or 0)
            for it in self.items.select_related("service").all()
        )

    # tempo total estimado em horas
    @property
    def total_estimated_hours(self) -> float:
        return round(self.total_estimated_minutes() / 60.0, 1)


# itens dentro da OS (serviço + quantidade + valor)
class WorkItem(TimeStamped):
    workorder = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name="items")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="work_items")
    quantity = models.PositiveIntegerField("Quantidade", default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        "Preço unitário",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal("0.00"),
    )

    def __str__(self):
        return f"{self.service.name} x{self.quantity} (OS #{self.workorder_id})"

    # calcula subtotal do item
    @property
    def subtotal(self) -> Decimal:
        value = (self.unit_price or Decimal("0.00")) * Decimal(self.quantity or 0)
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # tempo total estimado dessa linha (serviço x quantidade)
    def line_estimated_minutes(self) -> int:
        return (self.quantity or 0) * (getattr(self.service, "estimated_minutes", 0) or 0)

    # atualiza o título da OS sempre que um item é salvo
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_workorder_title()

    # também atualiza quando deleta
    def delete(self, *args, **kwargs):
        wo = self.workorder
        super().delete(*args, **kwargs)
        self._update_workorder_title(wo)

    # gera o título automático da OS (ex: "Troca de óleo | Alinhamento (+1)")
    def _update_workorder_title(self, workorder=None):
        workorder = workorder or self.workorder
        items = workorder.items.order_by("created_at", "id").select_related("service")

        if not items.exists():
            workorder.title = ""
            workorder.save(update_fields=["title"])
            return

        seen, names = set(), []
        for wi in items:
            name = wi.service.name
            if name not in seen:
                seen.add(name)
                names.append(name)

        if len(names) <= 2:
            title = " | ".join(names)
        else:
            title = " | ".join(names[:2]) + f" (+{len(names) - 2})"

        workorder.title = title[:100]
        workorder.save(update_fields=["title"])


# perfil do usuário (foto, bio e telefone)
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Perfil de {self.user}"


# cria automaticamente o perfil quando o usuário é criado
    @receiver(post_save, sender=get_user_model())
    def ensure_user_profile(sender, instance, created, **kwargs):
        Profile.objects.get_or_create(user=instance)

    @property
    def phone_formatted(self):
        """Retorna o telefone no formato (99) 99999-9999"""
        if not self.phone:
            return ""
        digits = re.sub(r"\D", "", self.phone)
        if len(digits) == 11:
            return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
        elif len(digits) == 10:
            return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
        return self.phone
