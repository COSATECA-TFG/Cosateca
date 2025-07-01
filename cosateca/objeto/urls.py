from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('catalogo', views.catalogo, name='catalogo'),
    path('catalogo/<int:objeto_id>', views.detalle_objeto, name='detalle_objeto'),
    path('valorar_objeto/<int:objeto_id>', views.valorar_objeto, name='valorar_objeto'),
    path('comentarios_objeto/<int:objeto_id>', views.obtener_comentarios_objeto, name='comentarios_obj'),
    path('denunciar_valoracion_objeto/<int:comentario_id>', views.denunciar_valoracion_objeto, name='denunciar_valoracion_objeto'),
    path('eliminar_valoracion_objeto/<int:comentario_id>', views.eliminar_valoracion_objeto, name='eliminar_valoracion_objeto'),
    path('recomendaciones_personalizadas', views.lista_objetos_recomendados, name='recomendaciones_personalizadas'),

    path('gestion_objetos_gestor', views.gestion_objetos_gestor, name='gestion_objetos_gestor'),
    path('eliminar_articulo_gestor/<int:objeto_id>', views.eliminar_articulo_catalogo_gestor, name='eliminar_articulo_catalogo_gestor'),
    path('editar_articulo_gestor/<int:objeto_id>', views.editar_articulo_catalogo_gestor, name='editar_articulo_catalogo_gestor'),

]