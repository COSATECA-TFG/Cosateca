from django.urls import path
from . import views
from django.conf import settings


urlpatterns = [
    path('mis_reservas', views.historial_reservas, name='mis_reservas'),
    path('cancelar_reserva/<int:reserva_id>', views.cancelar_reserva, name='cancelar_reserva'),

]