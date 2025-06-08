from django.shortcuts import render, redirect
from .forms import RegistroForm, InicioSesionForm, CuestionarioForm
from django.contrib import messages
from .models import Usuario, Preferencia
from objeto.models import Objeto
from almacen.models import Almacen
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required



# Create your views here.


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
            sexo = form.cleaned_data['sexo']
            correo_electronico = form.cleaned_data['correo_electronico']
            telefono = form.cleaned_data['telefono']
            dni = form.cleaned_data['dni']
            nombre_usuario = form.cleaned_data['nombre_usuario']
            contraseña = form.cleaned_data['contraseña']

            
            
            nuevo_usuario = Usuario(
                first_name = nombre,
                last_name = apellido,
                fecha_nacimiento = fecha_nacimiento,
                sexo = sexo,
                email = correo_electronico,
                telefono =  telefono,
                dni = dni,
                username = nombre_usuario,
            )
            
            nuevo_usuario.set_password(contraseña)
            nuevo_usuario.save()
            request.session['usuario_id'] = nuevo_usuario.id
            
            return redirect('cuestionario_preferencias')
            
    else:
        form = RegistroForm()

    return render(request, 'registro.html', {'form': form})



def inicio_sesion(request):
    if request.method == 'POST':
        form = InicioSesionForm(request.POST)
        if form.is_valid():
            nombre_usuario = form.cleaned_data['nombre_usuario']
            contraseña = form.cleaned_data['contraseña']
            usuario_autenticado = authenticate(request, username=nombre_usuario, password=contraseña)
            
            if usuario_autenticado is not None:
                try:
                    usuario_autenticado.preferencia
                    login(request, usuario_autenticado)
                    return redirect('menu')
                except Preferencia.DoesNotExist:
                    request.session['usuario_id'] = usuario_autenticado.id
                    return redirect('cuestionario_preferencias')        

    else:
        form = InicioSesionForm()

    return render(request, 'inicio_sesion.html', {'form': form})

def cerrar_sesion(request):
    logout(request)
    return redirect('/')

def cuestionario_preferencias(request):
    if request.method == 'POST':
        form = CuestionarioForm(request.POST)
        if form.is_valid():
            usuario_id = request.session.get('usuario_id')
            if usuario_id:
                usuario = Usuario.objects.get(id=usuario_id)
                tarea_tipo = form.cleaned_data['tarea_tipo']
                frecuencia_uso = form.cleaned_data['frecuencia_uso']
                experiencia = form.cleaned_data['experiencia']
                franja_horaria = form.cleaned_data['franja_horaria']
                nueva_preferencia = Preferencia(
                    tarea_tipo=tarea_tipo,
                    frecuencia_uso=frecuencia_uso,
                    experiencia=experiencia,
                    franja_horaria=franja_horaria,
                    usuario=usuario
                )
                nueva_preferencia.save()
                login(request, usuario)
                request.session.pop('usuario_id', None)
                return redirect('menu')

    else:
        form = CuestionarioForm()

    return render(request, 'cuestionario_preferencias.html', {'form': form})
    

@login_required
def menu(request):
    return render(request, 'menu.html')

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
    if orden_condicion: #Si queremos meter mas tipos de ordenacion seguramente tengamos que meter js en el template para cambiar el valor de la url y cambiar aqui el if
        herramientas = herramientas.order_by('condicion')
    if request.method == 'GET':
        nombre = request.GET.get('nombre_herramienta', '')
        if nombre:
            herramientas = herramientas.filter(nombre__icontains=nombre)
    return render(request, 'catalogo.html', {'herramientas': herramientas, 'almacenes':almacenes})
        

