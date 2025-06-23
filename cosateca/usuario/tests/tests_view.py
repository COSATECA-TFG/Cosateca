from django.test import TestCase, Client
from usuario.models import Usuario, Preferencia
from datetime import date
from django.urls import reverse

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

        self.registro_url = reverse('registro')
        self.inicio_sesion_url = reverse('inicio_sesion')
        self.cerrar_sesion_url = reverse('cerrar_sesion')
        self.cuestionario_preferencias_url = reverse('cuestionario_preferencias')
        self.menu_url = reverse('menu')
        self.lista_deseos_url = reverse('lista_deseos')
        self.eliminar_objeto_lista_deseos_url = reverse('eliminar_objeto', args=[1])
        self.detalles_usuario_url = reverse('usuario')
        self.agregar_objeto_lista_deseos_url = reverse('agregar_objeto', args=[1])
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

    def test_lista_deseos_valida(self):
        self.client.login(username='usuario_test2', password='test12345')
        response = self.client.get(self.lista_deseos_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lista_deseos.html')
        objetos_deseados = response.context['objetos_deseados']
        self.assertEqual(len(objetos_deseados), 0)

    def test_lista_deseos_invalida(self):
        response = self.client.get(self.lista_deseos_url)
        self.assertEqual(response.status_code, 302) 