from django.db import models


class Localizacion(models.Model):    
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=False, null=False)
    longitud = models.DecimalField(max_digits=9,decimal_places=6, blank=False, null=False)
    calle = models.CharField(max_length=100, blank=False, null=False)
    numero = models.CharField(max_length=20, blank=False, null=False)
    pais = models.CharField(max_length=50, blank=False, null=False)
    ciudad = models.CharField(max_length=50, blank=False, null=False)
    codigo_postal = models.CharField(max_length=10, blank=False, null=False)
    
class Almacen(models.Model):
    nombre = models.CharField(max_length=100, blank=False, null=False)
    descripcion = models.TextField(max_length=500, blank=False, null=False) 
    
    localizacion = models.OneToOneField(Localizacion, on_delete=models.CASCADE, related_name='almacen', blank=False, null=False)

    def __str__(self):
        return f"Almacén: {self.nombre}, Ubicación: {self.localizacion.calle} {self.localizacion.numero}, {self.localizacion.ciudad}, {self.localizacion.pais}"    

class Horario(models.Model):
    dia_semana = models.CharField(max_length=10, blank=False, null=False) 
    hora_inicio = models.TimeField(blank=False, null=False)
    hora_fin = models.TimeField(blank=False, null=False)
    
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name='horarios', blank=False, null=False)
    
    class Meta:
        unique_together = ('almacen', 'dia_semana') 
        
    def __str__(self):
        return f"Horario de {self.almacen.nombre} - {self.dia_semana}: {self.hora_inicio} a {self.hora_fin}"
