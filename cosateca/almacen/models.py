from django.db import models
from core.models import BaseValoracion, BaseValoracionDenuncia

class Localizacion(models.Model):    
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=False, null=False)
    longitud = models.DecimalField(max_digits=9,decimal_places=6, blank=False, null=False)
    calle = models.CharField(max_length=100, blank=False, null=False)
    numero = models.CharField(max_length=20, blank=False, null=False)
    pais = models.CharField(max_length=50, blank=False, null=False)
    ciudad = models.CharField(max_length=50, blank=False, null=False)
    codigo_postal = models.CharField(max_length=10, blank=False, null=False)

    class Meta:
        verbose_name = 'Localización'
        verbose_name_plural = 'Localizaciones'
    
class Almacen(models.Model):
    nombre = models.CharField(max_length=100, blank=False, null=False)
    descripcion = models.TextField(max_length=500, blank=False, null=False) 
    
    localizacion = models.OneToOneField(Localizacion, on_delete=models.CASCADE, related_name='almacen', blank=False, null=False)

    def __str__(self):
        return f"Almacén: {self.nombre}, Ubicación: {self.localizacion.calle} {self.localizacion.numero}, {self.localizacion.ciudad}, {self.localizacion.pais}"   

    class Meta:
        verbose_name = 'Almacén'
        verbose_name_plural = 'Almacenes' 

class Horario(models.Model):
    dia_semana = models.CharField(max_length=10, blank=False, null=False) 
    hora_inicio = models.TimeField(blank=False, null=False)
    hora_fin = models.TimeField(blank=False, null=False)
    
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name='horarios', blank=False, null=False)
    
    class Meta:
        unique_together = ('almacen', 'dia_semana') 
        verbose_name = 'Horario de Almacén'
        verbose_name_plural = 'Horarios de Almacenes'
        
    def __str__(self):
        return f"Horario de {self.almacen.nombre} - {self.dia_semana}: {self.hora_inicio} a {self.hora_fin}"
    
class AlmacenValoracion(BaseValoracion):
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name='valoraciones_recibidas_almacen', blank=False, null=False)
    usuario = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE, related_name='valoraciones_impuestas_almacen', blank=False, null=False)


    class Meta:
        unique_together = ('almacen', 'usuario')  
        verbose_name = 'Valoración de Almacén'
        verbose_name_plural = 'Valoraciones de Almacenes'
    def __str__(self):
        return f"Valoración de {self.usuario.username} para {self.almacen.nombre}: {self.estrellas} estrellas"


class AlmacenValoracionDenuncia(BaseValoracionDenuncia):
    valoracion = models.ForeignKey(AlmacenValoracion, on_delete=models.CASCADE, related_name='denuncias_recibidas_almacen', blank=False, null=False)
    usuario = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE, related_name='denuncias_impuestas_valoracion_almacen', blank=False, null=False)

    class Meta:
        unique_together = ('valoracion', 'usuario')
        verbose_name = 'Denuncia de Valoración de Almacén'
        verbose_name_plural = 'Denuncias de Valoraciones de Almacenes'  

    def __str__(self):
        return f"Denuncia de {self.usuario.username} para valoración  de {self.valoracion.almacen.nombre}"