from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from servicios.views import custom_context
from pagos.models import Pago, Paypal_App
from servicios.models import Alojamiento, Servicio, Reserva, Moneda, Pais, Provincia, Favorito, Habitacion, Reserva_Habitacion
from emails.models import Email
from usuarios.models import Usuario
import json


def transaccion_exitosa(request):
    # En esta vista recibimos la información del pago para proceder según corresponda.
    # Obtenemos el paymentID del diccionario GET del objeto request, para si está la información correcta, ejecutar el pago
    if 'paymentId' in request.GET and 'PayerID' in request.GET:
        paymentId = request.GET.get('paymentId')
        PayerID = request.GET.get('PayerID')

        # Se ejecuta el pago, pero antes verificamos que el mismo esté reflejado correctamente en nuestra BD
        # Lo anterior nos asegura que disponemos de la información necesaria del producto que se ha comprado
        if Pago.objects.filter(paypal_payment_id = paymentId):
            # Relacionamos el pago de Paypal que nos llega con el pago que debemos tener pendiente registrado en nuestra BD
            pago = Pago.objects.get(paypal_payment_id = paymentId)

            # Ahora se ejecuta el pago, para que se haga efectiva la transferencia del dinero
            executed_payment = pago.ejecutar_pago(PayerID)

            if executed_payment:
                # Luego que se ha ejecutado el pago, se debe actuar de una forma u otra en función de si el usuario que ha pagado
                # se encuentra logeado en el sistema o es un usuario anónimo
                # 1 - Escenario en que el usuario está logeado (autenticado) en el sistema
                # 1.1 - Se redirecciona a la vista de reserva confirmada sin mayores acciones
                payer = executed_payment['payer']


                if request.user.is_authenticated:
                    # Se comprueba si hay que completar algún dato del Usuario que no esté en el perfil y que se pueda tomar de Paypal
                    usuario = Usuario.objects.get(user = request.user)
                    usuario.completar_datos_from_Paypal(payer = payer)
                    reservas = [pago.reserva]

                # 2 - El usuario que ha pagado es un usuario anónimo
                else:
                    reservas = []
                    # Para la creación (o selección) del usuario que ha pagado, hacemos uso del diccionario "payer" que devuelve Paypal

                    # Creamos el nuevo usuario o seleccionamos el que corresponda con la dirección de email aportada en el pago
                    n_usuario = Usuario.nuevo_usuario_tras_pago_paypal(payer = payer)

                    # Al tener ya un objeto Usuario, debemos pasar a BD todas las Reservas que hay en la session
                    for reserva_dict in request.session['en_el_carro']:
                        reservas.append(Reserva.crear_reserva_from_session(
                            usuario = n_usuario,
                            reserva_dict = reserva_dict,
                        ))

                    # Debemos pasar también a BD los registros de Favoritos
                    if 'favoritos' in request.session:
                        for favorito in request.session['favoritos']:
                            Favorito.nuevo_favorito(
                                servicio = Servicio.objects.get(id = int(favorito)),
                                usuario = n_usuario,
                            )

                    # Al terminar de procesar todas las reservas y Favoritos, se vacían dichos diccionarios de request.session
                    if 'en_el_carro' in request.session:
                        del request.session['en_el_carro']
                        request.session['en_el_carro'] = []
                    if 'favoritos' in request.session:
                        del request.session['favoritos']
                        request.session['favoritos'] = []

                    # Se realiza el login del usuario
                    login(request, n_usuario.user)

                # -- Independientemente del caso de autenticación, hechos todos los pasos anteriores, se prosigue con lo siguiente:
                # Se genera un pdf con la información de la reserva y se envía por mail al cliente
                # TODO: Sustituir por celery
                for reserva in reservas:
                    Email.enviar_correo_reserva_alojamiento(host = request.get_host(), reserva_id = reserva.id)

                    # Se genera un pdf con la información de la reserva y se envía por mail al proveedor
                    # TODO: sustituir por celery
                    Email.enviar_correo_reserva_alojamiento_proveedor(host = request.get_host(), reserva_id = reserva.id)

                # Realizados todos los cambios, se redirige a la vista de reserva confirmada
                return redirect('pagos:reserva_confirmada', pago_id = pago.id)

            else:
                return redirect('pagos:transaccion_error')
        else:
            return redirect('pagos:transaccion_error')
    else:
        return redirect('pagos:transaccion_error')


def reserva_confirmada(request, pago_id):
    # Esta vista procesa la información del pago recibido de Paypal y la muestra en el template
    pago = Pago.objects.get(id = pago_id)
    reserva = Reserva.objects.detalles_reserva(id = pago.reserva.id)
    servicio = reserva.servicio
    if servicio.alojamiento:
        # Se trata de un Alojamiento
        alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = servicio.alojamiento.id)

        context = {
            'pago': pago,
            'reserva': reserva,
            'alojamiento': alojamiento,
        }
        context.update(custom_context(request))

        # Lo próximo es ver si el Alojamiento se alquila completo o por habitaciones
        if servicio.alojamiento.por_habitacion:
            # Si el Alojamiento se alquila por habitaciones, añadimos la información de las reservas de habitaciones
            context['reservas_habitaciones'] = reserva.reserva_habitacion_set.all(),
            # Se llama a una vista preparada para mostrar la confirmación del pago para reservas de Alojamientos por habitación
            return render(request, 'pagos/pago_exitoso_reserva_alojamiento_por_habitacion.html', context)
        else:
            # Se llama a una vista preparada para mostrar la confirmación del pago para reservas de Alojamientos completos
            return render(request, 'pagos/pago_exitoso_reserva_alojamiento_completo.html', context)
    else:
        # todo: Escenario de reservas de otros servicios que no sean alojamientos
        pass



def transaccion_error(request):
    context = {

    }

    context.update(custom_context(request))
    return render(request, 'pagos/pago_erroneo.html', context)