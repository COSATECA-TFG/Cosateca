from django.urls import path
from . import views
from django.conf import settings


urlpatterns = [
    path('mis_reservas', views.historial_reservas, name='mis_reservas'),

]