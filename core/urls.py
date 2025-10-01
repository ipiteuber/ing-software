from django.urls import path
from . import views

urlpatterns = [
# ---------------------- Index ----------------------
    path('', views.landing_page, name='landing_page'),

# ---------------------- Reservas ----------------------
    path('reservar/', views.reservar, name='reservar'),
    path('mis_reservas/', views.mis_reservas, name='mis_reservas'),

# ---------------------- Admin ----------------------
    path('login_admin/', views.login_admin, name='login_admin'),
    path('gestion_reservas/', views.gestion_reservas, name='gestion_reservas'),
    path('logout_admin/', views.logout_admin, name='logout_admin'),
    path('eliminar_admin/', views.eliminar_admin, name='eliminar_admin'),

# ---------------------- Habitaciones ----------------------
    path('habitacion/agregar/', views.agregar_habitacion, name='agregar_habitacion'),
    path('habitacion/<str:id_habitacion>/editar/', views.editar_habitacion, name='editar_habitacion'),
    path('habitacion/<str:id_habitacion>/eliminar/', views.eliminar_habitacion, name='eliminar_habitacion'),

# ---------------------- Pagos ----------------------
    path('pago/<str:codigo>/', views.simular_pago, name='simular_pago'),
]