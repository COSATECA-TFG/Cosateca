from django.urls import path
from . import views

urlpatterns = [
    path('almacenes', views.obtener_almacenes, name='almacenes'),
    path('valorar_almacen/<int:almacen_id>', views.obtener_almacen, name='almacen'),
    path('comentarios_almacen/<int:almacen_id>', views.obtener_comentarios, name='comentarios'),
    path('crear_valoracion_almacen/<int:almacen_id>', views.valorar_almacen, name='valoracion_almacen'),
    path('eliminar_valoracion_almacen/<int:comentario_id>', views.eliminar_valoracion_almacen, name='eliminar_valoracion_almacen'),
    path('denunciar_valoracion_almacen/<int:comentario_id>', views.denunciar_valoracion_almacen, name='denunciar_valoracion_almacen'),

    path('gestion_almacenes_administrador', views.obtener_almacenes, name='almacenes_administrador'),
    path('crear_almacen', views.crear_almacen, name='crear_almacen'),
    path('editar_almacen/<int:almacen_id>', views.editar_almacen, name='editar_almacen'),
    path('eliminar_almacen/<int:almacen_id>', views.eliminar_almacen, name='eliminar_almacen'),
]