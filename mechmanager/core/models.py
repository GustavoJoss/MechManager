from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP

# Pega o modelo de usuário padrão do Django
User = settings.AUTH_USER_MODEL

# Classe base pra adicionar data de criação e atualização automática
class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True  # não cria tabela, só serve pra herança

# Modelo de mecânico da oficina
class Mechanic(TimeStamped):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

# Modelo de veículo, ligado a um dono (usuário)
class Vehicle(TimeStamped):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vehicles")
    plate = models.CharField("Placa", max_length=10, unique=True)
    make = models.CharField("Marca", max_length=60)
    model = models.CharField(max_length=80)
    year = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    def __str__(self):
        return f"{self.plate} - {self.make} {self.model} ({self.year})"

# Modelo de serviço (ex: troca de óleo, alinhamento)
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
    # ⏱️ tempo padrão por unidade (em minutos) — **aqui fica o tempo estimado**
    estimated_minutes = models.PositiveIntegerField(
        "Tempo padrão (min)",
        default=0,
        help_text="Tempo estimado por unidade do serviço (em minutos).",
    )
    is_active = models.BooleanField("Ativo", default=True)

    def __str__(self):
        return f"{self.name} (R${self.default_price})"

# Modelo da Ordem de Serviço (OS)
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

    @property
    def total(self) -> Decimal:
        """Soma dos subtotais dos itens (Decimal)."""
        total = sum((wi.subtotal for wi in self.items.all()), Decimal("0.00"))
        # normaliza para 2 casas
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def total_estimated_minutes(self) -> int:
        """Tempo total estimado da OS em minutos = Σ (qty × tempo_do_serviço)."""
        return sum(
            (it.quantity or 0) * (getattr(it.service, "estimated_minutes", 0) or 0)
            for it in self.items.select_related("service").all()
        )

    @property
    def total_estimated_hours(self) -> float:
        return round(self.total_estimated_minutes() / 60.0, 1)

# Modelo dos itens dentro de uma OS (serviço + quantidade + valor)
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

    @property
    def subtotal(self) -> Decimal:
        """Preço unitário × quantidade (Decimal)."""
        value = (self.unit_price or Decimal("0.00")) * Decimal(self.quantity or 0)
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def line_estimated_minutes(self) -> int:
        """Tempo estimado desta linha = qty × tempo padrão do serviço."""
        return (self.quantity or 0) * (getattr(self.service, "estimated_minutes", 0) or 0)

    # Atualiza o título da OS quando salva ou deleta
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_workorder_title()

    def delete(self, *args, **kwargs):
        wo = self.workorder
        super().delete(*args, **kwargs)
        self._update_workorder_title(wo)

    def _update_workorder_title(self, workorder=None):
        """Ex.: 'Troca de óleo | Alinhamento (+1)'."""
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