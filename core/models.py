from django.db import models
import uuid
import secrets
from decimal import Decimal

def generate_reservation_code(length=8):
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_habitacion_id():
    return str(uuid.uuid4())

def generate_admin_id():
    return uuid.uuid4().hex

class Cliente(models.Model):
    rut = models.CharField(max_length=20)
    nombre = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.rut} - {self.nombre or 'Cliente'}"

class Habitacion(models.Model):
    ESTADO_CHOICES = [
        ("disponible", "Disponible"),
        ("ocupada", "Ocupada"),
        ("mantenimiento", "Mantenimiento"),
    ]
    id_habitacion = models.CharField(max_length=32, unique=True, default=generate_habitacion_id)
    tipo = models.CharField(max_length=100)
    capacidad = models.PositiveSmallIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="disponible")

    def __str__(self):
        return f"{self.id_habitacion} - {self.tipo}"

class Reserva(models.Model):
    ESTADO_RESERVA = [
        ("pendiente", "Pendiente"),
        ("confirmada", "Confirmada"),
        ("cancelada", "Cancelada"),
        ("completada", "Completada"),
    ]
    id_reserva = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=16, unique=True, default=generate_reservation_code)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="reservas")
    habitacion = models.ForeignKey(Habitacion, on_delete=models.PROTECT, related_name="reservas")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_RESERVA, default="pendiente")
    precio_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    monto_porcentaje = models.PositiveSmallIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def deposito_requerido(self):
        return (self.precio_total * Decimal(self.monto_porcentaje)) / Decimal(100)

    def __str__(self):
        return f"{self.codigo} ({self.cliente.rut})"

class Pago(models.Model):
    id_pago = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name="pagos")
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    metodo = models.CharField(max_length=20, blank=True)
    referencia = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"Pago {self.id_pago} - {self.monto} for {self.reserva.codigo}"

class Administrador(models.Model):
    id_admin = models.CharField(max_length=64, unique=True, default=generate_admin_id)
    nombre = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    session_token = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"{self.id_admin} - {self.nombre}"
