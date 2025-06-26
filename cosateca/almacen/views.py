from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Almacen, AlmacenValoracion, ObjetoValoracionDenuncia
from django.db.models import Avg
from core.models import BaseValoracionDenuncia

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
            valoracion_existente = AlmacenValoracion.objects.filter(almacen=almacen, usuario=request.user).first()
            return render(request, 'almacen_valoracion.html', {'almacen': almacen, 'valoracion': valoracion_existente})
        except Almacen.DoesNotExist:
            return render(request, 'almacen_valoracion.html', {'error': 'Almacén no encontrado'})
    else:
        return render(request, 'almacen_valoracion.html', {'error': 'ID de almacén no proporcionado'})
    
@login_required
def obtener_comentarios(request, almacen_id):
    if almacen_id:
        try:
            almacen = Almacen.objects.get(id=almacen_id)
            comentarios = almacen.valoraciones_recibidas_almacen.all()
            valoracion_media = comentarios.aggregate(Avg('estrellas'))['estrellas__avg']
            denuncia_choices = BaseValoracionDenuncia.ENUM_CATEGORIA_DENUNCIA

            # Añadir información de denuncia para cada comentario
            comentarios_info = []
            for comentario in comentarios:
                ya_denunciado = ObjetoValoracionDenuncia.objects.filter(
                    valoracion=comentario, usuario=request.user
                ).exists()
                comentarios_info.append({
                    'comentario': comentario,
                    'ya_denunciado': ya_denunciado
                })

            return render(request, 'comentarios_almacen.html', {
                'almacen': almacen,
                'comentarios_info': comentarios_info,
                'valoracion_media': valoracion_media,
                'denuncia_choices': denuncia_choices
})
        except Almacen.DoesNotExist:
            return render(request, 'comentarios_almacen.html', {'error': 'Almacén no encontrado'})
    else:
        return render(request, 'comentarios_almacen.html', {'error': 'ID de almacén no proporcionado'})
    
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
                valoracion_existente.estrellas = valoracion
                valoracion_existente.comentario = comentario.strip()
                valoracion_existente.save()
            else:
                nueva_valoracion = AlmacenValoracion(
                    almacen=almacen,
                    usuario=request.user,
                    estrellas=valoracion,
                    comentario=comentario.strip()
                )
                nueva_valoracion.save()

            return redirect('comentarios', almacen_id=almacen_id)

        return render(request, 'almacen_valoracion.html', {
            'almacen': almacen,
            'valoracion': valoracion_existente
        })
    except Almacen.DoesNotExist:
        return render(request, 'almacenes.html', {'error': 'Almacén no encontrado'})

@login_required
def eliminar_valoracion_almacen(request, comentario_id):
    try:
        comentario = AlmacenValoracion.objects.get(id=comentario_id, usuario=request.user)
        almacen_id = comentario.almacen.id
        comentario.delete()
        return redirect('comentarios', almacen_id=almacen_id)
    except AlmacenValoracion.DoesNotExist:
        return redirect('menu')
@login_required
def denunciar_valoracion_almacen(request, comentario_id):
    try:
        comentario = AlmacenValoracion.objects.get(id=comentario_id)
        denuncia_existente = ObjetoValoracionDenuncia.objects.filter(valoracion=comentario, usuario=request.user).first()
        if denuncia_existente:
            denuncia_existente.categoria = request.POST.get('categoria', '')
            denuncia_existente.contexto = request.POST.get('contexto', '')
            denuncia_existente.save()
        else:
            nueva_denuncia = comentario.denuncias_recibidas_almacen.create(
                usuario=request.user,
                categoria=request.POST.get('categoria', ''),
                contexto= request.POST.get('contexto', '')
            )
            nueva_denuncia.save()
        return redirect('comentarios', almacen_id=comentario.almacen.id)
    except AlmacenValoracion.DoesNotExist:
        return render(request, 'comentarios_almacen.html', {'error': 'Comentario no encontrado o no autorizado'})
