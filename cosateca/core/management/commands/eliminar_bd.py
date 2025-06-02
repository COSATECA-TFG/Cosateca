from django.core.management.base import BaseCommand
from usuario.models import Usuario   # importa todos los modelos que quieras borrar

class Command(BaseCommand):
    help = 'Borra los datos de la base de datos'

    def handle(self, *args, **kwargs):
        Usuario.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Todos los datos han sido eliminados'))