from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Almacen , AlmacenValoracion

@login_required
def obtener_almacenes(request):

    filtro = request.GET.get('busqueda_almacen', '')
    almacenes = Almacen.objects.all()
    if filtro:
        almacenes = almacenes.filter(nombre__icontains=filtro) | almacenes.filter(localizacion__ciudad__icontains=filtro)
    return render(request, 'almacenes.html', {'almacenes': almacenes,})

@login_required
def obtener_almacen(request, almacen_id):
    if almacen_id:
        try:
            almacen = Almacen.objects.get(id=almacen_id)
            return render(request, 'almacen_valoracion.html', {'almacen': almacen})
        except Almacen.DoesNotExist:
            return render(request, 'almacen_valoracion.html', {'error': 'Almacén no encontrado'})
    else:
        return render(request, 'almacen_valoracion.html', {'error': 'ID de almacén no proporcionado'})
    
@login_required
def obtener_comentarios(request, almacen_id):
    if almacen_id:
        try:
            almacen = Almacen.objects.get(id=almacen_id)
            comentarios = almacen.comentarios.all()
            return render(request, 'comentarios.html', {'almacen': almacen, 'comentarios': comentarios})
        except Almacen.DoesNotExist:
            return render(request, 'comentarios.html', {'error': 'Almacén no encontrado'})
    else:
        return render(request, 'comentarios.html', {'error': 'ID de almacén no proporcionado'})
    
@login_required
def valorar_almacen(request, almacen_id):
    try:
        almacen = Almacen.objects.get(id=almacen_id)
        valoracion_existente = AlmacenValoracion.objects.filter(almacen=almacen, usuario=request.user).first()

        if request.method == 'POST':
            valoracion = request.POST.get('puntuacion')
            comentario = request.POST.get('comentario')

            if not valoracion or not comentario.strip():
                return render(request, 'almacen_valoracion.html', {
                    'almacen': almacen,
                    'valoracion': valoracion_existente,
                    'error': 'Debes proporcionar una puntuación y un comentario.'
                })

            if valoracion_existente:
                # Actualizar valoración existente
                valoracion_existente.estrellas = valoracion
                valoracion_existente.comentario = comentario.strip()
                valoracion_existente.save()
            else:
                # Crear nueva valoración
                nueva_valoracion = AlmacenValoracion(
                    almacen=almacen,
                    usuario=request.user,
                    estrellas=valoracion,
                    comentario=comentario.strip()
                )
                nueva_valoracion.save()

            return render(request, 'menu.html')

        return render(request, 'almacen_valoracion.html', {
            'almacen': almacen,
            'valoracion': valoracion_existente
        })
    except Almacen.DoesNotExist:
        return render(request, 'almacenes.html', {'error': 'Almacén no encontrado'})
