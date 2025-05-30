from django.db import models

class Alquiler(models.Model):
    fecha_inicio = models.DateField(null=False, blank=False)
    fecha_fin = models.DateField(null=False, blank=False)
    fecha_recogida = models.DateField(null=True, blank=True)
    fecha_entrega = models.DateField(null=True, blank=True)

    usuario = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE, related_name='alquileres', blank=False, null=False)
    objeto = models.ForeignKey('objeto.Objeto', on_delete=models.CASCADE, related_name='reservas', blank=False, null=False)


    def __str__(self):
        return f"Alquiler de {self.objeto.nombre} por {self.usuario.username} desde {self.fecha_inicio} hasta {self.fecha_fin}"
    
    class Meta:
        verbose_name = "Alquiler"
        verbose_name_plural = "Alquileres"
