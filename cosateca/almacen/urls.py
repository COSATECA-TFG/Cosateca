from django.urls import path
from . import views

urlpatterns = [
    path('almacenes', views.obtener_almacenes, name='almacenes'),
    path('valorar_almacen/<int:almacen_id>', views.obtener_almacen, name='almacen'),
    path('comentarios_almacen/<int:almacen_id>', views.obtener_comentarios, name='comentarios'),
    path('crear_valoracion_almacen/<int:almacen_id>', views.valorar_almacen, name='valoracion_almacen'),
    path('eliminar_valoracion_almacen/<int:comentario_id>', views.eliminar_valoracion_almacen, name='eliminar_valoracion_almacen'),
    path('denunciar_valoracion_almacen/<int:comentario_id>', views.denunciar_valoracion_almacen, name='denunciar_valoracion_almacen'),
]