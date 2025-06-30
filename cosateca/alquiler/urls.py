from django.urls import path
from . import views
from django.conf import settings


urlpatterns = [
    path('mis_reservas', views.historial_reservas, name='mis_reservas'),
    path('cancelar_reserva/<int:reserva_id>', views.cancelar_reserva, name='cancelar_reserva'),
    path('editar_reserva/<int:reserva_id>', views.editar_reserva, name='editar_reserva'),
    path('reservas_ocupadas/<int:objeto_id>/', views.reservas_ocupadas, name='reservas_ocupadas'),

    path('gestion_reservas_gestor', views.gestion_reserva_gestor, name='gestion_reserva_gestor'),

]