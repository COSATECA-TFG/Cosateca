from django.test import TestCase, Client
from usuario.models import Usuario, Preferencia
from datetime import date
from django.urls import reverse
from objeto.models import Objeto
from almacen.models import Almacen, Localizacion
from django.contrib.messages import get_messages

class UsuarioViewsTest(TestCase):
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
        usuario=self.user2,
        almacen=self.almacen
        )

        self.objeto2 = Objeto.objects.create(
        nombre='Objeto de prueba 2',
        descripcion='Descripción del objeto de prueba 2',
        imagen='https://i.blogs.es/f7234d/imagen/1200_800.webp',
        categoria='Herramientas',
        condicion='Bueno',
        huella_carbono=10.00,
        almacen=self.almacen
        )

        self.registro_url = reverse('registro')
        self.inicio_sesion_url = reverse('inicio_sesion')
        self.cerrar_sesion_url = reverse('cerrar_sesion')
        self.cuestionario_preferencias_url = reverse('cuestionario_preferencias')
        self.menu_url = reverse('menu')
        self.lista_deseos_url = reverse('lista_deseos')
        self.eliminar_objeto_lista_deseos_url = reverse('eliminar_objeto', args=[self.objeto.id])
        self.eliminar_objeto_lista_deseos_url_2 = reverse('eliminar_objeto', args=[self.objeto2.id])
        self.detalles_usuario_url = reverse('usuario')
        self.agregar_objeto_lista_deseos_url = reverse('agregar_objeto', args=[self.objeto2.id])
        self.agregar_objeto_lista_deseos_url_2 = reverse('agregar_objeto', args=[self.objeto.id])
        self.consultar_huella_carbono_reducida_url = reverse('huella_carbono_reducida')
        self.consultar_amonestaciones_url = reverse('consultar_amonestaciones')

    def test_registro_valido(self):
        data = {
            'nombre_usuario': 'testuser',
            'contraseña': 'testpassword',
            'confirmar_contraseña': 'testpassword',
            'correo_electronico': 'test@example.es',
            'nombre': 'Test',
            'apellido': 'User',
            'fecha_nacimiento': '1990-01-01',
            'sexo': 'NB',
            'telefono': '600000002',
            'dni': '12345678Z'
            }
        response = self.client.post(self.registro_url, data)
        
        self.assertRedirects(response, reverse('cuestionario_preferencias'))

        user = Usuario.objects.get(username='testuser')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.email, 'test@example.es')

        self.assertTrue(user.check_password('testpassword'))

        session_user_id = self.client.session.get('usuario_id')
        self.assertEqual(session_user_id, user.id)

    def test_registro_invalido(self):
        data = {
            'nombre_usuario': 'testuser',
            'contraseña': 'testpassword',
            'confirmar_contraseña': 'testpassword',
            'correo_electronico': 'invalid-email',
            'nombre': '',
            'apellido': '',
            'fecha_nacimiento': '',
            'sexo': '',
            'telefono': '',
            'dni': ''
        }
        response = self.client.post(self.registro_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Este campo es obligatorio.')

    def test_inicio_sesion_valido(self):
        data = {
            'nombre_usuario': 'usuario_test',
            'contraseña': 'test12345'
        }
        response = self.client.post(self.inicio_sesion_url, data)
        
        self.assertRedirects(response, self.cuestionario_preferencias_url)

        session_user_id = self.client.session.get('usuario_id')
        self.assertEqual(session_user_id, self.user.id)
    
    def test_inicio_sesion_invalido(self):
        data = {
            'nombre_usuario': 'usuario_test',
            'contraseña': 'wrongpassword'
        }
        response = self.client.post(self.inicio_sesion_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nombre de usuario o contraseña incorrectos.')

    def test_cerrar_sesion(self):
        self.client.login(username='usuario_test', password='test12345')
        response = self.client.get(self.cerrar_sesion_url)
        
        self.assertRedirects(response, '/')
        session_user_id = self.client.session.get('usuario_id')
        self.assertIsNone(session_user_id)

    def test_cuestionario_preferencias_valido(self):
        self.client.login(username='usuario_test', password='test12345')

        session = self.client.session
        session['usuario_id'] = self.user.id  
        session.save()

        data = {
            'tarea_tipo': 'Bricolaje',
            'frecuencia_uso': 'Diario',
            'experiencia': 'Intermedio',
            'franja_horaria': 'Mañana'
        }
        response = self.client.post(self.cuestionario_preferencias_url, data)
        self.assertRedirects(response, self.menu_url)
    
    def test_cuestionario_preferencias_invalido(self):
        self.client.login(username='usuario_test', password='test12345')

        session = self.client.session
        session['usuario_id'] = self.user.id  
        session.save()

        data = {
            'tarea_tipo': '',
            'frecuencia_uso': '',
            'experiencia': '',
            'franja_horaria': ''
        }
        response = self.client.post(self.cuestionario_preferencias_url, data)
        
        self.assertEqual(response.status_code, 200)

    def test_menu_valido(self):
        self.client.login(username='usuario_test2', password='test12345')
        response = self.client.get(self.menu_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'menu.html')

    def test_menu_invalido(self):
        response = self.client.get(self.menu_url)
        self.assertEqual(response.status_code, 302)

    def test_lista_deseos_valido(self):
        self.client.login(username='usuario_test2', password='test12345')
        response = self.client.get(self.lista_deseos_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lista_deseos.html')
        objetos_deseados = response.context['objetos_deseados']
        self.assertEqual(len(objetos_deseados), 1)

    def test_lista_deseos_invalido(self):
        response = self.client.get(self.lista_deseos_url)
        self.assertEqual(response.status_code, 302) 

    def test_eliminar_objeto_lista_deseos_valido(self):
        self.client.login(username='usuario_test2', password='test12345')
        
        response = self.client.get(self.eliminar_objeto_lista_deseos_url)
        
        self.assertRedirects(response, self.lista_deseos_url)

        response2 = self.client.get(self.lista_deseos_url)

        objetos_deseados = response2.context['objetos_deseados']
        self.assertEqual(len(objetos_deseados), 0)

    def test_eliminar_objeto_lista_deseos_invalido(self):
        self.client.login(username='usuario_test2', password='test12345')

        response = self.client.get(self.eliminar_objeto_lista_deseos_url_2)

        self.assertRedirects(response, self.lista_deseos_url)

        response2 = self.client.get(self.lista_deseos_url)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "El objeto no se encuentra en la lista de deseos.")

        objetos_deseados = response2.context['objetos_deseados']
        self.assertEqual(len(objetos_deseados), 1)

    def test_detalles_usuario_valido(self):
        self.client.login(username='usuario_test2', password='test12345')
        response = self.client.get(self.detalles_usuario_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detalles_usuario.html')
        usuario = response.context['usuario']
        self.assertEqual(usuario.username, 'usuario_test2')
        self.assertEqual(usuario.email, 'test2@example.com')
        self.assertEqual(usuario.first_name, 'Test2')
        self.assertEqual(usuario.last_name, 'User2')
        self.assertEqual(usuario.fecha_nacimiento, date(1990, 1, 1))
        self.assertEqual(usuario.sexo, 'NB')
        self.assertEqual(usuario.telefono, '800000000')
        self.assertEqual(usuario.dni, '12345679X')
    
    def test_post_detalles_usuario_valido(self):
        self.client.login(username='usuario_test2', password='test12345')
        
        data = {
            'nombre': 'NuevoNombre',
            'apellido': 'NuevoApellido',
            'fecha_nacimiento': '1990-01-01',
            'sexo': 'NB',
            'correo_electronico': 'test2@example.com',
            'telefono': '800000001',
            'dni': '12345679X',
            'nombre_usuario': 'usuario_test2'
        }
        response = self.client.post(self.detalles_usuario_url, data)
        usuario = Usuario.objects.get(username='usuario_test2')
        self.assertEqual(usuario.first_name, 'NuevoNombre')
        self.assertEqual(usuario.last_name, 'NuevoApellido')
        self.assertEqual(usuario.email, 'test2@example.com')
        self.assertEqual(usuario.telefono, '800000001')
        self.assertEqual(usuario.dni, '12345679X')
        self.assertEqual(usuario.telefono, '800000001')
        self.assertEqual(usuario.sexo, 'NB')

    def test_post_detalles_usuario_invalido(self):
        self.client.login(username='usuario_test2', password='test12345')
        
        data = {
            'nombre': '',
            'apellido': '',
            'fecha_nacimiento': '',
            'sexo': '',
            'correo_electronico': '',
            'telefono': '',
            'dni': '',
            'nombre_usuario': ''
        }
        response = self.client.post(self.detalles_usuario_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Este campo es obligatorio.')




    def test_detalles_usuario_invalido(self):
        response = self.client.get(self.detalles_usuario_url)
        self.assertEqual(response.status_code, 302)

    def test_agregar_objeto_lista_deseos_valido(self):
        self.client.login(username='usuario_test2', password='test12345')
        
        response = self.client.get(self.agregar_objeto_lista_deseos_url)
        
        self.assertRedirects(response, self.lista_deseos_url)

        response2 = self.client.get(self.lista_deseos_url)

        objetos_deseados = response2.context['objetos_deseados']
        self.assertEqual(len(objetos_deseados), 2)

    def test_agregar_objeto_lista_deseos_invalido(self):
        self.client.login(username='usuario_test2', password='test12345')
        
        response = self.client.get(self.agregar_objeto_lista_deseos_url_2)
        
        self.assertRedirects(response, self.lista_deseos_url)

        response2 = self.client.get(self.lista_deseos_url)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "El objeto ya está en la lista de deseos.")

        objetos_deseados = response2.context['objetos_deseados']
        self.assertEqual(len(objetos_deseados), 1)

    def test_consultar_huella_carbono_reducida_valido(self):
        self.client.login(username='usuario_test2', password='test12345')

        response = self.client.get(self.consultar_huella_carbono_reducida_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'huella_carbono_reducida.html')
        self.assertEqual(response.context['cantidad_huella_ahorrada'], 0.00)

    def test_consultar_huella_carbono_reducida_invalido(self):
        response = self.client.get(self.consultar_huella_carbono_reducida_url)
        self.assertEqual(response.status_code, 302)

    def test_consultar_amonestaciones_valido(self):
        self.client.login(username='usuario_test2', password='test12345')

        response = self.client.get(self.consultar_amonestaciones_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'consultar_amonestaciones.html')
        self.assertEqual(len(response.context['amonestaciones']), 0)
        self.assertEqual(response.context['total_amonestaciones'], 0)

    def test_consultar_amonestaciones_invalido(self):
        response = self.client.get(self.consultar_amonestaciones_url)
        self.assertEqual(response.status_code, 302)
