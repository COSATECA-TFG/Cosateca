from django.core.management.base import BaseCommand
from usuario.models import Usuario, Gestor, Preferencia, Amonestacion
from almacen.models import Almacen, Localizacion, Horario, AlmacenValoracion, AlmacenValoracionDenuncia
from objeto.models import Objeto
from django.utils import timezone
from datetime import date

class Command(BaseCommand):
    help = 'Puebla la base de datos con datos iniciales'

    def handle(self, *args, **kwargs):
        usuarios = [
            {
                'username': 'usuario1',
                'first_name': 'Ana',
                'last_name': 'García',
                'fecha_nacimiento': date(1990, 5, 15),
                'sexo': 'F',
                'email': 'ana.garcia@example.com',
                'telefono': '600123456',
                'dni': '12345678A',
                'estado': 'A',
                'password': 'password123'
            },
            {
                'username': 'usuario2',
                'first_name': 'Luis',
                'last_name': 'Pérez',
                'fecha_nacimiento': date(1985, 8, 22),
                'sexo': 'M',
                'email': 'luis.perez@example.com',
                'telefono': '600654321',
                'dni': '87654321B',
                'estado': 'A',
                'password': 'password123'
            },
            {
                'username': 'usuario3',
                'first_name': 'Alex',
                'last_name': 'Martín',
                'fecha_nacimiento': date(1995, 3, 9),
                'sexo': 'NB',
                'email': 'alex.martin@example.com',
                'telefono': '111541111',
                'dni': '11223344C',
                'estado': 'S',
                'password': 'password123'
            },
        ]
        
        
        gestores = [
            {
                'username': 'gestor1',
                'first_name': 'Pepe',
                'last_name': 'Martín',
                'fecha_nacimiento': date(1995, 3, 9),
                'sexo': 'NB',
                'email': 'pepe1@example.com',
                'telefono': '600789782',
                'dni': '11223377C',
                'estado': 'S',
                'password': 'password123'
                
            },
            
            {
                'username': 'gestor2',
                'first_name': 'Papa',
                'last_name': 'Gestora',
                'fecha_nacimiento': date(1995, 3, 9),
                'sexo': 'P',
                'email': 'pepe2@example.com',
                'telefono': '111111111',
                'dni': '11111111A',
                'estado': 'S',
                'password': 'password123'
                
            }
            
        ]



        for data in usuarios:
            if not Usuario.objects.filter(username=data['username']).exists():
                user = Usuario(
                    username=data['username'],
                    email=data['email'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    fecha_nacimiento=data['fecha_nacimiento'],
                    sexo=data['sexo'],
                    telefono=data['telefono'],
                    dni=data['dni'],
                    estado=data['estado'],
                )
                user.set_password(data['password'])
                user.save()
                
        
        for data in gestores:
            if not Gestor.objects.filter(username=data['username']).exists():
                gestor = Gestor(
                    username=data['username'],
                    email=data['email'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    fecha_nacimiento=data['fecha_nacimiento'],
                    sexo=data['sexo'],
                    telefono=data['telefono'],
                    dni=data['dni'],
                    estado=data['estado'],
                    )
                gestor.set_password(data['password'])
                gestor.save()
                
        if not Almacen.objects.exists():
            localizacion = Localizacion.objects.create(
                latitud=37.388630,
                longitud=-5.995340,
                calle="Calle Ejemplo",
                numero="123",
                pais="España",
                ciudad="Sevilla",
                codigo_postal="41001"
            )
            almacen = Almacen.objects.create(
                nombre="Almacén Central",
                descripcion="Almacén principal de la empresa",
                localizacion=localizacion
            )
                
                
        
        preferencia1 = Preferencia(
            tarea_tipo='Bricolaje',
            frecuencia_uso='Semanal',
            experiencia='Intermedio',
            franja_horaria='Tarde'
        )
        
        
        amonestacion1 = Amonestacion(
            motivo= "Mal comportamiento",
            severidad='Leve',
        )
        
        
        horario1 = Horario(
            dia_semana='Lunes',
            hora_inicio=timezone.now().replace(hour=9, minute=0, second=0, microsecond=0),
            hora_fin=timezone.now().replace(hour=17, minute=0, second=0, microsecond=0),
        )
        
        
        valoracion_almacen1 = AlmacenValoracion(
            estrellas=4,
            comentario="Buen servicio y atención al cliente",
        )
        
        
        valoracion_denuncia1 = AlmacenValoracionDenuncia(
            categoria="Opinión falsa",
            contexto="El usuario ha publicado una opinión falsa sobre el servicio.",
        )


        
        
        almacen = Almacen.objects.get(nombre="Almacén Central")
        objetos = [
    {
        'nombre': 'Taladro Bosch',
        'descripcion': 'Taladro eléctrico Bosch de 500W, ideal para bricolaje doméstico.',
        'categoria': 'Bricolaje',
        'condicion': 'Bueno',
        'huella_carbono': 12.50,
        'imagen': '',  
    },
    {
        'nombre': 'Cortacésped',
        'descripcion': 'Cortacésped manual para jardines pequeños y medianos.',
        'categoria': 'Jardín',
        'condicion': 'Desgastado',
        'huella_carbono': 8.20,
        'imagen': '',
    },
    {
        'nombre': 'Batidora Moulinex',
        'descripcion': 'Batidora de mano Moulinex, perfecta para repostería y cocina diaria.',
        'categoria': 'Cocina',
        'condicion': 'Nuevo',
        'huella_carbono': 5.75,
        'imagen': '',
    },
    {
        'nombre': 'Multímetro digital',
        'descripcion': 'Multímetro digital para mediciones eléctricas y electrónicas.',
        'categoria': 'Electrónica',
        'condicion': 'Bueno',
        'huella_carbono': 3.10,
        'imagen': '',
    },
    {
        'nombre': 'Martillo',
        'descripcion': 'Martillo de acero inoxidable, resistente y duradero.',
        'categoria': 'Herramientas',
        'condicion': 'Bueno',
        'huella_carbono': 2.80,
        'imagen': '',
    },
    {
        'nombre': 'Aspiradora Rowenta',
        'descripcion': 'Aspiradora potente para limpieza de alfombras y suelos.',
        'categoria': 'Limpieza',
        'condicion': 'Bueno',
        'huella_carbono': 9.60,
        'imagen': '',
    },
    {
        'nombre': 'Caja de tornillos',
        'descripcion': 'Caja con tornillos de varios tamaños para bricolaje.',
        'categoria': 'Otros',
        'condicion': 'Nuevo',
        'huella_carbono': 1.20,
        'imagen': '',
    },
    {
        'nombre': 'Destornillador eléctrico',
        'descripcion': 'Destornillador eléctrico recargable, incluye varias puntas.',
        'categoria': 'Herramientas',
        'condicion': 'Bueno',
        'huella_carbono': 4.50,
        'imagen': '',
    },
    ]



        for obj in objetos:
            if not Objeto.objects.filter(nombre=obj['nombre']).exists():
                Objeto.objects.create(
                    nombre=obj['nombre'],
                    descripcion=obj['descripcion'],
                    categoria=obj['categoria'],
                    condicion=obj['condicion'],
                    huella_carbono=obj['huella_carbono'],
                    almacen=almacen,
                    imagen= 'https://res.cloudinary.com/cosateca/image/upload/v1751389089/placeholder_oiztci.png'
                )

        
        
        


        
                
                
                
        # Relaciones preferencias                
        usuario1 = Usuario.objects.get(username='usuario1')
        preferencia1.usuario = usuario1
        preferencia1.save()        
        
        # Relaciones almacen        
        gestor1  = Gestor.objects.get(username='gestor1')
        gestor2  = Gestor.objects.get(username='gestor2')
        almacen = Almacen.objects.get(nombre="Almacén Central")
        gestor1.almacen = almacen
        gestor2.almacen = almacen
        gestor1.save()
        gestor2.save()
        
        
        #Relacion amonestacion
        amonestacion1.usuario = usuario1
        amonestacion1.gestor = gestor1 
        amonestacion1.save()
        
        
        #Relaciones horarios
        horario1.almacen = almacen
        horario1.save()

        # Relaciones valoracion almacen
        valoracion_almacen1.almacen = almacen
        valoracion_almacen1.usuario = usuario1
        valoracion_almacen1.save()
        
        # Relaciones valoracion denuncia
        usuario2 = Usuario.objects.get(username='usuario2')
        valoracion_denuncia1.valoracion = valoracion_almacen1
        valoracion_denuncia1.usuario = usuario2
        valoracion_denuncia1.save()
        
        
        self.stdout.write(self.style.SUCCESS("¡Población exitosa!"))


