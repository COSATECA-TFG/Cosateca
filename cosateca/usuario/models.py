from django.db import models

# Create your models here.


class Usuario(models.Model):
    
    SEXOS = [('M', 'Masculino'), ('F', 'Femenino')]
    
    
    nombre = models.CharField()
    apellido = models.CharField()
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1, choices=SEXOS)
    correo_electronico = models.EmailField()
    telefono = models.CharField()
    dni = models.CharField()
    nombre_usuario = models.CharField()
    contraseña = models.CharField()
    
    
    

