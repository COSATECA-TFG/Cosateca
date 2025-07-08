from django.test import TestCase, Client
from objeto.models import Objeto, ObjetoValoracion
from django.urls import reverse
from usuario.models import Usuario, Preferencia, Gestor
from almacen.models import Almacen, Localizacion
from datetime import date
from django.contrib.messages import get_messages



class ObjetoViewTest(TestCase):
    def setUp(self):

        self.client = Client()

        self.user = Usuario.objects.create_user(
        username='usuario_test',
        password='test12345',
        email='test@example.com',
        first_name='Test',
        last_name='User',
        fecha_nacimiento=date(1990, 1, 1),
        sexo='NB',
        telefono='600000000',
        dni='12345678X'
        )

        self.user2 = Usuario.objects.create_user(
        username='usuario_test2',
        password='test12345',
        email='test2@example.com',
        first_name='Test2',
        last_name='User2',
        fecha_nacimiento=date(1990, 1, 1),
        sexo='NB',
        telefono='800000000',
        dni='12345679X'
        )

        self.cuestionario_preferencias = Preferencia.objects.create(
        usuario=self.user2,
        tarea_tipo='Bricolaje',
        frecuencia_uso='Semanal',
        experiencia='Intermedio',
        franja_horaria='Tarde'
        )

        self.localizacion_prueba = Localizacion.objects.create(
            latitud = 12.345678,
            longitud = 98.765432,
            calle = "Calle de prueba",
            numero = "1",
            pais = "País de prueba",
            ciudad = "Ciudad de prueba",
            codigo_postal = "12345"
        )

        self.localizacion_prueba2 = Localizacion.objects.create(
            latitud = 13.345678,
            longitud = 97.765432,
            calle = "Calle de prueba 2",
            numero = "2",
            pais = "País de prueba 2",
            ciudad = "Ciudad de prueba 2",
            codigo_postal = "12045"
        )
        
        self.almacen = Almacen.objects.create(
            id=1,
            nombre="Almacen test 1",
            descripcion="Descripción del almacén de prueba 1",
            localizacion = self.localizacion_prueba
        )


        self.gestor = Gestor.objects.create_user(
        username='gestor_test',
        password='test12345',
        email='testGestor@example.com',
        first_name='Test',
        last_name='User',
        fecha_nacimiento=date(1990, 1, 1),
        sexo='NB',
        telefono='600000001',
        dni='12345674X',
        almacen=self.almacen

        )

        self.almacen2 = Almacen.objects.create(
            id=2,
            nombre="Almacen test 2",
            descripcion="Descripción del almacén de prueba 2",
            localizacion = self.localizacion_prueba2
        )

        self.objeto = Objeto.objects.create(
        nombre='Objeto de prueba',
        descripcion='Descripción del objeto de prueba',
        imagen='https://i.blogs.es/f7234d/imagen/1200_800.webp',
        categoria='Herramientas',
        condicion='Bueno',
        huella_carbono=10.00,
        almacen=self.almacen
        )

        self.objeto2 = Objeto.objects.create(
        nombre='Objeto de prueba 2',
        descripcion='Descripción del objeto de prueba 2',
        imagen='https://i.blogs.es/f7234d/imagen/1200_800.webp',
        categoria='Bricolaje',
        condicion='Nuevo',
        huella_carbono=10.00,
        almacen=self.almacen2
        )

        self.valoracion = ObjetoValoracion.objects.create(
            objeto=self.objeto, 
            usuario=self.user2, 
            estrellas=5, 
            comentario="Comentario de prueba"
            )

        self.catalogo_url = reverse('catalogo')
        self.detalle_objeto_url = reverse('detalle_objeto', args=[self.objeto.id])
        self.detalle_objeto_url2 = reverse('detalle_objeto', args=[0]) # Objeto no existente
        self.valorar_objeto_url = reverse('valorar_objeto', args=[self.objeto.id])
        self.obtener_comentarios_objeto_url = reverse('comentarios_obj', args=[self.objeto.id])
        self.denunciar_valoracion_objeto_url = reverse('denunciar_valoracion_objeto', args=[self.valoracion.id])
        self.eliminar_valoracion_objeto_url = reverse('eliminar_valoracion_objeto', args=[self.valoracion.id])
        self.lista_objetos_recomendados_url = reverse('recomendaciones_personalizadas')

        self.gestion_objetos_gestor_url = reverse('gestion_objetos_gestor')
        self.eliminar_articulo_catalogo_gestor_url =  lambda objeto_id: reverse('eliminar_articulo_catalogo_gestor', kwargs={'objeto_id': objeto_id})
        self.test_editar_articulo_catalogo_gestor_url = lambda objeto_id: reverse('editar_articulo_catalogo_gestor', kwargs={'objeto_id': objeto_id})
        self.crear_articulo_catalogo_gestor_url = reverse('crear_articulo_catalogo_gestor')

    def test_catalogo_valido(self):
        self.client.login(username='usuario_test2', password='test12345')
        response = self.client.get(self.catalogo_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo.html')
        self.assertEqual(len(response.context['herramientas']), 2)

    def test_catalogo_valido_con_recomendaciones_destacadas(self):
        self.client.login(username='usuario_test2', password='test12345')
        response = self.client.get(self.catalogo_url, {'recomendaciones_destacadas': True})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo.html')
        self.assertEqual(len(response.context['herramientas']), 2)
        self.assertEqual(response.context['herramientas'][0].nombre, 'Objeto de prueba') # Al tener una valoración de 5 estrellas, su valoración media es 5, y debería aparecer primero
        self.assertEqual(response.context['herramientas'][1].nombre, 'Objeto de prueba 2') # Al no tener valoraciones, su valoración media es 0, y debería aparecer segundo

    def test_catalogo_valido_con_filtros(self):
        self.client.login(username='usuario_test2', password='test12345')
        response = self.client.get(self.catalogo_url, {'categoria': 'Bricolaje'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo.html')
        self.assertEqual(len(response.context['herramientas']), 1)
        self.assertEqual(response.context['herramientas'][0].categoria, 'Bricolaje')

    def test_catalogo_valido_con_busqueda(self):
        self.client.login(username='usuario_test2', password='test12345')
        response = self.client.get(self.catalogo_url, {'nombre_herramienta': 'Objeto de prueba'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo.html')
        self.assertEqual(len(response.context['herramientas']), 2)
        self.assertEqual(response.context['herramientas'][0].nombre, 'Objeto de prueba')
        self.assertEqual(response.context['herramientas'][1].nombre, 'Objeto de prueba 2')

    def test_catalogo_invalido(self):
        response = self.client.get(self.catalogo_url)
        self.assertEqual(response.status_code, 302)

    def test_detalle_objeto_valido(self):
        self.client.login(username='usuario_test2', password='test12345')
        response = self.client.get(self.detalle_objeto_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detalle_objeto.html')
        self.assertEqual(response.context['objeto'].nombre, "Objeto de prueba")
        self.assertEqual(response.context['objeto'].descripcion, "Descripción del objeto de prueba")
        self.assertEqual(response.context['objeto'].categoria, "Herramientas")
        self.assertEqual(response.context['objeto'].condicion, "Bueno")
        self.assertEqual(response.context['objeto'].huella_carbono, 10.00)

    def test_detalle_objeto_invalido(self):
        self.client.login(username='usuario_test2', password='test12345')
        response = self.client.get(self.detalle_objeto_url2)
        self.assertRedirects(response, self.catalogo_url)

    def test_post_detalle_objeto_valido(self):
        self.client.login(username='usuario_test2', password='test12345')
        response = self.client.post(self.detalle_objeto_url, {
            'fecha_inicio_principal': '2026-01-01',
            'fecha_fin_principal': '2026-01-10'
        })
        self.assertRedirects(response, '/mis_reservas')
        response2 = self.client.get(self.detalle_objeto_url)
        self.assertEqual(response2.context['objeto'].reservas.count(), 1)

    def test_post_detalle_objeto_invalido(self):
        self.client.login(username='usuario_test2', password='test12345')
        response = self.client.post(self.detalle_objeto_url, {
            'fecha_inicio_principal': '2026-01-10',
            'fecha_fin_principal': '2025-01-01'
        })
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(messages[0].message, "Las fechas de inicio y fin deben ser válidas y la fecha de inicio no puede ser posterior a la fecha de fin.")
        self.assertTemplateUsed(response, 'detalle_objeto.html')

    def test_valorar_objeto_valido(self):
        self.client.login(username='usuario_test', password='test12345')
        response = self.client.post(self.valorar_objeto_url, {
            'puntuacion': 4,
            'comentario': 'Buen objeto'
        })
        self.assertRedirects(response, self.obtener_comentarios_objeto_url)
        self.assertEqual(ObjetoValoracion.objects.count(), 2)
        valoracion = ObjetoValoracion.objects.last()
        self.assertEqual(valoracion.estrellas, 4)
        self.assertEqual(valoracion.comentario, 'Buen objeto')
    
    def test_valorar_objeto_invalido(self):
        self.client.login(username='usuario_test', password='test12345')
        response = self.client.post(self.valorar_objeto_url, {
            'puntuacion': '',
            'comentario': ''
        })
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(messages[0].message, 'No se puede valorar un objeto sin puntuación o comentario.')
        self.assertTemplateUsed(response, 'objeto_valoracion.html')

    def test_obtener_comentarios_objeto_valido(self):
        self.client.login(username='usuario_test2', password='test12345')
        response = self.client.get(self.obtener_comentarios_objeto_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comentarios_objeto.html')
        self.assertEqual(len(response.context['valoraciones']), 1)
        self.assertEqual(response.context['valoraciones'][0].estrellas, 5)
        self.assertEqual(response.context['valoraciones'][0].comentario, "Comentario de prueba")

    def test_obtener_comentarios_objeto_invalido(self):
        response = self.client.get(self.obtener_comentarios_objeto_url)
        self.assertEqual(response.status_code, 302)
    
    def test_denunciar_valoracion_objeto_valido(self):
        self.client.login(username='usuario_test', password='test12345')
        response = self.client.post(self.denunciar_valoracion_objeto_url, {
            'categoria': 'Otra',
            'contexto': 'Contexto de prueba'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.valoracion.denuncias_recibidas_objeto.count(), 1)
        denuncia = self.valoracion.denuncias_recibidas_objeto.first()
        self.assertEqual(denuncia.contexto, 'Contexto de prueba')

    def test_denunciar_valoracion_objeto_invalido(self):
        self.client.login(username='usuario_test', password='test12345')
        response = self.client.post(self.denunciar_valoracion_objeto_url, {
            'categoria': '',
            'contexto': ''
        })
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(messages[0].message,  'Debe seleccionar una categoría y proporcionar un contexto para la denuncia.')
        self.assertTemplateUsed(response, 'comentarios_objeto.html')

    def test_eliminar_valoracion_objeto_valido(self):
        self.client.login(username='usuario_test2', password='test12345')
        response = self.client.post(self.eliminar_valoracion_objeto_url)
        self.assertRedirects(response, self.obtener_comentarios_objeto_url)
        response2 = self.client.get(self.obtener_comentarios_objeto_url)
        self.assertEqual(response2.context['valoraciones'].count(), 0)

    def test_eliminar_valoracion_objeto_invalido(self):
        self.client.login(username='usuario_test', password='test12345')
        response = self.client.post(self.eliminar_valoracion_objeto_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(messages[0].message, 'No tienes permiso para eliminar esta valoración.')
    
    def test_lista_objetos_recomendados_valido(self):
        self.client.login(username='usuario_test2', password='test12345')
        response = self.client.get(self.lista_objetos_recomendados_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo.html')
        self.assertEqual(len(response.context['herramientas']), 2)
        self.assertEqual(response.context['herramientas'][0].nombre, 'Objeto de prueba 2') # Según las preferencias del usuario, el objeto de prueba 2 debería aparecer primero, con una puntuación de 4
        self.assertEqual(response.context['herramientas'][1].nombre, 'Objeto de prueba') # Según las preferencias del usuario, el objeto de prueba 1 debería aparecer segundo, con una puntuación de 2

    def test_lista_objetos_recomendados_invalido(self):
        response = self.client.get(self.lista_objetos_recomendados_url)
        self.assertEqual(response.status_code, 302)



#------------------------------------------------------------------------------------------------------------------------------------

#Tests relacionados con el gestor

#------------------------------------------------------------------------------------------------------------------------------------

    def test_catalogo_gestor_valido(self):
        self.client.login(username='gestor_test', password='test12345')
        response = self.client.get(self.gestion_objetos_gestor_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo_gestor.html')
        self.assertEqual(len(response.context['herramientas']), 2)

    def test_catalogo_gestor_valido_con_recomendaciones_destacadas(self):
        self.client.login(username='gestor_test', password='test12345')
        response = self.client.get(self.gestion_objetos_gestor_url, {'recomendaciones_destacadas': True})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo_gestor.html')
        self.assertEqual(len(response.context['herramientas']), 2)
        self.assertEqual(response.context['herramientas'][0].nombre, 'Objeto de prueba') # Al tener una valoración de 5 estrellas, su valoración media es 5, y debería aparecer primero
        self.assertEqual(response.context['herramientas'][1].nombre, 'Objeto de prueba 2') # Al no tener valoraciones, su valoración media es 0, y debería aparecer segundo

    def test_catalogo_gestor_valido_con_filtros(self):
        self.client.login(username='gestor_test', password='test12345')
        response = self.client.get(self.gestion_objetos_gestor_url, {'categoria': 'Bricolaje'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo_gestor.html')
        self.assertEqual(len(response.context['herramientas']), 1)
        self.assertEqual(response.context['herramientas'][0].categoria, 'Bricolaje')

    def test_catalogo_gestor_valido_con_busqueda(self):
        self.client.login(username='gestor_test', password='test12345')
        response = self.client.get(self.gestion_objetos_gestor_url, {'nombre_herramienta': 'Objeto de prueba'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo_gestor.html')
        self.assertEqual(len(response.context['herramientas']), 2)
        self.assertEqual(response.context['herramientas'][0].nombre, 'Objeto de prueba')
        self.assertEqual(response.context['herramientas'][1].nombre, 'Objeto de prueba 2')

    def test_catalogo_gestor_invalido(self):
        response = self.client.get(self.gestion_objetos_gestor_url)
        self.assertEqual(response.status_code, 302)

    def test_eliminar_articulo_catalogo_gestor_valido(self):
        self.client.login(username='gestor_test', password='test12345')
        response = self.client.post(self.eliminar_articulo_catalogo_gestor_url(self.objeto.id))
        
        mensajes = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Objeto eliminado correctamente." in str(m) for m in mensajes))
        self.assertRedirects(response, self.gestion_objetos_gestor_url)

        self.assertEqual(Objeto.objects.count(), 1)


    def test_eliminar_articulo_catalogo_gestor_invalido(self):
        response = self.client.post(self.eliminar_articulo_catalogo_gestor_url(self.objeto.id))
        self.assertEqual(response.status_code, 302, "El código de estado de la respuesta no es 302, se esperaba redirección")

        self.client.login(username='usuario_test2', password='test12345')
        response = self.client.post(self.eliminar_articulo_catalogo_gestor_url(self.objeto.id))
        self.assertEqual(response.status_code, 302, "El código de estado de la respuesta no es 302, se esperaba redirección")

        self.client.login(username='gestor_test', password='test12345')
        response = self.client.post(self.eliminar_articulo_catalogo_gestor_url(objeto_id=10000000))
        mensajes = list(get_messages(response.wsgi_request))
        self.assertTrue(any("El objeto no existe." in str(m) for m in mensajes))
        self.assertRedirects(response, self.gestion_objetos_gestor_url)

        response = self.client.get(self.eliminar_articulo_catalogo_gestor_url(self.objeto2.id))
        mensajes = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Método no permitido." in str(m) for m in mensajes))
        self.assertRedirects(response, self.gestion_objetos_gestor_url)


    def test_editar_articulo_catalogo_gestor_valido(self):
        self.client.login(username='gestor_test', password='test12345')
        
        datos_editar = {
            'nombre': 'Objeto de prueba editado',
            'descripcion': 'Descripción del objeto de prueba editado',
            'categoria': 'Herramientas',
            'condicion': 'Bueno',
            'huella_carbono': 5.00,
            'almacen': self.almacen.id,
            'imagen': 'https://i.blogs.es/f7234d/imagen/1200_800.webp'
        }
        
        response = self.client.post(self.test_editar_articulo_catalogo_gestor_url(objeto_id=self.objeto.id), datos_editar)
        
        mensajes = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Objeto actualizado correctamente.' in str(m) for m in mensajes))
        self.assertRedirects(response, self.gestion_objetos_gestor_url)

        self.objeto.refresh_from_db()
        self.assertEqual(self.objeto.nombre, 'Objeto de prueba editado')
        self.assertEqual(self.objeto.descripcion, 'Descripción del objeto de prueba editado')
        self.assertEqual(self.objeto.categoria, 'Herramientas')
        self.assertEqual(self.objeto.condicion, 'Bueno')
        self.assertEqual(self.objeto.huella_carbono, 5.00)

    def test_editar_articulo_catalogo_gestor_invalido(self):

        datos_editar = {
            'nombre': 'Objeto de prueba editado',
            'descripcion': 'Descripción del objeto de prueba editado',
            'categoria': 'Herramientas',
            'condicion': 'Bueno',
            'huella_carbono': 5.00,
            'almacen': self.almacen.id,
            'imagen': 'https://i.blogs.es/f7234d/imagen/1200_800.webp'
        }
        response = self.client.post(self.eliminar_articulo_catalogo_gestor_url(self.objeto.id))
        self.assertEqual(response.status_code, 302, "El código de estado de la respuesta no es 302, se esperaba redirección")

        self.client.login(username='usuario_test2', password='test12345')
        response = self.client.post(self.test_editar_articulo_catalogo_gestor_url(objeto_id=self.objeto.id), datos_editar)
        self.assertEqual(response.status_code, 302, "El código de estado de la respuesta no es 302, se esperaba redirección")

        datos_editar = {
            'nombre': 'Objeto de prueba editado',
            'descripcion': 'Descripción del objeto de prueba editado',
            'categoria': 'Herramientas',
            'condicion': '',
            'huella_carbono': 5.00,
            'almacen': self.almacen.id,
            'imagen': ''
        }
        self.client.login(username='gestor_test', password='test12345')
        response = self.client.post(self.test_editar_articulo_catalogo_gestor_url(objeto_id=self.objeto.id), datos_editar)
        mensajes = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Todos los campos son obligatorios.' in str(m) for m in mensajes))

        response = self.client.post(self.test_editar_articulo_catalogo_gestor_url(objeto_id=10000000000), datos_editar)
        mensajes = list(get_messages(response.wsgi_request))
        self.assertTrue(any('El objeto no existe.' in str(m) for m in mensajes))

    def test_crear_articulo_catalogo_gestor(self):
        self.client.login(username='gestor_test', password='test12345')
        
        datos_crear = {
            'nombre': 'Nuevo Objeto',
            'descripcion': 'Descripción del nuevo objeto',
            'categoria': 'Herramientas',
            'condicion': 'Bueno',
            'huella_carbono': 5.00,
            'almacen': self.almacen.id,
            'imagen': 'https://i.blogs.es/f7234d/imagen/1200_800.webp'
        }
        
        response = self.client.post(self.crear_articulo_catalogo_gestor_url, datos_crear)
        
        mensajes = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Objeto creado correctamente.' in str(m) for m in mensajes))
        self.assertRedirects(response, self.gestion_objetos_gestor_url)

        self.assertEqual(Objeto.objects.count(), 3)
        nuevo_objeto = Objeto.objects.last()
        self.assertEqual(nuevo_objeto.nombre, 'Nuevo Objeto')
        self.assertEqual(nuevo_objeto.descripcion, 'Descripción del nuevo objeto')
        self.assertEqual(nuevo_objeto.categoria, 'Herramientas')
        self.assertEqual(nuevo_objeto.condicion, 'Bueno')
        self.assertEqual(nuevo_objeto.huella_carbono, 5.00)

    def test_crear_articulo_catalogo_gestor_invalido(self):
        datos_crear_correctos = {
            'nombre': 'Nuevo Objeto',
            'descripcion': 'Descripción del nuevo objeto',
            'categoria': 'Herramientas',
            'condicion': 'Bueno',
            'huella_carbono': 5.00,
            'almacen': self.almacen.id,
            'imagen': 'https://i.blogs.es/f7234d/imagen/1200_800.webp'
        }

        response = self.client.post(self.crear_articulo_catalogo_gestor_url, datos_crear_correctos)
        self.assertEqual(response.status_code, 302, "El código de estado de la respuesta no es 302, se esperaba redirección")

        self.client.login(username='usuario_test2', password='test12345')
        response = self.client.post(self.crear_articulo_catalogo_gestor_url, datos_crear_correctos)
        self.assertEqual(response.status_code, 302, "El código de estado de la respuesta no es 302, se esperaba redirección")


        self.client.login(username='gestor_test', password='test12345')
        
        datos_crear = {
            'nombre': '',
            'descripcion': 'Descripción del nuevo objeto',
            'categoria': 'Herramientas',
            'condicion': 'Bueno',
            'huella_carbono': 5.00,
            'almacen': self.almacen.id,
            'imagen': ''
        }
        
        response = self.client.post(self.crear_articulo_catalogo_gestor_url, datos_crear)
        
        mensajes = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Todos los campos son obligatorios.' in str(m) for m in mensajes))
