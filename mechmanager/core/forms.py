from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from .models import Vehicle, WorkOrder, WorkItem

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ["username", "email", "password"]

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["owner", "plate", "make", "model", "year", "notes"]

class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            base = "form-control"
            if isinstance(field.widget, forms.Select):
                base = "form-select"
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css} {base}".strip()

class WorkOrderForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ["vehicle", "assigned_mechanic", "status", "notes"]
        labels = {
            "vehicle": "Veículo",
            "assigned_mechanic": "Mecânico responsável",
            "status": "Status",
            "notes": "Notas",
        }
        # (Opcional) pode manter widgets específicos:
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),  # classe será adicionada pelo mixin
        }

class WorkItemForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = WorkItem
        fields = ["service", "quantity", "unit_price"]

WorkItemFormSet = forms.inlineformset_factory(
    WorkOrder,
    WorkItem,
    form=WorkItemForm,
    extra=1,
    can_delete=True,
)