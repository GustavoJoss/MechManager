from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from .models import Vehicle, WorkOrder, WorkItem, Profile


# --- cadastro simples de usuário ---
class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    phone = forms.CharField(label="Telefone", max_length=20, required=False)  # <- novo campo

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            # Cria o profile automaticamente com o telefone
            Profile.objects.update_or_create(
                user=user,
                defaults={"phone": self.cleaned_data.get("phone", "")}
            )
        return user


# --- mixin para aplicar classes do Bootstrap automaticamente ---
class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            base = "form-control"
            if isinstance(field.widget, forms.Select):
                base = "form-select"          # selects usam classe do bootstrap própria
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css} {base}".strip()


# --- formulário de veículo ---
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
            "year": forms.NumberInput(attrs={"min": 1900, "max": 2100}),  # limite básico de ano
        }


# --- formulário de OS (sem itens) ---
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


# --- formulário de item da OS ---
class WorkItemForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = WorkItem
        fields = ["service", "quantity", "unit_price"]


# --- formset para gerenciar vários itens dentro da OS ---
WorkItemFormSet = inlineformset_factory(
    WorkOrder,
    WorkItem,
    form=WorkItemForm,
    extra=1,          # começa com 1 linha
    can_delete=True,  # permite remover linhas
)


# --- perfil do usuário (foto + dados básicos) ---
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["photo", "bio", "phone"]
        labels = {
            "photo": "Foto de perfil",
            "bio": "Biografia",
            "phone": "Telefone",
        }
        widgets = {
            # input escondido: é acionado pelo botão de câmera no template
            "photo": forms.FileInput(attrs={
                "accept": "image/*",
                "id": "id_photo",
                "class": "d-none",
            }),
            "bio": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
        }


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(label="Nome", required=False)
    last_name  = forms.CharField(label="Sobrenome", required=False)
    email      = forms.EmailField(label="E-mail", required=False)

    class Meta:
        model = Profile
        fields = ["photo", "bio", "phone"]
        labels = {"photo": "Foto", "bio": "Biografia", "phone": "Telefone"}
        widgets = {
            "photo": forms.FileInput(attrs={"accept": "image/*"}),
            "bio": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # inicializa campos do User
        if user:
            self.user = user
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial  = user.last_name
            self.fields["email"].initial      = user.email
        # aplica classes bootstrap
        for name, field in self.fields.items():
            if name == "photo":
                field.widget.attrs.setdefault("class", "form-control")
            else:
                base = "form-control"
                if isinstance(field.widget, forms.Select):
                    base = "form-select"
                css = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = f"{css} {base}".strip()

    def save(self, commit=True):
        profile = super().save(commit=False)
        # salva campos do User
        self.user.first_name = self.cleaned_data.get("first_name", "")
        self.user.last_name  = self.cleaned_data.get("last_name", "")
        self.user.email      = self.cleaned_data.get("email", "")
        if commit:
            self.user.save()
            profile.user = self.user
            profile.save()
        return profile
