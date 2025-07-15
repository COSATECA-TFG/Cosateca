from django.test import TestCase
from almacen.models import Almacen, Localizacion, AlmacenValoracion, AlmacenValoracionDenuncia
from usuario.models import Usuario, Preferencia
from django.urls import reverse
from datetime import date
from django.test import Client




class almacenViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        
        self.usuario = Usuario.objects.create_user(
            username= 'testuser',
            first_name = 'tester',
            last_name = 'tester',
            fecha_nacimiento = date(1990, 5, 15),
            sexo = 'F',
            email = 'tester@example.com',
            telefono = '600123456',
            dni = '12345678A',
            estado = 'A',
            password = 'tester1'
        )

        self.admin = Usuario.objects.create_user(
            username='admin_test',
            password='test12345',
            email='testadmin@example.com',
            first_name='Testadmin',
            last_name='Useradmin',
            fecha_nacimiento=date(1990, 1, 1),
            sexo='NB',
            telefono='800000002',
            dni='12345679A',
            is_staff=True
        )
        
        self.preferencia = Preferencia.objects.create(
            tarea_tipo='Bricolaje',
            frecuencia_uso='Semanal',
            experiencia='Intermedio',
            franja_horaria='Mañana',
            usuario = self.usuario 
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

        
        self.almacen = Almacen.objects.create(
            nombre="Almacen test 1",
            descripcion="Descripción del almacén de prueba 1",
            localizacion = self.localizacion_prueba
        )
        
        self.valoracion_almacen = AlmacenValoracion.objects.create(
            almacen = self.almacen,
            usuario = self.usuario,
            estrellas = 4,
            comentario = "Comentario de prueba para el almacén",
        )
        
        self.denuncia_valoracion_almacen = AlmacenValoracionDenuncia.objects.create(
            valoracion = self.valoracion_almacen,
            usuario = self.usuario,
            categoria = "Otra",
            contexto = "Denuncia de prueba para la valoración del almacén"
        )
        
        
        self.url_obtener_almacenes = reverse('almacenes')
        self.url_obtener_almacen = lambda almacen_id: reverse('almacen', kwargs={'almacen_id': almacen_id})
        self.url_obtener_comentarios = lambda almacen_id: reverse('comentarios', kwargs={'almacen_id': almacen_id})
        self.url_valorar_almacen = lambda almacen_id: reverse('valoracion_almacen', kwargs={'almacen_id': almacen_id}) 
        self.url_eliminar_valoracion_almacen = lambda comentario_id: reverse('eliminar_valoracion_almacen', kwargs={'comentario_id': comentario_id})
        self.url_denunciar_valoracion_almacen = lambda comentario_id: reverse('denunciar_valoracion_almacen', kwargs={'comentario_id': comentario_id})

        self.url_gestion_almacenes_administrador = reverse('almacenes_administrador')
        self.url_crear_almacen = reverse('crear_almacen')
        self.url_editar_almacen = lambda almacen_id: reverse('editar_almacen', kwargs={'almacen_id': almacen_id})
        self.url_eliminar_almacen = lambda almacen_id: reverse('eliminar_almacen', kwargs={'almacen_id': almacen_id})
        
    def test_obtener_almacenes_valido(self):
        log = self.client.login(username='testuser', password='tester1')
        self.assertTrue(log, "El usuario no pudo iniciar sesión")
        response = self.client.get(self.url_obtener_almacenes)
        self.assertEqual(response.status_code, 200 )
        self.assertTemplateUsed(response, 'almacenes.html', 'La plantilla utilizada no es la esperada')
        self.assertContains(response, 'Almacen test 1')
        self.assertContains(response, 'Descripción del almacén de prueba 1')
        
        
        response = self.client.get(self.url_obtener_almacenes,  {'busqueda_almacen': 'Almacen test 1'})
        self.assertContains(response, "Almacen test 1")

    
    
    def test_obtener_almacenes_invalido(self):
        response = self.client.get(self.url_obtener_almacenes)
        self.assertEqual(response.status_code, 302, "El usuario al no estar logueado debe de ser redirigido")    
        
        self.client.login(username='testuser', password='tester1')
        response = self.client.get(self.url_obtener_almacenes,  {'busqueda_almacen': 'Almacen test invalido'})
        number_of_almacenes = len(response.context['almacenes'])
        self.assertEqual(number_of_almacenes, 0, "No debería haber almacenes con ese nombre")


    def test_obtener_almacen_valido(self):
        log = self.client.login(username='testuser', password='tester1')
        self.assertTrue(log, "El usuario no pudo iniciar sesión")
        response = self.client.get(self.url_obtener_almacen(almacen_id=self.almacen.id))
        self.assertTemplateUsed(response, 'almacen_valoracion.html', 'La plantilla utilizada no es la esperada')
        self.assertIsNotNone(response.context['valoracion'], "Debería de existir una valoración para el almacén")
        self.assertEqual(response.context['valoracion'].estrellas, 4, "Debería haber una valoración que puntue el almacén")
        self.assertEqual(response.context['valoracion'].comentario, "Comentario de prueba para el almacén", "Debería haber una valoración con un comentario para el almacén")

    
    def test_obtener_almacen_invalido(self):
        response = self.client.get(self.url_obtener_almacen(almacen_id=self.almacen.id))
        self.assertEqual(response.status_code, 302, "El usuario al no estar logueado debe de ser redirigido")   
        
        
        self.client.login(username='testuser', password='tester1')
        # Usar un ID que no existe
        nonexistent_id = self.almacen.id + 1000
        response = self.client.get(self.url_obtener_almacen(almacen_id=nonexistent_id))
        self.assertTemplateUsed(response, 'almacen_valoracion.html', 'La plantilla utilizada no es la esperada')
        self.assertIsNotNone(response.context['error'], "Debería de haber un error al no encontrar el almacén")
        self.assertEqual(response.context['error'], 'Almacén no encontrado', "El mensaje de error no es el esperado")
        
    def test_obtener_comentarios_valido(self):
        log = self.client.login(username='testuser', password='tester1')
        self.assertTrue(log, "El usuario no pudo iniciar sesión")
        response = self.client.get(self.url_obtener_comentarios(almacen_id=self.almacen.id))
        self.assertTemplateUsed(response, 'comentarios_almacen.html', 'La plantilla utilizada no es la esperada')
        self.assertEqual(response.context['almacen'].nombre, "Almacen test 1", "Debería haber al menos un almacén devuelto por la función")
        self.assertEqual(len(response.context['comentarios_info']), 1, "Debería haber al menos un comentario devuelto por la función")
        self.assertEqual(response.context['comentarios_info'][0]['ya_denunciado'], True ,"Debería haber una denuncia para la valoración del almacén")

    def test_obtener_comentarios_invalido(self):
        response = self.client.get(self.url_obtener_comentarios(almacen_id=self.almacen.id))
        self.assertEqual(response.status_code, 302, "El usuario al no estar logueado debe de ser redirigido")   
        
        self.client.login(username='testuser', password='tester1')
        # Usar un ID que no existe
        nonexistent_id = self.almacen.id + 1000
        response = self.client.get(self.url_obtener_comentarios(almacen_id=nonexistent_id))
        self.assertTemplateUsed(response, 'comentarios_almacen.html', 'La plantilla utilizada no es la esperada')
        self.assertIsNotNone(response.context['error'], "Debería de haber un error al no encontrar el almacén")
        self.assertEqual(response.context['error'], 'Almacén no encontrado', "El mensaje de error no es el esperado")

    def test_valorar_almacen_valido(self):
        log = self.client.login(username='testuser', password='tester1')
        self.assertTrue(log, "El usuario no pudo iniciar sesión")
        response = self.client.get(self.url_valorar_almacen(almacen_id=self.almacen.id))
        self.assertTemplateUsed(response, 'almacen_valoracion.html', 'La plantilla utilizada no es la esperada')
        self.assertIsNotNone(response.context['valoracion'], "Debería de existir una valoración para el almacén")
        self.assertEqual(response.context['valoracion'].estrellas, 4, "Debería haber una valoración que puntue el almacén")
        self.assertEqual(response.context['valoracion'].comentario, "Comentario de prueba para el almacén", "Debería haber una valoración con un comentario para el almacén")
        
        formulario_valoracion = {'puntuacion': 5, 'comentario': 'Excelente almacén'}
        response = self.client.post(self.url_valorar_almacen(almacen_id=self.almacen.id), formulario_valoracion)
        self.assertEqual(response.status_code, 302, "Debería redirigir al usuario después de valorar el almacén")
        self.valoracion_almacen.refresh_from_db()
        self.assertEqual(self.valoracion_almacen.estrellas, 5, "La valoración del almacén debería actualizarse a 5 estrellas")
        self.assertEqual(self.valoracion_almacen.comentario, 'Excelente almacén', "El comentario de la valoración del almacén debería actualizarse correctamente")
    
    def test_valorar_almacen_invalido(self):
        response = self.client.get(self.url_valorar_almacen(almacen_id=self.almacen.id))
        self.assertEqual(response.status_code, 302, "El usuario al no estar logueado debe de ser redirigido")   
        
        self.client.login(username='testuser', password='tester1')
        formulario_valoracion = {'puntuacion': '', 'comentario': ''}
        response = self.client.post(self.url_valorar_almacen(almacen_id=self.almacen.id), formulario_valoracion)
        self.assertTemplateUsed(response, 'almacen_valoracion.html')
        self.assertIn('error', response.context)
        self.assertEqual(response.context['error'], 'Debes proporcionar una puntuación y un comentario.')

    def test_eliminar_valoracion_almacen(self):
        log = self.client.login(username='testuser', password='tester1')
        self.assertTrue(log, "El usuario no pudo iniciar sesión")
        response = self.client.get(self.url_eliminar_valoracion_almacen(comentario_id=self.valoracion_almacen.id))
        
        self.assertEqual(response.status_code, 302)
        esEliminada = not (AlmacenValoracion.objects.filter(id=self.valoracion_almacen.id).exists())
        self.assertTrue(esEliminada, "La valoración del almacén debería eliminarse correctamente")
    
    def test_eliminar_valoracion_almacen_invalido(self):
        response = self.client.get(self.url_eliminar_valoracion_almacen(comentario_id=self.valoracion_almacen.id))
        self.assertEqual(response.status_code, 302, "El usuario al no estar logueado debe de ser redirigido")   
        
        self.client.login(username='testuser', password='tester1')
        # Usar un ID que no existe
        nonexistent_id = self.valoracion_almacen.id + 1000
        response = self.client.get(self.url_eliminar_valoracion_almacen(comentario_id=nonexistent_id))
        self.assertEqual(response.status_code, 302, "Debería redirigir al usuario al no encontrar ninguna valoración")
        self.assertEqual(response.url, reverse('menu'), "Debería redirigir al usuario al menú principal")
        
    def test_denunciar_valoracion_almacen_valido(self):
        log = self.client.login(username='testuser', password='tester1')
        self.assertTrue(log, "El usuario no pudo iniciar sesión")
        
        datos_denuncia = {
            'categoria': 'Acoso',
            'contexto': 'Este comentario es acoso.'
        }
        response = self.client.post(self.url_denunciar_valoracion_almacen(comentario_id=self.valoracion_almacen.id), datos_denuncia)
        
        self.assertEqual(response.status_code, 302, "Debería redirigir al usuario después de denunciar la valoración")
        self.denuncia_valoracion_almacen.refresh_from_db()
        self.assertEqual(self.denuncia_valoracion_almacen.categoria, "Acoso", "La categoría de la denuncia debería actualizarse correctamente")
        self.assertEqual(self.denuncia_valoracion_almacen.contexto, 'Este comentario es acoso.', "El contexto de la denuncia debería actualizarse correctamente")
        
    def test_denunciar_valoracion_almacen_invalido(self):
        response = self.client.get(self.url_denunciar_valoracion_almacen(comentario_id=self.valoracion_almacen.id))
        self.assertEqual(response.status_code, 302, "El usuario al no estar logueado debe de ser redirigido")   
        
        self.client.login(username='testuser', password='tester1')
        datos_denuncia = {
            'categoria': '',
            'contexto': ''
        }
        # Usar un ID que no existe
        nonexistent_id = self.valoracion_almacen.id + 10000
        response = self.client.post(self.url_denunciar_valoracion_almacen(comentario_id=nonexistent_id), datos_denuncia)
        self.assertTemplateUsed(response, 'comentarios_almacen.html')
        self.assertEqual(response.context['error'], 'Comentario no encontrado o no autorizado', "El mensaje de error no es el esperado")

#------------------------------------------------------------------------------------------------------------------------------------

#Tests relacionados con el administrador

#------------------------------------------------------------------------------------------------------------------------------------

    def test_obtener_almacenes_administrador_valido(self):
        self.client.login(username='admin_test', password='test12345')
        response = self.client.get(self.url_gestion_almacenes_administrador)
        self.assertTemplateUsed(response, 'gestion_almacen_administrador.html', 'La plantilla utilizada no es la esperada')
        almacenes = response.context['almacenes']
        self.assertEqual(len(almacenes), 1, "Debería haber un almacén para el administrador")

    def test_obtener_almacenes_administrador_invalido(self):
        response = self.client.get(self.url_gestion_almacenes_administrador)
        self.assertEqual(response.status_code, 302, "El usuario al no estar logueado debe de ser redirigido")   
        

    def test_crear_almacen_valido(self):
        self.client.login(username='admin_test', password='test12345')
        

        datos_almacen = {
            'nombre': 'Nuevo Almacen',
            'descripcion': 'Descripción del nuevo almacén',
            'latitud' : 17.345678,
            'longitud' : 48.765432,
            'calle' : "Calle de prueba 2",
            'numero_calle' : "12",
            'pais' : "País de prueba 2",
            'ciudad' : "Ciudad de prueba 2",
            'codigo_postal' : "22222"

        }
        
        response = self.client.post(self.url_crear_almacen, datos_almacen)
        self.assertEqual(response.status_code, 302, "Debería redirigir al usuario después de crear el almacén")
        self.assertTrue(Almacen.objects.filter(nombre='Nuevo Almacen').exists(), "El nuevo almacén debería haberse creado correctamente")

    def test_crear_almacen_invalido(self):
        response = self.client.get(self.url_crear_almacen)
        self.assertEqual(response.status_code, 302, "El usuario al no estar logueado debe de ser redirigido")   
        
        self.client.login(username='admin_test', password='test12345')
        datos_almacen = {}
        
        response = self.client.post(self.url_crear_almacen, datos_almacen)
        self.assertEqual(response.status_code, 302, "Debería redirigir al usuario cuando faltan campos obligatorios")

    def test_editar_almacen_valido(self):
        self.client.login(username='admin_test', password='test12345')
        
        datos_almacen = {
            'nombre': 'Almacen Editado',
            'descripcion': 'Descripción del almacén editado',
            'latitud' : 20.123456,
            'longitud' : 30.654321,
            'calle' : "Calle de prueba editada",
            'numero_calle' : "34",
            'pais' : "País de prueba editado",
            'ciudad' : "Ciudad de prueba editada",
            'codigo_postal' : "33333"
        }
        
        response = self.client.post(self.url_editar_almacen(almacen_id=self.almacen.id), datos_almacen)
        self.assertEqual(response.status_code, 302, "Debería redirigir al usuario después de editar el almacén")
        self.almacen.refresh_from_db()
        self.assertEqual(self.almacen.nombre, 'Almacen Editado', "El nombre del almacén debería actualizarse correctamente")

    def test_editar_almacen_invalido(self):
        response = self.client.get(self.url_editar_almacen(almacen_id=self.almacen.id))
        self.assertEqual(response.status_code, 302, "El usuario al no estar logueado debe de ser redirigido")   
        
        self.client.login(username='admin_test', password='test12345')
        datos_almacen = {}
        
        response = self.client.post(self.url_editar_almacen(almacen_id=self.almacen.id), datos_almacen)
        self.assertEqual(response.status_code, 302, "Debería redirigir al usuario cuando faltan campos obligatorios")
    
    def test_eliminar_almacen_valido(self):
        self.client.login(username='admin_test', password='test12345')
        response = self.client.get(self.url_eliminar_almacen(almacen_id=self.almacen.id))
        
        self.assertEqual(response.status_code, 302, "Debería redirigir al usuario después de eliminar el almacén")
        esEliminado = not (Almacen.objects.filter(id=self.almacen.id).exists())
        self.assertTrue(esEliminado, "El almacén debería eliminarse correctamente")
    
    def test_eliminar_almacen_invalido(self):
        response = self.client.get(self.url_eliminar_almacen(almacen_id=self.almacen.id))
        self.assertEqual(response.status_code, 302, "El usuario al no estar logueado debe de ser redirigido")   
        
        self.client.login(username='admin_test', password='test12345')
        nonexistent_id = self.almacen.id + 1000
        response = self.client.get(self.url_eliminar_almacen(almacen_id=nonexistent_id))
        self.assertEqual(response.status_code, 302, "Debería redirigir al usuario al no encontrar ningún almacén")
        self.assertEqual(response.url, reverse('almacenes_administrador'), "Debería redirigir al usuario al menú principal")
        

