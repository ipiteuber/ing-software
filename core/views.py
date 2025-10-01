from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cliente, Habitacion, Reserva, Administrador, Pago
from .forms import ReservaForm, ConsultaReservaForm, AdminLoginForm, HabitacionForm, PagoSimuladoForm
from .decorators import admin_required

# ---------------------- Index ----------------------
def landing_page(request):
    return render(request, 'landing_page.html')

# ---------------------- Reservas ----------------------
def reservar(request):
    if request.method == "POST":
        form = ReservaForm(request.POST)
        if form.is_valid():
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
                fecha_inicio=form.cleaned_data['fecha_inicio'],
                fecha_fin=form.cleaned_data['fecha_fin'],
                precio_total=habitacion.precio,
            )
            habitacion.estado = "ocupada"
            habitacion.save()
            messages.success(request, f"Reserva creada. Código: {reserva.codigo}")
            return redirect('simular_pago', codigo=reserva.codigo)
    else:
        form = ReservaForm()
    return render(request, "reservar.html", {"form": form})

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
        return redirect('mis_reservas')
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
            return redirect('mis_reservas')
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