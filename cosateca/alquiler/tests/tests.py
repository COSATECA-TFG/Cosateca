from django.test import TestCase
from django.test import Client
from django.urls import reverse
from usuario.models import Usuario, Preferencia
from datetime import date
from alquiler.models import Alquiler
from objeto.models import Objeto
from almacen.models import Almacen, Localizacion
from django.contrib.messages import get_messages



class alquilerViewTest(TestCase):
    
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
        
        
        self.objeto = Objeto.objects.create(
            nombre='Objeto de prueba',
            descripcion='Descripción del objeto de prueba',
            imagen='https://i.blogs.es/f7234d/imagen/1200_800.webp',
            categoria='Herramientas',
            condicion='Bueno',
            huella_carbono=10.00,
            usuario=self.usuario,
            almacen=self.almacen
        )
        
        self.alquiler = Alquiler.objects.create(
            id = 1,
            fecha_inicio = date(2023, 10, 1),
            fecha_fin = date(2023, 10, 10),
            fecha_recogida = date(2023, 10, 2),
            fecha_entrega =  date(2023, 10, 9),
            cancelada = False,
            usuario = self.usuario,
            objeto = self.objeto
        )
        
        self.url_historial_reservas = reverse('mis_reservas')
        self.url_cancelar_reserva = lambda reserva_id: reverse('cancelar_reserva',  kwargs={'reserva_id': reserva_id})
        self.url_editar_reserva = lambda reserva_id: reverse('editar_reserva', kwargs={'reserva_id': reserva_id})
        self.url_reservas_ocupadas = lambda objeto_id: reverse('reservas_ocupadas', kwargs={'objeto_id': objeto_id})
        
    def test_historial_reservas_valido(self):
        log = self.client.login(username='testuser', password='tester1')
        self.assertTrue(log, "El usuario no pudo iniciar sesión")
        response = self.client.get(self.url_historial_reservas)
        
        self.assertEqual(response.status_code, 200, "El código de estado de la respuesta no es 200")
        self.assertTemplateUsed(response, 'historial_reservas.html', "La plantilla utilizada no es la correcta")
        
        filtro = {'filtro': 'finalizadas'}
        response = self.client.get(self.url_historial_reservas,filtro)
        self.assertEqual(len(response.context['reservas']), 1, "El número de reservas finalizadas no es el esperado")
        
        filtro = {'filtro': 'en_curso'}
        response = self.client.get(self.url_historial_reservas,filtro)
        self.assertEqual(len(response.context['reservas']), 0, "El número de reservas finalizadas no es el esperado")
        
    def test_historial_reservas_invalido(self):
        response = self.client.get(self.url_historial_reservas)
        self.assertEqual(response.status_code, 302, "El código de estado de la respuesta no es 302, se esperaba redirección")
        
    def test_cancelar_reserva_valido(self):
        log = self.client.login(username='testuser', password='tester1')
        self.assertTrue(log, "El usuario no pudo iniciar sesión")
        response = self.client.get(self.url_cancelar_reserva(self.alquiler.id))        
        
        self.alquiler.refresh_from_db()
        self.assertTrue(self.alquiler.cancelada, "La reserva no se canceló correctamente")
        self.assertEqual(response.status_code, 302, "El código de estado de la respuesta no es 302, se esperaba redirección")
    
    def test_cancelar_reserva_invalido(self):
        response = self.client.get(self.url_cancelar_reserva(self.alquiler.id))
        self.assertEqual(response.status_code, 302, "El código de estado de la respuesta no es 302, se esperaba redirección")
        
        response = self.client.get(self.url_cancelar_reserva(1000))
        self.assertEqual(response.status_code, 302, "El código de estado de la respuesta no es 302, se esperaba redirección al fallar en la búsqueda de una reserva con un id inexistente")

    def test_editar_reserva_valido(self):
        log = self.client.login(username='testuser', password='tester1')
        self.assertTrue(log, "El usuario no pudo iniciar sesión")
        

        datos_editar = {
            'fecha_inicio': '2023-10-05',
            'fecha_fin': '2023-10-15'
        }
        response = self.client.post(self.url_editar_reserva(reserva_id=1), datos_editar)
        
        self.alquiler.refresh_from_db()
        self.assertEqual(self.alquiler.fecha_inicio.isoformat(), '2023-10-05', "La fecha de inicio no se actualizó correctamente")
        self.assertEqual(self.alquiler.fecha_fin.isoformat(), '2023-10-15', "La fecha de fin no se actualizó correctamente")
        self.assertEqual(response.status_code, 302, "El código de estado de la respuesta no es 302, se esperaba redirección")
    
    def test_editar_reserva_invalido(self):
        response = self.client.get(self.url_editar_reserva(reserva_id=1))
        self.assertEqual(response.status_code, 302, "El código de estado de la respuesta no es 302, se esperaba redirección")
        
        log = self.client.login(username='testuser', password='tester1')
        self.assertTrue(log, "El usuario no pudo iniciar sesión")
        response = self.client.get(self.url_editar_reserva(reserva_id=1000))
        self.assertEqual(response.status_code, 302, "El código de estado de la respuesta no es 302, se esperaba redirección al fallar en la búsqueda de una reserva con un id inexistente")
        
        datos_editar_invalidos = {
            'fecha_inicio': '',
            'fecha_fin': ''
        }
        response = self.client.post(self.url_editar_reserva(reserva_id=1), datos_editar_invalidos)
        mensajes = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Por favor, selecciona fechas válidas." in str(m) for m in mensajes))
        
    def test_reservas_ocupadas_valido(self):
        log = self.client.login(username='testuser', password='tester1')
        self.assertTrue(log, "El usuario no pudo iniciar sesión")
        
        datos = {
            'reserva_id': self.alquiler.id,
        }
        response = self.client.get(self.url_reservas_ocupadas(objeto_id=self.objeto.id), datos)
        self.assertEqual(response.status_code, 200, "El código de estado de la respuesta no es 200")
        resultado = response.json()
        self.assertEqual(len(resultado['reservas']), 1, "El número de reservas ocupadas no es el esperado")
    
    def test_reservas_ocupadas_invalido(self):
        response = self.client.get(self.url_reservas_ocupadas(objeto_id=self.objeto.id))
        self.assertEqual(response.status_code, 302, "El código de estado de la respuesta no es 302, se esperaba redirección")
    