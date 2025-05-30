from django.contrib import admin
from .models import Usuario, Gestor, Amonestacion, Preferencia

admin.site.register(Usuario)
admin.site.register(Gestor)
admin.site.register(Amonestacion)
admin.site.register(Preferencia)