from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from .models import Vehicle, WorkOrder, WorkItem

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ["username", "email", "password"]



class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            base = "form-control"
            if isinstance(field.widget, forms.Select):
                base = "form-select"
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css} {base}".strip()

class VehicleForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["owner", "plate", "make", "model", "year", "notes"]
        labels = {
            "owner": "Proprietário",
            "plate": "Placa",
            "make": "Marca",
            "model": "Modelo",
            "year": "Ano",
            "notes": "Notas",
        }
        widgets = {
            "year": forms.NumberInput(attrs={"min": 1900, "max": 2100}),
        }


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
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
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