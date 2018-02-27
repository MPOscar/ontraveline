from django.shortcuts import render, HttpResponseRedirect, HttpResponse, redirect
from servicios.models import Habitacion, Moneda, Alojamiento, Tipo_Cambio, Destino, Provincia, Municipio
from website.forms import Contacto_Form, Buscar_Alojamientos_Por_Habitacion, Buscar_Alojamientos_Completos
from website.models import Mensaje_Contacto, Testimonio, Aeropuerto
from servicios.views import custom_context
from forex_python.converter import CurrencyRates
from django.contrib.admin.views.decorators import staff_member_required
from usuarios.models import Usuario
import random, json
from support.globals import GMaps_APIKey

def index(request):

    if request.method == 'POST':
        if 'flight' in request.POST:
            pass
            # Esta variante estáprogramada en la vista "website/search" a donde se llega con la información del formulario a través del "action" del mismo

        elif 'habitaciones' in request.POST:
            destino = request.POST['destino_habitacion']
            lugar = None
            if 'Destino' in destino:
                lugar = destino.split(' (Destino)')[0]

            elif 'Provincia' in destino:
                lugar = destino.split(' (Provincia)')[0]

            elif 'Municipio' in destino:
                lugar = destino.split(' (Municipio)')[0]
            else:
                print('Escenario no previsto hasta ahora')

            # Ahora obtengo las fechas del Formulario y la cantidad de huéspedes
            fecha_desde = request.POST['start']
            fecha_hasta = request.POST['end']
            huespedes = request.POST['huespedes']

            # Se almacenan los criterios de búsqueda en la session para recuperarlos luego desde la otra vista
            request.session['criterio_alojamientos_por_habitacion'] = {
                'lugar': lugar,
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
                'huespedes': huespedes,
            }

            # En este punto tengo el lugar en el que deben estar los Alojamientos que muestre al Usuario, las fechas y la cantidad de huéspedes
            return redirect('website:buscar_alojamientos_por_habitacion')

        elif 'alojamientos' in request.POST:
            destino = request.POST['destino_alojamiento']
            lugar = None
            if 'Destino' in destino:
                lugar = destino.split(' (Destino)')[0]

            elif 'Provincia' in destino:
                lugar = destino.split(' (Provincia)')[0]

            elif 'Municipio' in destino:
                lugar = destino.split(' (Municipio)')[0]
            else:
                print('Escenario no previsto hasta ahora')

            # Ahora obtengo las fechas del Formulario y la cantidad de huéspedes
            fecha_desde = request.POST['start']
            fecha_hasta = request.POST['end']
            huespedes = request.POST['huespedes']

            # Se almacenan los criterios de búsqueda en la session para recuperarlos luego desde la otra vista
            request.session['criterio_alojamientos_completos'] = {
                'lugar': lugar,
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
                'huespedes': huespedes,
            }

            # En este punto tengo el lugar en el que deben estar los Alojamientos que muestre al Usuario, las fechas y la cantidad de huéspedes
            return redirect('website:buscar_alojamientos_completos')

        else:
            return redirect('website:index')

    else:

        # Se definen las listas vacías para almacenar los elementos que serán mostrados en el index
        alojamientos_por_habitacion = []
        alojamientos_completos = []

        # Servicios destacados
        alojamientos_destacados = []

        # Se definen los Alojamientos que pueden ser mostrados
        alojamientos = Alojamiento.objects.detalles_alojamientos(
            # Se definen los criterios de filtrado para los Alojamientos que deseamos listar
            usuarios = Usuario.get_proveedores_validados(), # Solo Alojamientos de usuarios activos y verificados como proveedores
            activos = True, # Solo Alojamientos asociados a Servicios Activos
        )[:12] # Solo se muestra una cantidad limitada de Alojamientos establecida en la Configuración

        # Se agrupan los Alojamientos según su tipo de alquiler
        for alojamiento in alojamientos:
            if alojamiento.por_habitacion:
                if alojamiento.cantidad_habitaciones > 0 and alojamiento.fotos:
                    alojamientos_por_habitacion.append(alojamiento)
            elif alojamiento.fotos:
                    alojamientos_completos.append(alojamiento)

            # Destacados
            if alojamiento.servicio.destacado:
                alojamientos_destacados.append(alojamiento)

        # De momento se selecciona un Alojamiento destacado al azar
        if alojamientos_destacados:
            alojamiento_destacado = alojamientos_destacados[random.randint(0, len(alojamientos_destacados) - 1)]
        else:
            alojamiento_destacado = None

        # Se hace un bucle luego de la consulta para realizar una sola consulta a la BD
        # En este punto tenemos listas con los tipos de elementos que deben ser mostrados en el index

        # Se pasa el listado de Aeropuertos de Cuba, para el selector del buscador de Inicio
        aeropuertos_cuba = Aeropuerto.objects.filter(cuba = True).order_by('codigo_iata')

        context = {
            'alojamientos_por_habitacion': alojamientos_por_habitacion,
            'alojamientos_completos': alojamientos_completos,
            'alojamiento_destacado': alojamiento_destacado, # Si hay más de uno, varía cuál se muestra entre una vista y otra
            'aeropuertos_cuba': aeropuertos_cuba,
            'GMaps_APIKey': GMaps_APIKey,
        }

        context.update(custom_context(request))
        return render(request, 'website/index.html', context)

def contacto(request):
    if request.method == 'POST':
        form = Contacto_Form(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            n_mensaje = Mensaje_Contacto.nuevo_mensaje_contacto(
                nombre = nombre,
                email = email,
                message = message,
            )

            if n_mensaje:
                context = {
                    'form': Contacto_Form(),
                    'message': 'Gracias por ponerse en contacto con nosotros. En breve le responderemos a la dirección de correo que nos ha indicado',
                    'class_alert': 'alert alert-success',
                }
            else:
                context = {
                    'form': Contacto_Form(request.POST),
                    'message': 'No ha sido posible procesar su solicitud en este momento, inténtelo más tarde por favor.',
                    'class_alert': 'alert alert-danger',
                }
        else:
            context = {
                'form': Contacto_Form(request.POST),
                'message': 'Hay errores en el formulario, por favor revise los datos introducidos',
                'class_alert': 'alert alert-danger',
            }
    else:
        context = {
            'form': Contacto_Form(),
        }

    context['GMaps_APIKey'] = GMaps_APIKey
    context.update(custom_context(request))
    return render(request, 'website/contacto.html', context)

def servicios(request):
    context = {

    }
    context.update(custom_context(request))
    return render(request, 'website/servicios.html', context)

def sobre_nosotros(request):
    context = {

    }
    context.update(custom_context(request))
    return render(request, 'website/sobre_nosotros.html', context)

def ofreces_servicios(request):
    testimonios = Testimonio.objects.filter(mostrar = True, usuario__proveedor = True)[:3]
    context = {
        'testimonios': testimonios,
    }
    context.update(custom_context(request))
    return render(request, 'website/ofreces_servicios.html', context)

def terminos_de_uso(request):
    context = {

    }
    context.update(custom_context(request))
    return render(request, 'website/terminos_de_uso.html', context)

def condiciones_legales(request):
    context = {

    }
    context.update(custom_context(request))
    return render(request, 'website/condiciones_legales.html', context)

def politica_de_privacidad_de_datos(request):
    context = {

    }
    context.update(custom_context(request))
    return render(request, 'website/politica_de_privacidad_de_datos.html', context)

def buscar_alojamientos_por_habitacion(request):
    # Por defecto se mostrarán todos los Alojamientos por Habitación que cumplan con las condiciones de indexado
    # Estas condiciones son:
    # 1 - Que el usuario propietario esté activo y validado como proveedor
    # 2 - Que el servicio esté activo y tenga al menos una habitación registrada y esta tenga fotos

    # Debe comprobarse si hay criterios de búsqueda almacenadas en la session para inicializar el Formulario y realizar la primera búsqueda
    if 'criterio_alojamientos_por_habitacion' in request.session:
        lugar = request.session['criterio_alojamientos_por_habitacion']['lugar']
        fecha_desde = request.session['criterio_alojamientos_por_habitacion']['fecha_desde']
        fecha_hasta = request.session['criterio_alojamientos_por_habitacion']['fecha_hasta']
        huespedes = request.session['criterio_alojamientos_por_habitacion']['huespedes']
    else:
        lugar, fecha_desde, fecha_hasta, huespedes = None, None, None, None

    busqueda = {
        'lugar': lugar,
        'fecha_entrada': fecha_desde,
        'fecha_salida': fecha_hasta,
    }

    # Si se pasan algunos valores iniciales de búsqueda debe inicializarse el formulario con estos valores y realizar una primera búsqueda
    if fecha_desde or fecha_hasta or huespedes:
        fechas_huespedes = [fecha_desde, fecha_hasta, int(huespedes)]
    else:
        fechas_huespedes = None

    alojamientos = Alojamiento.objects.detalles_alojamientos(
        # Se definen los criterios de filtrado para los Alojamientos que deseamos listar
        usuarios = Usuario.get_proveedores_validados(),
        activos = True,
        con_habitaciones = True,
        por_modalidad = True,
        por_habitacion = True,
        lugar = lugar,
        fechas_huespedes = fechas_huespedes
    )

    # Se obtiene la lista de todas las habitaciones registradas para los Alojamientos anteriormente definidos
    habitaciones = Habitacion.get_habitaciones_alojamientos(alojamientos)

    # Se obtienen los Alojamientos agrupados por Evaluación
    alojamientos_agrupados_evaluacion = Alojamiento.get_agrupados_evaluacion(alojamientos)

    # Se obtienen los Alojamientos agrupados por Características
    alojamientos_agrupados_caracteristicas = Alojamiento.get_agrupados_caracteristicas(alojamientos)

    if request.method == 'POST':
        # Si se realiza un POST es porque se están pasando los criterios de búsqueda desde esta misma vitsa, así que debemos eliminar
        # los criterios que estaban almacenados en la session para que no interfieran con los actuales criterios de búsqueda
        if 'criterio_alojamientos_por_habitacion' in request.session:
            del request.session['criterio_alojamientos_por_habitacion']
        form = Buscar_Alojamientos_Por_Habitacion(request.POST)
        if form.is_valid():
            # Se aplican los filtros del Formulario
            alojamientos = Alojamiento.objects.detalles_alojamientos(
                activos = True,
                con_habitaciones = True,
                por_modalidad = True,
                por_habitacion = True,
                lugar = form.cleaned_data['lugar'],
                fechas_huespedes = [
                    form.cleaned_data['fecha_entrada'],
                    form.cleaned_data['fecha_salida'],
                    int(form.cleaned_data['huespedes'])
                ],
                ordered = form.cleaned_data['ordenar_por'],
                rango_precio = form.cleaned_data['rango_precio'],

                rating_1_estrella = form.cleaned_data['rating_1_estrella'],
                rating_2_estrellas = form.cleaned_data['rating_2_estrellas'],
                rating_3_estrellas = form.cleaned_data['rating_3_estrellas'],
                rating_4_estrellas = form.cleaned_data['rating_4_estrellas'],
                rating_5_estrellas = form.cleaned_data['rating_5_estrellas'],

                acceso_discapacitados = form.cleaned_data['acceso_discapacitados'],
                desayuno_cena = form.cleaned_data['desayuno_cena'],
                internet = form.cleaned_data['internet'],
                parqueo = form.cleaned_data['parqueo'],
                patio_terraza_balcon = form.cleaned_data['patio_terraza_balcon'],
                permitido_fumar = form.cleaned_data['permitido_fumar'],
                permitido_mascotas = form.cleaned_data['permitido_mascotas'],
                permitido_ninnos = form.cleaned_data['permitido_ninnos'],
                piscina = form.cleaned_data['piscina'],
                transporte_aeropuerto = form.cleaned_data['transporte_aeropuerto'],
                apartamento = form.cleaned_data['apartamento'],
                casa = form.cleaned_data['casa'],
                mansion = form.cleaned_data['mansion'],
                aire_acondicionado = form.cleaned_data['aire_acondicionado'],
                agua_caliente = form.cleaned_data['agua_caliente'],
                nevera_bar = form.cleaned_data['nevera_bar'],
                balcon = form.cleaned_data['balcon'],
                caja_fuerte = form.cleaned_data['caja_fuerte'],
                tv = form.cleaned_data['tv'],
                estereo = form.cleaned_data['estereo'],
                ventanas = form.cleaned_data['ventanas'],
                banno_independiente = form.cleaned_data['banno_independiente'],
            )

            context = {
                'form': form,
                'alojamientos': alojamientos,
                'habitaciones': habitaciones,
                'alojamientos_5_estrellas': alojamientos_agrupados_evaluacion['5_estrellas'],
                'alojamientos_4_estrellas': alojamientos_agrupados_evaluacion['4_estrellas'],
                'alojamientos_3_estrellas': alojamientos_agrupados_evaluacion['3_estrellas'],
                'alojamientos_2_estrellas': alojamientos_agrupados_evaluacion['2_estrellas'],
                'alojamientos_1_estrellas': alojamientos_agrupados_evaluacion['1_estrellas'],

                'acceso_discapacitados': alojamientos_agrupados_caracteristicas['acceso_discapacitados'],
                'desayuno_cena': alojamientos_agrupados_caracteristicas['desayuno_cena'],
                'internet': alojamientos_agrupados_caracteristicas['internet'],
                'parqueo': alojamientos_agrupados_caracteristicas['parqueo'],
                'patio_terraza_balcon': alojamientos_agrupados_caracteristicas['patio_terraza_balcon'],
                'permitido_fumar': alojamientos_agrupados_caracteristicas['permitido_fumar'],
                'permitido_mascotas': alojamientos_agrupados_caracteristicas['permitido_mascotas'],
                'permitido_ninnos': alojamientos_agrupados_caracteristicas['permitido_ninnos'],
                'piscina': alojamientos_agrupados_caracteristicas['piscina'],
                'transporte_aeropuerto': alojamientos_agrupados_caracteristicas['transporte_aeropuerto'],
                'apartamento': alojamientos_agrupados_caracteristicas['apartamento'],
                'casa': alojamientos_agrupados_caracteristicas['casa'],
                'mansion': alojamientos_agrupados_caracteristicas['mansion'],
                'aire_acondicionado': alojamientos_agrupados_caracteristicas['aire_acondicionado'],
                'agua_caliente': alojamientos_agrupados_caracteristicas['agua_caliente'],
                'nevera_bar': alojamientos_agrupados_caracteristicas['nevera_bar'],
                'balcon': alojamientos_agrupados_caracteristicas['balcon'],
                'caja_fuerte': alojamientos_agrupados_caracteristicas['caja_fuerte'],
                'tv': alojamientos_agrupados_caracteristicas['tv'],
                'estereo': alojamientos_agrupados_caracteristicas['estereo'],
                'ventanas': alojamientos_agrupados_caracteristicas['ventanas'],
                'banno_independiente': alojamientos_agrupados_caracteristicas['banno_independiente'],
            }
        else:
            print('El formulario es inválido')
            context = {
                'form': form,
                'message': 'Hay errores en el Formulario',
                'class_alert': 'alert alert-danger',
                'alojamientos': None,
                'habitaciones': None,
                'alojamientos_5_estrellas': [],
                'alojamientos_4_estrellas': [],
                'alojamientos_3_estrellas': [],
                'alojamientos_2_estrellas': [],
                'alojamientos_1_estrellas': [],

                'acceso_discapacitados': [],
                'desayuno_cena': [],
                'internet': [],
                'parqueo': [],
                'patio_terraza_balcon': [],
                'permitido_fumar': [],
                'permitido_mascotas': [],
                'permitido_ninnos': [],
                'piscina': [],
                'transporte_aeropuerto': [],
                'apartamento': [],
                'casa': [],
                'mansion': [],

                'aire_acondicionado': [],
                'agua_caliente': [],
                'nevera_bar': [],
                'balcon': [],
                'caja_fuerte': [],
                'tv': [],
                'estereo': [],
                'ventanas': [],
                'banno_independiente': [],
            }
    else:
        context = {
            'form': Buscar_Alojamientos_Por_Habitacion(busqueda),
            'alojamientos': alojamientos,
            'habitaciones': habitaciones,
            'alojamientos_5_estrellas': alojamientos_agrupados_evaluacion['5_estrellas'],
            'alojamientos_4_estrellas': alojamientos_agrupados_evaluacion['4_estrellas'],
            'alojamientos_3_estrellas': alojamientos_agrupados_evaluacion['3_estrellas'],
            'alojamientos_2_estrellas': alojamientos_agrupados_evaluacion['2_estrellas'],
            'alojamientos_1_estrellas': alojamientos_agrupados_evaluacion['1_estrellas'],

            'acceso_discapacitados': alojamientos_agrupados_caracteristicas['acceso_discapacitados'],
            'desayuno_cena': alojamientos_agrupados_caracteristicas['desayuno_cena'],
            'internet': alojamientos_agrupados_caracteristicas['internet'],
            'parqueo': alojamientos_agrupados_caracteristicas['parqueo'],
            'patio_terraza_balcon': alojamientos_agrupados_caracteristicas['patio_terraza_balcon'],
            'permitido_fumar': alojamientos_agrupados_caracteristicas['permitido_fumar'],
            'permitido_mascotas': alojamientos_agrupados_caracteristicas['permitido_mascotas'],
            'permitido_ninnos': alojamientos_agrupados_caracteristicas['permitido_ninnos'],
            'piscina': alojamientos_agrupados_caracteristicas['piscina'],
            'transporte_aeropuerto': alojamientos_agrupados_caracteristicas['transporte_aeropuerto'],
            'apartamento': alojamientos_agrupados_caracteristicas['apartamento'],
            'casa': alojamientos_agrupados_caracteristicas['casa'],
            'mansion': alojamientos_agrupados_caracteristicas['mansion'],
            'aire_acondicionado': alojamientos_agrupados_caracteristicas['aire_acondicionado'],
            'agua_caliente': alojamientos_agrupados_caracteristicas['agua_caliente'],
            'nevera_bar': alojamientos_agrupados_caracteristicas['nevera_bar'],
            'balcon': alojamientos_agrupados_caracteristicas['balcon'],
            'caja_fuerte': alojamientos_agrupados_caracteristicas['caja_fuerte'],
            'tv': alojamientos_agrupados_caracteristicas['tv'],
            'estereo': alojamientos_agrupados_caracteristicas['estereo'],
            'ventanas': alojamientos_agrupados_caracteristicas['ventanas'],
            'banno_independiente': alojamientos_agrupados_caracteristicas['banno_independiente'],
        }
    context.update(custom_context(request))
    return render(request, 'website/buscar_alojamientos_por_habitacion.html', context)

def buscar_alojamientos_completos(request):
    # Por defecto se mostrarán todos los Alojamientos Completos que cumplan con las condiciones de indexado
    # Estas condiciones son: que el servicio se encuentre activo

    # Debe comprobarse si hay criterios de búsqueda almacenadas en la session para inicializar el Formulario y realizar la primera búsqueda
    if 'criterio_alojamientos_completos' in request.session:
        lugar = request.session['criterio_alojamientos_completos']['lugar']
        fecha_desde = request.session['criterio_alojamientos_completos']['fecha_desde']
        fecha_hasta = request.session['criterio_alojamientos_completos']['fecha_hasta']
        huespedes = request.session['criterio_alojamientos_completos']['huespedes']
    else:
        lugar, fecha_desde, fecha_hasta, huespedes = None, None, None, None

    busqueda = {
        'lugar': lugar,
        'fecha_entrada': fecha_desde,
        'fecha_salida': fecha_hasta,
    }

    # Si se pasan algunos valores iniciales de búsqueda debe inicializarse el formulario con estos valores y realizar una primera búsqueda
    if fecha_desde or fecha_hasta or huespedes:
        fechas_huespedes = [fecha_desde, fecha_hasta, int(huespedes)]
    else:
        fechas_huespedes = None

    alojamientos = Alojamiento.objects.detalles_alojamientos(
        activos = True,
        por_modalidad = True,
        con_habitaciones = True,
        por_habitacion = False,
        lugar = lugar,
        fechas_huespedes = fechas_huespedes,
    )

    # Se obtiene la lista de todas las habitaciones registradas para los Alojamientos anteriormente definidos
    habitaciones = Habitacion.get_habitaciones_alojamientos(alojamientos)

    # Se obtienen los Alojamientos agrupados por Evaluación
    alojamientos_agrupados_evaluacion = Alojamiento.get_agrupados_evaluacion(alojamientos)

    # Se obtienen los Alojamientos agrupados por Características
    alojamientos_agrupados_caracteristicas = Alojamiento.get_agrupados_caracteristicas(alojamientos)

    if request.method == 'POST':
        # Si se realiza un POST es porque se están pasando los criterios de búsqueda desde esta misma vitsa, así que debemos eliminar
        # los criterios que estaban almacenados en la session para que no interfieran con los actuales criterios de búsqueda
        if 'criterio_alojamientos_completos' in request.session:
            del request.session['criterio_alojamientos_completos']
        form = Buscar_Alojamientos_Completos(request.POST)
        if form.is_valid():
            # Se aplican los filtros del Formulario
            alojamientos = Alojamiento.objects.detalles_alojamientos(
                activos = True,
                por_modalidad = True,
                con_habitaciones = True,
                por_habitacion = False,
                lugar = form.cleaned_data['lugar'],
                fechas_huespedes = [
                    form.cleaned_data['fecha_entrada'],
                    form.cleaned_data['fecha_salida'],
                    int(form.cleaned_data['huespedes']),
                ],
                ordered = form.cleaned_data['ordenar_por'],
                rango_precio = form.cleaned_data['rango_precio'],

                rating_1_estrella = form.cleaned_data['rating_1_estrella'],
                rating_2_estrellas = form.cleaned_data['rating_2_estrellas'],
                rating_3_estrellas = form.cleaned_data['rating_3_estrellas'],
                rating_4_estrellas = form.cleaned_data['rating_4_estrellas'],
                rating_5_estrellas = form.cleaned_data['rating_5_estrellas'],

                acceso_discapacitados = form.cleaned_data['acceso_discapacitados'],
                cantidad_habitaciones = form.cleaned_data['cantidad_habitaciones'],
                cocina = form.cleaned_data['cocina'],
                desayuno_cena = form.cleaned_data['desayuno_cena'],
                internet = form.cleaned_data['internet'],
                parqueo = form.cleaned_data['parqueo'],
                patio_terraza_balcon = form.cleaned_data['patio_terraza_balcon'],
                permitido_fumar = form.cleaned_data['permitido_fumar'],
                permitido_mascotas = form.cleaned_data['permitido_mascotas'],
                permitido_ninnos = form.cleaned_data['permitido_ninnos'],
                piscina = form.cleaned_data['piscina'],
                transporte_aeropuerto = form.cleaned_data['transporte_aeropuerto'],
                apartamento = form.cleaned_data['apartamento'],
                casa = form.cleaned_data['casa'],
                mansion = form.cleaned_data['mansion'],
                aire_acondicionado = form.cleaned_data['aire_acondicionado'],
                agua_caliente = form.cleaned_data['agua_caliente'],
                nevera_bar = form.cleaned_data['nevera_bar'],
                balcon = form.cleaned_data['balcon'],
                caja_fuerte = form.cleaned_data['caja_fuerte'],
                tv = form.cleaned_data['tv'],
                estereo = form.cleaned_data['estereo'],
                lavadora = form.cleaned_data['lavadora'],
            )

            context = {
                'form': form,
                'alojamientos': alojamientos,
                'habitaciones': habitaciones,
                'alojamientos_5_estrellas': alojamientos_agrupados_evaluacion['5_estrellas'],
                'alojamientos_4_estrellas': alojamientos_agrupados_evaluacion['4_estrellas'],
                'alojamientos_3_estrellas': alojamientos_agrupados_evaluacion['3_estrellas'],
                'alojamientos_2_estrellas': alojamientos_agrupados_evaluacion['2_estrellas'],
                'alojamientos_1_estrellas': alojamientos_agrupados_evaluacion['1_estrellas'],

                'acceso_discapacitados': alojamientos_agrupados_caracteristicas['acceso_discapacitados'],
                'desayuno_cena': alojamientos_agrupados_caracteristicas['desayuno_cena'],
                'internet': alojamientos_agrupados_caracteristicas['internet'],
                'parqueo': alojamientos_agrupados_caracteristicas['parqueo'],
                'patio_terraza_balcon': alojamientos_agrupados_caracteristicas['patio_terraza_balcon'],
                'permitido_fumar': alojamientos_agrupados_caracteristicas['permitido_fumar'],
                'permitido_mascotas': alojamientos_agrupados_caracteristicas['permitido_mascotas'],
                'permitido_ninnos': alojamientos_agrupados_caracteristicas['permitido_ninnos'],
                'piscina': alojamientos_agrupados_caracteristicas['piscina'],
                'transporte_aeropuerto': alojamientos_agrupados_caracteristicas['transporte_aeropuerto'],
                'apartamento': alojamientos_agrupados_caracteristicas['apartamento'],
                'casa': alojamientos_agrupados_caracteristicas['casa'],
                'mansion': alojamientos_agrupados_caracteristicas['mansion'],
                'lavadora': alojamientos_agrupados_caracteristicas['lavadora'],
                'cocina': alojamientos_agrupados_caracteristicas['cocina'],
                'aire_acondicionado': alojamientos_agrupados_caracteristicas['aire_acondicionado'],
                'agua_caliente': alojamientos_agrupados_caracteristicas['agua_caliente'],
                'nevera_bar': alojamientos_agrupados_caracteristicas['nevera_bar'],
                'balcon': alojamientos_agrupados_caracteristicas['balcon'],
                'caja_fuerte': alojamientos_agrupados_caracteristicas['caja_fuerte'],
                'tv': alojamientos_agrupados_caracteristicas['tv'],
                'estereo': alojamientos_agrupados_caracteristicas['estereo'],
            }
        else:
            print('El formulario es inválido')
            context = {
                'form': form,
                'message': 'Hay errores en el Formulario',
                'class_alert': 'alert alert-danger',
                'alojamientos': None,
                'habitaciones': None,
                'alojamientos_5_estrellas': [],
                'alojamientos_4_estrellas': [],
                'alojamientos_3_estrellas': [],
                'alojamientos_2_estrellas': [],
                'alojamientos_1_estrellas': [],

                'acceso_discapacitados': [],
                'desayuno_cena': [],
                'internet': [],
                'parqueo': [],
                'patio_terraza_balcon': [],
                'permitido_fumar': [],
                'permitido_mascotas': [],
                'permitido_ninnos': [],
                'piscina': [],
                'transporte_aeropuerto': [],
                'apartamento': [],
                'casa': [],
                'mansion': [],

                'aire_acondicionado': [],
                'agua_caliente': [],
                'nevera_bar': [],
                'balcon': [],
                'caja_fuerte': [],
                'tv': [],
                'estereo': [],
            }
    else:
        context = {
            'form': Buscar_Alojamientos_Completos(busqueda),
            'alojamientos': alojamientos,
            'habitaciones': habitaciones,
            'alojamientos_5_estrellas': alojamientos_agrupados_evaluacion['5_estrellas'],
            'alojamientos_4_estrellas': alojamientos_agrupados_evaluacion['4_estrellas'],
            'alojamientos_3_estrellas': alojamientos_agrupados_evaluacion['3_estrellas'],
            'alojamientos_2_estrellas': alojamientos_agrupados_evaluacion['2_estrellas'],
            'alojamientos_1_estrellas': alojamientos_agrupados_evaluacion['1_estrellas'],

            'acceso_discapacitados': alojamientos_agrupados_caracteristicas['acceso_discapacitados'],
            'desayuno_cena': alojamientos_agrupados_caracteristicas['desayuno_cena'],
            'internet': alojamientos_agrupados_caracteristicas['internet'],
            'parqueo': alojamientos_agrupados_caracteristicas['parqueo'],
            'patio_terraza_balcon': alojamientos_agrupados_caracteristicas['patio_terraza_balcon'],
            'permitido_fumar': alojamientos_agrupados_caracteristicas['permitido_fumar'],
            'permitido_mascotas': alojamientos_agrupados_caracteristicas['permitido_mascotas'],
            'permitido_ninnos': alojamientos_agrupados_caracteristicas['permitido_ninnos'],
            'piscina': alojamientos_agrupados_caracteristicas['piscina'],
            'transporte_aeropuerto': alojamientos_agrupados_caracteristicas['transporte_aeropuerto'],
            'apartamento': alojamientos_agrupados_caracteristicas['apartamento'],
            'casa': alojamientos_agrupados_caracteristicas['casa'],
            'mansion': alojamientos_agrupados_caracteristicas['mansion'],
            'lavadora': alojamientos_agrupados_caracteristicas['lavadora'],
            'cocina': alojamientos_agrupados_caracteristicas['cocina'],
            'aire_acondicionado': alojamientos_agrupados_caracteristicas['aire_acondicionado'],
            'agua_caliente': alojamientos_agrupados_caracteristicas['agua_caliente'],
            'nevera_bar': alojamientos_agrupados_caracteristicas['nevera_bar'],
            'balcon': alojamientos_agrupados_caracteristicas['balcon'],
            'caja_fuerte': alojamientos_agrupados_caracteristicas['caja_fuerte'],
            'tv': alojamientos_agrupados_caracteristicas['tv'],
            'estereo': alojamientos_agrupados_caracteristicas['estereo'],
        }
    context.update(custom_context(request))
    return render(request, 'website/buscar_alojamientos_completos.html', context)

def buscar_excursiones(request):
    context = {

    }
    context.update(custom_context(request))
    return render(request, 'website/buscar_excursiones.html', context)


def buscar_tours(request):
    context = {

    }
    context.update(custom_context(request))
    return render(request, 'website/buscar_tours.html', context)


def buscar_citytours(request):
    context = {

    }
    context.update(custom_context(request))
    return render(request, 'website/buscar_citytours.html', context)

def buscar_recorridos(request):
    context = {

    }
    context.update(custom_context(request))
    return render(request, 'website/buscar_recorridos.html', context)

def buscar_paquetes(request):
    context = {

    }
    context.update(custom_context(request))
    return render(request, 'website/buscar_paquetes.html', context)

def buscar_taxis(request):
    context = {

    }
    context.update(custom_context(request))
    return render(request, 'website/buscar_taxis.html', context)

def buscar_destinos(request):
    context = {

    }
    context.update(custom_context(request))
    return render(request, 'website/buscar_destinos.html', context)

def como_funciona(request):
    testimonios = Testimonio.objects.filter(mostrar = True, usuario__proveedor = False)[:3]
    # alojamientos_populares = Alojamiento.objects.detalles_alojamientos()[:4]
    context = {
        'testimonios': testimonios,
        # 'alojamientos_populares': alojamientos_populares,
    }

    context.update(custom_context(request))
    return render(request, 'website/como_funciona.html', context)

def blog(request):

    context = {

    }
    context.update(custom_context(request))
    return render(request, 'website/blog.html', context)

def pruebas_html(request):
    context = {

    }

    context.update(custom_context(request))
    return render(request, 'website/pruebas_html.html', context)

def set_currency(request, moneda):
    # Actualiza en la sesión la moneda en que desea visualizar los precios el usuario así como el tipo de cambio entre la moneda base y esa moneda
    # para poder mostrar los precios correspondientes en la moneda seleccionada
    moneda = Moneda.objects.get(codigo_iso = moneda)

    # Extraemos el diccionario "user_data" de la sesión para modificarlo
    user_data = request.session['user_data']

    # 1 - Escribimos la moneda seleccionada en la sesión
    user_data['moneda_id'] = moneda.id
    user_data['moneda_codigo'] = moneda.codigo_iso

    # 2 - Determinar la tasa de cambio moneda_base / moneda_seleccionada y guardarla en "user_data"
    # Si la moneda seleccionada es el CUC o el USD, la tasa de cambio es 1, puesto que el CUC es la moneda base y 1 USD = 1 CUC ( Así es... y yo tampoco entiendo por qué :) )
    if moneda.codigo_iso in ['CUC', 'USD']:
        user_data['rate'] = '1'
    else:
        # Si es cualquier otra moneda se obtiene del último Tipo de Cambio almacenado en la BD
        # Se utiliza el USD para calcular el tipo de Cambio porque el CUC no está disponible, y son iguales en valor así que nos sirve
        user_data['rate'] = str(Tipo_Cambio.objects.get(moneda_2 = moneda, moneda_1__codigo_iso = 'USD').tipo_cambio)

    # Se guarda el diccionario modificado de vuelta en la sesión
    request.session['user_data'] = user_data

    # Se recarga la página cualquiera que esta sea
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def temporalmente_indisponible(request):
    context = {

    }
    return render(request, 'website/temporalmente_indisponible.html', context)

def destino(request, destino_id):
    # Se identifica el destino que se ha seleccionado por el usuario
    destino = Destino.objects.get(id = destino_id)

    # Se obtiene un alista de Destinos Populares
    destinos_populares = Destino.get_destinos_populares()[:4]

    # Se obtiene una lista de alojamientos cerca del destino
    alojamientos_cercanos = destino.get_alojamientos_cercanos()[:4]

    context = {
        'destino': destino,
        'destinos_populares': destinos_populares,
        'alojamientos_cercanos': alojamientos_cercanos,
    }

    context.update(custom_context(request))
    return render(request, 'website/destino.html', context)

def get_destinos(request):
    # Devuelve una lista de los destinos con sus IDs
    destinos = []
    for destino in Destino.objects.all():
        destinos.append({'name': destino.nombre, 'id': destino.id})

    resultado = {
        'destinos': destinos,
    }
    return HttpResponse(json.dumps(resultado), content_type = 'application/json')

def get_aeropuertos_mundo(request):
    # Devuelve una lista de los destinos con sus IDs
    aeropuertos_mundo = []
    for aeropuerto_mundo in Aeropuerto.objects.filter(cuba = False).order_by('codigo_iata'):
        aeropuertos_mundo.append(
            {
                'name': aeropuerto_mundo.info_completa,
            }
        )
    return HttpResponse(json.dumps(aeropuertos_mundo), content_type = 'application/json')

def search(request, elemento):
    if request.method == 'POST':
        if 'flight' in request.POST:
            aeropuerto_salida = request.POST['aeropuerto_salida'].split(' ')[0]
            aeropuerto_cuba = Aeropuerto.objects.get(id = request.POST['aeropuerto_cuba']).codigo_iata

            fecha_ida = request.POST['start'].split('-')
            fecha_ida = '%s/%s/%s' %(fecha_ida[2], fecha_ida[1], fecha_ida[0])

            fecha_regreso = request.POST['end'].split('-')
            fecha_regreso = '%s/%s/%s' % (fecha_regreso[2], fecha_regreso[1], fecha_regreso[0])

            adultos = request.POST['adultos']
            ninnos = request.POST['ninnos']
            bebes = request.POST['bebes']

            onlinetravel_url = 'http://booking.ontraveline.com/air/index.php?goal=direct_search&action=listAvailableAirports&search=true' \
                               '&airsearchhtmlformview_incluir_vuelos=true&airsearchhtmlformview_lowcost=true' \
                               '&airsearchhtmlformview_vuelos_regulares=true&language_code=es&airsearchhtmlformview_flight_type=roundtrip' \
                               '&s_0_airsearchhtmlformview_airsearchflighthtmlformview_from=%s' \
                               '&s_0_airsearchhtmlformview_airsearchflighthtmlformview_to=%s' \
                               '&s_0_airsearchhtmlformview_airsearchflighthtmlformview_depart_date=%s' \
                               '&s_1_airsearchhtmlformview_airsearchflighthtmlformview_depart_date=%s' \
                               '&airsearchhtmlformview_adults=%s' \
                               '&airsearchhtmlformview_children=%s' \
                               '&airsearchhtmlformview_babies=%s' \
                               '&airsearchhtmlformview_residente=false' %(aeropuerto_salida, aeropuerto_cuba, fecha_ida, fecha_regreso, adultos, ninnos, bebes)

            request.session['onlinetravel_url'] = onlinetravel_url
            # return redirect('website:search', 'flights')

        else:
            return redirect('website:index')

    else:
        return redirect('website:index')


    if elemento == 'flights':
        context = {
            'elemento': 'vuelos'
        }
        context.update(custom_context(request))
        return render(request, 'website/loading.html', context)

def get_destinos_provincias_municipios_alojamientos(request):
    resultados = []
    # La lista de posibles resultados es la unión de coincidencias del criterio de búsqueda con el nombre de Destinos, Provincias, Municipios y Alojamientos

    for provincia in Provincia.objects.filter(pais__nombre = 'CUBA'):
        if not {'name': provincia.nombre.upper()} in resultados:
            resultados.append(
                {'name': provincia.nombre.upper()}
            )
    for destino in Destino.objects.order_by('nombre'):
        if not {'name': destino.nombre.upper()} in resultados:
            resultados.append(
                {'name': destino.nombre.upper()}
            )
    for municipio in Municipio.objects.filter(provincia__pais__nombre = 'CUBA'):
        if not {'name': municipio.nombre.upper()} in resultados:
            resultados.append(
                {'name': municipio.nombre.upper()}
            )

    return HttpResponse(json.dumps(resultados), content_type='application/json')
