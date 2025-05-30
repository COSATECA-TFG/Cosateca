from django.contrib import admin
from .models import Objeto, ObjetoValoracion, ObjetoValoracionDenuncia

admin.site.register(Objeto)
admin.site.register(ObjetoValoracion)
admin.site.register(ObjetoValoracionDenuncia)
