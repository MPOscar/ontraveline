from django.contrib.auth.models import User
from django import forms
from servicios.models import Provincia, Pais

class Registro_Usuario(forms.Form):
    username = forms.CharField(label = 'Nombre de Usuario', max_length = 64, required = True)
    email = forms.EmailField(label = 'E-Mail', max_length = 64, required = True)
    password = forms.CharField(label = 'Password', min_length = 5, widget = forms.PasswordInput())
    password2 = forms.CharField(label = 'Repetir Password', min_length = 5, widget = forms.PasswordInput())

    def check_username(self, username):
        """Comprueba que no exista un nombre de usuario igual en la db"""
        if User.objects.filter(username = username):
            print('Ya existe un usuario registrado con nombre de usuario %s' %(username))
            return None
        else:
            return username

    def check_email(self, email):
        """Comprueba que no exista un email igual en la db"""
        if User.objects.filter(email = email):
            print('Ya existe un usuario registrado con email: %s' %(email))
            return None
        else:
            return email

    def check_password(self, password, password2):
        """Comprueba que password y password2 sean iguales."""
        if password != password2:
            print('Las contraseñas no coinciden.')
            return None
        else:
            return password

class Login_Form(forms.Form):
    username = forms.CharField(label = 'Usuario/E-Mail', max_length = 64, required = True)
    password = forms.CharField(label = 'Password', widget = forms.PasswordInput(), required = True)

class Forgot_Password_Form(forms.Form):
    email = forms.EmailField(label = 'E-Mail', required = True, max_length = 64)

class Cambiar_Password_Form(forms.Form):
    new_password = forms.CharField(label = 'Nueva Contraseña', widget = forms.PasswordInput(), required = True)
    new_password_2 = forms.CharField(label = 'Repita la Nueva Contraseña', widget = forms.PasswordInput(), required = True)
    old_password = forms.CharField(label = 'Contraseña Actual', widget = forms.PasswordInput(), required = True)

class Recovery_Password_Form(forms.Form):
    new_password = forms.CharField(label = 'New Password', widget = forms.PasswordInput(), required = True)
    new_password_2 = forms.CharField(label = 'Repeat New Password', widget = forms.PasswordInput(), required = True)

class Datos_Usuario_Form(forms.Form):
    nombre = forms.CharField(label = 'Nombre', max_length = 64, required = False)
    apellidos = forms.CharField(label = 'Apellidos', max_length = 64, required = False)
    email = forms.EmailField(label = 'E-Mail', required = False)
    movil = forms.CharField(label = 'Móvil', required = False, max_length = 16)
    direccion = forms.CharField(label = 'Dirección', max_length = 64, required = False)
    pais = forms.ModelChoiceField(label = 'País', queryset = Pais.objects.order_by('nombre'), empty_label = 'País', required = False)
    provincia = forms.ModelChoiceField(label = 'Provincia', queryset = Provincia.objects.order_by('nombre'), empty_label = 'Provincia', required = False)
    ciudad = forms.CharField(label = 'Ciudad', max_length = 32, required = False)
    codigo_postal = forms.CharField(label = 'Código Postal', max_length = 12, required = False)
    proveedor = forms.BooleanField(label = 'Proveedor', required = False)
    foto = forms.ImageField(label = 'Foto', required = False)

class Verificar_Movil(forms.Form):
    codigo_verificacion = forms.CharField(label = 'Código Verificación', max_length = 6, required = False)

class Verificar_Identidad(forms.Form):
    foto = forms.ImageField(label = 'Foto de Documento de Identidad', required = False)

class Verificar_Actividad(forms.Form):
    foto = forms.ImageField(label = 'Foto de Licencia de Actividad', required = False)