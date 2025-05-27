from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Usuario(AbstractUser):
    
    SEXOS = [('M', 'Masculino'), ('F', 'Femenino'), ('NB','No binario'), ('O', 'Otro'), ('P', 'Prefiero no responder')]
    ESTADOS = [('A', 'Activo'), ('S', 'Suspendido')]
    
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=100, blank=False, null=False)
    fecha_nacimiento = models.DateField(blank=False, null=False)
    sexo = models.CharField( choices=SEXOS, blank=False, null=False)
    email = models.EmailField (blank=False, null=False, unique=True)
    telefono = models.CharField(blank=False, null=False, unique=True)
    dni = models.CharField(blank=False, null=False, unique=True)
    estado= models.CharField(choices=ESTADOS, blank=False, null=False, default='A')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
    
class Preferencia(models.Model):
     ENUM_TAREA_TIPO= [('Bricolaje', 'Bricolaje'), ('Jardín', 'Jardín'), ('Cocina', 'Cocina'), ('Electrónica', 'Electrónica'), ('Herramientas', 'Herramientas'), ('Limpieza', 'Limpieza'), ('Otros', 'Otros')]
     ENUM_FRECUENCIA_USO = [('Diario', 'Diario'), ('Semanal', 'Semanal'), ('Mensual', 'Mensual'), ('Ocasiones puntuales', 'Ocasiones puntuales')]
     ENUM_EXPERIENCIA = [('Principiante', 'Principiante'), ('Intermedio', 'Intermedio'), ('Avanzado', 'Avanzado')]
     ENUM_FRANJA_HORARIA = [('Mañana', 'Mañana'), ('Tarde', 'Tarde'), ('Fines de semana', 'Fines de semana'), ('Sin preferencia', 'Sin preferencia')]
     tarea_tipo = models.CharField( blank=False, null=False)
     frecuencia_uso = models.CharField( blank=False, null=False)
     experiencia = models.CharField(blank=False, null=False)
     franja_horaria = models.CharField( blank=False, null=False)

     usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='preferencia')


    
    

