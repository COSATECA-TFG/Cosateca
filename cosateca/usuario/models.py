from django.db import models
from django.contrib.auth.models import AbstractUser

from almacen.models import Almacen

# Create your models here.


class Usuario(AbstractUser):
    
    SEXOS = [('M', 'Masculino'), ('F', 'Femenino'), ('NB','No binario'), ('O', 'Otro'), ('P', 'Prefiero no responder')]
    ESTADOS = [('A', 'Activo'), ('S', 'Suspendido')]
    
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=100, blank=False, null=False)
    fecha_nacimiento = models.DateField(blank=False, null=False)
    sexo = models.CharField( choices=SEXOS, blank=False, null=False)
    email = models.EmailField (blank=False, null=False, unique=True)
    telefono = models.CharField(blank=False, null=False, unique=True, max_length=9)
    dni = models.CharField(blank=False, null=False, unique=True)
    estado= models.CharField(choices=ESTADOS, blank=False, null=False, default='A')

    REQUIRED_FIELDS = [
        'email',
        'first_name',
        'last_name',
        'fecha_nacimiento',
        'sexo',
        'telefono',
        'dni',
        
    ]
    
    USERNAME_FIELD = 'username'
    

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    
class Gestor(Usuario):    
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name='gestores', blank=True, null=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
    
    class Meta:
        verbose_name = 'Gestor'
        verbose_name_plural = 'Gestores'
    
class Preferencia(models.Model):
     ENUM_TAREA_TIPO= [('Bricolaje', 'Bricolaje'), ('Jardín', 'Jardín'), ('Cocina', 'Cocina'), ('Electrónica', 'Electrónica'), ('Herramientas', 'Herramientas'), ('Limpieza', 'Limpieza'), ('Otros', 'Otros')]
     ENUM_FRECUENCIA_USO = [('Diario', 'Diario'), ('Semanal', 'Semanal'), ('Mensual', 'Mensual'), ('Ocasiones puntuales', 'Ocasiones puntuales')]
     ENUM_EXPERIENCIA = [('Principiante', 'Principiante'), ('Intermedio', 'Intermedio'), ('Avanzado', 'Avanzado')]
     ENUM_FRANJA_HORARIA = [('Mañana', 'Mañana'), ('Tarde', 'Tarde'), ('Fines de semana', 'Fines de semana'), ('Sin preferencia', 'Sin preferencia')]
     tarea_tipo = models.CharField(choices=ENUM_TAREA_TIPO, blank=False, null=False)
     frecuencia_uso = models.CharField(choices=ENUM_FRECUENCIA_USO ,blank=False, null=False)
     experiencia = models.CharField(choices=ENUM_EXPERIENCIA,blank=False, null=False)
     franja_horaria = models.CharField(choices=ENUM_FRANJA_HORARIA, blank=False, null=False)

     usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='preferencia')
     
     def __str__(self):
        return f"Preferencia de: {self.usuario.username}"
     
     class Meta:
        verbose_name = 'Preferencia'
        verbose_name_plural = 'Preferencias'


class Amonestacion(models.Model):
    ENUM_SEVERIDAD = [('Leve', 'Leve'), ('Media', 'Media'), ('Grave', 'Grave')]
    
    motivo = models.TextField(max_length=500, blank=False, null=False)
    severidad = models.CharField(choices=ENUM_SEVERIDAD, blank=False, null=False)
    fecha = models.DateField(auto_now_add=True)
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='amonestaciones_recibidas', blank=True, null=True)
    gestor = models.ForeignKey(Gestor, on_delete=models.CASCADE, related_name='amonestaciones_creadas', blank=True, null=True)
    
    def __str__(self):
        return f"Amonestación de: {self.gestor.username} hacia: {self.usuario.username}, el día: {self.fecha}"
    
    class Meta:
        verbose_name = 'Amonestación'
        verbose_name_plural = 'Amonestaciones'
    
    

