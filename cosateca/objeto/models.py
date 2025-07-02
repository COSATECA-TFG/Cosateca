from django.db import models
from cloudinary.models import CloudinaryField

from core.models import BaseValoracion, BaseValoracionDenuncia
class Objeto(models.Model):
    ENUM_TAREA_TIPO= [('Bricolaje', 'Bricolaje'), ('Jardín', 'Jardín'), ('Cocina', 'Cocina'), ('Electrónica', 'Electrónica'), ('Herramientas', 'Herramientas'), ('Limpieza', 'Limpieza'), ('Otros', 'Otros')]
    ENUM_CONDICION = [('Nuevo', 'Nuevo'), ('Bueno', 'Bueno'), ('Desgastado', 'Desgastado'), ('Perdido', 'Perdido')]

    nombre = models.CharField(max_length=100, blank=False, null=False)
    descripcion = models.TextField(max_length=500, blank=False, null=False)
    imagen = CloudinaryField('imagen', blank=False, null=False, default='https://res.cloudinary.com/cosateca/image/upload/v1751389089/placeholder_oiztci.png')
    categoria = models.CharField(choices=ENUM_TAREA_TIPO, blank=False, null=False)
    condicion = models.CharField(choices=ENUM_CONDICION, blank=False, null=False)
    huella_carbono = models.DecimalField(max_digits=7, decimal_places=2, blank=False, null=False)

    almacen = models.ForeignKey('almacen.Almacen', on_delete=models.CASCADE, related_name='objetos', blank=False, null=False)
    usuario = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE, related_name='objetos_deseados', blank=True, null=True)

    def __str__(self):
        return f"Objeto: {self.nombre}"
    
    class Meta:
        verbose_name = 'Objeto'
        verbose_name_plural = 'Objetos'
    
class ObjetoValoracion(BaseValoracion):
    objeto = models.ForeignKey(Objeto, on_delete=models.CASCADE, related_name='valoraciones_recibidas_objeto', blank=False, null=False)
    usuario = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE, related_name='valoraciones_impuestas_objeto', blank=False, null=False)


    class Meta:
        unique_together = ('objeto', 'usuario')  
        verbose_name = 'Valoración de Objeto'
        verbose_name_plural = 'Valoraciones de Objetos'

    def __str__(self):
        return f"Valoración de {self.usuario.username} para {self.objeto.nombre}: {self.estrellas} estrellas"
    
class ObjetoValoracionDenuncia(BaseValoracionDenuncia):
    valoracion = models.ForeignKey(ObjetoValoracion, on_delete=models.CASCADE, related_name='denuncias_recibidas_objeto', blank=False, null=False)
    usuario = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE, related_name='denuncias_impuestas_valoracion_objeto', blank=False, null=False)

    class Meta:
        unique_together = ('valoracion', 'usuario') 
        verbose_name = 'Denuncia de Valoración de Objeto'
        verbose_name_plural = 'Denuncias de Valoraciones de Objetos' 

    def __str__(self):
        return f"Denuncia de {self.usuario.username} para valoración de {self.valoracion.objeto.nombre}"