from django.core.management.base import BaseCommand
from usuario.models import Usuario, Gestor, Preferencia, Amonestacion
from almacen.models import Almacen, Localizacion, Horario, AlmacenValoracion, AlmacenValoracionDenuncia

class Command(BaseCommand):
    help = 'Borra los datos de la base de datos'

    def handle(self, *args, **kwargs):
        Usuario.objects.all().delete()
        Gestor.objects.all().delete()
        Preferencia.objects.all().delete()
        Amonestacion.objects.all().delete()
        Almacen.objects.all().delete()
        Localizacion.objects.all().delete()
        Horario.objects.all().delete()
        AlmacenValoracion.objects.all().delete()
        AlmacenValoracionDenuncia.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Todos los datos han sido eliminados'))
        
        