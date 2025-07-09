from django.shortcuts import render, redirect
from objeto.models import Objeto, ObjetoValoracion, ObjetoValoracionDenuncia
from django.contrib import messages
from almacen.models import Almacen, Horario
from alquiler.models import Alquiler
from core.models import BaseValoracionDenuncia
from django.db.models import Q, F, ExpressionWrapper, FloatField, OuterRef, Exists, Count
from django.utils.timezone import now 
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, IntegerField, Value, Avg
from core.decorators import usuario_required, gestor_required
from almacen.models import AlmacenValoracion


CONDICIONES_POR_EXPERIENCIA = {
    'Principiante': ['Nuevo', 'Bueno'],
    'Intermedio':   ['Nuevo', 'Bueno', 'Desgastado'],
    'Avanzado':     ['Nuevo', 'Bueno', 'Desgastado', 'Perdido'],
}

DIAS_POR_FRANJA = {
    'Mañana':           ['Lunes','Martes','Miércoles','Jueves','Viernes'],
    'Tarde':            ['Lunes','Martes','Miércoles','Jueves','Viernes'],
    'Fines de semana':  ['Sábado','Domingo'],
    'Sin preferencia':  ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'],
}

@usuario_required
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


@usuario_required
def detalle_objeto(request, objeto_id):
    objeto = Objeto.objects.filter(id=objeto_id).first()
    """
    Vista para mostrar el detalle de un objeto.
    """

    if not objeto:
        messages.error(request, 'El objeto no existe.')
        return redirect('catalogo')
    almacen_asociado = objeto.almacen

    estrellas = objeto.valoraciones_recibidas_objeto.aggregate(
        media_estrellas = Avg('estrellas')
    ) ['media_estrellas'] or 0


    if request.method == 'POST':
        fecha_inicio = request.POST.get('fecha_inicio_principal')
        fecha_fin = request.POST.get('fecha_fin_principal')
        
        if fecha_inicio and fecha_fin:
            if (datetime.strptime(fecha_inicio, '%Y-%m-%d').date() < now().date()) or (datetime.strptime(fecha_fin, '%Y-%m-%d').date() < now().date())  or (datetime.strptime(fecha_inicio, '%Y-%m-%d').date() > datetime.strptime(fecha_fin, '%Y-%m-%d').date()):
                messages.error(request, 'Las fechas de inicio y fin deben ser válidas y la fecha de inicio no puede ser posterior a la fecha de fin.')
                return render(request, 'detalle_objeto.html', {'objeto': objeto, 'estrellas': estrellas, 'almacen_asociado':almacen_asociado})
            else:
                Alquiler.objects.create(
                objeto=objeto,
                usuario=request.user,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            return redirect('/mis_reservas')  


        


    return render(request, 'detalle_objeto.html', {'objeto': objeto, 'estrellas': estrellas ,'almacen_asociado':almacen_asociado })
        

@usuario_required
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

@usuario_required
def obtener_comentarios_objeto(request, objeto_id):
    objeto = Objeto.objects.get(id=objeto_id)
    valoraciones_recibidas = objeto.valoraciones_recibidas_objeto.all()
    valoracion_media = valoraciones_recibidas.aggregate(Avg('estrellas'))['estrellas__avg']
    denuncia_choices = BaseValoracionDenuncia.ENUM_CATEGORIA_DENUNCIA
    comentarios_info = []
    for comentario in valoraciones_recibidas:
        ya_denunciado = ObjetoValoracionDenuncia.objects.filter(
        valoracion=comentario, usuario=request.user).exists()
        comentarios_info.append({
            'comentario': comentario,
            'ya_denunciado': ya_denunciado
        })

    return render(request, 'comentarios_objeto.html', {'objeto': objeto, 'valoraciones': valoraciones_recibidas, 'valoracion_media': valoracion_media, 'comentarios_info':comentarios_info,'denuncia_choices': denuncia_choices})

@usuario_required
def denunciar_valoracion_objeto(request, comentario_id):
    comentario = ObjetoValoracion.objects.filter(id=comentario_id).first()
    if not comentario:
        messages.error(request, 'El comentario no existe.')
        return redirect('catalogo')

    if request.method == 'POST':
        categoria1=request.POST.get('categoria', '')
        contexto1= request.POST.get('contexto', '')
        if not categoria1 or not contexto1.strip():
            messages.error(request, 'Debe seleccionar una categoría y proporcionar un contexto para la denuncia.')
            return render(request, 'comentarios_objeto.html', {'comentario': comentario})
        nueva_denuncia = comentario.denuncias_recibidas_objeto.create(
            usuario=request.user,
            categoria= categoria1,
            contexto= contexto1
        )
        nueva_denuncia.save()

    return render(request, 'comentarios_objeto.html', {'comentario': comentario})

@usuario_required
def eliminar_valoracion_objeto(request, comentario_id):
    comentario = ObjetoValoracion.objects.filter(id=comentario_id, usuario=request.user).first()
    if not comentario:
        messages.error(request, 'No tienes permiso para eliminar esta valoración.')
        return redirect('catalogo')

    objeto_id = comentario.objeto.id
    comentario.delete()
    return redirect('comentarios_obj', objeto_id=objeto_id)

@usuario_required
def objetos_recomendados(request):
    pref = request.user.preferencia

    horario_qs = Horario.objects.filter(
        almacen=OuterRef('almacen'),
        dia_semana__in=DIAS_POR_FRANJA[pref.franja_horaria]
    )

    objetos = Objeto.objects.annotate(
        match_categoria=Case(
            When(categoria=pref.tarea_tipo, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        ),
        match_experiencia=Case(
            When(condicion__in=CONDICIONES_POR_EXPERIENCIA[pref.experiencia], then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        ),
        match_horario=Case(
            When(Exists(horario_qs), then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        ),
    ).annotate(
        score=ExpressionWrapper(
            F('match_categoria')*5 +
            F('match_experiencia')*3 +
            F('match_horario')*1 -
            F('huella_carbono')*0.1,
            output_field=FloatField()
        )
    ).order_by('-score', 'huella_carbono')

    return objetos

@usuario_required
def lista_objetos_recomendados(request):
    
    objetos = objetos_recomendados(request)
    almacenes = Almacen.objects.all()

    return render(request, 'catalogo.html', {'herramientas': objetos, 'almacenes':almacenes})


#------------------------------------------------------------------------------------------------------------------------------------

#Funcionalidades relacionadas con el gestor

#------------------------------------------------------------------------------------------------------------------------------------
ENUM_TAREA_TIPO= [('Bricolaje', 'Bricolaje'), ('Jardín', 'Jardín'), ('Cocina', 'Cocina'), ('Electrónica', 'Electrónica'), ('Herramientas', 'Herramientas'), ('Limpieza', 'Limpieza'), ('Otros', 'Otros')]
ENUM_CONDICION = [('Nuevo', 'Nuevo'), ('Bueno', 'Bueno'), ('Desgastado', 'Desgastado'), ('Perdido', 'Perdido')]


@gestor_required
def gestion_objetos_gestor(request):
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
    return render(request, 'catalogo_gestor.html', {'herramientas': herramientas, 'almacenes':almacenes, 'ENUM_TAREA_TIPO':ENUM_TAREA_TIPO, 'ENUM_CONDICION':ENUM_CONDICION})

@gestor_required
def eliminar_articulo_catalogo_gestor(request, objeto_id):
    try:
        objeto = Objeto.objects.get(id=objeto_id)

        if request.method == 'POST':
            objeto.delete()
            messages.success(request, 'Objeto eliminado correctamente.')
        else:
            messages.error(request, 'Método no permitido.')
        return redirect('gestion_objetos_gestor')

    except Objeto.DoesNotExist:
        messages.error(request, 'El objeto no existe.')
        return redirect('gestion_objetos_gestor')
    
    
@gestor_required
def editar_articulo_catalogo_gestor(request, objeto_id):
    try:
        objeto_a_modificar = Objeto.objects.get(id=objeto_id)
        if request.method == 'POST':
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            categoria = request.POST.get('categoria')
            condicion = request.POST.get('condicion')
            huella_carbono = request.POST.get('huella_carbono')
            almacen_id = request.POST.get('almacen')
            imagen = request.FILES.get('imagen') #Añadir validador para comprobar que sea una imagen, no un pdf o video ....
            
            
            

            if not nombre or not descripcion or not categoria or not condicion or not huella_carbono or not almacen_id:
                messages.error(request, 'Todos los campos son obligatorios.')
                return redirect('gestion_objetos_gestor')

            objeto_a_modificar.nombre = nombre
            objeto_a_modificar.descripcion = descripcion
            objeto_a_modificar.categoria = categoria
            objeto_a_modificar.condicion = condicion
            huella_carbono = huella_carbono.replace(',', '.')
            objeto_a_modificar.huella_carbono = float(huella_carbono)
            objeto_a_modificar.almacen = Almacen.objects.get(id=almacen_id)
            if imagen:
                objeto_a_modificar.imagen = imagen
            objeto_a_modificar.save()

            messages.success(request, 'Objeto actualizado correctamente.')
            return redirect('gestion_objetos_gestor')
    except Objeto.DoesNotExist:
        messages.error(request, 'El objeto no existe.')
        return redirect('gestion_objetos_gestor')

@gestor_required
def crear_articulo_catalogo_gestor(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        categoria = request.POST.get('categoria')
        condicion = request.POST.get('condicion')
        huella_carbono = request.POST.get('huella_carbono')
        almacen_id = request.POST.get('almacen')
        imagen = request.FILES.get('imagen') #Añadir validador para comprobar que sea una imagen, no un pdf o video ....
        
        

        if not nombre or not descripcion or not categoria or not condicion or not huella_carbono or not almacen_id:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('gestion_objetos_gestor')

        nuevo_objeto = Objeto(
            nombre=nombre,
            descripcion=descripcion,
            categoria=categoria,
            condicion=condicion,
            huella_carbono=float(huella_carbono.replace(',', '.')),
            almacen=Almacen.objects.get(id=almacen_id),
            imagen=imagen
        )
        nuevo_objeto.save()

        messages.success(request, 'Objeto creado correctamente.')
        return redirect('gestion_objetos_gestor')


#------------------------------------------------------------------------------------------------------------------------------------

#Funcionalidades relacionadas con el administrador

#------------------------------------------------------------------------------------------------------------------------------------

def gestion_denuncias_administrador(request):
    valoraciones_objeto_denunciadas = ObjetoValoracion.objects.annotate(
        num_denuncias=Count('denuncias_recibidas_objeto')
    ).filter(num_denuncias__gt=2)

    valoraciones_almacen_denunciadas = AlmacenValoracion.objects.annotate(
        num_denuncias=Count('denuncias_recibidas_almacen')
    ).filter(num_denuncias__gt=2)


    return render(request, 'gestion_denuncias_administrador.html', {'valoraciones_objeto_denunciadas': valoraciones_objeto_denunciadas, 'valoraciones_almacen_denunciadas': valoraciones_almacen_denunciadas})

def eliminar_denuncias_valoracion_objeto_administrador(request, valoracion_id):
    try:
        valoracion = ObjetoValoracion.objects.get(id=valoracion_id)
        if request.method == 'POST':
            valoracion.denuncias_recibidas_objeto.all().delete()
            messages.success(request, 'Denuncias eliminadas correctamente.')
        else:
            messages.error(request, 'Método no permitido.')
        return redirect('gestion_denuncias_administrador')
    except ObjetoValoracion.DoesNotExist:
        messages.error(request, 'La valoración no existe.')
        return redirect('gestion_denuncias_administrador')
    
def eliminar_valoracion_objeto_administrador(request, valoracion_id):
    try:
        valoracion = ObjetoValoracion.objects.get(id=valoracion_id)
        if request.method == 'POST':
            valoracion.delete()
            messages.success(request, 'Valoración eliminada correctamente.')
        else:
            messages.error(request, 'Método no permitido.')
        return redirect('gestion_denuncias_administrador')
    except ObjetoValoracion.DoesNotExist:
        messages.error(request, 'La valoración no existe.')
        return redirect('gestion_denuncias_administrador')
    
def eliminar_denuncias_valoracion_almacen_administrador(request, valoracion_id):
    try:
        valoracion = AlmacenValoracion.objects.get(id=valoracion_id)
        if request.method == 'POST':
            valoracion.denuncias_recibidas_almacen.all().delete()
            messages.success(request, 'Denuncias eliminadas correctamente.')
        else:
            messages.error(request, 'Método no permitido.')
        return redirect('gestion_denuncias_administrador')
    except AlmacenValoracion.DoesNotExist:
        messages.error(request, 'La valoración no existe.')
        return redirect('gestion_denuncias_administrador')
    
def eliminar_valoracion_almacen_administrador(request, valoracion_id):
    try:
        valoracion = AlmacenValoracion.objects.get(id=valoracion_id)
        if request.method == 'POST':
            valoracion.delete()
            messages.success(request, 'Valoración eliminada correctamente.')
        else:
            messages.error(request, 'Método no permitido.')
        return redirect('gestion_denuncias_administrador')
    except AlmacenValoracion.DoesNotExist:
        messages.error(request, 'La valoración no existe.')
        return redirect('gestion_denuncias_administrador')