from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class BaseValoracion(models.Model):
    estrellas = models.PositiveIntegerField(default=0, blank=False, null=False, validators=[MinValueValidator(0), MaxValueValidator(5)])
    comentario = models.TextField(blank=True, null=True)
    class Meta:
        abstract = True

class BaseValoracionDenuncia(models.Model):
    ENUM_CATEGORIA_DENUNCIA = [("Opinión falsa", "Opinión falsa"),
                              ("Lenguaje ofensivo", "Lenguaje ofensivo"),
                              ("Acoso", "Acoso"),
                              ("Contenido sexual", "Contenido sexual"),
                              ("Autolesiones", "Autolesiones"),
                              ("Difamación", "Difamación"),
                              ("Violación de privacidad", "Violación de privacidad"),
                              ("Otra", "Otra")]

    categoria = models.CharField(choices= ENUM_CATEGORIA_DENUNCIA, blank=False, null=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    contexto = models.TextField(max_length=500, blank=False, null=False)
    class Meta:
        abstract = True