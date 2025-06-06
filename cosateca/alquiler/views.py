from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Alquiler
from django.utils import timezone

# Create your views here.

@login_required
def historial_reservas(request):
    usuario = request.user
    reservas = Alquiler.objects.filter(usuario=usuario)
    return render(request, 'historial_reservas.html', {
        'reservas': reservas,
        'timezone': timezone,
        })