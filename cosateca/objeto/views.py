from django.shortcuts import render, redirect
from objeto.models import Objeto, ObjetoValoracion, ObjetoValoracionDenuncia
from django.contrib import messages
from almacen.models import Almacen
from alquiler.models import Alquiler
from core.models import BaseValoracionDenuncia


from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, IntegerField, Value, Avg

@login_required
def catalogo(request):
    herramientas = Objeto.objects.all()
    almacenes = Almacen.objects.all()
    categoria = request.GET.get('categoria', '')
    if categoria:
        herramientas = herramientas.filter(categoria__icontains=categoria)

    condicion = request.GET.get('condicion', '')
    if condicion:
        herramientas = herramientas.filter(condicion__icontains=condicion)

    localizacion = request.GET.get('almacen', '')
    if localizacion:
        herramientas = herramientas.filter(almacen__nombre__icontains=localizacion)

    orden_condicion = request.GET.get('orden_condicion', '')
    if orden_condicion: 
        herramientas = herramientas.annotate(
            condicion_valor=Case(
                When(condicion='Nuevo', then=Value(1)),
                When(condicion='Bueno', then=Value(2)),
                When(condicion='Desgastado', then=Value(3)),
                When(condicion='Perdido', then=Value(4)),
                default=0,
                output_field=IntegerField()
            )
        )
        if orden_condicion == 'Menor':
            herramientas = herramientas.order_by('-condicion_valor')
        else:
            herramientas = herramientas.order_by('condicion_valor')

    orden_valoracion = request.GET.get('orden_valoracion', '')
    if orden_valoracion:
        if orden_valoracion == 'Mayor':
            herramientas = herramientas.order_by('-valoraciones_recibidas_objeto__estrellas')
        else:
            herramientas = herramientas.order_by('valoraciones_recibidas_objeto__estrellas')
    if request.method == 'GET':
        nombre = request.GET.get('nombre_herramienta', '')
        if nombre:
            herramientas = herramientas.filter(nombre__icontains=nombre)
    return render(request, 'catalogo.html', {'herramientas': herramientas, 'almacenes':almacenes})


@login_required
def detalle_objeto(request, objeto_id):
    objeto = Objeto.objects.get(id=objeto_id)
    almacen_asociado = objeto.almacen

    estrellas = objeto.valoraciones_recibidas_objeto.aggregate(
        media_estrellas = Avg('estrellas')
    ) ['media_estrellas'] or 0


    if request.method == 'POST':
        fecha_inicio = request.POST.get('fecha_inicio_principal')
        fecha_fin = request.POST.get('fecha_fin_principal')
        if fecha_inicio and fecha_fin:
            Alquiler.objects.create(
                objeto=objeto,
                usuario=request.user,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            return redirect('/mis_reservas')  


        


    return render(request, 'detalle_objeto.html', {'objeto': objeto, 'estrellas': estrellas ,'almacen_asociado':almacen_asociado })
        

@login_required
def valorar_objeto(request, objeto_id):
    objeto = Objeto.objects.get(id=objeto_id)
    valoracion_existente = ObjetoValoracion.objects.filter(objeto=objeto, usuario=request.user).first()

    
    
    if request.method == 'POST':
            valoracion = request.POST.get('puntuacion')
            comentario = request.POST.get('comentario')

            if not valoracion or not comentario.strip():
                messages.error(request, 'No se puede valorar un objeto sin puntuación o comentario.')
                return render(request, 'objeto_valoracion.html', {'objeto': objeto, 'valoracion': valoracion_existente})

            if valoracion_existente:
                valoracion_existente.estrellas = valoracion
                valoracion_existente.comentario = comentario.strip()
                valoracion_existente.save()
            else:
                nueva_valoracion = ObjetoValoracion(
                    objeto=objeto,
                    usuario=request.user,
                    estrellas=valoracion,
                    comentario=comentario.strip()
                )
                nueva_valoracion.save()

            return redirect('comentarios_obj', objeto_id=objeto_id)

    
    return render(request, 'objeto_valoracion.html', {'objeto': objeto, 'valoracion': valoracion_existente})

@login_required
def obtener_comentarios_objeto(request, objeto_id):
    objeto = Objeto.objects.get(id=objeto_id)
    valoraciones_recibidas = objeto.valoraciones_recibidas_objeto.all()
    valoracion_media = valoraciones_recibidas.aggregate(Avg('estrellas'))['estrellas__avg']
    denuncia_choices = BaseValoracionDenuncia.ENUM_CATEGORIA_DENUNCIA

    
                # Añadir información de denuncia para cada comentario
    comentarios_info = []
    for comentario in valoraciones_recibidas:
        ya_denunciado = ObjetoValoracionDenuncia.objects.filter(
        valoracion=comentario, usuario=request.user).exists()
        comentarios_info.append({
            'comentario': comentario,
            'ya_denunciado': ya_denunciado
        })

    return render(request, 'comentarios_objeto.html', {'objeto': objeto, 'valoraciones': valoraciones_recibidas, 'valoracion_media': valoracion_media, 'comentarios_info':comentarios_info,'denuncia_choices': denuncia_choices})

@login_required
def denunciar_valoracion_objeto(request, comentario_id):
    comentario = ObjetoValoracion.objects.get(id=comentario_id)
    nueva_denuncia = comentario.denuncias_recibidas_objeto.create(
        usuario=request.user,
        categoria=request.POST.get('categoria', ''),
        contexto= request.POST.get('contexto', '')
    )
    nueva_denuncia.save()
    
    return render(request, 'comentarios_objeto.html', {'comentario': comentario})


def eliminar_valoracion_objeto(request, comentario_id):
    comentario = ObjetoValoracion.objects.get(id=comentario_id, usuario=request.user)
    objeto_id = comentario.objeto.id
    comentario.delete()
    return redirect('comentarios_obj', objeto_id=objeto_id)
