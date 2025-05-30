from django.contrib import admin

from .models import Almacen, Localizacion, Horario, AlmacenValoracion, ObjetoValoracionDenuncia
admin.site.register(Almacen)
admin.site.register(Localizacion)
admin.site.register(Horario)    
admin.site.register(AlmacenValoracion)
admin.site.register(ObjetoValoracionDenuncia)