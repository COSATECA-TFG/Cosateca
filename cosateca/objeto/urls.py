from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('catalogo', views.catalogo, name='catalogo'),
    path('catalogo/<int:objeto_id>', views.detalle_objeto, name='detalle_objeto'),
]#urls de objeto