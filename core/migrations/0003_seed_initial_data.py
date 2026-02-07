from django.db import migrations
from decimal import Decimal


def seed_data(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Administrador = apps.get_model('core', 'Administrador')
    Cliente = apps.get_model('core', 'Cliente')
    Habitacion = apps.get_model('core', 'Habitacion')
    Reserva = apps.get_model('core', 'Reserva')

    # 1. Django superuser (para /admin/)
    from django.contrib.auth.hashers import make_password
    if not User.objects.filter(username='admin').exists():
        User.objects.create(
            username='admin',
            email='admin@hotel.com',
            password=make_password('admin123'),
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )

    # 2. Administrador del hotel (para /login_admin/)
    admin, _ = Administrador.objects.get_or_create(
        id_admin='admin001',
        defaults={
            'nombre': 'Administrador Hotel',
            'email': 'admin@hotel.com',
        }
    )

    # 3. Habitaciones
    habitaciones_data = [
        {'id_habitacion': 'HAB001', 'tipo': 'Suite', 'capacidad': 2, 'precio': Decimal('80000.00')},
        {'id_habitacion': 'HAB002', 'tipo': 'Doble', 'capacidad': 2, 'precio': Decimal('50000.00')},
        {'id_habitacion': 'HAB003', 'tipo': 'Familiar', 'capacidad': 4, 'precio': Decimal('120000.00')},
        {'id_habitacion': 'HAB004', 'tipo': 'Individual', 'capacidad': 1, 'precio': Decimal('35000.00')},
    ]
    for hab_data in habitaciones_data:
        Habitacion.objects.get_or_create(
            id_habitacion=hab_data['id_habitacion'],
            defaults={
                'tipo': hab_data['tipo'],
                'capacidad': hab_data['capacidad'],
                'precio': hab_data['precio'],
                'estado': 'disponible',
            }
        )

    # 4. Cliente de ejemplo
    cliente, _ = Cliente.objects.get_or_create(
        rut='123456789',
        defaults={
            'nombre': 'Juan Pérez',
            'email': 'juan@test.com',
            'telefono': '+56912345678',
        }
    )

    # 5. Reserva de ejemplo (confirmada)
    from datetime import date, timedelta
    suite = Habitacion.objects.get(id_habitacion='HAB001')
    fecha_inicio = date.today() + timedelta(days=1)
    fecha_fin = fecha_inicio + timedelta(days=7)

    if not Reserva.objects.filter(codigo='DEMO0001').exists():
        Reserva.objects.create(
            codigo='DEMO0001',
            cliente=cliente,
            habitacion=suite,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado='confirmada',
            precio_total=Decimal('560000.00'),
            monto_porcentaje=30,
        )


def reverse_seed(apps, schema_editor):
    """Reverse: borrar datos de seed si se revierte la migración."""
    User = apps.get_model('auth', 'User')
    Administrador = apps.get_model('core', 'Administrador')
    Cliente = apps.get_model('core', 'Cliente')
    Habitacion = apps.get_model('core', 'Habitacion')
    Reserva = apps.get_model('core', 'Reserva')

    Reserva.objects.filter(codigo='DEMO0001').delete()
    Cliente.objects.filter(rut='123456789').delete()
    Habitacion.objects.filter(id_habitacion__in=['HAB001', 'HAB002', 'HAB003', 'HAB004']).delete()
    Administrador.objects.filter(id_admin='admin001').delete()
    User.objects.filter(username='admin').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_reserva_fecha_fin_alter_reserva_fecha_inicio'),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_seed),
    ]
