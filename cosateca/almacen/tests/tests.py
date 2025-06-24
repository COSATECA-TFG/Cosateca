from django.test import TestCase
from almacen.models import Almacen, Localizacion, AlmacenValoracion, ObjetoValoracionDenuncia
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
            id=1,
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
        
        self.denuncia_valoracion_almacen = ObjetoValoracionDenuncia.objects.create(
            valoracion = self.valoracion_almacen,
            usuario = self.usuario,
            categoria = "Otra",
            contexto = "Denuncia de prueba para la valoración del almacén"
        )
        
        
        self.url_obtener_almacenes = reverse('almacenes')
        self.url_obtener_almacen = lambda almacen_id: reverse('almacen', kwargs={'almacen_id': almacen_id})
        self.url_obtener_comentarios = lambda almacen_id: reverse('comentarios', kwargs={'almacen_id': almacen_id})
        self.url_valorar_almacen = lambda almacen_id: reverse('valoracion_almacen', kwargs={'almacen_id': almacen_id}) 
        
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
        response = self.client.get(self.url_obtener_almacen(almacen_id=1))
        self.assertTemplateUsed(response, 'almacen_valoracion.html', 'La plantilla utilizada no es la esperada')
        self.assertIsNotNone(response.context['valoracion'], "Debería de existir una valoración para el almacén")
        self.assertEqual(response.context['valoracion'].estrellas, 4, "Debería haber una valoración que puntue el almacén")
        self.assertEqual(response.context['valoracion'].comentario, "Comentario de prueba para el almacén", "Debería haber una valoración con un comentario para el almacén")

    
    def test_obtener_almacen_invalido(self):
        response = self.client.get(self.url_obtener_almacen(almacen_id=1))
        self.assertEqual(response.status_code, 302, "El usuario al no estar logueado debe de ser redirigido")   
        
        
        self.client.login(username='testuser', password='tester1')
        response = self.client.get(self.url_obtener_almacen(almacen_id=1000))
        self.assertTemplateUsed(response, 'almacen_valoracion.html', 'La plantilla utilizada no es la esperada')
        self.assertIsNotNone(response.context['error'], "Debería de haber un error al no encontrar el almacén")
        self.assertEqual(response.context['error'], 'Almacén no encontrado', "El mensaje de error no es el esperado")
        
    def test_obtener_comentarios_valido(self):
        log = self.client.login(username='testuser', password='tester1')
        self.assertTrue(log, "El usuario no pudo iniciar sesión")
        response = self.client.get(self.url_obtener_comentarios(almacen_id=1))
        self.assertTemplateUsed(response, 'comentarios_almacen.html', 'La plantilla utilizada no es la esperada')
        self.assertEqual(response.context['almacen'].nombre, "Almacen test 1", "Debería haber al menos un almacén devuelto por la función")
        self.assertEqual(len(response.context['comentarios_info']), 1, "Debería haber al menos un comentario devuelto por la función")
        self.assertEqual(response.context['comentarios_info'][0]['ya_denunciado'], True ,"Debería haber una denuncia para la valoración del almacén")

    def test_obtener_comentarios_invalido(self):
        response = self.client.get(self.url_obtener_comentarios(almacen_id=1))
        self.assertEqual(response.status_code, 302, "El usuario al no estar logueado debe de ser redirigido")   
        
        self.client.login(username='testuser', password='tester1')
        response = self.client.get(self.url_obtener_comentarios(almacen_id=1000))
        self.assertTemplateUsed(response, 'comentarios_almacen.html', 'La plantilla utilizada no es la esperada')
        self.assertIsNotNone(response.context['error'], "Debería de haber un error al no encontrar el almacén")
        self.assertEqual(response.context['error'], 'Almacén no encontrado', "El mensaje de error no es el esperado")

    def test_valorar_almacen_valido(self):
        log = self.client.login(username='testuser', password='tester1')
        self.assertTrue(log, "El usuario no pudo iniciar sesión")
        response = self.client.get(self.url_valorar_almacen(almacen_id=1))
        self.assertTemplateUsed(response, 'almacen_valoracion.html', 'La plantilla utilizada no es la esperada')
        self.assertIsNotNone(response.context['valoracion'], "Debería de existir una valoración para el almacén")
        self.assertEqual(response.context['valoracion'].estrellas, 4, "Debería haber una valoración que puntue el almacén")
        self.assertEqual(response.context['valoracion'].comentario, "Comentario de prueba para el almacén", "Debería haber una valoración con un comentario para el almacén")
        
        formulario_valoracion = {'puntuacion': 5, 'comentario': 'Excelente almacén'}
        response = self.client.post(self.url_valorar_almacen(almacen_id=1), formulario_valoracion)
        self.assertEqual(response.status_code, 302, "Debería redirigir al usuario después de valorar el almacén")
        self.valoracion_almacen.refresh_from_db()
        self.assertEqual(self.valoracion_almacen.estrellas, 5, "La valoración del almacén debería actualizarse a 5 estrellas")
        self.assertEqual(self.valoracion_almacen.comentario, 'Excelente almacén', "El comentario de la valoración del almacén debería actualizarse correctamente")
    
    def test_valorar_almacen_invalido(self):
        response = self.client.get(self.url_valorar_almacen(almacen_id=1))
        self.assertEqual(response.status_code, 302, "El usuario al no estar logueado debe de ser redirigido")   
        
        self.client.login(username='testuser', password='tester1')
        formulario_valoracion = {'puntuacion': '', 'comentario': ''}
        response = self.client.post(self.url_valorar_almacen(almacen_id=1), formulario_valoracion)
        self.assertTemplateUsed(response, 'almacen_valoracion.html')
        self.assertIn('error', response.context)
        self.assertEqual(response.context['error'], 'Debes proporcionar una puntuación y un comentario.')
