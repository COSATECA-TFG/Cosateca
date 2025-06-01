from django.shortcuts import render, redirect
from .forms import RegistroForm
from .models import Usuario


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
            
            return redirect('/')
            
    else:
        form = RegistroForm()

    return render(request, 'registro.html', {'form': form})


