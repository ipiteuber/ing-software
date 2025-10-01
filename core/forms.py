import re
from django import forms
from .models import Reserva, Cliente, Habitacion, Pago

def validar_rut_chileno(rut):
    rut = rut.upper().replace("-", "").replace(".", "")
    if not re.match(r'^\d{7,8}[0-9K]$', rut):
        raise forms.ValidationError("Formato de RUT inválido.")
    cuerpo = rut[:-1]
    dv = rut[-1]
    suma = 0
    multiplo = 2
    for c in reversed(cuerpo):
        suma += int(c) * multiplo
        multiplo = 9 if multiplo == 2 else multiplo - 1
    res = 11 - (suma % 11)
    dv_calc = "K" if res == 10 else "0" if res == 11 else str(res)
    if dv != dv_calc:
        raise forms.ValidationError("RUT inválido.")
    return rut

class ReservaForm(forms.Form):
    rut = forms.CharField(label="RUT", max_length=20)
    nombre = forms.CharField(label="Nombre", max_length=150)
    email = forms.EmailField(label="Email")
    telefono = forms.CharField(label="Teléfono", max_length=30)
    habitacion = forms.ModelChoiceField(queryset=Habitacion.objects.filter(estado="disponible"))
    fecha_inicio = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    fecha_fin = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    def clean_rut(self):
        return validar_rut_chileno(self.cleaned_data['rut'])

class ConsultaReservaForm(forms.Form):
    rut = forms.CharField(label="RUT", max_length=20)
    codigo = forms.CharField(label="Código de Reserva", max_length=16)

    def clean_rut(self):
        return validar_rut_chileno(self.cleaned_data['rut'])

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