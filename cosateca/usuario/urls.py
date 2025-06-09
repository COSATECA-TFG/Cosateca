from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('registro', views.registro, name='registro'),
    path('inicio_sesion', views.inicio_sesion, name='inicio_sesion'),
    path('cuestionario_preferencias', views.cuestionario_preferencias, name='cuestionario_preferencias'),
    path('menu', views.menu, name='menu'),
    path('cerrar_sesion', views.cerrar_sesion, name='cerrar_sesion'),
    path('catalogo', views.catalogo, name='catalogo'),
    path('catalogo/<int:objeto_id>', views.detalle_objeto, name='detalle_objeto'),
]