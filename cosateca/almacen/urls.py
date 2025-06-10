from django.urls import path
from . import views

urlpatterns = [
    path('almacenes', views.obtener_almacenes, name='almacenes'),
]