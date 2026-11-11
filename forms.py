from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class RegistroClienteForm(UserCreationForm):
    nombre = forms.CharField(
        max_length=120,
        label="Nombre completo",
        required=True,
        error_messages={"required": "Por favor ingresa tu nombre completo."}
    )
    telefono = forms.CharField(
        max_length=20,
        label="Teléfono",
        required=True,
        error_messages={"required": "Por favor ingresa un número de teléfono de contacto."}
    )
    correo = forms.EmailField(
        label="Correo electrónico",
        required=True,
        error_messages={
            "required": "Por favor ingresa tu correo electrónico.",
            "invalid": "Ingresa una dirección de correo válida."
        }
    )

    class Meta:
        model = User
        fields = ["username", "nombre", "telefono", "correo", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Nombre de usuario"
        self.fields["username"].error_messages["required"] = "El nombre de usuario es obligatorio."
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Confirmar contraseña"
        self.fields["password2"].error_messages["required"] = "Debes confirmar la contraseña."

    def clean_correo(self):
        correo = self.cleaned_data.get("correo", "").strip().lower()
        if User.objects.filter(email__iexact=correo).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado con otra cuenta.")
        return correo

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está ocupado. Prueba con otro.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["correo"].strip().lower()
        nombre = self.cleaned_data["nombre"].strip()
        parts = nombre.split(" ", 1)
        user.first_name = parts[0]
        if len(parts) > 1:
            user.last_name = parts[1]
        if commit:
            user.save()
        return user
