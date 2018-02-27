import datetime, json, requests
from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from forex_python.converter import CurrencyRates
from servicios.forms import Add_Habitacion_Alojamiento_Por_Habitacion, Add_Habitacion_Alojamiento_Completo, \
    Add_Alojamiento_Datos_Generales, Add_Alojamiento_Completo, Foto_Habitacion_Form, Foto_Servicio_Form, Add_Regla_Precio,\
    Modificar_Habitacion_Alojamiento_Por_Habitacion, Modificar_Habitacion_Alojamiento_Completo, Modificar_Alojamiento_Completo, \
    Modificar_Alojamiento, Consultar_Disponibilidad_Alojamiento_Por_Habitacion, Consultar_Disponibilidad_Alojamiento_Completo,\
    Add_Indisponibilidad, URL_Video_Form

from servicios.models import Habitacion, Habitacion_Alojamiento_Por_Habitacion, Alojamiento_Completo, Servicio, \
    Excursion, CityTour, Tour, Taxi, Destino, Pais, Alojamiento_sin_finalizar, Alojamiento, Regla_Precio, Comision,\
    Foto_Habitacion, Foto_Servicio, Recorrido, Pack, Favorito, Reserva, Reserva_Habitacion, Moneda,\
    Tipo_Cambio, Indisponibilidad, Provincia, Cancelacion_Reserva, Evaluacion

from emails.models import Email

from pagos.models import Paypal_App, Pago
from usuarios.models import Usuario
from support.globals import meses, GMaps_APIKey
from support import populate

# Custom context processor
def custom_context(request):
    # Lo primero es obtener la configuración básica del Sistema definida en el objeto "COnfiguración" y que esté seleccionado como "en_uso"
    # Esto sirve para determinar algunos valores iniciales útiles como:
    # 1 - costo_gestion: Precio que se le cobra al cliente por el servicio de intermediación de la plataforma
    # 2 - impuesto: El impuesto aplicable al costo de gestión definido anteriormente y que se carga al cliente
    # 3 - moneda_base: Es la moneda en la que se muestran los precios de todos los servicios (Por defecto es el CUC. También se puede usar a efectos prácticos el USD por ser iguales en valor)
    # 4 - moneda_por_defecto: Es la moneda en que se mostrarán todos los precios de servicios del sitio, si no se puede establecer lógicamente la moneda en que deberían mostrarse
    # 5 - pais_por_defecto: Es el país desde el cual se asumirá que navega el usuario, si no se puede establecer lógicamente el mismo. Normalmente se intenta a partir de la IP
    # 6 - idioma_por_defecto: Es el idioma en el cual se verá el sitio por defecto, en caso que no se pueda detectar el idioma que debería mostrarse para el usuario
    # 7 - edad_minima_huesped: Es la edad mínima a partir de la cual una persona ocupa una plaza de pax en los servicios de la plataforma (Normalmente 3 años)
    # 8 - registros_index: Es la cantidad de servicios que se muestran en el index para cada categoría
    # En caso de que no haya una configuración establecida por defecto en el sistema, se dirigirá el usuario a un sitio u otro en dependencia de su nivel de usuario

    # Lo próximo que se hace es verificar si el usuario ya ha navegado antes con esta sesión o si es totalmente nuevo
    # Esto se puede saber por la existencia en la sesión del diccionario "user_data" que almacena toda la información posible
    # del usuario nada más comienza su navegación.

    euro = Moneda.objects.get(codigo_iso = 'EUR')

    # Caso en que el usuario es completamente nuevo (no existe "user_data" en la sesión)
    if not 'user_data' in request.session:
        # En este caso hay que recavar toda la información posible y almacenarla en la sesión
        # La mayor parte de esta información se obtiene a partir de la IP
        ip = request.META.get('REMOTE_ADDR')

        ip_data = requests.get('http://ip-api.com/json', params = (ip)).json()
        country_code = ip_data['countryCode']
        isp = ip_data['isp']
        city = ip_data['city']
        region_name = ip_data['regionName']
        codigo_postal = ip_data['zip']
        timezone = ip_data['timezone']
        region = ip_data['region']
        country_name = ip_data['country']

        # Algunos valores se obtienen a partir de los datos obtenidos de la IP
        # Caso en que el país identificado con la IP lo tengamos registrado en el sistema
        if Pais.objects.filter(nombre = country_name):
            pais = Pais.objects.get(nombre = country_name)
            pais_id = pais.id
            moneda_id = pais.moneda.id
            moneda_codigo = pais.moneda.codigo_iso
            moneda_actual = pais.moneda
        else:
            # Si no podemos determinar el país de navegación del usuario, establecemos por defecto los valores definidos en la configuración inicial
            pais_id = Pais.objects.get(nombre = 'SPAIN').id
            moneda_actual = euro
            moneda_id = euro.id
            moneda_codigo = euro.codigo_iso

        # Una vez establecida la moneda en que se van a mostrar los precios de los servicios del sitio, se determina la razón de cambio respecto a la moneda base del sistema
        rate = str(Tipo_Cambio.get_tipo_cambio(moneda_actual))
        billing_rate = str(Tipo_Cambio.get_tipo_cambio(euro))

        # Se guarda toda la información en el diccionario "user_data"
        user_data = {
            'ip': ip,
            'country_code': country_code,
            'isp': isp,
            'city': city,
            'region_name': region_name,
            'codigo_postal': codigo_postal,
            'timezone': timezone,
            'region': region,
            'country_name': country_name,
            'pais_id': pais_id,
            'moneda_id': moneda_id,
            'moneda_codigo': moneda_codigo,
            'rate': rate,
            'billing_rate': billing_rate,
        }

        # Se guarda el diccionario "user_data" en la sesión
        request.session['user_data'] = user_data

    # Si ya existe un diccionario "user_data" en la sesión, simplemente se carga, pues muchos de sus valores serán procesados
    # o directamente servidos desde el context de esta vista
    else:
        user_data = request.session['user_data']

    # Se definen otras variables para disponer de ellas a partir del contexto de esta vista
    # Monedas que se muestran en el menú
    monedas_menu = Moneda.objects.filter(menu = True)

    # Valor de usuario que siempre se consulta en el menú
    user = request.user

    # Favoritos y en el carro
    if user.is_authenticated:
        usuario = Usuario.objects.get(user = user)
        # Obtener los favoritos del usuario logueado es una llamada a un método del modelo Favorito, que devuelve una lista de ids de servicios
        favoritos = Favorito.get_favoritos(usuarios = [usuario,])

        # Por definición en el carro existen todas las Reservas que estén incompletas para un usuario determinad
        en_el_carro = []
        for pago in Pago.objects.filter(completado = False, reserva__usuario = usuario):
            if pago.reserva not in en_el_carro:
                en_el_carro.append(Reserva.objects.detalles_reserva(pago.reserva.id))
    else:
        usuario = None
        # Obtener los favoritos de un usuario sin autenticar, es hacer una consulta a la session, a ver si hay alguno
        if 'favoritos' in request.session:
            favoritos = request.session['favoritos']
        else:
            favoritos = []

        # En este caso en_el_carro se encuentra almacenada en forma de lista de diccionarios en la sesión del navegador
        if 'en_el_carro' in request.session:
            en_el_carro = request.session['en_el_carro']
        else:
            en_el_carro = []

    # Destinos más importantes a listar en el menú
    destinos = Destino.objects.mas_importantes(
        criterio = 'intereses',
        cantidad = 10,
    )

    # Status de administrador del usuario
    if request.user.is_staff:
        admin = True
    else:
        admin = False

    # Definición de los valores que se quieren siempre en el context dict
    custom_context = {
        'usuario': usuario,
        'destinos': destinos,
        'admin': admin,
        'favoritos': favoritos,
        'en_el_carro': en_el_carro,
        'ip': user_data['ip'],
        'country_code': user_data['country_code'],
        'isp': user_data['isp'],
        'city': user_data['city'],
        'region_name': user_data['region_name'],
        'codigo_postal': user_data['codigo_postal'],
        'timezone': user_data['timezone'],
        'region': user_data['region'],
        'country_name': user_data['country_name'],
        'pais': Pais.get_user_pais(user_data['pais_id']),
        'moneda': Moneda.get_user_moneda(user_data['moneda_id']),
        'moneda_por_defecto': Moneda.get_moneda_por_defecto(),
        'monedas_menu': monedas_menu,
    }
    return custom_context

@login_required()
def mis_servicios(request):
    # Información extra útil a todas las vistas
    cc = custom_context(request)
    usuario = cc['usuario']

    # Alojamiento sin finalizar (Si tiene alguno)
    alojamiento_sin_finalizar = Alojamiento_sin_finalizar.objects.filter(usuario = usuario).first() or None

    # Alojamientos (Completos y Por Habitaciones)
    alojamientos = Alojamiento.objects.detalles_alojamientos(usuarios = [usuario,], cerrado = True)
    alojamientos_por_habitacion = []
    alojamientos_completos = []
    for alojamiento in alojamientos:
        if alojamiento.por_habitacion:
            alojamientos_por_habitacion.append(alojamiento)
        else:
            alojamientos_completos.append(alojamiento)

    # Excursiones
    excursiones = Excursion.get_excursiones_usuario(usuario)

    # CityTours
    citytours = CityTour.get_citytours_usuario(usuario)

    # Tours
    tours = Tour.get_tours_usuario(usuario)

    context = {
        'alojamiento_sin_finalizar': alojamiento_sin_finalizar,
        'alojamientos': alojamientos,
        'alojamientos_por_habitacion': alojamientos_por_habitacion,
        'alojamientos_completos': alojamientos_completos,
        'excursiones': excursiones,
        'citytour': citytours,
        'tours': tours,
    }
    context.update(cc)
    return render(request, 'servicios/servicios/mis_servicios.html', context)

@login_required()
def add_habitacion_alojamiento_por_habitacion(request, alojamiento_id):
    # Definición y obtención de datos para el Alojamiento y el Servicio
    alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = alojamiento_id)

    if request.method == 'POST':
        form = Add_Habitacion_Alojamiento_Por_Habitacion(request.POST)
        if form.is_valid():
            n_habitacion_alojamiento_por_habitacion = Habitacion_Alojamiento_Por_Habitacion.nueva_habitacion_alojamiento_por_habitacion(
                agua_caliente = form.cleaned_data['agua_caliente'],
                aire_acondicionado = form.cleaned_data['aire_acondicionado'],
                alojamiento = alojamiento,
                balcon = form.cleaned_data['balcon'],
                banno_independiente = form.cleaned_data['banno_independiente'],
                caja_fuerte = form.cleaned_data['caja_fuerte'],
                camas_dobles = form.cleaned_data['camas_dobles'],
                camas_individuales = form.cleaned_data['camas_individuales'],
                capacidad = form.cleaned_data['capacidad'],
                estereo = form.cleaned_data['estereo'],
                nevera_bar = form.cleaned_data['nevera_bar'],
                precio_base = form.cleaned_data['precio_base'],
                tv = form.cleaned_data['tv'],
                ventanas = form.cleaned_data['ventanas'],
            )
            if n_habitacion_alojamiento_por_habitacion:
                message = 'Ha creado correctamente la Habitación asociada al Alojamiento %s' %(alojamiento)
                class_alert = 'alert alert-success'
                form = Add_Habitacion_Alojamiento_Por_Habitacion()
            else:
                message = 'No se ha podido registrar la Habitación al Alojamiento %s' %(alojamiento)
                class_alert = 'alert alert-danger'
                form = Add_Habitacion_Alojamiento_Por_Habitacion(request.POST)
        else:
            message = 'Hay errores en el Formulario'
            class_alert = 'alert alert-danger'
            Add_Habitacion_Alojamiento_Por_Habitacion()

        context = {
            'message': message,
            'class_alert': class_alert,
            'alojamiento': alojamiento,
            'form': Add_Habitacion_Alojamiento_Por_Habitacion(),
        }
        context.update(custom_context(request))
        return render(request, 'servicios/habitaciones/add_habitacion_alojamiento_por_habitacion.html', context)

    elif not alojamiento.check_add_habitacion():
        return redirect('servicios:mis_servicios')
    else:
        context = {
            'alojamiento': alojamiento,
            'form': Add_Habitacion_Alojamiento_Por_Habitacion(),
        }
        context.update(custom_context(request))
        return render(request, 'servicios/habitaciones/add_habitacion_alojamiento_por_habitacion.html', context)

@login_required()
def add_habitacion_alojamiento_completo(request, alojamiento_id):
    # Definición del Alojamiento y el Servicio
    alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = alojamiento_id)

    if request.method == 'POST':
        form = Add_Habitacion_Alojamiento_Completo(request.POST)
        if form.is_valid():
            n_habitacion_alojamiento = Habitacion.nueva_habitacion(
                agua_caliente = form.cleaned_data['agua_caliente'],
                aire_acondicionado = form.cleaned_data['aire_acondicionado'],
                alojamiento = alojamiento,
                balcon = form.cleaned_data['balcon'],
                caja_fuerte = form.cleaned_data['caja_fuerte'],
                camas_dobles = form.cleaned_data['camas_dobles'],
                camas_individuales = form.cleaned_data['camas_individuales'],
                estereo = form.cleaned_data['estereo'],
                nevera_bar = form.cleaned_data['nevera_bar'],
                tv = form.cleaned_data['tv'],
                ventanas = form.cleaned_data['ventanas'],
            )
            if n_habitacion_alojamiento:
                context = {
                    'alojamiento': alojamiento,
                    'form': Add_Habitacion_Alojamiento_Completo(),
                    'message': 'Ha creado correctamenta la habitación asociada a %s' %(alojamiento.servicio.nombre),
                    'class_alert': 'alert alert-success',
                }
            else:
                context = {
                    'alojamiento': alojamiento,
                    'form': Add_Habitacion_Alojamiento_Completo(),
                    'message': 'No se ha podido crear la Habitación, pónganse en contacto con nosotros para ayudarle a resolver el problema',
                    'class_alert': 'alert alert-danger',
                }
        else:
            context = {
                'alojamiento': alojamiento,
                'form': Add_Habitacion_Alojamiento_Completo(request.POST),
                'message': 'Hay errores en el Formulario',
                'class_alert': 'alert alert-danger',
            }
    else:
        context = {
            'alojamiento': alojamiento,
            'form': Add_Habitacion_Alojamiento_Completo(),
        }

    context.update(custom_context(request))
    return render(request, 'servicios/habitaciones/add_habitacion_alojamiento_completo.html', context)

@login_required()
def administrar_alojamiento(request, alojamiento_id):
    # Se define el Alojamiento que se desea administrar y se le llama con el Object manager para obtener toda la información necesaria del mismo
    alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = alojamiento_id)

    # Este filtro es para evitar que algún usuario pueda administrar un Alojamiento que está cerrado.
    if alojamiento.servicio.cerrado:
        return redirect('servicios:mis_servicios')

    context = {
        'alojamiento': alojamiento,
        'muestra_evaluaciones': alojamiento.muestra_evaluaciones,
    }
    context.update(custom_context(request))
    if alojamiento.por_habitacion:
        return render(request, 'servicios/alojamientos/administrar_alojamiento_por_habitacion.html', context)
    else:
        return render(request, 'servicios/alojamientos/administrar_alojamiento_completo.html', context)

# Este es el paso común a al creación de cualquier tipo de Alojamiento. Si se alquila por habitaciones pasará directamente a la Administración
# Mientras que si se alquila compelto se irá a una segunda vista donde se podrán definir los datos más específicos de un Alojamiento Completo
# Por defecto un Alojamiento que se alquila por Habitaciones se crea inactivo, hasta tanto se registre al menos una habitación
@login_required()
def add_alojamiento(request):
    # Valida que Cuba sea una opción a seleccionar, dado que exista en la BD
    if not Pais.objects.filter(nombre = 'CUBA'):
        # Si no existe se crea y se recarga la página
        populate.populate_cuba()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # Se definen las provincias que van a estar disponibles para seleccionar en el formulario. Solo pueden ser de Cuba
    provincias_cuba = []
    for provincia in Provincia.objects.filter(pais__nombre = 'CUBA').order_by('nombre'):
        provincias_cuba.append([provincia.id, provincia])

    # Se llega aquí si Cuba está registrado como país en la BD
    if request.method == 'POST':
        form = Add_Alojamiento_Datos_Generales(provincias_cuba, request.POST)
        if form.is_valid():
            # Se obtienen los datos necesarios...
            acceso_discapacitados = form.cleaned_data['acceso_discapacitados']
            cantidad_habitaciones = form.cleaned_data['cantidad_habitaciones']
            codigo_postal = form.cleaned_data['codigo_postal']
            desayuno_cena = form.cleaned_data['desayuno_cena']
            descripcion = form.cleaned_data['descripcion']
            direccion = form.cleaned_data['direccion']
            internet = form.cleaned_data['internet']
            municipio = form.cleaned_data['municipio']
            nombre = form.cleaned_data['nombre']
            pais = Pais.objects.get(nombre = 'CUBA')
            parqueo = form.cleaned_data['parqueo']
            patio_terraza_balcon = form.cleaned_data['patio_terraza_balcon']
            permitido_fumar = form.cleaned_data['permitido_fumar']
            permitido_mascotas = form.cleaned_data['permitido_mascotas']
            permitido_ninnos = form.cleaned_data['permitido_ninnos']
            piscina = form.cleaned_data['piscina']
            por_habitacion = request.POST.get('modalidad_alquiler') == 'por_habitacion'
            provincia = Provincia.objects.get(id = form.cleaned_data['provincia'])
            tipo_alojamiento = form.cleaned_data['tipo_alojamiento']
            transporte_aeropuerto = form.cleaned_data['transporte_aeropuerto']
            usuario = Usuario.objects.get(user = request.user)

            # Se obtienen de los input hidden que capturan las coordenadas del Mapa la longitud y latitud del Alojamiento indicado por el usuario
            latitud = request.POST.get('latitud')
            longitud = request.POST.get('longitud')

            if not latitud or not longitud:
                context = {
                    'form': Add_Alojamiento_Datos_Generales(provincias_cuba, request.POST),
                    'class_alert': 'alert alert-danger',
                    'message': 'Debe ubicar su Alojamiento en el Mapa. Asegúrese de que coincida con la dirección indicada en el formulario',
                    'GMaps_APIKey': GMaps_APIKey,
                }
                # En este caso no se prosigue con el proceso de registro del Alojamiento
                context.update(custom_context(request))
                return render(request, 'servicios/alojamientos/add_alojamiento.html', context)

            # Si la modalidad de alquiler es Por Habitación, se crea el Alojamiento por Habitación y se lleva al usuario a que añada las habitaciones
            elif por_habitacion:
                n_alojamiento = Alojamiento.nuevo_alojamiento(
                    acceso_discapacitados = acceso_discapacitados,
                    activo = False,
                    cantidad_habitaciones = cantidad_habitaciones,
                    codigo_postal = codigo_postal,
                    desayuno_cena = desayuno_cena,
                    descripcion = descripcion,
                    direccion = direccion,
                    latitud = latitud,
                    longitud = longitud,
                    internet = internet,
                    municipio = municipio,
                    nombre = nombre,
                    pais = pais,
                    parqueo = parqueo,
                    patio_terraza_balcon = patio_terraza_balcon,
                    permitido_fumar = permitido_fumar,
                    permitido_mascotas = permitido_mascotas,
                    permitido_ninnos = permitido_ninnos,
                    piscina = piscina,
                    por_habitacion = por_habitacion,
                    provincia = provincia,
                    tipo_alojamiento = tipo_alojamiento,
                    transporte_aeropuerto = transporte_aeropuerto,
                    usuario = usuario,
                )
                # Si se ha podido crear el Alojamiento, se lleva a la vista de Administración del mismo
                if n_alojamiento:
                    return redirect('servicios:administrar_alojamiento', n_alojamiento.id)
                else:
                    context = {
                        'form': Add_Alojamiento_Datos_Generales(provincias_cuba, request.POST),
                        'class_alert': 'alert alert-danger',
                        'message': 'No se han podido registrar los Datos Generales del Alojamiento',
                        'GMaps_APIKey': GMaps_APIKey,
                    }
                    context.update(custom_context(request))
                    return render(request, 'servicios/alojamientos/add_alojamiento.html', context)
            else:
                n_alojamiento_sin_finalizar = Alojamiento_sin_finalizar.nuevo_alojamiento_sin_finalizar(
                    acceso_discapacitados = acceso_discapacitados,
                    cantidad_habitaciones = cantidad_habitaciones,
                    codigo_postal = codigo_postal,
                    desayuno_cena = desayuno_cena,
                    descripcion = descripcion,
                    direccion = direccion,
                    latitud = latitud,
                    longitud = longitud,
                    internet = internet,
                    municipio = municipio,
                    nombre = nombre,
                    pais = pais,
                    parqueo = parqueo,
                    patio_terraza_balcon = patio_terraza_balcon,
                    permitido_fumar = permitido_fumar,
                    permitido_mascotas = permitido_mascotas,
                    permitido_ninnos = permitido_ninnos,
                    piscina = piscina,
                    por_habitacion = por_habitacion,
                    provincia = provincia,
                    tipo_alojamiento = tipo_alojamiento,
                    transporte_aeropuerto = transporte_aeropuerto,
                    usuario = usuario,
                )
                # Si se ha podido crear el Alojamiento sin finalizar, se piden el resto de los datos del Alojamiento Completo
                if n_alojamiento_sin_finalizar:
                    return redirect('servicios:add_alojamiento_completo', n_alojamiento_sin_finalizar.id)
                else:
                    context = {
                        'form': Add_Alojamiento_Datos_Generales(provincias_cuba, request.POST),
                        'class_alert': 'alert alert-danger',
                        'message': 'No se han podido registrar los Datos Generales del Alojamiento',
                        'GMaps_APIKey': GMaps_APIKey,
                    }
                    context.update(custom_context(request))
                    return render(request, 'servicios/alojamientos/add_alojamiento.html', context)
        else:
            print(form.errors)
            context = {
                'form': Add_Alojamiento_Datos_Generales(provincias_cuba, request.POST),
                'class_alert': 'alert alert-danger',
                'message': 'Hay errores en el Formulario',
                'GMaps_APIKey': GMaps_APIKey,
            }
            context.update(custom_context(request))
            return render(request, 'servicios/alojamientos/add_alojamiento.html', context)
    else:
        context = {
            'form': Add_Alojamiento_Datos_Generales(provincias_cuba, ),
            'GMaps_APIKey': GMaps_APIKey,
        }
        context.update(custom_context(request))
        return render(request, 'servicios/alojamientos/add_alojamiento.html', context)

@login_required()
def add_alojamiento_completo(request, alojamiento_sin_finalizar_id):
    # Recupera el Alojamiento sin finalizar que se ha guardado
    alojamiento_sin_finalizar = Alojamiento_sin_finalizar.objects.get(id = alojamiento_sin_finalizar_id)

    if request.method == 'POST':
        # Caso en que el Alojamiento que se está registrando se alquile por habitacion y no completo
        form = Add_Alojamiento_Completo(request.POST)
        if form.is_valid():
            # Se crea el Alojamiento Completo con los datos guardados en el Alojamiento sin finalizar y los datos obtenidos ahora del formulario
            n_alojamiento_completo = Alojamiento_Completo.nuevo_alojamiento_completo(
                acceso_discapacitados = alojamiento_sin_finalizar.acceso_discapacitados,
                aire_acondicionado_central = form.cleaned_data['aire_acondicionado_central'], #__Form__
                cantidad_bannos = form.cleaned_data['cantidad_bannos'], #________________________Form__
                cantidad_habitaciones = alojamiento_sin_finalizar.cantidad_habitaciones,
                capacidad = form.cleaned_data['capacidad'], #____________________________________Form__
                cocina = form.cleaned_data['cocina'], #__________________________________________Form__
                codigo_postal = alojamiento_sin_finalizar.codigo_postal,
                desayuno_cena = alojamiento_sin_finalizar.desayuno_cena,
                descripcion = alojamiento_sin_finalizar.descripcion,
                direccion = alojamiento_sin_finalizar.direccion,
                latitud = alojamiento_sin_finalizar.latitud,
                longitud = alojamiento_sin_finalizar.longitud,
                estereo = form.cleaned_data['estereo'], #________________________________________Form__
                internet = alojamiento_sin_finalizar.internet,
                lavadora = form.cleaned_data['lavadora'], #______________________________________Form__
                municipio = alojamiento_sin_finalizar.municipio,
                nevera_bar = form.cleaned_data['nevera_bar'], #__________________________________________Form__
                nombre = alojamiento_sin_finalizar.nombre,
                pais = alojamiento_sin_finalizar.pais,
                parqueo = alojamiento_sin_finalizar.parqueo,
                patio_terraza_balcon = alojamiento_sin_finalizar.patio_terraza_balcon,
                permitido_fumar = alojamiento_sin_finalizar.permitido_fumar,
                permitido_mascotas = alojamiento_sin_finalizar.permitido_mascotas,
                permitido_ninnos = alojamiento_sin_finalizar.permitido_ninnos,
                piscina = alojamiento_sin_finalizar.piscina,
                por_habitacion = alojamiento_sin_finalizar.por_habitacion,
                precio_base = form.cleaned_data['precio_base'], #________________________________Form__
                provincia = alojamiento_sin_finalizar.provincia,
                tipo_alojamiento = alojamiento_sin_finalizar.tipo_alojamiento,
                transporte_aeropuerto = alojamiento_sin_finalizar.transporte_aeropuerto,
                tv = form.cleaned_data['tv'], #__________________________________________________Form__
                usuario = alojamiento_sin_finalizar.usuario,
            )
            # Si se han creado correctamente el Servicio, Alojamiento, y Alojamiento Completo relacionados, se elimina el Alojamiento sin finalizar actual
            if n_alojamiento_completo:
                # Se elimina el Alojamiento provisional (sin finalizar)
                alojamiento_sin_finalizar.delete()
                # Se redirige a la vista de administración del Alojamiento creado
                return redirect('servicios:administrar_alojamiento', n_alojamiento_completo.alojamiento.id)
            # Caso en que no se haya podido crear alguno de los elementos necesarios (Servicio, Alojamiento, Alojamiento_Completo)
            else:
                context = {
                    'form': Add_Alojamiento_Completo(request.POST),
                    'class_alert': 'alert alert-danger',
                    'message': 'No se ha podido crear el Alojamiento Completo con los datos que ha proporcionado'
                }
                context.update(custom_context(request))
                return render(request, 'servicios/alojamientos/add_alojamiento_completo.html', context)
        # Caso en que haya errores en el Formulario
        else:
            context = {
                'form': Add_Alojamiento_Completo(request.POST),
                'class_alert': 'alert alert-danger',
                'message': 'Hay errores en el formulario'
            }
            context.update(custom_context(request))
            return render(request, 'servicios/alojamientos/add_alojamiento_completo.html', context)
    # Caso en que la Página se carga sin hacer POST
    else:
        context = {
            'form': Add_Alojamiento_Completo(),
        }
        context.update(custom_context(request))
        return render(request, 'servicios/alojamientos/add_alojamiento_completo.html', context)

@login_required()
def modificar_alojamiento_por_habitacion(request, alojamiento_id):
    # Definición del Alojamiento
    alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = alojamiento_id)

    # Se definen las provincias que van a estar disponibles para seleccionar en el formulario. Solo pueden ser de Cuba
    provincias_cuba = []
    for provincia in Provincia.objects.filter(pais__nombre = 'CUBA').order_by('nombre'):
        provincias_cuba.append([provincia.id, provincia])

    # Cargar los datos actuales del Alojamiento
    datos_alojamiento_por_habitacion = {
        'acceso_discapacitados': alojamiento.acceso_discapacitados,
        'cantidad_habitaciones': alojamiento.cantidad_habitaciones,
        'codigo_postal': alojamiento.codigo_postal,
        'desayuno_cena': alojamiento.desayuno_cena,
        'descripcion': alojamiento.servicio.descripcion,
        'direccion': alojamiento.direccion,
        'internet': alojamiento.internet,
        'municipio': alojamiento.municipio,
        'nombre': alojamiento.servicio.nombre,
        'patio_terraza_balcon': alojamiento.patio_terraza_balcon,
        'parqueo': alojamiento.parqueo,
        'permitido_fumar': alojamiento.permitido_fumar,
        'permitido_mascotas': alojamiento.permitido_mascotas,
        'permitido_ninnos': alojamiento.permitido_ninnos,
        'piscina': alojamiento.piscina,
        'provincia': alojamiento.provincia.id,
        'tipo_alojamiento': alojamiento.tipo_alojamiento,
        'transporte_aeropuerto': alojamiento.transporte_aeropuerto,
    }
    if request.method == 'POST':
        form = Modificar_Alojamiento(provincias_cuba, request.POST)
        if form.is_valid():
            m_alojamiento_por_habitacion = alojamiento.modificar_alojamiento(
                acceso_discapacitados = form.cleaned_data['acceso_discapacitados'],
                cantidad_habitaciones = form.cleaned_data['cantidad_habitaciones'],
                codigo_postal = form.cleaned_data['codigo_postal'],
                desayuno_cena = form.cleaned_data['desayuno_cena'],
                descripcion = form.cleaned_data['descripcion'],
                direccion = form.cleaned_data['direccion'],
                internet = form.cleaned_data['internet'],
                municipio = form.cleaned_data['municipio'],
                nombre = form.cleaned_data['nombre'],
                patio_terraza_balcon = form.cleaned_data['patio_terraza_balcon'],
                parqueo = form.cleaned_data['parqueo'],
                permitido_fumar = form.cleaned_data['permitido_fumar'],
                permitido_mascotas = form.cleaned_data['permitido_mascotas'],
                permitido_ninnos = form.cleaned_data['permitido_ninnos'],
                piscina = form.cleaned_data['piscina'],
                provincia = Provincia.objects.get(id = form.cleaned_data['provincia']),
                tipo_alojamiento = form.cleaned_data['tipo_alojamiento'],
                transporte_aeropuerto = form.cleaned_data['transporte_aeropuerto'],
                latitud = request.POST.get('latitud'),
                longitud = request.POST.get('longitud'),

                precio_base = None,
            )
            if m_alojamiento_por_habitacion:
                context = {
                    'message': 'Ha modificado correctamente el Alojamiento',
                    'class_alert': 'alert alert-success',
                    'alojamiento': alojamiento,
                    'form': Modificar_Alojamiento(provincias_cuba, request.POST),
                    'GMaps_APIKey': GMaps_APIKey,
                }
                context.update(custom_context(request))
                return render(request, 'servicios/alojamientos/modificar_alojamiento_por_habitacion.html', context)
            else:
                context = {
                    'message': 'No se ha podido actualizar la información de su Alojamiento',
                    'class_alert': 'alert alert-danger',
                    'alojamiento': alojamiento,
                    'form': Modificar_Alojamiento(provincias_cuba, datos_alojamiento_por_habitacion),
                    'GMaps_APIKey': GMaps_APIKey,
                }
                context.update(custom_context(request))
                return render(request, 'servicios/alojamientos/modificar_alojamiento_por_habitacion.html', context)
        else:
            context = {
                'message': 'Hay errores en el Formulario',
                'class_alert': 'alert alert-danger',
                'alojamiento': alojamiento,
                'form': Modificar_Alojamiento(provincias_cuba, datos_alojamiento_por_habitacion),
                'GMaps_APIKey': GMaps_APIKey,
            }
            context.update(custom_context(request))
            return render(request, 'servicios/alojamientos/modificar_alojamiento_por_habitacion.html', context)
    else:
        context = {
            'alojamiento': alojamiento,
            'form': Modificar_Alojamiento(provincias_cuba, datos_alojamiento_por_habitacion),
            'GMaps_APIKey': GMaps_APIKey,
        }
        context.update(custom_context(request))
        return render(request, 'servicios/alojamientos/modificar_alojamiento_por_habitacion.html', context)

@login_required()
def modificar_alojamiento_completo(request, alojamiento_id):
    # Definición del Alojamiento
    alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = alojamiento_id)

    # Se definen las provincias que van a estar disponibles para seleccionar en el formulario. Solo pueden ser de Cuba
    provincias_cuba = []
    for provincia in Provincia.objects.filter(pais__nombre = 'CUBA').order_by('nombre'):
        provincias_cuba.append([provincia.id, provincia])

    # Cargar los datos actuales del Alojamiento
    datos_alojamiento_compelto = {
        'acceso_discapacitados': alojamiento.acceso_discapacitados,
        'aire_acondicionado_central': alojamiento.alojamiento_completo.aire_acondicionado_central,
        'cantidad_bannos': alojamiento.alojamiento_completo.cantidad_bannos,
        'cantidad_habitaciones': alojamiento.cantidad_habitaciones,
        'capacidad': alojamiento.alojamiento_completo.capacidad,
        'cocina': alojamiento.alojamiento_completo.cocina,
        'codigo_postal': alojamiento.codigo_postal,
        'desayuno_cena': alojamiento.desayuno_cena,
        'descripcion': alojamiento.servicio.descripcion,
        'direccion': alojamiento.direccion,
        'estereo': alojamiento.alojamiento_completo.estereo,
        'internet': alojamiento.internet,
        'lavadora': alojamiento.alojamiento_completo.lavadora,
        'municipio': alojamiento.municipio,
        'nevera_bar': alojamiento.alojamiento_completo.nevera_bar,
        'nombre': alojamiento.servicio.nombre,
        'patio_terraza_balcon': alojamiento.patio_terraza_balcon,
        'parqueo': alojamiento.parqueo,
        'permitido_fumar': alojamiento.permitido_fumar,
        'permitido_mascotas': alojamiento.permitido_mascotas,
        'permitido_ninnos': alojamiento.permitido_ninnos,
        'piscina': alojamiento.piscina,
        'precio_base': alojamiento.servicio.precio_base,
        'provincia': alojamiento.provincia.id,
        'servicio': alojamiento.servicio,
        'tipo_alojamiento': alojamiento.tipo_alojamiento,
        'transporte_aeropuerto': alojamiento.transporte_aeropuerto,
        'tv': alojamiento.alojamiento_completo.tv,
    }
    if request.method == 'POST':
        form = Modificar_Alojamiento_Completo(provincias_cuba, request.POST)
        if form.is_valid():

            # Se obtienen de los input hidden que capturan las coordenadas del Mapa la longitud y latitud del Alojamiento indicado por el usuario
            latitud = request.POST.get('latitud')
            longitud = request.POST.get('longitud')

            m_alojamiento_completo = alojamiento.alojamiento_completo.modificar_alojamiento_completo(
                acceso_discapacitados = form.cleaned_data['acceso_discapacitados'],
                aire_acondicionado_central = form.cleaned_data['aire_acondicionado_central'],
                cantidad_bannos = form.cleaned_data['cantidad_bannos'],
                cantidad_habitaciones = form.cleaned_data['cantidad_habitaciones'],
                capacidad = form.cleaned_data['capacidad'],
                cocina = form.cleaned_data['cocina'],
                codigo_postal = form.cleaned_data['codigo_postal'],
                desayuno_cena = form.cleaned_data['desayuno_cena'],
                descripcion = form.cleaned_data['descripcion'],
                direccion = form.cleaned_data['direccion'],
                estereo = form.cleaned_data['estereo'],
                internet = form.cleaned_data['internet'],
                lavadora = form.cleaned_data['lavadora'],
                municipio = form.cleaned_data['municipio'],
                nevera_bar = form.cleaned_data['nevera_bar'],
                nombre = form.cleaned_data['nombre'],
                parqueo = form.cleaned_data['parqueo'],
                patio_terraza_balcon = form.cleaned_data['patio_terraza_balcon'],
                permitido_fumar = form.cleaned_data['permitido_fumar'],
                permitido_mascotas = form.cleaned_data['permitido_mascotas'],
                permitido_ninnos = form.cleaned_data['permitido_ninnos'],
                piscina = form.cleaned_data['piscina'],
                precio_base = form.cleaned_data['precio_base'],
                provincia = Provincia.objects.get(id = form.cleaned_data['provincia']),
                tipo_alojamiento = form.cleaned_data['tipo_alojamiento'],
                transporte_aeropuerto = form.cleaned_data['transporte_aeropuerto'],
                tv = form.cleaned_data['tv'],

                latitud = latitud,
                longitud = longitud,
            )
            if m_alojamiento_completo:
                context = {
                    'message': 'Ha modificado correctamente el Alojamiento',
                    'class_alert': 'alert alert-success',
                    'alojamiento': alojamiento,
                    'form': Modificar_Alojamiento_Completo(provincias_cuba, request.POST),
                    'GMaps_APIKey': GMaps_APIKey,
                }
                context.update(custom_context(request))
                return render(request, 'servicios/alojamientos/modificar_alojamiento_completo.html', context)
            else:
                context = {
                    'message': 'No se ha podido actualizar la información de su Habitación',
                    'class_alert': 'alert alert-danger',
                    'alojamiento': alojamiento,
                    'form': Modificar_Alojamiento_Completo(provincias_cuba, datos_alojamiento_compelto),
                    'GMaps_APIKey': GMaps_APIKey,
                }
                context.update(custom_context(request))
                return render(request, 'servicios/alojamientos/modificar_alojamiento_completo.html', context)
        else:
            context = {
                'message': 'Hay errores en el Formulario',
                'class_alert': 'alert alert-danger',
                'alojamiento': alojamiento,
                'form': Modificar_Alojamiento_Completo(provincias_cuba, datos_alojamiento_compelto),
                'GMaps_APIKey': GMaps_APIKey,
            }
            context.update(custom_context(request))
            return render(request, 'servicios/alojamientos/modificar_alojamiento_completo.html', context)
    else:
        context = {
            'alojamiento': alojamiento,
            'form': Modificar_Alojamiento_Completo(provincias_cuba, datos_alojamiento_compelto),
            'GMaps_APIKey': GMaps_APIKey,
        }
        context.update(custom_context(request))
        return render(request, 'servicios/alojamientos/modificar_alojamiento_completo.html', context)

@login_required()
def administrar_habitacion_alojamiento_por_habitacion(request, habitacion_id):
    habitacion = Habitacion.objects.detalles_habitacion(id_habitacion = habitacion_id)

    # Esta valicación es para evitar que un usuario pueda acceder a esta vista de administración si la Habitación está cerrada
    if habitacion.cerrada:
        return redirect('servicios:administrar_alojamiento', habitacion.alojamiento.id)

    # Si la Habitación no está cerrada, entonces se puede Administrar
    context = {
        'habitacion': habitacion,
    }

    context.update(custom_context(request))
    return render(request, 'servicios/habitaciones/administrar_habitacion_alojamiento_por_habitacion.html', context)

@login_required()
def modificar_habitacion_alojamiento_por_habitacion(request, habitacion_id):
    # Definición del Alojamiento
    habitacion = Habitacion.objects.detalles_habitacion(id_habitacion = habitacion_id)

    # Cargar los datos actuales de la Habitación
    datos_habitacion = {
        'agua_caliente': habitacion.agua_caliente,
        'aire_acondicionado': habitacion.aire_acondicionado,
        'balcon': habitacion.balcon,
        'banno_independiente': habitacion.habitacion_alojamiento_por_habitacion.banno_independiente,
        'caja_fuerte': habitacion.caja_fuerte,
        'camas_dobles': habitacion.camas_dobles,
        'camas_individuales': habitacion.camas_individuales,
        'capacidad': habitacion.habitacion_alojamiento_por_habitacion.capacidad,
        'estereo': habitacion.estereo,
        'nevera_bar': habitacion.nevera_bar,
        'precio_base': habitacion.habitacion_alojamiento_por_habitacion.precio_base,
        'tv': habitacion.tv,
        'ventanas': habitacion.ventanas,
    }
    if request.method == 'POST':
        form = Modificar_Habitacion_Alojamiento_Por_Habitacion(request.POST)
        if form.is_valid():
            m_habitacion = habitacion.habitacion_alojamiento_por_habitacion.modificar_habitacion_alojamiento_por_habitacion(
                agua_caliente = form.cleaned_data['agua_caliente'],
                aire_acondicionado = form.cleaned_data['aire_acondicionado'],
                balcon = form.cleaned_data['balcon'],
                banno_independiente = form.cleaned_data['banno_independiente'],
                caja_fuerte = form.cleaned_data['caja_fuerte'],
                camas_dobles = form.cleaned_data['camas_dobles'],
                camas_individuales = form.cleaned_data['camas_individuales'],
                capacidad = form.cleaned_data['capacidad'],
                estereo = form.cleaned_data['estereo'],
                nevera_bar = form.cleaned_data['nevera_bar'],
                precio_base = form.cleaned_data['precio_base'],
                tv = form.cleaned_data['tv'],
                ventanas = form.cleaned_data['ventanas'],
            )
            if m_habitacion:
                context = {
                    'message': 'Ha modificado correctamente la Habitación',
                    'class_alert': 'alert alert-success',
                    'habitacion': habitacion,
                    'form': Modificar_Habitacion_Alojamiento_Por_Habitacion(request.POST),
                    'GMaps_APIKey': GMaps_APIKey,
                }
                context.update(custom_context(request))
                return render(request, 'servicios/habitaciones/modificar_habitacion_alojamiento_por_habitacion.html', context)
            else:
                context = {
                    'message': 'No se ha podido actualizar la información de su Habitación',
                    'class_alert': 'alert alert-danger',
                    'habitacion': habitacion,
                    'form': Modificar_Habitacion_Alojamiento_Por_Habitacion(datos_habitacion),
                    'GMaps_APIKey': GMaps_APIKey,
                }
                context.update(custom_context(request))
                return render(request, 'servicios/habitaciones/modificar_habitacion_alojamiento_por_habitacion.html', context)
        else:
            context = {
                'message': 'Hay errores en el Formulario',
                'class_alert': 'alert alert-danger',
                'habitacion': habitacion,
                'form': Modificar_Habitacion_Alojamiento_Por_Habitacion(datos_habitacion),
                'GMaps_APIKey': GMaps_APIKey,
            }
            context.update(custom_context(request))
            return render(request, 'servicios/habitaciones/modificar_habitacion_alojamiento_por_habitacion.html', context)
    else:
        context = {
            'habitacion': habitacion,
            'form': Modificar_Habitacion_Alojamiento_Por_Habitacion(datos_habitacion),
            'GMaps_APIKey': GMaps_APIKey,
        }
        context.update(custom_context(request))
        return render(request, 'servicios/habitaciones/modificar_habitacion_alojamiento_por_habitacion.html', context)

@login_required()
def modificar_habitacion(request, habitacion_id):
    # Definición del Alojamiento
    habitacion = Habitacion.objects.get(id = habitacion_id)
    alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = habitacion.alojamiento.id)

    # Cargar los datos actuales de la Habitación
    datos_habitacion = {
        'agua_caliente': habitacion.agua_caliente,
        'aire_acondicionado': habitacion.aire_acondicionado,
        'balcon': habitacion.balcon,
        'caja_fuerte': habitacion.caja_fuerte,
        'camas_dobles': habitacion.camas_dobles,
        'camas_individuales': habitacion.camas_individuales,
        'estereo': habitacion.estereo,
        'nevera_bar': habitacion.nevera_bar,
        'tv': habitacion.tv,
        'ventanas': habitacion.ventanas,
    }
    if request.method == 'POST':
        form = Modificar_Habitacion_Alojamiento_Completo(request.POST)
        if form.is_valid():
            m_habitacion = habitacion.modificar_habitacion(
                agua_caliente = form.cleaned_data['agua_caliente'],
                aire_acondicionado = form.cleaned_data['aire_acondicionado'],
                balcon = form.cleaned_data['balcon'],
                caja_fuerte = form.cleaned_data['caja_fuerte'],
                camas_dobles = form.cleaned_data['camas_dobles'],
                camas_individuales = form.cleaned_data['camas_individuales'],
                estereo = form.cleaned_data['estereo'],
                nevera_bar = form.cleaned_data['nevera_bar'],
                tv = form.cleaned_data['tv'],
                ventanas = form.cleaned_data['ventanas'],
            )
            if m_habitacion:
                context = {
                    'message': 'Ha modificado correctamente la Habitación',
                    'class_alert': 'alert alert-success',
                    'habitacion': habitacion,
                    'alojamiento': alojamiento,
                    'form': Modificar_Habitacion_Alojamiento_Completo(request.POST),
                }
                context.update(custom_context(request))
                return render(request, 'servicios/habitaciones/modificar_habitacion.html', context)
            else:
                context = {
                    'message': 'No se ha podido actualizar la información de su Habitación',
                    'class_alert': 'alert alert-danger',
                    'habitacion': habitacion,
                    'alojamiento': alojamiento,
                    'form': Modificar_Habitacion_Alojamiento_Completo(datos_habitacion),
                }
                context.update(custom_context(request))
                return render(request, 'servicios/habitaciones/modificar_habitacion.html', context)
        else:
            context = {
                'message': 'Hay errores en el Formulario',
                'class_alert': 'alert alert-danger',
                'habitacion': habitacion,
                'alojamiento': alojamiento,
                'form': Modificar_Habitacion_Alojamiento_Completo(datos_habitacion),
            }
            context.update(custom_context(request))
            return render(request, 'servicios/habitaciones/modificar_habitacion.html', context)
    else:
        context = {
            'habitacion': habitacion,
            'alojamiento': alojamiento,
            'form': Modificar_Habitacion_Alojamiento_Completo(datos_habitacion),
        }
        context.update(custom_context(request))
        return render(request, 'servicios/habitaciones/modificar_habitacion.html', context)

@login_required()
def eliminar_habitacion(request, habitacion_id):
    # Eiminar una habitación implica eliminar todas las fotos asociadas a la misma, así como los ficheros relacionados con estas
    # 1 - Determinar el Alojamiento (y tipo) relacionado con la Habitación: Servirá para redireccionar a la vista de administrar Alojamiento luego de eliminar a Habitación
    # 2 - Si la Habitación pertenece a un Alojamiento que se alquia completo, no tiene mayores implicaciones. Si el Alojamiento se alquila por Habitaciones, hay que:
    #   2.1 - Eliminar todos los objetos de Fotos de Habitaciones asociados
    #   2.2 - Eliminar todos los ficheros de Fotos asociados
    #   2.3 - Eliminar todos los directorios asociados
    habitacion = Habitacion.objects.get(id = habitacion_id)
    alojamiento = habitacion.alojamiento
    habitacion.eliminar_habitacion()

    # Una vez eliminada la Habitación y lo que implicaba, se redirige a la página de Administración del Alojamiento al que pertenecía
    return redirect('servicios:administrar_alojamiento', alojamiento.id)

def add_habitacion_carro(request):
    # todo: Añadir una habitación al carrito de la compra
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required()
def eliminar_foto_habitacion(request, foto_habitacion_id):
    foto_habitacion = Foto_Habitacion.objects.get(id = foto_habitacion_id)
    foto_habitacion.eliminar_foto_habitacion()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required()
def eliminar_foto_servicio(request, foto_servicio_id):
    foto_servicio = Foto_Servicio.objects.get(id = foto_servicio_id)
    foto_servicio.foto.delete()
    foto_servicio.delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required()
def eliminar_alojamiento(request, alojamiento_id):
    # Determinar el Objeto Alojamiento y llamar al método que se encarga de su eliminación
    Alojamiento.objects.get(id = alojamiento_id).eliminar_alojamiento()
    return redirect('servicios:mis_servicios')

def eliminar_alojamiento_sin_finalizar(request, alojamiento_sin_finalizar_id):
    alojamiento_sin_finalizar = Alojamiento_sin_finalizar.objects.get(id = alojamiento_sin_finalizar_id)
    alojamiento_sin_finalizar.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required()
def fotos_habitacion(request, habitacion_id):
    habitacion = Habitacion.objects.get(id = habitacion_id)

    max_fotos = range(habitacion.max_fotos - 1)
    fotos_habitacion = habitacion.foto_habitacion_set.all()
    cantidad_fotos_habitacion = len(fotos_habitacion)

    show_fotos = []
    for foto in max_fotos:
        if cantidad_fotos_habitacion <= foto:
            show_fotos.append('template')
        else:
            show_fotos.append(fotos_habitacion[foto])

    # Definición del Orden y Completamiento de los Pasos a mostrar en el Template
    # Varía dinámicamente según la cantidad de Habitaciones que se hayan registrado ya
    if request.method == 'POST':
        form = Foto_Habitacion_Form(request.POST)
        if form.is_valid():
            if request.FILES:
                # Se lee si viene algun campo llamado "foto" del formulario
                foto = request.FILES['foto']
                n_foto_habitacion = Foto_Habitacion.nueva_foto_habitacion(habitacion, foto)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            context = {
                'message': 'Hay errores en el formulario',
                'class_alert': 'alert alert-danger',
                'form': Foto_Habitacion_Form(request.POST),
                'habitacion': habitacion,
                'fotos_habitacion': fotos_habitacion,
                'show_fotos': show_fotos,
            }
            context.update(custom_context(request))
            return render(request, 'servicios/habitaciones/fotos_habitacion.html', context)
    else:
        context = {
            'form': Foto_Habitacion_Form(),
            'habitacion': habitacion,
            'fotos_habitacion': fotos_habitacion,
            'show_fotos': show_fotos,
        }
        context.update(custom_context(request))
        return render(request, 'servicios/habitaciones/fotos_habitacion.html', context)

@login_required
def fotos_servicio(request, servicio_id):
    servicio = Servicio.objects.get(id = servicio_id)
    photos_rows = servicio.get_photos_rows(columns = 4)

    if servicio.max_fotos == len(servicio.foto_servicio_set.all()):
        max_photos = True
    else:
        max_photos = False

    if request.method == 'POST':
        form = Foto_Servicio_Form(request.POST)
        if form.is_valid():
            if request.FILES:
                # Se lee si viene algun campo llamado "foto" del formulario
                foto = request.FILES['foto']
                Foto_Servicio.nueva_foto_servicio(servicio, foto)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            context = {
                'message': 'Hay errores en el formulario',
                'class_alert': 'alert alert-danger',
                'form': Foto_Servicio_Form(request.POST),
                'servicio': servicio,
                'photos_rows': photos_rows,
                'max_photos': max_photos,
            }
            context.update(custom_context(request))
            return render(request, 'servicios/servicios/fotos_servicio.html', context)
    else:
        context = {
            'form': Foto_Servicio_Form(),
            'servicio': servicio,
            'photos_rows': photos_rows,
            'max_photos': max_photos,
        }
        context.update(custom_context(request))
        return render(request, 'servicios/servicios/fotos_servicio.html', context)

@login_required
def video_servicio(request, servicio_id):
    servicio = Servicio.objects.get(id = servicio_id)

    message, class_alert = None, None

    if request.method == 'POST':
        form = URL_Video_Form(request.POST)
        if form.is_valid():
            url_video = form.cleaned_data['url_video']
            result = servicio.set_url_video(url_video = url_video)
            if not isinstance(result, dict):
                message = 'Se ha asociado correctamente el video al Servicio'
                class_alert = 'alert alert-success'
            else:
                message = result['message']
                class_alert = 'alert alert-danger'
        else:
            message = 'Hay errores en el Formulario'
            class_alert = 'alert alert-danger'
    else:
        form = URL_Video_Form()

    context = {
        'message': message,
        'class_alert': class_alert,
        'servicio': servicio,
        'form': form,
    }

    context.update(custom_context(request))
    return render(request, 'servicios/servicios/video_servicio.html', context)

@login_required
def eliminar_video_servicio(request, servicio_id):
    servicio = Servicio.objects.get(id = servicio_id)
    servicio.eliminar_url_video()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def administrar_servicio(request, servicio_id):
    servicio = Servicio.objects.get(id = servicio_id)
    # Se comprueba cada uno de los diferentes tipos de Servicios existentes y según sea el caso se redirige a la página de Administración correspondiente
    # 1 - Alojamiento
    if servicio.alojamiento:
        return redirect('servicios:administrar_alojamiento', servicio.alojamiento.id)
    # 2 - Recorrido
    elif servicio.recorrido:
        return redirect('servicios:administrar_recorrido', servicio.recorrido.id)
    # 3 - Taxi
    elif servicio.taxi:
        return redirect('servicios:administrar_taxi', servicio.taxi.id)
    # Pack
    elif servicio.pack:
        return redirect('servicio:administrar_pack', servicio.pack.id)

@login_required()
def administrar_recorrido(request, recorrido_id):
    recorrido = Recorrido.objects.get(id = recorrido_id)
    context = {

    }
    context.update(custom_context(request))
    return render(request, 'servicios/recorridos/administrar_recorrido.html', context)

@login_required()
def administrar_taxi(request, taxi_id):
    taxi = Taxi.objects.get(id = taxi_id)
    context = {

    }
    context.update(custom_context(request))
    return render(request, 'servicios/taxis/administrar_taxi.html', context)

@login_required()
def administrar_pack(request, pack_id):
    pack = Pack.objects.get(id = pack_id)
    context = {

    }
    context.update(custom_context(request))
    return render(request, 'servicios/packs/administrar_pack.html', context)

def evaluaciones_servicio(request, servicio_id):
    servicio = Servicio.objects.detalles_servicio(servicio_id = servicio_id)
    context = {
        'evaluaciones': servicio.evaluaciones,
        'servicio': servicio,
    }
    context.update(custom_context(request))
    return render(request, 'servicios/servicios/evaluaciones.html', context)

def detalles_alojamiento(request, alojamiento_id):
    alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = alojamiento_id)
    # Cada vez que se accede a los detalles de un Alojamiento, se incrementa en una las visualizaciones del servicio
    alojamiento.servicio.new_visualization()
    if alojamiento.servicio.cerrado:
        # Guardamos la página actual en la session para poder ofrecer al usuario la posibilidad de regresar atrás sea cual sea la página
        # request.session['actual_url'] = request.get_full_path()
        return redirect('servicios:servicio_cerrado', alojamiento.servicio.id)

    elif alojamiento.por_habitacion:
        return redirect('servicios:detalles_alojamiento_por_habitacion', alojamiento_id)
    else:
        return redirect('servicios:detalles_alojamiento_completo', alojamiento_id)

@login_required
def administrar_reglas_precio(request, elemento, id):
    if elemento == 'servicio':
        servicio = Servicio.objects.detalles_servicio(servicio_id = id)
        reglas_precio = servicio.reglas_precio
        habitacion = None
        alojamiento = servicio.alojamiento
    elif elemento == 'habitacion':
        servicio = None
        habitacion = Habitacion.objects.get(id = id)
        reglas_precio = habitacion.regla_precio_set.all()
        alojamiento = habitacion.alojamiento
    else:
        servicio = None
        habitacion = None
        alojamiento = None
        reglas_precio = None

    if request.method == 'POST':
        # Caso en que se realiza POST para añadir una nueva regla de precio
        if 'add_regla_precio' in request.POST:
            form = Add_Regla_Precio(request.POST)
            if form.is_valid():
                n_regla_precio = Regla_Precio.nueva_regla_precio(
                    servicio = servicio,
                    habitacion = habitacion,
                    fecha_desde = meses[form.cleaned_data['fecha_desde']],
                    fecha_hasta = meses[form.cleaned_data['fecha_hasta']],
                    precio = form.cleaned_data['precio'],
                )

                if isinstance(n_regla_precio, dict):
                    context = {
                        'form': Add_Regla_Precio(),
                        'servicio': servicio,
                        'habitacion': habitacion,
                        'alojamiento': alojamiento,
                        'reglas_precio': reglas_precio,
                        'class_alert': 'alert alert-danger',
                        'message': n_regla_precio['message'],
                    }

                elif n_regla_precio:
                    context = {
                        'form': Add_Regla_Precio(),
                        'servicio': servicio,
                        'habitacion': habitacion,
                        'alojamiento': alojamiento,
                        'reglas_precio': reglas_precio,
                        'class_alert': 'alert alert-success',
                        'message': 'Se ha creado correctamente la Regla de Precio',
                    }
                else:
                    context = {
                        'form': Add_Regla_Precio(),
                        'servicio': servicio,
                        'habitacion': habitacion,
                        'alojamiento': alojamiento,
                        'reglas_precio': reglas_precio,
                        'class_alert': 'alert alert-danger',
                        'message': 'No se ha podido crear la Regla de Precio',
                    }

                context.update(custom_context(request))
                return render(request, 'servicios/servicios/reglas_precio.html', context)
            else:
                context = {
                    'form': Add_Regla_Precio(),
                    'servicio': servicio,
                    'habitacion': habitacion,
                    'alojamiento': alojamiento,
                    'reglas_precio': reglas_precio,
                    'class_alert': 'alert alert-danger',
                    'message': 'Hay errores en el Formulario',
                }

                context.update(custom_context(request))
                return render(request, 'servicios/servicios/reglas_precio.html', context)


        # Se asume que existe 'modificar_regla_precio' en el request.POST
        # Si quisiéramos manejar más de dos posibilidades de POST, usaríamos elif
        else:
            regla_precio, fecha_desde, fecha_hasta, precio = [None, None, None, None]
            for post_element in request.POST:
                if 'fecha_desde_regla_precio' in post_element:
                    fecha_desde = meses[request.POST[post_element]]
                    regla_precio = Regla_Precio.objects.get(id = post_element.split('_')[-1])
                elif 'fecha_hasta_regla_precio' in post_element:
                    fecha_hasta = meses[request.POST[post_element]]
                elif 'precio_regla_precio' in post_element:
                    precio = request.POST[post_element]

            if not None in [regla_precio, fecha_desde, fecha_hasta, precio]:
                m_regla_precio = regla_precio.modificar_regla_precio(
                    fecha_desde = fecha_desde,
                    fecha_hasta = fecha_hasta,
                    precio = precio,
                )

                if isinstance(m_regla_precio, dict):
                    context = {
                        'form': Add_Regla_Precio(),
                        'servicio': servicio,
                        'habitacion': habitacion,
                        'alojamiento': alojamiento,
                        'reglas_precio': reglas_precio,
                        'class_alert': 'alert alert-danger',
                        'message': m_regla_precio['message'],
                    }
                else:
                    context = {
                        'form': Add_Regla_Precio(),
                        'servicio': servicio,
                        'habitacion': habitacion,
                        'alojamiento': alojamiento,
                        'reglas_precio': reglas_precio,
                        'class_alert': 'alert alert-success',
                        'message': 'Se ha modificado correctamente la Regla de Precio',
                    }

                context.update(custom_context(request))
                return render(request, 'servicios/servicios/reglas_precio.html', context)
            else:
                context = {
                    'form': Add_Regla_Precio(),
                    'servicio': servicio,
                    'habitacion': habitacion,
                    'alojamiento': alojamiento,
                    'reglas_precio': reglas_precio,
                    'class_alert': 'alert alert-danger',
                    'message': 'No se ha podido modificar la Regla de Precio',
                }

                context.update(custom_context(request))
                return render(request, 'servicios/servicios/reglas_precio.html', context)
    else:
        context = {
            'form': Add_Regla_Precio(),
            'servicio': servicio,
            'habitacion': habitacion,
            'alojamiento': alojamiento,
            'reglas_precio': reglas_precio,
        }

        context.update(custom_context(request))
        return render(request, 'servicios/servicios/reglas_precio.html', context)

@login_required
def administrar_disponibilidades(request, elemento, id):
    if elemento == 'servicio':
        servicio = Servicio.objects.detalles_servicio(servicio_id = id)
        alojamiento = servicio.alojamiento
        habitacion = None
        indisponibilidades = servicio.indisponibilidad_set.order_by('fecha_desde')

    elif elemento == 'habitacion':
        servicio = None
        habitacion = Habitacion.objects.get(id = id)
        alojamiento = habitacion.alojamiento
        indisponibilidades = habitacion.indisponibilidad_set.order_by('fecha_desde')

    else:
        servicio = None
        habitacion = None
        alojamiento = None
        indisponibilidades = None

    if request.method == 'POST':
        # Caso en que se realiza POST para añadir una nueva indisponibilidad
        if 'add_indisponibilidad' in request.POST:
            form = Add_Indisponibilidad(request.POST)
            if form.is_valid():
                n_indisponibilidad = Indisponibilidad.nueva_indisponibilidad(
                    servicio = servicio,
                    habitacion = habitacion,
                    fecha_desde = form.cleaned_data['fecha_desde'],
                    fecha_hasta = form.cleaned_data['fecha_hasta'],
                )

                if isinstance(n_indisponibilidad, dict):
                    context = {
                        'form': Add_Indisponibilidad(),
                        'servicio': servicio,
                        'habitacion': habitacion,
                        'alojamiento': alojamiento,
                        'indisponibilidades': indisponibilidades,
                        'class_alert': 'alert alert-danger',
                        'message': n_indisponibilidad['message'],
                    }

                elif n_indisponibilidad:
                    context = {
                        'form': Add_Indisponibilidad(),
                        'servicio': servicio,
                        'habitacion': habitacion,
                        'alojamiento': alojamiento,
                        'indisponibilidades': indisponibilidades,
                        'class_alert': 'alert alert-success',
                        'message': 'Se ha creado correctamente la Indisponibilidad',
                    }
                else:
                    context = {
                        'form': Add_Indisponibilidad(),
                        'servicio': servicio,
                        'habitacion': habitacion,
                        'alojamiento': alojamiento,
                        'indisponibilidades': indisponibilidades,
                        'class_alert': 'alert alert-danger',
                        'message': 'No se ha podido crear la Indisponibilidad',
                    }

                context.update(custom_context(request))
                return render(request, 'servicios/servicios/indisponibilidades.html', context)
            else:
                context = {
                    'form': Add_Indisponibilidad(),
                    'servicio': servicio,
                    'habitacion': habitacion,
                    'alojamiento': alojamiento,
                    'indisponibilidades': indisponibilidades,
                    'class_alert': 'alert alert-danger',
                    'message': 'Hay errores en el Formulario',
                }

                context.update(custom_context(request))
                return render(request, 'servicios/servicios/indisponibilidades.html', context)


        # Se asume que existe 'modificar_indisponibilidad' en el request.POST
        # Si quisiéramos manejar más de dos posibilidades de POST, usaríamos elif
        else:
            indisponibilidad, fecha_desde, fecha_hasta = [None, None, None]
            for post_element in request.POST:
                if 'fecha_desde_indisponibilidad' in post_element:
                    fecha_desde = request.POST[post_element]
                    indisponibilidad = Indisponibilidad.objects.get(id = post_element.split('_')[-1])
                elif 'fecha_hasta_indisponibilidad' in post_element:
                    fecha_hasta = request.POST[post_element]

            if not None in [indisponibilidad, fecha_desde, fecha_hasta]:
                m_indisponibilidad = indisponibilidad.modificar_indisponibilidad(
                    fecha_desde = fecha_desde,
                    fecha_hasta = fecha_hasta,
                )

                if isinstance(m_indisponibilidad, dict):
                    context = {
                        'form': Add_Indisponibilidad(),
                        'servicio': servicio,
                        'habitacion': habitacion,
                        'alojamiento': alojamiento,
                        'indisponibilidades': indisponibilidades,
                        'class_alert': 'alert alert-danger',
                        'message': m_indisponibilidad['message'],
                    }
                else:
                    context = {
                        'form': Add_Indisponibilidad(),
                        'servicio': servicio,
                        'habitacion': habitacion,
                        'alojamiento': alojamiento,
                        'indisponibilidades': indisponibilidades,
                        'class_alert': 'alert alert-success',
                        'message': 'Se ha modificado correctamente la Indisponibilidad',
                    }

                context.update(custom_context(request))
                return render(request, 'servicios/servicios/indisponibilidades.html', context)
            else:
                context = {
                    'form': Add_Indisponibilidad(),
                    'servicio': servicio,
                    'habitacion': habitacion,
                    'alojamiento': alojamiento,
                    'indisponibilidades': indisponibilidades,
                    'class_alert': 'alert alert-danger',
                    'message': 'No se ha podido modificar la Indisponibilidad',
                }

                context.update(custom_context(request))
                return render(request, 'servicios/servicios/indisponibilidades.html', context)
    else:
        context = {
            'form': Add_Indisponibilidad(),
            'servicio': servicio,
            'habitacion': habitacion,
            'alojamiento': alojamiento,
            'indisponibilidades': indisponibilidades,
        }

        context.update(custom_context(request))
        return render(request, 'servicios/servicios/indisponibilidades.html', context)

def detalles_alojamiento_por_habitacion(request, alojamiento_id):
    cc = custom_context(request)

    # Inicialmente se definen unas fechas por defecto para llevar a cabo el análisis de disponibilidad de las Habitaciones
    fecha_entrada = datetime.date.today() + datetime.timedelta(days = 3)
    fecha_salida = datetime.date.today() + datetime.timedelta(days = 10)

    alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = alojamiento_id)

    # Lo primero que se hace en esta vista es determinar el estado de Favorito del Servicio
    # Para determinar si el Alojamiento pertenece a un Servicio seleccionado como Favorito por el usuario, hay que considerar dos escenarios:
    # 1 - El usuario se encuentra registrado en el sistema, con lo cual se realiza una consulta a los favoritos en la BD
    if cc['usuario']:
        favorito = cc['usuario'].check_favorito(servicio_id = alojamiento.servicio.id)
    # 2 - El usuario es aún anónimo, con lo cual la información de sus favoritos (además de intención de compra, etc) se almacena en la sesión del navegador
    # Se comprueba que exista algún favorito registrado en la sesion
    elif str(alojamiento.servicio.id) in cc['favoritos']:
        favorito = True
    else:
        favorito = False

    # Después se analiza el comportamiento de la página ante las consultas
    if request.method == 'POST':
        form = Consultar_Disponibilidad_Alojamiento_Por_Habitacion(request.POST)

        # Se valida que el formulario tiene valores correctos
        if form.is_valid():

            if 'reservar' in request.POST:
                # En este caso se ha configurado una combinación de Adultos Niños para al menos una habitación del Alojamiento y se desea reservar
                fecha_entrada = form.cleaned_data['fecha_entrada']
                fecha_salida = form.cleaned_data['fecha_salida']

                reservas = {}
                for post_element in request.POST:
                    if 'habitacion_' in post_element:
                        # Si se encuentra el fragmento de cadena "habitacion_" es un input con información de reserva
                        # Lo primero es determinar el ID de la Habitación y la cantidad de niños o adultos del elemento
                        id_habitacion = int(post_element.split('_')[1]) # ID de la Habitación
                        # Comprobando si se trata de el input de niños
                        if '_ninnos' in post_element:
                            # Si es el caso, se obtiene el número de niños indicados por el usuario
                            ninnos = request.POST[post_element]
                            # Primero se valida que el campo no se haya recibido en blanco
                            if ninnos != '':
                                # Si hay algún valor en el campo, se comprueba que este sea un número
                                try:
                                    ninnos = int(ninnos)
                                    # Si se puede convertir el valor recibido en un entero, entonces se comprueba que este sea mayor que cero
                                    if ninnos <= 0:
                                        # Si se ha introducido un número pero este es menos o igual que cero, no se asume valor alguno
                                        # Así que se establece el 0 que es igual que si hubiera estado en blanco el campo
                                        ninnos = 0
                                except:
                                    # Si el valor introducido no es un número entero, entonces ninnos se setea a 0
                                    ninnos = 0
                            else:
                                # Si el campo está vacío, entonces ninnos = 0
                                ninnos = 0
                            # Cualquiera sea la situación con el valor de ninnos en el formulario, lo seguro es que adultos = 0
                            # debido a que se encontró la cadena "_ninnos" en el name del elemento del post que se está analizando
                            adultos = 0
                            # En este punto ninnos es o bien 0, o bien un entero positivo que haya indicado el usuario en el formulario

                        # Si se encuentra "_habitacion" en el elemento del POST pero no se encuentra "_ninnos", entonces se trata de un campo de adultos
                        # Deberíamos encontrar "_adultos" en el name del elemento del POST
                        elif '_adultos' in post_element:
                            # Si es el caso, se obtiene el número de adultos indicados por el usuario
                            adultos = request.POST[post_element]
                            # Primero se valida que el campo no se haya recibido en blanco
                            if adultos != '':
                                # Si hay algún valor en el campo, se comprueba que este sea un número
                                try:
                                    adultos = int(adultos)
                                    # Si se puede convertir el valor recibido en un entero, entonces se comprueba que este sea mayor que cero
                                    if adultos <= 0:
                                        # Si se ha introducido un número pero este es menos o igual que cero, no se asume valor alguno
                                        # Así que se establece el 0 que es igual que si hubiera estado en blanco el campo
                                        adultos = 0
                                except:
                                    # Si el valor introducido no es un número entero, entonces adultos se setea a 0
                                    adultos = 0
                            else:
                                # Si el campo está vacío, entonces adultos = 0
                                adultos = 0
                            # Cualquiera sea la situación con el valor de adultos en el formulario, lo seguro es que ninnos = 0
                            # debido a que se encontró la cadena "_adultos" en el name del elemento del post que se está analizando
                            ninnos = 0
                            # En este punto adultos es o bien 0, o bien un entero positivo que haya indicado el usuario en el formulario
                        else:
                            # Si se encuentra "_habitacion" en el name del elemento, pero no "_ninnos" ni "_adultos", entonces ambos se establecen en 0
                            # Pero debe advertirse de un error puesto que debería haberse encontrado una u otra cadena de caracteres (_ninnos o _adultos)
                            # Como no hay información útil de cantidades se pasa al siguiente elemento del POST
                            print('El request_element no tenía ni adultos ni ninnos lo cual es un Error. Revisar esto')
                            adultos = 0
                            ninnos = 0
                            continue

                        # Habiendo terminado de analizar el elemento del POST, y teniendo el id de la Habitación, así como una cantidad para ninnos y adultos
                        # Se analiza si alguno de estos es mayor que cero, y en ese caso; si se crea un nuevo diccionario con información de la Reserva
                        # O si se actualiza uno ya existente creado anteriormente
                        if ninnos > 0 or adultos > 0:

                            # Comprobar si ya se ha creado previamente un diccionario con información de Reserva para una Habitación con el mismo ID
                            if id_habitacion in reservas:
                                # Si ya se ha creado antes, entonces se actualizan las cantidades de niños y adultos
                                reservas[id_habitacion]['ninnos'] += ninnos
                                reservas[id_habitacion]['adultos'] += adultos
                            else:
                                # Si no, se crea el diccionario con la información obtenida
                                reservas[id_habitacion] = {
                                    'ninnos': ninnos,
                                    'adultos': adultos,
                                }
                        else:
                            # Si ambas cantidades (ninnos y adultos) son igual a 0, se pasa entonces al siguiente elemento del POST
                            continue
                    else:
                        # Si no se encuentra "_habitacion" en el name del elemento, no es de interés pues no aporta información de reserva
                        continue

                # En este punto se crea una Reserva con la información recogida.
                # Hay dos posibles escenarios (El usuario se encuentra autenticado o no se encuentra autenticado)
                # Si el usuario se encuentra autenticado:
                if cc['usuario']:
                    n_reserva_servicio = Reserva.nueva_reserva_servicio(
                        servicio = alojamiento.servicio,
                        initial_date = fecha_entrada,
                        final_date = fecha_salida,
                        usuario = cc['usuario'],
                    )

                    for reserva in reservas:
                        # Se obtienen los objetos Habitación y Precio para las fechas indicadas (Una vez eliminados del diccionario los elementos que no usaremos aquí)
                        habitacion = Habitacion.objects.get(id = reserva)

                        precio, comision = habitacion.alojamiento.servicio.get_precio_comision_fechas(
                            fecha_entrada = fecha_entrada,
                            fecha_salida = fecha_salida,
                            habitacion = habitacion,
                        )

                        n_reserva_habitacion = Reserva_Habitacion.nueva_reserva_habitacion(
                            reserva = n_reserva_servicio,
                            habitacion = habitacion,
                            ninnos = reservas[reserva]['ninnos'],
                            adultos = reservas[reserva]['adultos'],
                            precio = precio,
                            comision = comision,
                        )

                    # Se determina la información restante de precios globales de la Reserva
                    n_reserva_servicio.set_precio_from_habitaciones()

                    # A continuación, se redirige al usuario a la página de checkout para mostrar la información de pago y proceder a confirmar el mismo
                    return redirect('servicios:checkout_alojamiento_por_habitacion', reserva_id = n_reserva_servicio.id)

                # Si por el contrario, la reserva la está realizando un usuario anónimo:
                else:
                    # Se crea el diccionario con la información genérica de la reserva que se tiene hasta el momento
                    reserva_servicio = {
                        'servicio_id': alojamiento.servicio.id,
                        'alojamiento_id': alojamiento.id,
                        'initial_date': fecha_entrada,
                        'final_date': fecha_salida,
                        'fecha_creacion': datetime.date.today(),
                        # La firma de tiempo (timestamp) es una combinación de la fecha y hora exactas de su registro, con el id del servicio y un identificador único de la sesión
                        'timestamp': '%s%s%s' %(str(request.session.__dict__['_SessionBase__session_key']), str(datetime.datetime.now()).replace('-', '').replace(' ', '').replace(':', '').replace('.', ''), str(alojamiento.servicio.id))
                    }

                    # Ahora se crean los diccionarios con la información de la reserva de caha habitación el Alojamiento
                    precio_total = 0
                    comision_total = 0
                    for reserva in reservas:
                        # Se obtienen los objetos Habitación y Precio para las fechas indicadas (Una vez eliminados del diccionario los elementos que no usaremos aquí)
                        habitacion = Habitacion.objects.get(id = reserva)
                        precio, comision = habitacion.alojamiento.servicio.get_precio_comision_fechas(
                            fecha_entrada = fecha_entrada,
                            fecha_salida = fecha_salida,
                            habitacion = habitacion,
                        )

                        # Se va añadiendo al precio de la Reserva del Servicio el precio de la Resevra de cada Habitación así como la Comisión
                        precio_total += precio
                        comision_total += comision

                        reserva_habitacion = {
                            'ninnos': reservas[reserva]['ninnos'],
                            'adultos': reservas[reserva]['adultos'],
                            'precio': str(round(float(precio), 2)),
                            'capacidad': habitacion.habitacion_alojamiento_por_habitacion.capacidad,
                        }
                        # Se relaciona la información de reserva de la Habitación con la Reserva del Servicio
                        reserva_servicio[reserva] = reserva_habitacion

                    # Se añade información adicional al diccionario de la reserva
                    reserva_servicio = Reserva.objects.detalles_reserva(id = None, reserva_servicio = reserva_servicio)

                    # Se determina la información restante de precios globales de la Reserva
                    reserva_servicio['precio_servicio'] = str(round(float(precio_total), 2))
                    reserva_servicio['comision'] = str(round(float(comision_total), 2))
                    reserva_servicio['total_a_pagar'] = str(round(float(reserva_servicio['costo_gestion'] + precio_total + reserva_servicio['impuestos']), 2))
                    reserva_servicio['pago_online'] = str(round(float(comision_total + reserva_servicio['costo_gestion'] + reserva_servicio['impuestos']), 2))
                    reserva_servicio['pago_offline'] = str(round(float((reserva_servicio['costo_gestion'] + precio_total + reserva_servicio['impuestos']) - (comision_total + reserva_servicio['costo_gestion'] + reserva_servicio['impuestos'])), 2))
                    reserva_servicio['costo_gestion'] = str(round(float(reserva_servicio['costo_gestion']), 2))
                    reserva_servicio['impuestos'] = str(round(float(reserva_servicio['impuestos']), 2))
                    reserva_servicio['initial_date'] = str(reserva_servicio['initial_date'])
                    reserva_servicio['final_date'] = str(reserva_servicio['final_date'])
                    reserva_servicio['fecha_creacion'] = str(reserva_servicio['fecha_creacion'])
                    reserva_servicio['timestamp'] = str(reserva_servicio['timestamp'])

                    # Una vez se tiene toda la información de la Reserva, esta se almacena en la sesión y se procede al checkout
                    if 'en_el_carro' in request.session:
                        # Si ya existe alguna reserva de servicio guardada previamente en la sesión, se añade uan nueva
                        en_el_carro = request.session['en_el_carro']
                        en_el_carro.append(reserva_servicio)
                        del request.session['en_el_carro']
                        request.session['en_el_carro'] = en_el_carro
                    else:
                        # En caso contrario se crea la lista y se le añade el diccionario actual
                        request.session['en_el_carro'] = [reserva_servicio,]

                    return redirect('servicios:checkout_alojamiento_por_habitacion_servicio', servicio_id = alojamiento.servicio.id)
            else:
                # En este caso la consulta es para la disponibilidad de las habitaciones en las fechas indicadas en el calendario del formulario
                fecha_entrada = form.cleaned_data['fecha_entrada']
                fecha_salida = form.cleaned_data['fecha_salida']

                # Se definen las habitaciones que están disponibles en las fechas indicadas
                habitaciones_disponibles = alojamiento.get_habitaciones_disponibles(
                    fecha_entrada = fecha_entrada,
                    fecha_salida = fecha_salida,
                )

                context = {
                    'form': form,
                    'alojamiento': alojamiento,
                    'muestra_evaluaciones': alojamiento.muestra_evaluaciones,
                    'habitaciones_disponibles': habitaciones_disponibles,
                    'favorito': favorito,
                }
        else:
            print('Hay errores en el formulario')
            # En este caso la consulta es para la disponibilidad de las habitaciones en las fechas indicadas en el calendario del formulario
            fecha_entrada = form.cleaned_data['fecha_entrada']
            fecha_salida = form.cleaned_data['fecha_salida']

            # Se definen las habitaciones que están disponibles en las fechas indicadas
            habitaciones_disponibles = alojamiento.get_habitaciones_disponibles(
                fecha_entrada = fecha_entrada,
                fecha_salida = fecha_salida,
            )

            context = {
                'form': form,
                'alojamiento': alojamiento,
                'muestra_evaluaciones': alojamiento.muestra_evaluaciones,
                'habitaciones_disponibles': habitaciones_disponibles,
                'favorito': favorito,
            }

    else:
        # Se le pasan como parámetros al formulario, las fechas. (Estos campos siempre deben tener una fecha establecida)
        form = Consultar_Disponibilidad_Alojamiento_Por_Habitacion(
            {
                'fecha_entrada': fecha_entrada,
                'fecha_salida': fecha_salida,
            }
        )

        # Se definen las habitaciones que están disponibles en las fechas indicadas
        habitaciones_disponibles = alojamiento.get_habitaciones_disponibles(
            fecha_entrada = fecha_entrada,
            fecha_salida = fecha_salida,
        )

        context = {
            'form': form,
            'alojamiento': alojamiento,
            'muestra_evaluaciones': alojamiento.muestra_evaluaciones,
            'habitaciones_disponibles': habitaciones_disponibles,
            'favorito': favorito,
        }

    context.update(cc)
    return render(request, 'servicios/alojamientos/detalles_alojamiento_por_habitacion.html', context)

def detalles_alojamiento_completo(request, alojamiento_id):
    cc = custom_context(request)

    alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = alojamiento_id)

    # Inicialmente se definen unas fechas por defecto para llevar a cabo el análisis de disponibilidad de las Habitaciones
    fecha_entrada = datetime.date.today() + datetime.timedelta(days=3)
    fecha_salida = datetime.date.today() + datetime.timedelta(days=10)

    # Lo primero que se hace en esta vista es determinar el estado de Favorito del Servicio
    # Para determinar si el Alojamiento pertenece a un Servicio seleccionado como Favorito por el usuario, hay que considerar dos escenarios:
    # 1 - El usuario se encuentra registrado en el sistema, con lo cual se realiza una consulta a los favoritos en la BD
    if cc['usuario']:
        favorito = cc['usuario'].check_favorito(servicio_id = alojamiento.servicio.id)
    # 2 - El usuario es aún anónimo, con lo cual la información de sus favoritos (además de intención de compra, etc) se almacena en la sesión del navegador
    # Se comprueba que exista algún favorito registrado en la sesion
    elif str(alojamiento.servicio.id) in cc['favoritos']:
        favorito = True
    else:
        favorito = False

    # Después se analiza el comportamiento de la página ante las consultas
    if request.method == 'POST':
        form = Consultar_Disponibilidad_Alojamiento_Completo(request.POST)
        if form.is_valid():
            # Caso en que el POST viene del submit de Reservar el Servicio
            if 'reservar' in request.POST:
                fecha_entrada = form.cleaned_data['fecha_entrada']
                fecha_salida = form.cleaned_data['fecha_salida']

                # Determinar la cantidad de adultos de la Reserva
                adultos = form.cleaned_data['adultos'] or 0
                if not adultos:
                    adultos = 0
                else:
                    adultos = int(adultos)

                # Determinar la cantidad de niños de la Reserva
                ninnos = form.cleaned_data['ninnos'] or 0
                if not ninnos:
                    ninnos = 0
                else:
                    ninnos = int(ninnos)

                # Se definen los precios y comisiones
                precio_total, comision = alojamiento.servicio.get_precio_comision_fechas(fecha_entrada = fecha_entrada, fecha_salida = fecha_salida)

                # En este punto se crea una Reserva con la información recogida.
                # Hay dos posibles escenarios (El usuario se encuentra autenticado; El usuario es anónimo (No se encuentra autenticado o logeado)
                # Si el usuario se encuentra autenticado:
                if cc['usuario']:
                    n_reserva_servicio = Reserva.nueva_reserva_servicio(
                        servicio = alojamiento.servicio,
                        initial_date = fecha_entrada,
                        final_date = fecha_salida,
                        usuario = cc['usuario'],
                        precio_servicio = precio_total,
                        comision = comision,
                        ninnos = ninnos,
                        adultos = adultos,
                    )

                    n_reserva_servicio.comision = Comision.get_comision(n_reserva_servicio.precio_servicio)
                    n_reserva_servicio.save()

                    # A continuación, se redirige al usuario a la página de checkout para mostrar la información de pago y proceder a confirmar el mismo
                    return redirect('servicios:checkout_alojamiento_completo', reserva_id = n_reserva_servicio.id)

                # Si por el contrario, la reserva la está realizando un usuario anónimo:
                else:
                    # Se crea el diccionario con la información genérica de la reserva que se tiene hasta el momento
                    reserva_servicio = {
                        'servicio_id': alojamiento.servicio.id,
                        'alojamiento_id': alojamiento.id,
                        'initial_date': fecha_entrada,
                        'final_date': fecha_salida,
                        'ninnos': ninnos,
                        'adultos': adultos,
                        'precio_servicio': str(round(float(precio_total), 2)),
                        'comision': str(round(float(comision), 2)),
                        'fecha_creacion': datetime.date.today(),
                        # La firma de tiempo (timestamp) es una combinación de la fecha y hora exactas de su registro, con el id del servicio y un identificador único de la sesión
                        'timestamp': '%s%s%s' %(str(request.session.__dict__['_SessionBase__session_key']), str(datetime.datetime.now()).replace('-', '').replace(' ', '').replace(':', '').replace('.', ''), str(alojamiento.servicio.id))
                    }

                    # Se añade información adicional al diccionario de la reserva
                    reserva_servicio = Reserva.objects.detalles_reserva(id = None, reserva_servicio = reserva_servicio)

                    # Se determina la información restante de precios globales de la Reserva
                    reserva_servicio['total_a_pagar'] = str(round(float(reserva_servicio['costo_gestion'] + precio_total + reserva_servicio['impuestos']), 2))
                    reserva_servicio['pago_online'] = str(round(float(comision + reserva_servicio['costo_gestion'] + reserva_servicio['impuestos']), 2))
                    reserva_servicio['pago_offline'] = str(round(float((reserva_servicio['costo_gestion'] + precio_total + reserva_servicio['impuestos']) - (comision + reserva_servicio['costo_gestion'] + reserva_servicio['impuestos'])), 2))
                    reserva_servicio['costo_gestion'] = str(round(float(reserva_servicio['costo_gestion']), 2))
                    reserva_servicio['impuestos'] = str(round(float(reserva_servicio['impuestos']), 2))
                    reserva_servicio['initial_date'] = str(reserva_servicio['initial_date'])
                    reserva_servicio['final_date'] = str(reserva_servicio['final_date'])
                    reserva_servicio['fecha_creacion'] = str(reserva_servicio['fecha_creacion'])
                    reserva_servicio['timestamp'] = str(reserva_servicio['timestamp'])

                    # Una vez se tiene toda la información de la Reserva, esta se almacena en la sesión y se procede al checkout
                    if 'en_el_carro' in request.session:
                        # Si ya existe alguna reserva de servicio guardada previamente en la sesión, se añade uan nueva
                        en_el_carro = request.session['en_el_carro']
                        en_el_carro.append(reserva_servicio)
                        del request.session['en_el_carro']
                        request.session['en_el_carro'] = en_el_carro
                    else:
                        # En caso contrario se crea la lista y se le añade el diccionario actual
                        request.session['en_el_carro'] = [reserva_servicio, ]

                    return redirect('servicios:checkout_alojamiento_completo_servicio', servicio_id = alojamiento.servicio.id)

            elif 'buscar' in request.POST:
                # En este caso la consulta es para la disponibilidad de las habitaciones en las fechas indicadas en el calendario del formulario
                fecha_entrada = form.cleaned_data['fecha_entrada']
                fecha_salida = form.cleaned_data['fecha_salida']

                disponible = alojamiento.servicio.check_disponibilidad(fecha_entrada = fecha_entrada, fecha_salida = fecha_salida)
                if disponible:
                    class_alert = 'alert alert-success'
                    message = 'El alojamiento está disponible para las fechas consultadas'
                else:
                    class_alert = 'alert alert-danger'
                    message = 'El alojamiento no está disponible para las fechas consultadas'

                precio = alojamiento.servicio.get_precio_fechas(fecha_entrada, fecha_salida)

                context = {
                    'form': form,
                    'class_alert': class_alert,
                    'message': message,
                    'alojamiento': alojamiento,
                    'muestra_evaluaciones': alojamiento.muestra_evaluaciones,
                    'disponible': disponible,
                    'precio': precio,
                    'favorito': favorito,
                    'fecha_entrada': fecha_entrada,
                    'fecha_salida': fecha_salida,
                }

            else:
                message = 'Está llegando una opción de POST desconocida del Formulario'
                context = {
                    'form': form,
                    'class_alert': 'alert alert-danger',
                    'message': message,
                    'alojamiento': alojamiento,
                    'muestra_evaluaciones': alojamiento.muestra_evaluaciones,
                    'disponible': False,
                    'precio': None,
                    'favorito': False,
                    'fecha_entrada': None,
                    'fecha_salida': None,
                }

        else:
            print('Hay errores en el formulario')
            habitaciones_disponibles = []

            context = {
                'form': form,
                'muestra_evaluaciones': alojamiento.muestra_evaluaciones,
                'habitaciones_disponibles': habitaciones_disponibles,
                'favorito': favorito,
                'fecha_entrada': fecha_entrada,
                'fecha_salida': fecha_salida,
            }

    else:
        # Se le pasan como parámetros al formulario, las fechas. (Estos campos siempre deben tener una fecha establecida)
        form = Consultar_Disponibilidad_Alojamiento_Completo(
            {
                'fecha_entrada': fecha_entrada,
                'fecha_salida': fecha_salida,
            }
        )

        disponible = alojamiento.servicio.check_disponibilidad(fecha_entrada = fecha_entrada, fecha_salida = fecha_salida)
        precio, comision = alojamiento.servicio.get_precio_comision_fechas(fecha_entrada, fecha_salida)

        context = {
            'form': form,
            'alojamiento': alojamiento,
            'muestra_evaluaciones': alojamiento.muestra_evaluaciones,
            'favorito': favorito,
            'disponible': disponible,
            'precio': precio,
            'fecha_entrada': fecha_entrada,
            'fecha_salida': fecha_salida,
        }

    context.update(cc)
    return render(request, 'servicios/alojamientos/detalles_alojamiento_completo.html', context)

def eliminar_reserva(request, reserva_id):
    reserva = Reserva.objects.get(id = reserva_id)
    reserva.eliminar_reserva()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def cancelar_reserva(request, reserva_id):
    # Se obtiene toda la información de la Reserva
    reserva = Reserva.objects.detalles_reserva(id = reserva_id)

    if request.method == 'POST':
        n_cancelacion_reserva = Cancelacion_Reserva.nueva_cancelacion_reserva(
            reserva = reserva,
            motivo = request.POST['motivo_cancelacion'],
            cantidad_reembolso_euros = reserva.total_reembolso,
        )

        # Enviar un email al usuario con el comprobante de la Cancelación de la Reserva
        Email.enviar_correo_cancelacion_reserva_alojamiento(host = request.get_host(), reserva_id = reserva.id)

        # Antes de redirigir al usuario a la vista de las Reservas, dejamos indicado en la session que se debe mostrar el mensaje de cancelación exitosa
        request.session['mensaje_cancelacion'] = 'Se ha realizado correctamente la Cancelación de su Reserva'

        # Se redirige al usuario a la vista de sus reservas
        return redirect('servicios:mis_reservas')

    else:
        # Se asume que hay un Pago asociado a esta Reserva, pues en caso contratio no se podría llegar a esta vista
        pago = reserva.pago_set.first()

        context = {
            'pago': pago,
            'reserva': reserva,
            'tipo_cambio': reserva.tipo_cambio,
            'costo_gestion_euros': reserva.costo_gestion_euros,
            'impuesto_euros': reserva.impuesto_euros,
            'comision_euros': reserva.comision_euros,
            'total_reembolso': reserva.total_reembolso,
        }
        context.update(custom_context(request))
        return render(request, 'servicios/servicios/cancelar_reserva.html', context)

def checkout_alojamiento_por_habitacion(request, reserva_id = None, servicio_id = None):
    # Se define la Aplicación que se está utilizando
    paypal_app = Paypal_App.objects.get(en_uso = True)

    if reserva_id:
        reserva = Reserva.objects.detalles_reserva(id = reserva_id)
        alojamiento = Alojamiento.objects.detalles_alojamiento(reserva.servicio.alojamiento.id)
        pago_online_euros = str(round(reserva.pago_online * Decimal(request.session['user_data']['billing_rate']), 2))

        # Antes de crear realizar una nueva petición de Pago a Paypal, verificamos en nuestra BD que no exista ningún Pago incompleto
        # relacionado con esra Reservación. De existir, se reutiliza este en vez de crear un nuevo registro y realizar una nueva petición a Paypal
        if reserva.pago_set.filter(completado = False):
            # Debido a esta comprobación, se asume que nunca habrá más de un Pago incompleto asociado a una misma reserva, así que podemos hacer una consulta con .get()
            n_pago = reserva.pago_set.get(completado = False)
            approval_url = n_pago.approval_url

        # Si por el contrario no hay ningún pago incompleto asociado a la reserva en cuestión, se crea entonces un nuevo Pago en nuestra BD
        else:
            payment = paypal_app.create_payment(
                name = alojamiento.servicio.nombre,
                price = pago_online_euros,
                total = pago_online_euros,
            )

            # Se obtiene una URL para enviar al usuario a que autorice el pago
            approval_url = None
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = str(link.href)

            # Se crea el registro de Pago en nuestra BD
            n_pago = Pago.nuevo_pago(
                paypal_app = paypal_app,
                reserva = reserva,
                reserva_dict = None,
                paypal_payment_id = payment.__data__.get('id'),
                total_pagado_euros = Decimal(pago_online_euros),
                approval_url = approval_url,
            )

        context = {
            'approval_url': approval_url,
            'reserva': reserva,
            'reservas_habitaciones': reserva.reserva_habitacion_set.all(),
            'alojamiento': alojamiento,
        }
        context.update(custom_context(request))
        return render(request, 'servicios/servicios/checkout_alojamiento_por_habitacion.html', context)

    elif servicio_id:
        # Lo primero os obtener el Alojamiento a través del Servicio, para poder añadir la información del Object Manager de Alojamiento
        alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = Servicio.objects.get(id = servicio_id).alojamiento.id)

        # Determinar qué Reserva es la relacionada con el Checkout
        for reserva in request.session['en_el_carro']:

            if reserva['servicio_id'] == int(servicio_id):
                initial_date = reserva['initial_date']
                final_date = reserva['final_date']
                initial_date_week = reserva['initial_date_week']
                final_date_week = reserva['final_date_week']
                fecha_creacion = reserva['fecha_creacion']
                timestamp = reserva['timestamp']
                cantidad_noches = reserva['cantidad_noches']
                comision = reserva['comision']
                precio_servicio = reserva['precio_servicio']
                pago_online = reserva['pago_online']
                pago_offline = reserva['pago_offline']
                costo_gestion = reserva['costo_gestion']
                total_a_pagar = reserva['total_a_pagar']
                impuestos = reserva['impuestos']

                # Ahora determinamos la lista de reservas de habitaciones para pasar al template
                reservas_habitaciones = []
                for element in reserva:
                    # Solo las Reservas de Habitaciones son diccionarios dentro del diccionario de la Reserva del Servicio
                    if isinstance(reserva[element], dict):
                        capacidad = reserva[element]['capacidad']
                        adultos = reserva[element]['adultos']
                        ninnos = reserva[element]['ninnos']
                        precio = reserva[element]['precio']
                        # Añadimos los detalles de la Reserva de Habitación a la lista preparada para ello
                        reservas_habitaciones.append([capacidad, adultos, ninnos, precio])

                # Cálculo de la cantidad en € a pagar por parte del Cliente (Será enviada a Paypal como cantidad en la solicitud de pago)
                pago_online_euros = str(round(Decimal(pago_online) * Decimal(request.session['user_data']['billing_rate']), 2))

                # Antes de realizar una nueva petición de Pago a Paypal, verificamos en nuestra BD que no exista ningún Pago incompleto
                # relacionado con esa Reservación. De existir, se reutiliza este en vez de crear un nuevo registro y realizar una nueva petición a Paypal
                # Las creaciones de nuevos pagos en Paypal pueden demorar varios segundos, y no queremos que el cliente abandone en medio del proceso de compra
                db_pago = Pago.objects.filter(reserva_dict__contains = timestamp)
                if db_pago:
                    approval_url = db_pago[0].approval_url
                else:
                    # Si no se ha encontrado un pago asociado a la Reserva (quiere decir que se acaba de crear la Reserva), entonces creamos el pago con Paypal
                    payment = paypal_app.create_payment(
                        name = alojamiento.servicio.nombre,
                        price = pago_online_euros,
                        total = pago_online_euros,
                    )

                    # Se obtiene una URL para enviar al usuario a que autorice el pago
                    approval_url = None
                    for link in payment.links:
                        if link.rel == "approval_url":
                            approval_url = str(link.href)

                    # Se crea el registro de Pago en nuestra BD
                    print('Estoy a punto de crear el nuevo Pago, y la reserva que tengo es:')
                    print(reserva)
                    n_pago = Pago.nuevo_pago(
                        paypal_app = paypal_app,
                        reserva = None,  # Esto es un FK a Reserva que se usa cuando el Usuario se encuentra logeado
                        reserva_dict = json.dumps(reserva),
                        # Se guarda toda la información del diccionario de la reserva almacenada en la session
                        paypal_payment_id = payment.__data__.get('id'),
                        total_pagado_euros = Decimal(pago_online_euros),
                        approval_url = approval_url,
                    )

                context = {
                    'alojamiento': alojamiento,
                    'initial_date': initial_date,
                    'final_date': final_date,
                    'initial_date_week': initial_date_week,
                    'final_date_week': final_date_week,
                    'fecha_creacion': fecha_creacion,
                    'timestamp': timestamp,
                    'cantidad_noches': cantidad_noches,
                    'reserva': reserva,
                    'comision': comision,
                    'precio_servicio': precio_servicio,
                    'pago_online': pago_online,
                    'pago_offline': pago_offline,
                    'costo_gestion': costo_gestion,
                    'total_a_pagar': total_a_pagar,
                    'impuestos': impuestos,
                    'approval_url': approval_url,
                    'reservas_habitaciones': reservas_habitaciones,
                }

                context.update(custom_context(request))

                return render(request, 'servicios/servicios/checkout_alojamiento_por_habitacion_usuario_anonimo.html', context)

def checkout_alojamiento_completo(request, reserva_id = None, servicio_id = None):
    # Se define la Aplicación que se está utilizando
    paypal_app = Paypal_App.objects.get(en_uso = True)

    if reserva_id:
        reserva = Reserva.objects.detalles_reserva(id = reserva_id)
        alojamiento = Alojamiento.objects.detalles_alojamiento(reserva.servicio.alojamiento.id)
        pago_online_euros = str(round(reserva.pago_online * Decimal(request.session['user_data']['billing_rate']), 2))

        # Antes de crear realizar una nueva petición de Pago a Paypal, verificamos en nuestra BD que no exista ningún Pago incompleto
        # relacionado con esra Reservación. De existir, se reutiliza este en vez de crear un nuevo registro y realizar una nueva petición a Paypal
        if reserva.pago_set.filter(completado = False):
            # Debido a esta comprobación, se asume que nunca habrá más de un Pago incompleto asociado a una misma reserva, así que podemos hacer una consulta con .get()
            n_pago = reserva.pago_set.get(completado = False)
            approval_url = n_pago.approval_url

        # Si por el contrario no hay ningún pago incompleto asociado a la reserva en cuestión, se crea entonces un nuevo Pago en nuestra BD
        else:
            # Se crea una petición de crear un pago en Paypal
            payment = paypal_app.create_payment(
                name = alojamiento.servicio.nombre,
                price = pago_online_euros,
                total = pago_online_euros,
            )

            # Se obtiene una URL para enviar al usuario a que autorice el pago
            approval_url = None
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = str(link.href)

            # Se crea el registro de Pago en nuestra BD
            n_pago = Pago.nuevo_pago(
                paypal_app = paypal_app,
                reserva = reserva,
                reserva_dict = None,
                paypal_payment_id = payment.__data__.get('id'),
                total_pagado_euros = Decimal(pago_online_euros),
                approval_url = approval_url,
            )

        context = {
            'approval_url': approval_url,
            'reserva': reserva,
            'alojamiento': alojamiento,
        }
        context.update(custom_context(request))
        return render(request, 'servicios/servicios/checkout_alojamiento_completo.html', context)

    elif servicio_id:
        # Este es el escenario en que el usuario no se encuentra logeado en el sitio
        # Lo primero os obtener el Alojamiento a través del Servicio, para poder añadir la información del Object Manager de Alojamiento
        alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = Servicio.objects.get(id = servicio_id).alojamiento.id)

        # Determinar qué Reserva es la relacionada con el Checkout. Una vez hallada, pasamos a la página del Checkout
        for reserva in request.session['en_el_carro']:
            if reserva['servicio_id'] == int(servicio_id):

                # Si encontramos la Reserva que necesitamos, extraemos toda la información necesaria
                initial_date = reserva['initial_date']
                final_date = reserva['final_date']
                initial_date_week = reserva['initial_date_week']
                final_date_week = reserva['final_date_week']
                fecha_creacion = reserva['fecha_creacion']
                timestamp = reserva['timestamp']
                cantidad_noches = reserva['cantidad_noches']
                comision = reserva['comision']
                precio_servicio = reserva['precio_servicio']
                pago_online = reserva['pago_online']
                pago_offline = reserva['pago_offline']
                costo_gestion = reserva['costo_gestion']
                total_a_pagar = reserva['total_a_pagar']
                impuestos = reserva['impuestos']

                # Cálculo de la cantidad en € a pagar por parte del Cliente (Será enviada a Paypal como cantidad en la solicitud de pago)
                pago_online_euros = str(round(Decimal(pago_online) * Decimal(request.session['user_data']['billing_rate']), 2))

                # Antes de realizar una nueva petición de Pago a Paypal, verificamos en nuestra BD que no exista ningún Pago incompleto
                # relacionado con esa Reservación. De existir, se reutiliza este en vez de crear un nuevo registro y realizar una nueva petición a Paypal
                # Las creaciones de nuevos pagos en Paypal pueden demorar varios segundos, y no queremos que el cliente abandone en medio del proceso de compra
                db_pago = Pago.objects.filter(reserva_dict__contains = timestamp)
                if db_pago:
                    approval_url = db_pago[0].approval_url
                else:
                    # Si no se ha encontrado un pago asociado a la Reserva (quiere decir que se acaba de crear la Reserva), entonces creamos el pago con Paypal
                    payment = paypal_app.create_payment(
                        name = alojamiento.servicio.nombre,
                        price = pago_online_euros,
                        total = pago_online_euros,
                    )

                    # Se obtiene una URL para enviar al usuario a que autorice el pago
                    approval_url = None
                    for link in payment.links:
                        if link.rel == "approval_url":
                            approval_url = str(link.href)

                    # Se crea el registro de Pago en nuestra BD
                    n_pago = Pago.nuevo_pago(
                        paypal_app = paypal_app,
                        reserva = None, # Esto es un FK a Reserva que se usa cuando el Usuario se encuentra logeado
                        reserva_dict = json.dumps(reserva), # Se guarda toda la información del diccionario de la reserva almacenada en la session
                        paypal_payment_id = payment.__data__.get('id'),
                        total_pagado_euros = Decimal(pago_online_euros),
                        approval_url = approval_url,
                    )

                # Una vez tenemos en la mano toda la información de la Reserva y el Pago, procedemos a la página del Checkout
                context = {
                    'initial_date': initial_date,
                    'final_date': final_date,
                    'initial_date_week': initial_date_week,
                    'final_date_week': final_date_week,
                    'fecha_creacion': fecha_creacion,
                    'timestamp': timestamp,
                    'cantidad_noches': cantidad_noches,
                    'reserva': reserva,
                    'alojamiento': alojamiento,

                    'comision': comision,
                    'precio_servicio': precio_servicio,
                    'pago_online': pago_online,
                    'pago_offline': pago_offline,
                    'costo_gestion': costo_gestion,
                    'total_a_pagar': total_a_pagar,
                    'impuestos': impuestos,
                    'approval_url': approval_url,
                }

                context.update(custom_context(request))
                return render(request, 'servicios/servicios/checkout_alojamiento_completo_usuario_anonimo.html', context)

def add_favorito(request, servicio_id):
    # Determinar el Servicio que se quiere añadir como favorito por el usuario
    servicio = Servicio.objects.get(id = servicio_id)

    # Añadir a Favoritos, no es exclusivo de usuarios autenticados, con lo cual, hay que considerar los dos posibles escenarios
    # En caso de usuarios no autenticados, la información de favoritos se almacena en la sesión, hasta que el usuario se autentique o la sesión expire
    if request.user.is_authenticated():
        usuario = Usuario.objects.get(user = request.user)
        # Si el usuario se encuentra autenticado, se crea el registro de Favorito normalmente
        n_favorito = Favorito.nuevo_favorito(
            servicio = servicio,
            usuario = usuario,
        )
    else:
        # Si el usuario no se encuentra autenticado, se guarda en la sesión la información de favoritos
        # En este escenario, es posible que no sea el primer favorito que el usuario añade a su lista de favoritos
        # Nos aseguramos de no duplicar ids de servicios en los favoritos
        if 'favoritos' in request.session and not servicio_id in request.session['favoritos']:
            favoritos = request.session['favoritos']
            favoritos.append(str(servicio_id))
            del request.session['favoritos']
            request.session['favoritos'] = favoritos
        else:
            request.session['favoritos'] = [servicio_id]

    # Se recarga la página
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def eliminar_reserva_sesion(request, timestamp):
    reservas_sesion = request.session['en_el_carro']
    for reserva_sesion in reservas_sesion:
        if reserva_sesion['timestamp'] == timestamp:
            reservas_sesion.remove(reserva_sesion)
            break
    del request.session['en_el_carro']
    request.session['en_el_carro'] = reservas_sesion
    if not request.session['en_el_carro']:
        del request.session['en_el_carro']

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def activar_regla_precio(request, regla_precio_id):
    regla_precio = Regla_Precio.objects.get(id = regla_precio_id)
    regla_precio.activar_regla_precio()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def desactivar_regla_precio(request, regla_precio_id):
    regla_precio = Regla_Precio.objects.get(id = regla_precio_id)
    regla_precio.desactivar_regla_precio()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def eliminar_regla_precio(request, regla_precio_id):
    regla_precio = Regla_Precio.objects.get(id = regla_precio_id)
    regla_precio.eliminar_regla_precio()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def eliminar_indisponibilidad(request, indisponibilidad_id):
    indisponibilidad = Indisponibilidad.objects.get(id = indisponibilidad_id)
    indisponibilidad.eliminar_indisponibilidad()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def cambiar_activacion_regla_precio(request, regla_precio_id):
    regla_precio = Regla_Precio.objects.get(id = regla_precio_id)
    regla_precio.cambiar_activacion_regla_precio()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# Elimina un registro de Favorito a partir del id del servicio asociado
def eliminar_favorito(request, servicio_id):
    # Eliminar un Favorito puede presentarse en más de un escenario. Depende de si el usuario que realiza la acción está registrado en el sistema o no
    # 1 - Si el usuario se encuentra autenticado, se elimina entonces el registro del modelo Favorito
    if request.user.is_authenticated():
        favorito = Favorito.objects.get(servicio__id = servicio_id)
        favorito.eliminar_favorito()
    # 2 - Si el usuario no está autenticado hay que remover de la lista de ids de servicios favoritos guardados en la sesión, el id indicado en el argumento de la vista
    else:
        favoritos = request.session['favoritos']
        favoritos.remove(str(servicio_id))
        del request.session['favoritos']
        # Si el favorito que se eliminó fue el último, se elimina la variable de la sesión
        if favoritos:
            request.session['favoritos'] = favoritos

    # Se recarga la página
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def cart(request):
    # Se obtiene el diccionario custom_context para evitar la repetición de llamadas más adelante
    cc = custom_context(request)

    # Se ontiene la variable "en_el_carro" del custom_context para trabajar con ella
    # Esta variable puede ser una lista de Registros o bien una lista de diccionarios con la información completa de un registro
    # En dependencia de si el usuario está autenticado o no
    en_el_carro = cc['en_el_carro']

    # Se definen las listas vacías de los tipos de Servicios que se van a listar en las Reservas incompletas
    alojamientos = []
    recorridos = []
    taxis = []
    packs = []

    for reserva in en_el_carro:
        if cc['usuario']:
            servicio = reserva.servicio
            total_a_pagar = reserva.total_a_pagar
            fecha_creacion = reserva.fecha_creacion
            initial_date = reserva.initial_date
            final_date = reserva.final_date
            timestamp = None
        else:
            servicio = Servicio.objects.get(id = reserva['servicio_id'])
            total_a_pagar = reserva['total_a_pagar']
            fecha_creacion = reserva['fecha_creacion']
            initial_date = reserva['initial_date']
            final_date = reserva['final_date']
            timestamp = reserva['timestamp']
            reserva = None

        if Alojamiento.objects.filter(servicio = servicio):

            alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = servicio.alojamiento.id)
            alojamientos.append(
                {
                    'alojamiento': alojamiento,
                    'total_a_pagar': total_a_pagar,
                    'fecha_creacion': fecha_creacion,
                    'initial_date': initial_date,
                    'final_date': final_date,
                    'timestamp': timestamp,
                    'reserva': reserva,
                },
            )

        elif Recorrido.objects.filter(servicio = servicio):
            pass
        elif Taxi.objects.filter(servicio = servicio):
            pass
        elif Pack.objects.filter(servicio = servicio):
            pass

    context = {
        'alojamientos': alojamientos, # Es una lista de listas con la forma [Alojamiento, precio, servicio_id]
        'recorridos': recorridos,
        'taxis': taxis,
        'packs': packs,
    }
    context.update(custom_context(request))
    return render(request, 'servicios/servicios/cart.html', context)

def mis_favoritos(request):
    cc = custom_context(request)
    favoritos = cc['favoritos']

    if favoritos:
        alojamientos = Alojamiento.objects.detalles_alojamientos(
            favoritos = favoritos,
            cerrado = True,
        )
        recorridos = Recorrido.objects.filter(servicio__id__in = favoritos)
        taxis = Taxi.objects.filter(servicio__id__in = favoritos)
        packs = Pack.objects.filter(servicio__id__in = favoritos)
    else:
        alojamientos, recorridos, taxis, packs = None, None, None, None

    context = {
        'alojamientos': alojamientos,
        'recorridos': recorridos,
        'taxis': taxis,
        'packs': packs,
    }
    context.update(custom_context(request))
    return render(request, 'servicios/servicios/mis_favoritos.html', context)

def mis_reservas(request):
    cc = custom_context(request)
    usuario = cc['usuario']

    # El posible mensaje y la clase de la alerta se definen como nulos inicialmente
    message = None
    class_alert = None

    if request.method == 'POST':

        # El input hidden de todos los formularios tiene el mismo name, así que se puede separar de las posibles variantes de POST que se reciban
        reserva = Reserva.objects.detalles_reserva(id = request.POST['id'])

        if 'enviar_evaluacion' in request.POST:
            # Se recibe el POST del formulario diseñado para crear una nueva Evaluación

            n_evaluacion = Evaluacion.nueva_evaluacion(
                servicio = reserva.servicio,
                reserva = reserva,
                usuario = reserva.usuario,
                evaluacion = request.POST['calificacion'],
                titulo = request.POST['titulo_evaluacion'],
                comentario = request.POST['evaluacion'],
            )

            # Si se ha podido crear correctamente la Evaluación, mostramos el mensaje en el template
            if not isinstance(n_evaluacion, dict):
                message = 'Se ha crado correctamente la Evaluación'
                class_alert = 'alert alert-success'
            else:
                message = n_evaluacion['message']
                class_alert = 'alert alert-danger'

        elif 'modificar_evaluacion' in request.POST:
            # Se recibe el POST del formulario diseñado para modificar una Evaluación existente
            evaluacion = reserva.evaluacion_set.first()
            m_evaluacion = evaluacion.modificar_evaluacion(
                evaluacion = request.POST['calificacion'],
                titulo = request.POST['titulo_evaluacion'],
                comentario = request.POST['evaluacion'],
            )

            # Si se ha podido modificar correctamente la Evaluación, mostramos el mensaje en el template
            if not isinstance(m_evaluacion, dict):
                message = 'Se ha modificado correctamente la Evaluación'
                class_alert = 'alert alert-success'
            else:
                message = m_evaluacion['message']
                class_alert = 'alert alert-danger'

        # La lista de reservas a mostrar en la vista es independiente de cualquiera de las acciones anteriores
        reservas = Reserva.objects.detalles_reservas(completada = True, usuario = usuario)

    else:
        # Para saber si debemos mostrar el mensaje de Cancelación exitosa, buscamos en la session, si se ha indicado esto
        if 'mensaje_cancelacion' in request.session:
            message = request.session['mensaje_cancelacion']
            class_alert = 'alert alert-success'
            # Una vez obtenida la información útil de la session, eliminamos este parámetro de la misma
            del request.session['mensaje_cancelacion']

        reservas = Reserva.objects.detalles_reservas(completada = True, usuario = usuario)

    context = {
        'reservas': reservas,
        'message': message,
        'class_alert': class_alert,
    }
    context.update(cc)
    return render(request, 'servicios/servicios/mis_reservas.html', context)

def informacion_comercial(request):
    context = {
    }
    context.update(custom_context(request))
    return render(request, 'servicios/servicios/informacion_comercial.html', context)

def get_lat_lng(request, alojamiento_id):
    # Devuelve las coordenadas de un Alojamiento (latitud y longitud)
    alojamiento = Alojamiento.objects.get(id = alojamiento_id)
    latitud = alojamiento.latitud_gmaps
    longitud = alojamiento.longitud_gmaps

    resultado = {}
    resultado['latitud'] = latitud
    resultado['longitud'] = longitud

    return HttpResponse(json.dumps(resultado), content_type = 'application/json')

def get_data_alojamientos(request):
    # Devuelve las coordenadas de todos los Alojamientos (latitud y longitud), así como el id y el nombre
    alojamientos = Alojamiento.objects.detalles_alojamientos(
        usuarios = Usuario.get_proveedores_validados(),
        activos = True
    )

    rate = str(request.session['user_data']['rate']),
    moneda_codigo = request.session['user_data']['moneda_codigo'],

    data_alojamientos = []
    for alojamiento in alojamientos:
        id_alojamiento = alojamiento.id
        nombre = alojamiento.servicio.nombre
        descripcion = alojamiento.servicio.descripcion
        foto_url = alojamiento.fotos[0].foto.url
        latitud = alojamiento.latitud_gmaps
        longitud = alojamiento.longitud_gmaps
        cantidad_habitaciones = alojamiento.cantidad_habitaciones
        if alojamiento.por_habitacion:
            modo_alquiler = 'Por habitación'
        else:
            modo_alquiler = 'Completo'

        precio_minimo = str(alojamiento.precio_minimo)


        # data_alojamientos.append([id_alojamiento, nombre, descripcion, foto_url, latitud, longitud, cantidad_habitaciones, precio_minimo])
        data_alojamientos.append(
            [
                id_alojamiento,
                nombre,
                descripcion,
                foto_url,
                latitud,
                longitud,
                cantidad_habitaciones,
                modo_alquiler,
                precio_minimo,
                rate,
                moneda_codigo,
            ]
        )

    resultado = {
        'data_alojamientos': data_alojamientos
    }

    return HttpResponse(json.dumps(resultado), content_type = 'application/json')

def tabla_comisiones(request):
    comisiones = Comision.objects.order_by('precio')
    context = {
        'comisiones': comisiones,
    }

    context.update(custom_context(request))
    return render(request, 'servicios/servicios/comisiones.html', context)

# Devuelve una lista de empresas con sus ids relacionados para poder cargar selects
def get_municipios_provincia(request, provincia_id):
    provincia = Provincia.objects.get(id = provincia_id)
    municipios_provincia = []
    for municipio in provincia.municipio_set.order_by('nombre'):
        municipios_provincia.append([municipio.id, municipio.nombre])

    resultado = {
        'municipios': municipios_provincia,
    }

    return HttpResponse(json.dumps(resultado), content_type = 'application/json')

def onlinetravel(request):
    resultado = {
        'url': request.session['onlinetravel_url'],
    }

    # del request.session['onlinetravel_url']

    return HttpResponse(json.dumps(resultado), content_type='application/json')

def servicio_cerrado(request, servicio_id):
    servicio = Servicio.objects.get(id = servicio_id)
    # Obtenemos de la session de la view la url de la página anterior
    if 'actual_url' in request.session:
        # previous_url = request.session['actual_url']
        context = {
            'servicio': servicio,
            # 'previous_url': previous_url,
        }
        context.update(custom_context(request))
        return render(request, 'servicios/servicios/servicio_cerrado.html', context)
    else:
        return redirect('website:index')

# Cuando se cierra un servicio desde la vista de administración se dirige al usuario a la vista de Servicio cerrado
def cerrar_servicio(request, servicio_id):
    servicio = Servicio.objects.get(id = servicio_id)
    servicio.cerrado = True
    servicio.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def cerrar_habitacion(request, habitacion_id):
    habitacion = Habitacion.objects.get(id = habitacion_id)
    habitacion.cerrada = True
    habitacion.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def abrir_habitacion(request, habitacion_id):
    habitacion = Habitacion.objects.get(id = habitacion_id)
    habitacion.cerrada = False
    habitacion.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def abrir_servicio(request, servicio_id):
    servicio = Servicio.objects.get(id = servicio_id)
    servicio.cerrado = False
    servicio.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))