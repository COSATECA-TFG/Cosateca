from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Alquiler
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from django.contrib import messages
from django.http import JsonResponse



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


@login_required
def editar_reserva(request, reserva_id):
    if request.method == 'POST':
        try:
            reserva = Alquiler.objects.get(id=reserva_id, usuario=request.user)
            nueva_fecha_inicio = request.POST.get('fecha_inicio')
            nueva_fecha_fin = request.POST.get('fecha_fin')

            if nueva_fecha_inicio and nueva_fecha_fin:
                reserva.fecha_inicio = nueva_fecha_inicio
                reserva.fecha_fin = nueva_fecha_fin
                reserva.save()
                messages.success(request, "Reserva actualizada exitosamente.")
            else:
                messages.error(request, "Por favor, selecciona fechas válidas.")
        except Alquiler.DoesNotExist:
            messages.error(request, "Reserva no encontrada.")

    return redirect('mis_reservas')


@login_required
def reservas_ocupadas(request, objeto_id):
    reserva_id = request.GET.get('reserva_id')
    hoy = timezone.now().date()

    if reserva_id and reserva_id.isdigit(): 
        reservas = Alquiler.objects.filter(objeto_id=objeto_id).exclude(id=int(reserva_id))
    else:
        reservas = Alquiler.objects.filter(objeto_id=objeto_id)

    eventos_pasados = [{
        "start": "2000-01-01",
        "end": hoy.strftime('%Y-%m-%d'),
        "display": "background",
        "overlap": False,
        "color": "#d3d3d3"
    }]

    eventos_reservas = [
        {
            "start": reserva.fecha_inicio.strftime('%Y-%m-%d'),
            "end": (reserva.fecha_fin + timedelta(days=1)).strftime('%Y-%m-%d'),
            "display": "background",
            "overlap": False,
            "color": "#c72222"
        }
        for reserva in reservas
    ]

    eventos = eventos_pasados + eventos_reservas

    return JsonResponse({"reservas": eventos})
