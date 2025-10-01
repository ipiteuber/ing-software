import re
from django import forms
from django.core.exceptions import ValidationError
from .models import Reserva, Cliente, Habitacion, Pago


def validar_rut_chileno(rut):
    rut = str(rut).replace(".", "").replace("-", "").upper()
    if not re.match(r"^\d{7,8}[0-9K]$", rut):
        raise ValidationError("RUT invalido. Debe ser 7 u 8 numeros y un digito verificador.")
    return rut

class ReservaForm(forms.Form):
    rut = forms.CharField(label="RUT", max_length=12)
    nombre = forms.CharField(label="Nombre", max_length=150)
    email = forms.EmailField(label="Email")
    telefono = forms.CharField(label="Telefono", max_length=30)
    habitacion = forms.ModelChoiceField(queryset=Habitacion.objects.filter(estado="disponible"))
    fecha_inicio = forms.DateField(widget=forms.HiddenInput(), input_formats=['%Y-%m-%d'])
    fecha_fin = forms.DateField(widget=forms.HiddenInput(), input_formats=['%Y-%m-%d'])
    
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        return validar_rut_chileno(rut)

class ConsultaReservaForm(forms.Form):
    rut = forms.CharField(label="RUT", max_length=12)
    codigo = forms.CharField(label="Código de Reserva", max_length=16)

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        return validar_rut_chileno(rut)

class AdminLoginForm(forms.Form):
    id_admin = forms.CharField(label="ID Administrador", max_length=64)
    email = forms.EmailField(label="Email")

class HabitacionForm(forms.ModelForm):
    class Meta:
        model = Habitacion
        fields = ['tipo', 'capacidad', 'precio', 'estado']

# Simulación de pago
class PagoSimuladoForm(forms.Form):
    metodo = forms.ChoiceField(choices=[('tarjeta', 'Tarjeta'), ('transferencia', 'Transferencia'), ('efectivo', 'Efectivo')])
    referencia = forms.CharField(label="Referencia o comentario", max_length=120, required=False)