from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from usuarios.models import Usuario
from servicios.models import Alojamiento, Servicio, Destino
from servicios.views import custom_context
from administracion.forms import Add_Twilio_Client, Add_Twilio_Number
from twilio_app.models import Twilio_Client, Twilio_Number
import json

@staff_member_required
def dashboard(request):
    context = {

    }
    return render(request, 'administracion/dashboard.html', context)

@staff_member_required
def eliminar_alojamiento(request, alojamiento_id):
    alojamiento = Alojamiento.objects.get(id = alojamiento_id)
    if not alojamiento.por_habitacion:
        alojamiento.alojamiento_completo.eliminar_alojamiento_completo()
    else:
        # Eliminar un Alojamiento por Habitaciones implica, eliminar las habitaciones con todas las fotos y directorios
        # y posteriormente eliminar el Alojamiento en sí.
        habitaciones = alojamiento.habitacion_set.all()
        for habitacion in habitaciones:
            habitacion.eliminar_habitacion()
        alojamiento.servicio.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def administrar_usuarios(request):
    usuarios = Usuario.objects.detalles_usuarios()
    context = {
        'usuarios': usuarios,
    }
    return render(request, 'administracion/administrar_usuarios.html', context)

def administrar_alojamientos(request):
    alojamientos = Alojamiento.objects.detalles_alojamientos()
    context = {
        'alojamientos': alojamientos,
    }
    return render(request, 'administracion/administrar_alojamientos.html', context)

def administrar_destinos(request):
    destinos = Destino.objects.order_by('nombre')
    context = {
        'destinos': destinos,
    }
    return render(request, 'administracion/administrar_destinos.html', context)

def add_usuario(request):
    context = {

    }
    return render(request, 'administracion/add_usuario.html', context)


def add_alojamiento(request):
    context = {

    }
    return render(request, 'administracion/add_alojamiento.html', context)


def add_destino(request):
    context = {

    }
    return render(request, 'administracion/add_destino.html', context)

def datos_prueba(request):
    # Todos los usuarios registrados en el sistema (Se obtiene más información con el Object Manager)
    usuarios = Usuario.objects.detalles_usuarios()

    # Objeto Usuario del Administrador que está accediendo a la vista. Se utilizará para comparar con los demás usuarios en el template
    # y así poder diferenciar algunos comportamientos y opciones disponibles
    myself = Usuario.objects.get(user__id=request.user.id)

    context = {
        'usuarios': usuarios,
        'myself': myself,
    }

    context.update(custom_context(request))
    return render(request, 'administracion/datos_prueba.html', context)

def modificar_usuario(request, usuario_id):

    usuario = Usuario.objects.get(id = usuario_id)

    context = {
        'usuario': usuario,
    }
    return render(request, 'administracion/modificar_usuario.html', context)

def modificar_twilio_client(request, twilio_client_id):
    twilio_client = Twilio_Client.objects.get(id = twilio_client_id)
    context = {
        'twilio_client': twilio_client,
    }
    return render(request, 'administracion/modificar_twilio_client.html', context)

def modificar_twilio_number(request, twilio_number_id):
    twilio_number = Twilio_Number.objects.get(id = twilio_number_id)
    context = {
        'twilio_number': twilio_number,
    }
    return render(request, 'administracion/modificar_twilio_number.html', context)

def eliminar_twilio_client(request, twilio_client_id):
    twilio_client = Twilio_Client.objects.get(id = twilio_client_id)
    twilio_client.eliminar_twilio_client()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def eliminar_twilio_number(request, twilio_number_id):
    twilio_number = Twilio_Number.objects.get(id = twilio_number_id)
    twilio_number.eliminar_twilio_number()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def activar_usuario(request, usuario_id):
    usuario = Usuario.objects.get(id = usuario_id)
    usuario.cambiar_activacion_usuario()

    resultado = {}
    resultado['activado'] = usuario.user.is_active

    return HttpResponse(json.dumps(resultado), content_type = 'application/json')

def verificar_email(request, usuario_id):
    usuario = Usuario.objects.get(id = usuario_id)
    usuario.cambiar_verificacion_email()

    resultado = {}
    resultado['verificado_email'] = usuario.verificado_email

    return HttpResponse(json.dumps(resultado), content_type = 'application/json')

def verificar_movil(request, usuario_id):
    usuario = Usuario.objects.get(id = usuario_id)
    usuario.cambiar_verificacion_movil()

    resultado = {}
    resultado['verificado_movil'] = usuario.verificado_movil

    return HttpResponse(json.dumps(resultado), content_type = 'application/json')

def usar_twilio_number(request, twilio_number_id):
    twilio_number = Twilio_Number.objects.get(id = twilio_number_id)
    twilio_number.usar_twilio_number()

    resultado = {}
    resultado['en_uso'] = twilio_number.en_uso

    return HttpResponse(json.dumps(resultado), content_type = 'application/json')

def cambiar_uso_twilio_number(request, twilio_number_id):
    twilio_number = Twilio_Number.objects.get(id = twilio_number_id)
    twilio_number.cambiar_uso_twilio_number()

    resultado = {}
    resultado['en_uso'] = twilio_number.en_uso

    return HttpResponse(json.dumps(resultado), content_type = 'application/json')



def proveedor(request, usuario_id):
    usuario = Usuario.objects.get(id = usuario_id)
    usuario.cambiar_estado_proveedor()

    resultado = {}
    resultado['proveedor'] = usuario.proveedor

    return HttpResponse(json.dumps(resultado), content_type='application/json')

def verificado_proveedor(request, usuario_id):
    usuario = Usuario.objects.get(id = usuario_id)
    usuario.cambiar_estado_verificado_proveedor()

    resultado = {}
    resultado['varificado_proveedor'] = usuario.verificado_proveedor
    resultado['proveedor'] = usuario.proveedor

    return HttpResponse(json.dumps(resultado), content_type = 'application/json')

def add_twilio_client(request):
    if request.method == 'POST':
        form = Add_Twilio_Client(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            account = form.cleaned_data['account']
            token = form.cleaned_data['token']

            n_twilio_client = Twilio_Client.nuevo_twilio_client(
                email = email,
                account = account,
                token = token,
            )

            if isinstance(n_twilio_client, dict):
                message = n_twilio_client['message']
                class_alert = 'alert alert-danger'
            else:
                message = 'Se ha creado correctamente el Twilio Client para %s' %(email)
                class_alert = 'alert alert-success'
        else:
            message = 'Hay errores en el formulario'
            class_alert = 'alert alert-danger'
    else:
        form = Add_Twilio_Client(request.POST)
        message = None
        class_alert = None

    context = {
        'form': form,
        'message': message,
        'class_alert': class_alert,
    }

    return render(request, 'administracion/add_twilio_client.html', context)

def add_twilio_number(request):
    if request.method == 'POST':
        form = Add_Twilio_Number(request.POST)
        if form.is_valid():
            numero = form.cleaned_data['numero']
            sid = form.cleaned_data['sid']

            n_twilio_number = Twilio_Number.nuevo_twilio_number(
                numero = numero,
                sid = sid,
            )

            if isinstance(n_twilio_number, dict):
                message = n_twilio_number['message']
                class_alert = 'alert alert-danger'
            else:
                message = 'Se ha creado correctamente el Twilio Number %s' %(numero)
                class_alert = 'alert alert-success'
        else:
            message = 'Hay errores en el formulario'
            class_alert = 'alert alert-danger'
    else:
        form = Add_Twilio_Number(request.POST)
        message = None
        class_alert = None

    context = {
        'form': form,
        'message': message,
        'class_alert': class_alert,
    }

    return render(request, 'administracion/add_twilio_number.html', context)

def administrar_twilio_clients(request):
    twilio_clients = Twilio_Client.objects.order_by('email')
    context = {
        'twilio_clients': twilio_clients,
    }
    return render(request, 'administracion/administrar_twilio_clients.html', context)

def administrar_twilio_numbers(request):
    twilio_numbers = Twilio_Number.objects.order_by('numero')
    context = {
        'twilio_numbers': twilio_numbers,
    }
    return render(request, 'administracion/administrar_twilio_numbers.html', context)
