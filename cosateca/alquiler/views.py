from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Alquiler
from django.utils import timezone

# Create your views here.

@login_required
def historial_reservas(request):
    usuario = request.user
    filtro = request.GET.get('filtro', '')
    reservas = Alquiler.objects.filter(usuario=usuario)
    hoy = timezone.now().date()

    if filtro == 'programadas':
        reservas = reservas.filter(fecha_inicio__gt=hoy, cancelada=False)
    elif filtro == 'en_curso':
        reservas = reservas.filter(fecha_inicio__lte=hoy, fecha_fin__gte=hoy, cancelada=False)
    elif filtro == 'retrasadas':
        reservas = reservas.filter(fecha_fin__lt=hoy, fecha_entrega__isnull=True, cancelada=False)
    elif filtro == 'canceladas':
        reservas = reservas.filter(cancelada=True)
    elif filtro == 'finalizadas':
        reservas = reservas.filter(fecha_fin__lt=hoy, fecha_entrega__isnull=False, cancelada=False)

    return render(request, 'historial_reservas.html', {
        'reservas': reservas,
        'timezone': timezone,
    })

from django.contrib import messages

@login_required
def cancelar_reserva(request, reserva_id):
    try:
        reserva = Alquiler.objects.get(id=reserva_id, usuario=request.user)
        if not reserva.cancelada:
            reserva.cancelada = True
            reserva.save()
            messages.success(request, "Reserva cancelada exitosamente.")
        else:
            messages.info(request, "La reserva ya estaba cancelada.")
    except Alquiler.DoesNotExist:
        messages.error(request, "Reserva no encontrada.")

    return redirect('mis_reservas')


