from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cliente, Habitacion, Reserva, Administrador, Pago
from .forms import ReservaForm, ConsultaReservaForm, AdminLoginForm, HabitacionForm, PagoSimuladoForm
from .decorators import admin_required
from django.db.models import Q
from django.utils.dateparse import parse_date
from datetime import datetime

# ---------------------- Index ----------------------
def landing_page(request):
    return render(request, 'landing_page.html')

# ---------------------- Reservas ----------------------
def reservar(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    habitaciones_disponibles = None

    # Validar fechas
    if fecha_inicio and fecha_fin:
        fecha_inicio = parse_date(fecha_inicio)
        fecha_fin = parse_date(fecha_fin)

        if fecha_inicio >= fecha_fin:
            messages.error(request, "La fecha de inicio debe ser anterior a la fecha de fin.")
            return render(request, "reservar.html", {
                "form": None,
                "fecha_inicio": None,
                "fecha_fin": None,
            })

        habitaciones_disponibles = Habitacion.objects.filter(
            estado="disponible"
        ).exclude(
            Q(reservas__fecha_inicio__lt=fecha_fin) & Q(reservas__fecha_fin__gt=fecha_inicio)
        ).distinct()

    if request.method == "POST":
        form = ReservaForm(request.POST)
        if habitaciones_disponibles is not None:
            form.fields['habitacion'].queryset = habitaciones_disponibles
        if form.is_valid():
            fecha_inicio_dt = form.cleaned_data['fecha_inicio']
            fecha_fin_dt = form.cleaned_data['fecha_fin']
            rut = form.cleaned_data['rut']
            cliente, _ = Cliente.objects.get_or_create(
                rut=rut,
                defaults={
                    'nombre': form.cleaned_data['nombre'],
                    'email': form.cleaned_data['email'],
                    'telefono': form.cleaned_data['telefono'],
                }
            )
            habitacion = form.cleaned_data['habitacion']
            reserva = Reserva.objects.create(
                cliente=cliente,
                habitacion=habitacion,
                fecha_inicio=fecha_inicio_dt,
                fecha_fin=fecha_fin_dt,
                precio_total=habitacion.precio,
            )
            messages.success(request, f"Reserva creada. Código: {reserva.codigo}")
            return redirect('simular_pago', codigo=reserva.codigo)
    else:
        if habitaciones_disponibles is not None and habitaciones_disponibles.exists():
            form = ReservaForm(initial={
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin
            })
            form.fields['habitacion'].queryset = habitaciones_disponibles
        else:
            form = None

    return render(request, "reservar.html", {
        "form": form,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    })

def mis_reservas(request):
    reserva = None
    if request.method == "POST":
        form = ConsultaReservaForm(request.POST)
        if form.is_valid():
            rut = form.cleaned_data['rut']
            codigo = form.cleaned_data['codigo']
            try:
                reserva = Reserva.objects.get(codigo=codigo, cliente__rut=rut)
            except Reserva.DoesNotExist:
                messages.error(request, "Reserva no encontrada.")
    else:
        form = ConsultaReservaForm()
    return render(request, "mis_reservas.html", {"form": form, "reserva": reserva})

def simular_pago(request, codigo):
    reserva = get_object_or_404(Reserva, codigo=codigo)

    if reserva.estado != "pendiente":
        messages.info(request, "Esta reserva ya fue pagada o no está disponible para pago.")
        return render(request, "simular_pago.html", {"reserva": reserva, "form": None})
    
    if request.method == "POST":
        form = PagoSimuladoForm(request.POST)
        if form.is_valid():
            Pago.objects.create(
                reserva=reserva,
                monto=reserva.deposito_requerido(),
                metodo=form.cleaned_data['metodo'],
                referencia=form.cleaned_data['referencia']
            )
            reserva.estado = "confirmada"
            reserva.save()
            messages.success(request, "Pago simulado exitosamente. ¡Reserva confirmada!")
            return render(request, "simular_pago.html", {"reserva": reserva, "form": None})
    else:
        form = PagoSimuladoForm()

    return render(request, "simular_pago.html", {"reserva": reserva, "form": form})

# ---------------------- Admin ----------------------
def login_admin(request):
    if request.method == "POST":
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            id_admin = form.cleaned_data['id_admin']
            email = form.cleaned_data['email']
            try:
                admin = Administrador.objects.get(id_admin=id_admin, email=email)
                request.session['admin_id'] = admin.id_admin
                return redirect('gestion_reservas')
            except Administrador.DoesNotExist:
                messages.error(request, "Credenciales incorrectas.")
    else:
        form = AdminLoginForm()
    return render(request, "login_admin.html", {"form": form})


@admin_required
def gestion_reservas(request):
    habitaciones = Habitacion.objects.all()
    return render(request, "gestion_reservas.html", {"habitaciones": habitaciones})

@admin_required
def agregar_habitacion(request):
    if request.method == "POST":
        form = HabitacionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion_reservas')
    else:
        form = HabitacionForm()
    return render(request, "habitacion_form.html", {"form": form, "accion": "Agregar"})

@admin_required
def editar_habitacion(request, id_habitacion):
    habitacion = get_object_or_404(Habitacion, id_habitacion=id_habitacion)
    if request.method == "POST":
        form = HabitacionForm(request.POST, instance=habitacion)
        if form.is_valid():
            form.save()
            return redirect('gestion_reservas')
    else:
        form = HabitacionForm(instance=habitacion)
    return render(request, "habitacion_form.html", {"form": form, "accion": "Editar"})

@admin_required
def eliminar_habitacion(request, id_habitacion):
    habitacion = get_object_or_404(Habitacion, id_habitacion=id_habitacion)
    if request.method == "POST":
        habitacion.delete()
        return redirect('gestion_reservas')
    return render(request, "habitacion_confirm_delete.html", {"habitacion": habitacion})

def logout_admin(request):
    request.session.flush()
    return render(request, "logout_admin.html")

@admin_required
def eliminar_admin(request):
    admin_id = request.session.get('admin_id')
    admin = get_object_or_404(Administrador, id_admin=admin_id)
    if request.method == "POST":
        admin.delete()
        request.session.flush()
        return redirect('login_admin')
    return render(request, "sesion_admin.html", {"admin": admin})