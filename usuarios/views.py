from .forms import Login_Form, Registro_Usuario, Datos_Usuario_Form, Cambiar_Password_Form
from .models import Usuario
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
from servicios.views import custom_context
from emails.models import Email
from usuarios.forms import Verificar_Movil, Verificar_Identidad, Verificar_Actividad, Forgot_Password_Form, Recovery_Password_Form
from usuarios.models import Foto_Licencia_Actividad, Codigo_Recovery_Password
from twilio_app.models import Twilio_Client, Codigo_Verificacion, Solicitud_Verificacion
from servicios.models import Pais, Provincia
import json

# Create your views here.
def login_view(request):
    if request.user.is_authenticated():
        return redirect('website:index')

    if request.method == 'POST':
        # Caso en que el POST venga del formulario de Login de usuario
        if 'login' in request.POST: # Esto debe aparecer en el name del submit
            login_form = Login_Form(request.POST)
            register_form = Registro_Usuario()
            if login_form.is_valid():
                username = login_form.cleaned_data['username']
                password = login_form.cleaned_data['password']

                # Comprueba que existe un usuario con ese username o con ese email
                if User.objects.filter(username = username):
                    user = authenticate(username = username, password = password)
                elif User.objects.filter(email = username):
                    usuario = User.objects.get(email = username)
                    user = authenticate(username = usuario.username, password = password)
                else:
                    # Si no existe ningún usuario registrado con un username o un email igual al valor pasado por el usuario, user = None
                    user = None

                # Realiza las acciones correspondientes si se ha encontrado un usuario con las credenciales adquiridas
                if user:
                    # Comprueba que el usuario no está desactivado
                    if user.is_active:
                        # Realiza el login del usuario
                        login(request, user)
                        # Redirecciona a la página que se desee
                        return redirect('/index/')
                    else:
                        class_alert = 'alert alert-danger'
                        message = 'Este usuario se encuentra inactivo'
                        login_form = Login_Form(request.POST)
                else:
                    class_alert = 'alert alert-danger'
                    message = 'El usuario o password introducido es incorrecto'
                    login_form = Login_Form(request.POST)
            else:
                class_alert = 'alert alert-danger'
                message = 'Hay errores en el formulario'
                login_form = Login_Form(request.POST)

        # Caso en que el POST venga del formulario de Registro de nuevo usuario
        elif 'register' in request.POST: # Esto debe aparecer en el name del submit
            register_form = Registro_Usuario(request.POST)
            login_form = Login_Form()
            if register_form.is_valid():
                username = register_form.cleaned_data['username']
                email = register_form.cleaned_data['email']
                password = register_form.cleaned_data['password']
                password2 = register_form.cleaned_data['password2']

                # Comprueba que el username no exista en la BD
                if register_form.check_username(username):
                    # Comprueba que el email no exista en la BD
                    if register_form.check_email(email):
                        # Comprueba que los dos passwords introducidos coinciden
                        if register_form.check_password(password, password2):
                            # Crea el nuevo usuario
                            user_model = User.objects.create(
                                username = username,
                                email = email,
                            )

                            # Se le asigna el password
                            user_model.set_password(password)
                            user_model.save()

                            # Intentamos determinar el País a partir de la IP para añadir el dato en la creación del Usuario
                            pais, provincia = None, None
                            if 'user_data' in request.session:
                                user_data = request.session['user_data']
                                if 'country_code' in user_data:
                                    country_code = user_data['country_code']
                                    if Pais.objects.filter(codigo_iso_alfa2__exact = country_code):
                                        pais = Pais.objects.get(codigo_iso_alfa2 = country_code)
                                    else:
                                        pais = None
                                if 'region_name' in user_data:
                                    provincia_name = user_data['region_name']
                                    provincia = Provincia.get_provincia_from_name(provincia_name)

                            # Crea el objeto Usuario asociado al Usuario creado.
                            n_usuario = Usuario.nuevo_usuario(
                                user = user_model,
                                raw_password = password,
                                pais = pais,
                                provincia = provincia,
                            )

                            # Se envía el email con el link de Activación del Usuario
                            # 1 - Se crea el Email de Registro de Usuario
                            Email.enviar_correo_registro_usuario(n_usuario, request.get_host())

                            # Se define el mensaje a mostrar en la página
                            # TODO: Definir mensaje a mostrar en el Index que indique al usuario que se ha creado la cuenta y que se ha enviado un mail para su validación

                            # Realiza el login del usuario
                            # login(request, user_model)

                            # Se definen los parámetros a pasar en el template
                            context = {
                                'login_form': Login_Form(),
                                'register_form': Registro_Usuario(),
                            }

                            # Se añade el mensaje de acción exitosa
                            context['class_alert'] = 'alert alert-success'
                            context['message'] = 'Hemos enviado un email con un enlcace de confirmación a la dirección que nos ha indicado. Por favor, siga las instrucciones para poder validar su cuenta'

                            # Se renderiza el template con la información correspondiente
                            context.update(custom_context(request))
                            return render(request, 'usuarios/login.html', context)

                        else:
                            class_alert = 'alert alert-danger'
                            message = 'Las contraseñas no coinciden'
                            register_form = Registro_Usuario(request.POST)
                    else:
                        class_alert = 'alert alert-danger'
                        message = 'Ya existe un usuario registrado con este E-Mail'
                        register_form = Registro_Usuario(request.POST)
                else:
                    class_alert = 'alert alert-danger'
                    message = 'Ya existe un usuario registrado con este username(%s)' % (username)
                    register_form = Registro_Usuario(request.POST)
            else:
                class_alert = 'alert alert-danger'
                message = 'El formulario de registro contiene errores'
                register_form = Registro_Usuario(request.POST)

        else:
            print('Se ha recibido un POST que no viene ni de Login ni de Registro')
            class_alert = None
            message = None
            login_form = Login_Form()
            register_form = Registro_Usuario()
    else:
        class_alert = None
        message = None
        login_form = Login_Form()
        register_form = Registro_Usuario()

    # Se definen los parámetros a pasar en el template
    context = {
        'login_form': login_form,
        'register_form': register_form,
    }

    # Se añade un mensaje si es necesario
    if class_alert and message:
        context['class_alert'] = class_alert
        context['message'] = message

    # Se renderiza el template con la información correspondiente
    context.update(custom_context(request))
    return render(request, 'usuarios/login.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('/index/')

@login_required
@staff_member_required
def cambiar_estado_proveedor(request, usuario_id):
    usuario = Usuario.objects.get(id = usuario_id)
    usuario.cambiar_estado_proveedor()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
# Cualquier usuario puede cambiar su estado de Activo, pero debe estar logeado en el sitio
def cambiar_estado_activo(request, usuario_id):
    usuario = Usuario.objects.get(id = usuario_id)
    usuario.cambiar_estado_activo()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
@staff_member_required
# Solo un Administrador puede cambiar el estado de Admin de otro usuario del sistema
def cambiar_estado_admin(request, usuario_id):
    usuario = Usuario.objects.get(id = usuario_id)
    usuario.cambiar_estado_admin()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
@staff_member_required
# Un usuario solo puede ser eliminado por un admin, porque implica la eliminación de mucha información adyacente.
# El procedimiento permitido para un usuario común es el desactivar su usuario, no eliminarlo
def eliminar_usuario(request, usuario_id):
    usuario = Usuario.objects.get(id = usuario_id)
    usuario.eliminar_usuario()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def eliminar_foto_perfil(request, usuario_id):
    usuario = Usuario.objects.get(id = usuario_id)
    usuario.eliminar_foto()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def cerrar_cuenta_usuario(request, usuario_id):
    usuario = Usuario.objects.get(id = usuario_id)
    # Cerrar una cuenta de usuario implica setear active = False en el user asociado, y si es proveedor, cerrar todos sus servicios
    usuario.user.active = False
    usuario.user.save()

    if usuario.proveedor:
        usuario.cerrar_todos_servicios()

    # Enviar correo de notificación al usuario para confirmar que su cuenta ha sido cerrada

    return redirect('website:index')

@login_required
# Para que un usuario pueda ver su perfil, este debe estar logeado en el sitio
def perfil_usuario(request):

    # Se determina el usuario para poder obtener sus servicios asociados
    cstm_context = custom_context(request)
    usuario = cstm_context['usuario']
    fixed_message = None
    message = None
    fixed_class_alert = None
    class_alert = None
    allow_resend_verification_mail = False

    # Si el usuario no ha verificado su email, debe mostrarse de manera permanente un aviso en su perfil
    if not usuario.verificado_email:
        fixed_message = 'Hemos enviado un email de confirmación a la cuenta que nos ha facilitado cuando se registró. Por favor siga las instrucciones en el mismo para verificar su email'
        fixed_class_alert = 'alert alert-info'
        allow_resend_verification_mail = True

    if request.method == 'POST':
        # Variante si se trata del formulario de los datos personales del usuario
        if 'datos_personales' in request.POST:
            datos_usuario_form = Datos_Usuario_Form(request.POST, request.FILES)
            if datos_usuario_form.is_valid():

                # Definiendo si el usuario ha subido una foto en el formulario
                if request.FILES:
                    foto = request.FILES['foto']
                else:
                    foto = None

                m_usuario = usuario.modificar_usuario(
                    nombre = datos_usuario_form.cleaned_data['nombre'],
                    apellidos = datos_usuario_form.cleaned_data['apellidos'],
                    email = datos_usuario_form.cleaned_data['email'],
                    movil = datos_usuario_form.cleaned_data['movil'],
                    pais = datos_usuario_form.cleaned_data['pais'],
                    direccion = datos_usuario_form.cleaned_data['direccion'],
                    provincia = datos_usuario_form.cleaned_data['provincia'],
                    ciudad = datos_usuario_form.cleaned_data['ciudad'],
                    codigo_postal = datos_usuario_form.cleaned_data['codigo_postal'],
                    proveedor = datos_usuario_form.cleaned_data['proveedor'],
                    foto = foto,
                )
                context = {
                    'datos_usuario_form': Datos_Usuario_Form(request.POST, request.FILES),
                    'password_form': Cambiar_Password_Form(),
                    'message': 'Se han modificado correctamente sus datos del perfil',
                    'class_alert': 'alert alert-success',
                    'usuario': usuario,
                    'fixed_message': fixed_message,
                    'fixed_class_alert': fixed_class_alert,
                    'allow_resend_verification_mail': allow_resend_verification_mail,
                }
            else:
                context = {
                    'datos_usuario_form': Datos_Usuario_Form(request.POST, request.FILES),
                    'password_form': Cambiar_Password_Form(),
                    'message': 'Hay errores en el Formulario',
                    'class_alert': 'alert alert-danger',
                    'usuario': usuario,
                    'fixed_message': fixed_message,
                    'fixed_class_alert': fixed_class_alert,
                    'allow_resend_verification_mail': allow_resend_verification_mail,
                }
        # Variante si se trata del formulari para cambiar la contraseña del usuario
        elif 'contraseña' in request.POST:
            # Se definen los datos que se mostrarán siempre en el formulario superior
            datos_usuario = usuario.get_datos()
            password_form = Cambiar_Password_Form(request.POST)
            if password_form.is_valid():
                # Se extraen los datos introducidos por el usuario
                new_password = password_form.cleaned_data['new_password']
                new_password_2 = password_form.cleaned_data['new_password_2']
                old_password = password_form.cleaned_data['old_password']

                # La primera comprobación es que el password actual introducido sea el correcto
                if usuario.user.check_password(old_password):
                    # Si se supera esta prueba lo próximo es comprobar que los dos passwords nuevos coincidan
                    if new_password == new_password_2:
                        # Si son iguales entonces se procede a realizar el cambio de contraseña
                        usuario.user.set_password(new_password)
                        usuario.user.save()

                        # Autenticando al usuario de nuevo tras el cambio de password, para que no tenga que volver a iniciar su sesion
                        user = authenticate(username = datos_usuario['usuario'], password = new_password)
                        login(request, user)

                        context = {
                            'datos_usuario_form': Datos_Usuario_Form(datos_usuario),
                            'password_form': Cambiar_Password_Form(),
                            'message': 'Se ha cambiado correctamente su contraseña',
                            'class_alert': 'alert alert-success',
                            'usuario': usuario,
                            'fixed_message': fixed_message,
                            'fixed_class_alert': fixed_class_alert,
                            'allow_resend_verification_mail': allow_resend_verification_mail,
                        }
                    else:
                        context = {
                            'datos_usuario_form': Datos_Usuario_Form(datos_usuario),
                            'password_form': Cambiar_Password_Form(),
                            'message': 'Las dos nuevas contraseñas introducidas no coinciden',
                            'class_alert': 'alert alert-danger',
                            'usuario': usuario,
                            'fixed_message': fixed_message,
                            'fixed_class_alert': fixed_class_alert,
                            'allow_resend_verification_mail': allow_resend_verification_mail,
                        }
                else:
                    context = {
                        'datos_usuario_form': Datos_Usuario_Form(datos_usuario),
                        'password_form': Cambiar_Password_Form(),
                        'message': 'Su contraseña Actual y la introducida no coinciden',
                        'class_alert': 'alert alert-danger',
                        'usuario': usuario,
                        'fixed_message': fixed_message,
                        'fixed_class_alert': fixed_class_alert,
                        'allow_resend_verification_mail': allow_resend_verification_mail,
                    }
            else:
                context = {
                    'datos_usuario_form': Datos_Usuario_Form(datos_usuario),
                    'password_form': Cambiar_Password_Form(),
                    'message': 'Hay valores incorrectos en el formulario',
                    'class_alert': 'alert alert-danger',
                    'usuario': usuario,
                    'fixed_message': fixed_message,
                    'fixed_class_alert': fixed_class_alert,
                    'allow_resend_verification_mail': allow_resend_verification_mail,
                }
        else:
            context = {
                'datos_usuario_form': Datos_Usuario_Form(usuario.get_datos()),
                'password_form': Cambiar_Password_Form(),
                'message': 'Ha habido un error al leer el origen de la petición POST por generada',
                'class_alert': 'alert alert-danger',
                'usuario': usuario,
                'fixed_message': fixed_message,
                'fixed_class_alert': fixed_class_alert,
                'allow_resend_verification_mail': allow_resend_verification_mail,
            }
    else:
        # Se obtiene un diccionario con los datos del usuario para rellenar el Formulario
        datos_usuario_form = Datos_Usuario_Form(usuario.get_datos())
        context = {
            'datos_usuario_form': datos_usuario_form,
            'password_form': Cambiar_Password_Form(),
            'message': message,
            'class_alert': class_alert,
            'usuario': usuario,
            'fixed_message': fixed_message,
            'fixed_class_alert': fixed_class_alert,
            'allow_resend_verification_mail': allow_resend_verification_mail,
        }

    context.update(custom_context(request))
    return render(request, 'usuarios/perfil_usuario.html', context)

@login_required()
def centro_verificacion_datos(request):
    # Definición del usuario y de los formularios para los posibles escenarios de Validación previstos
    usuario = Usuario.objects.detalles_usuario(usuario = Usuario.objects.get(user = request.user))
    form_movil = Verificar_Movil()
    form_identidad = Verificar_Identidad()
    form_actividad = Verificar_Actividad()

    # Conectores a redes sociales
    twitter_conector = usuario.get_conector_twitter()

    if request.method =='POST':
        # Escenario de Verificación del número móvil del usuario
        if 'verificar_movil' in request.POST:
            form_movil = Verificar_Movil(request.POST)
            if form_movil.is_valid():
                codigo_verificacion = form_movil.cleaned_data['codigo_verificacion']
                if Codigo_Verificacion.validate_codigo_usuario(codigo_verificacion, usuario):
                    usuario.verificar_movil()
                    message = 'Se ha verificado correctamente el móvil %s %s' %(usuario.pais.prefijo_movil, usuario.movil)
                    class_alert = 'alert alert-success'
                else:
                    message = 'El código es incorrecto, vuelve a intentarlo nuevamente'
                    class_alert = 'alert alert-danger'
            else:
                message = 'Hay errores en el formulario'
                class_alert = 'alert alert-danger'

        # Escenario de Verificación de Documentos de Permiso de Actividad del Proveedor
        elif 'verificar_actividad' in request.POST:
            form_actividad = Verificar_Actividad(request.POST)
            if form_actividad.is_valid():
                # Definiendo si el usuario ha subido una foto en el formulario
                if request.FILES:
                    foto = request.FILES['foto']
                    n_foto_licencia_actividad = Foto_Licencia_Actividad.nueva_foto_licencia_actividad(
                        foto = foto,
                        usuario = usuario,
                    )
                    message = 'Se ha enviado correctamente el documento para su revisión. Por favor, deje pasar hasta 48 horas para su validación'
                    class_alert = 'alert alert-success'
                else:
                    message = 'Debe seleccionar un Documento primero para poder enviarlo'
                    class_alert = 'alert alert-danger'
            else:
                message = 'Hay errores en el Formulario'
                class_alert = 'alert alert-danger'
        else:
            message = None
            class_alert = None
    else:
        message = None
        class_alert = None

    context = {
        'usuario': usuario,
        'form_movil': form_movil,
        'form_identidad': form_identidad,
        'form_actividad': form_actividad,
        'message': message,
        'class_alert': class_alert,
        'confirmaciones_agotadas': usuario.confirmaciones_agotadas, # Determina si el usuario puede seguir solicitando confirmar su móvil
    }

    context.update(custom_context(request))
    return render(request, 'usuarios/centro_verificacion_datos.html', context)

@login_required()
def verificar_movil(request, usuario_id):
    usuario = Usuario.objects.detalles_usuario(usuario = Usuario.objects.get(id = usuario_id))

    # Lo primero es validar que el usuario pueda continuar haciendo solicitudes de verificación de móvil
    n_solicitud_verificacion = Solicitud_Verificacion.nueva_solicitud_verificacion(
        usuario = usuario,
        movil = usuario.movil,
    )
    if isinstance(n_solicitud_verificacion, dict):
        message = n_solicitud_verificacion['message']
        class_alert = 'alert alert-danger'
        context = {
            'usuario': usuario,
            'message': message,
            'class_alert': class_alert,
        }
        context.update(custom_context(request))
        return render(request, 'usuarios/centro_verificacion_datos.html', context)

    # Llegados a este punto, se genera un nuevo Código de verificación para el usuario
    codigo_verificacion = Codigo_Verificacion.generar_codigo_verificacion_twilio()
    usefull = False
    n_codigo_verificacion = None
    while not usefull:
        n_codigo_verificacion = Codigo_Verificacion.nuevo_codigo_verificacion(
            usuario = usuario,
            codigo = codigo_verificacion,
        )
        if not isinstance(n_codigo_verificacion, dict):
            usefull = True

    # Una vez obtenido el código de verificación y relacionado con el usuario, se envía el SMS
    twilio_client = Twilio_Client.objects.get(en_uso = True)

    twilio_client.send_sms(
        to = usuario.complete_movil,
        message = 'El código para verificar tu móvil en Ontraveline es: %s' %(n_codigo_verificacion.codigo)
    )

    context = {
        'usuario': usuario,
        'message': 'Hemos enviado un SMS con código de confirmación al %s, por favor, introdúzcalo a continuación para que podamos verificar su móvil' %(usuario.complete_movil),
        'class_alert': 'alert alert-success',
    }

    context.update(custom_context(request))
    return redirect('usuarios:centro_verificacion_datos')

    # return render(request, 'usuarios/centro_verificacion_datos.html', context)

def documentos_verificacion_actividad(request, usuario_id):
    usuario = Usuario.objects.get(id=usuario_id)
    documentos_actividad = usuario.foto_licencia_actividad_set.all()
    context = {
        'usuario': usuario,
        'documentos_actividad': documentos_actividad,
    }
    context.update(custom_context(request))
    return render(request, 'usuarios/documentos_verificacion_actividad.html', context)

def eliminar_foto_documento_actividad(request, foto_documento_actividad_id):
    foto_documento_actividad = Foto_Licencia_Actividad.objects.get(id = foto_documento_actividad_id)
    foto_documento_actividad.eliminar_foto_documento_actividad()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# Devuelve una lista de empresas con sus ids relacionados para poder cargar selects
def get_provincias_pais(request, pais_id):
    pais = Pais.objects.get(id = pais_id)
    provincias_pais = []
    for provincia in pais.provincia_set.order_by('nombre'):
        provincias_pais.append([provincia.id, provincia.nombre])

    resultado = {
        'provincias': provincias_pais,
    }

    return HttpResponse(json.dumps(resultado), content_type = 'application/json')

def forgot_password(request):
    if request.method == 'POST':
        form = Forgot_Password_Form(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            recovery_password = Usuario.recovery_password(email, host = request.get_host())
            if isinstance(recovery_password, dict):
                message = recovery_password['message']
                class_alert = 'alert alert-danger'
            else:
                form = Forgot_Password_Form()
                message = 'Hemos enviado un E-Mail a la dirección indicada con las instrucciones que debes seguir para recuperar tu contraseña'
                class_alert = 'alert alert-info'
        else:
            message = 'Hay errores en el Formulario'
            class_alert = 'alert alert-danger'

    else:
        form = Forgot_Password_Form()
        message = None
        class_alert = None

    context = {
        'form': form,
        'message': message,
        'class_alert': class_alert,
    }
    context.update(custom_context(request))
    return render(request, 'usuarios/forgot_password.html', context)

def recovery_password(request, code):
    codigo_recovery_password = Codigo_Recovery_Password.objects.filter(codigo = code)
    if codigo_recovery_password:
        codigo_recovery_password = Codigo_Recovery_Password.objects.get(codigo = code)
        if request.method == 'POST':
            form = Recovery_Password_Form(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                new_password_2 = form.cleaned_data['new_password_2']
                if new_password == new_password_2:
                    # Si las dos contraseñas indicadas por el usuario coinciden se realiza el cambio de contraseña
                    codigo_recovery_password.usuario.change_password(new_password)

                    # Se actualiza el Código para que no pueda volver a ser reutilizado
                    codigo_recovery_password.valido = False
                    codigo_recovery_password.save()

                    message = 'Se ha modificado correctamente su Contraseña'
                    class_alert = 'alert alert-success'
                    form = Recovery_Password_Form()

                else:
                    message = 'Las contraseñas deben coincidir. Por favor inténtelo de nuevo'
                    class_alert = 'alert alert-danger'
                    form = Recovery_Password_Form()

            else:
                message = 'Hay errores en el formulario'
                class_alert = 'alert alert-danger'
                form = Recovery_Password_Form(request.POST)

            context = {
                'form': form,
                'message': message,
                'class_alert': class_alert,
            }

        else:
            form = Recovery_Password_Form()
            context = {
                'form': form,
                'message': None,
                'class_alert': None,
            }

        context.update(custom_context(request))
        return render(request, 'usuarios/recovery_password.html', context)

    else:
        message = 'Ups! parece que el link que has seguido ya no es válido. Por favor, vuelve a solicitar un enlace para recuperar tu contraseña en la página de Ingreso'
        context = {
            'message': message,
            'class_alert': 'alert alert-danger',
        }

        context.update(custom_context(request))
        return render(request, 'usuarios/error_recovery_password.html', context)