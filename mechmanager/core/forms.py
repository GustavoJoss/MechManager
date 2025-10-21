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

class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ["vehicle", "assigned_mechanic", "status", "notes"]

class WorkItemForm(forms.ModelForm):
    class Meta:
        model = WorkItem
        fields = ["service", "quantity", "unit_price"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"min": 1}),
            "unit_price": forms.NumberInput(attrs={"step": "0.01", "min": 0}),
        }
WorkItemFormSet = inlineformset_factory(
    WorkOrder,
    WorkItem,
    form=WorkItemForm,
    extra=2,
    can_delete=True,
)
