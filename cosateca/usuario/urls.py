from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('registro', views.registro, name='registro'),
    path('inicio_sesion', views.inicio_sesion, name='inicio_sesion'),
]