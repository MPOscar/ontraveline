from django.shortcuts import render, redirect, HttpResponseRedirect
from emails.models import Link_Activacion, Email
from usuarios.models import Usuario
from servicios.models import Servicio, Reserva, Alojamiento
from servicios.views import custom_context

def plantilla_register(request):
    context = {
        'username': 'Test Username',
        'link_activacion': 'http://192.168.1.50:8002/usuarios/some_activation_code_goes_here'
    }

    return render(request, 'emails/plantillas/register.html', context)

def confirmar_email_usuario(request, codigo_activacion):
    # 1 - A partir del código de activación definir de qué usuario y que link se trata
    if not Link_Activacion.objects.filter(link__contains = codigo_activacion):
        message = 'El link que se ha seguido es inválido'
        context = {
            'message': message,
            'usuario': None,
        }
        return render(request, 'emails/error_activacion.html', context)

    else:
        link_activacion = Link_Activacion.objects.get(link__contains = codigo_activacion)
        usuario = link_activacion.usuario

        # Para poder verificar el mail, el link debe estar no activado y válido
        if link_activacion.activado or not link_activacion.valido:
            message = 'El link que se ha seguido es inválido'
            context = {
                'message': message,
                'usuario': None,
            }
            return render(request, 'emails/error_activacion.html', context)

        else:
            # 2 - Se registra como True el valor: "verificado_email" del Usuario
            usuario.verificar_email()

            # 3 - El link se marca como "activado" y "no válido"
            link_activacion.activar()

            # Todo: Enviar al index pero con un mensaje de confirmación de éxito en la verificación del mail

            # El usuario es redirigido al index
            return redirect('website:index' )

def error_activacion(request):
    context = {

    }
    return render(request, 'emails/error_activacion.html', context)

def reenviar_email_confirmacion(request, usuario_id):
    # Se determina el usuario al que hay que volver a enviar el email de confirmación
    usuario = Usuario.objects.get(id = usuario_id)

    # Se llama al proceso que envía el mail
    Email.enviar_correo_registro_usuario(usuario = usuario)

    # Se recarga la página donde se encuentra el usuario
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def pdf_reserva_alojamiento_completo(request, reserva_id):
    reserva = Reserva.objects.detalles_reserva(id = reserva_id)
    alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = reserva.servicio.alojamiento.id)

    context = {
        'alojamiento': alojamiento,
        'reserva': reserva,
    }

    context.update(custom_context(request))
    return render(request, 'emails/plantillas/reserva_alojamiento_completo.html', context)

def pdf_reserva_alojamiento_completo_proveedor(request, reserva_id):
    reserva = Reserva.objects.detalles_reserva(id = reserva_id)
    alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = reserva.servicio.alojamiento.id)

    context = {
        'alojamiento': alojamiento,
        'reserva': reserva,
    }

    context.update(custom_context(request))
    return render(request, 'emails/plantillas/reserva_alojamiento_completo_proveedor.html', context)

def pdf_reserva_alojamiento_por_habitacion(request, reserva_id):
    reserva = Reserva.objects.detalles_reserva(id = reserva_id)
    alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = reserva.servicio.alojamiento.id)

    context = {
        'alojamiento': alojamiento,
        'reserva': reserva,
        'reservas_habitaciones': reserva.reserva_habitacion_set.all(),
    }

    context.update(custom_context(request))
    return render(request, 'emails/plantillas/reserva_alojamiento_por_habitacion.html', context)

def pdf_reserva_alojamiento_por_habitacion_proveedor(request, reserva_id):
    reserva = Reserva.objects.detalles_reserva(id = reserva_id)
    alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = reserva.servicio.alojamiento.id)


    print(reserva.reserva_habitacion_set.all())

    context = {
        'alojamiento': alojamiento,
        'reserva': reserva,
        'reservas_habitaciones': reserva.reserva_habitacion_set.all(),
    }

    context.update(custom_context(request))
    return render(request, 'emails/plantillas/reserva_alojamiento_por_habitacion_proveedor.html', context)

def pdf_cancelacion_reserva_alojamiento(request, reserva_id):
    reserva = Reserva.objects.detalles_reserva(id = reserva_id)
    alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = reserva.servicio.alojamiento.id)

    context = {
        'alojamiento': alojamiento,
        'reserva': reserva,
    }

    context.update(custom_context(request))
    return render(request, 'emails/plantillas/cancelacion_reserva_alojamiento.html', context)