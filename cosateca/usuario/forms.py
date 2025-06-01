from django import forms
from datetime import date
from .models import Usuario

class RegistroForm(forms.Form):
    nombre = forms.CharField(required=True,max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Nombre', 'class':'form-control input_formulario'}), label='')
    apellido = forms.CharField(required=True,max_length=100, label='', widget=forms.TextInput(attrs={'placeholder': 'Apellido', 'class':'form-control input_formulario'}))
    fecha_nacimiento = forms.DateField(required=True,label= 'Fecha de nacimiento', widget=forms.DateInput(attrs={'type':'date', 'placeholder': 'Fecha de nacimiento', 'class':'form-control input_formulario'}))
    sexo = forms.ChoiceField(required=True,choices=[('', 'Sexo'),('M', 'Masculino'), ('F', 'Femenino'), ('NB','No binario'), ('O', 'Otro'), ('P', 'Prefiero no responder')], label='', widget=forms.Select(attrs={'class':'form-control input_formulario' ,'id': 'select_sexo',}))
    correo_electronico = forms.EmailField(required=True,label='', widget=forms.TextInput(attrs={'placeholder': 'Correo electrónico', 'class':'form-control input_formulario'}))
    telefono = forms.CharField(required=True,label='',  widget=forms.TextInput(attrs={'placeholder': 'Teléfono', 'class':'form-control input_formulario'}))
    dni = forms.CharField(required=True,label='', widget=forms.TextInput(attrs={'placeholder': 'DNI', 'class':'form-control input_formulario'}))
    nombre_usuario = forms.CharField(required=True,label='', widget=forms.TextInput(attrs={'placeholder': 'Nombre de usuario', 'class':'form-control input_formulario'}))
    contraseña = forms.CharField(required=True,label='', widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña', 'class':'form-control input_formulario'}))
    confirmar_contraseña = forms.CharField(required=True,label='', widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar contraseña', 'class':'form-control input_formulario'}))
    
    

    def clean(self):
        cleaned_data = super().clean()
        contraseña = cleaned_data.get("contraseña")
        confirmar_contraseña = cleaned_data.get("confirmar_contraseña")

        if contraseña and confirmar_contraseña and contraseña != confirmar_contraseña:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data
        
    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        fecha_actual = date.today().year
        if fecha_nacimiento.year > fecha_actual - 18:
            raise forms.ValidationError("Debes tener al menos 18 años para registrarte.")
        
        if fecha_nacimiento > date.today():
            raise forms.ValidationError("La fecha de nacimiento no puede ser futura.")
        return fecha_nacimiento
    
    def clean_dni(self):
        dni = self.cleaned_data['dni']
        if Usuario.objects.filter(dni=dni).exists():
            raise forms.ValidationError("Este DNI ya está registrado.")
        if len(dni) != 9 or not dni[:-1].isdigit() or not dni[-1].isalpha():
            raise forms.ValidationError("El formato del DNI es incorrecto")
        return dni
        
    def clean_correo_electronico(self):
        correo = self.cleaned_data['correo_electronico']
        if Usuario.objects.filter(email=correo).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return correo
    
    def clean_nombre_usuario(self):
        nombre_usuario = self.cleaned_data['nombre_usuario']
        if Usuario.objects.filter(username=nombre_usuario).exists():
            raise forms.ValidationError("Este nombre de usuario ya se encuentra registrado.")
        return nombre_usuario
    
    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        if Usuario.objects.filter(telefono=telefono).exists():
            raise forms.ValidationError("Este número de teléfono ya está registrado.")
        
        if len(telefono) < 9 or not telefono.isdigit():
            raise forms.ValidationError("El número de teléfono debe tener al menos 9 dígitos y solo contener números.")
        return telefono