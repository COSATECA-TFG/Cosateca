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
    path('lista_deseos', views.lista_deseos, name='lista_deseos'),
    path('lista_deseos/eliminar/<int:objeto_id>', views.eliminar_objeto_lista_deseos, name='eliminar_objeto'),
    path('lista_deseos/agregar/<int:objeto_id>', views.agregar_objeto_lista_deseos, name='agregar_objeto'),
    path('usuario', views.detalles_usuario, name='usuario'),
    path('usuario/huella_carbono', views.consultar_huella_carbono_reducida, name='huella_carbono_reducida'),
    path('usuario/amonestaciones', views.consultar_amonestaciones, name='consultar_amonestaciones'),

    path('amonestar_usuario/<int:usuario_id>', views.amonestar_usuario, name='amonestar_usuario'),
  

    path('gestion_usuarios_administrador', views.gestion_usuarios_administrador, name='gestion_usuarios_administrador'),
    path('registro_gestor', views.registro_gestor, name='registro_gestor'),
    path('suspender_usuario/<int:usuario_id>', views.suspender_usuario, name='suspender_usuario'),
    path('consultar_amonestaciones_administrador/<int:usuario_id>', views.consultar_amonestaciones_administrador, name='consultar_amonestaciones_administrador'),    
]