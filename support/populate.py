from servicios.models import Pais, Provincia, Municipio, Interes, Destino, Comision, Moneda, Idioma, Tipo_Alojamiento,\
    Servicio, Tipo_Cambio, Foto_Destino, Foto_Servicio, Regla_Cancelacion
from website.models import Aeropuerto
from administracion.models import Impuesto
from support import globals
from decimal import Decimal
from django.core.files import File
from forex_python.converter import CurrencyRates

from support.origin_data.countries import countries
from support.origin_data.cities import cities
from support.origin_data.idiomas import idiomas
from support.origin_data.monedas import monedas
from support.origin_data.comisiones import comisiones
from support.origin_data.aeropuertos_cuba import aeropuertos_cuba
from support.origin_data.aeropuertos_mundo import aeropuertos_mundo
from support.origin_data.reglas_cancelacion import reglas_cancelacion

import urllib3, json, os, zipfile, shutil
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1 - Inicializar todas las Monedas (populate_monedas)
# Se utiliza cuando la BD no tiene registros de Monedas. Registra los valores iniciales de Monedas con los que trabajará el sistema
# Se eliminan posibles registros para asegurarse que comienza desde cero
def populate_monedas():
    for moneda in monedas:
        if Moneda.objects.filter(codigo_iso = moneda):
            m = Moneda.objects.get(codigo_iso = moneda)
            m.modificar_moneda(
                codigo_iso = moneda,
                menu = monedas[moneda]['menu'],
            )
        else:
            Moneda.nueva_moneda(
                codigo_iso = moneda,
                menu = monedas[moneda]['menu'],
            )

# 2 - inicializar todos los Idiomas (populate_idiomas)
# Se utiliza cuando la BD no tiene registros de Idiomas. Registra los valores iniciales de Idiomas con los que trabajará el sistema
# Se eliminan posibles registros para asegurarse que comienza desde cero
def populate_idiomas():
    for idioma in idiomas:
        if Idioma.objects.filter(codigo = idioma):
            i = Idioma.objects.get(codigo = idioma)
            i.modificar_idioma(
                nombre = idiomas[idioma]['nombre']
            )
        else:
            Idioma.nuevo_idioma(
                nombre = idiomas[idioma]['nombre'],
                codigo = idioma
            )

# 3 - inicializar todos los Países (populate_paises)
# Se utiliza cuando la BD no tiene registros de Países. Registra los valores iniciales de País con los que trabajará el sistema
# Se eliminan posibles registros para asegurarse que comienza desde cero
def populate_paises():

    paises_nombres = []
    for pais in countries:
        # Actualizamos la lista con los nombres de los países que luego utilizaremos para contrastarla con los nombres de los países en BD
        paises_nombres.append(pais)

        # Definición de los objetos Moneda e Idioma a partir del valor en el diccionario de país
        if Moneda.objects.filter(codigo_iso = countries[pais]['moneda_codigo_iso']):
            moneda = Moneda.objects.get(codigo_iso = countries[pais]['moneda_codigo_iso'])
        else:
            moneda = None

        if Idioma.objects.filter(codigo = countries[pais]['idioma_codigo']):
            idioma = Idioma.objects.get(codigo = countries[pais]['idioma_codigo'])
        else:
            idioma = None

        # Si ya existe el país entonces lo modificamos con los datos que tengamos del mismo
        if Pais.objects.filter(nombre = pais):
            db_pais = Pais.objects.get(nombre = pais)
            db_pais.modificar_pais(
                union_europea = countries[pais]['union_europea'],
                prefijo_movil = countries[pais]['prefijo_movil'],
                codigo_iso_alfa2 = countries[pais]['codigo_iso_alfa2'],
                codigo_iso_alfa3 = countries[pais]['codigo_iso_alfa3'],
                codigo_iso_numerico = countries[pais]['codigo_iso_numerico'],
                moneda = moneda,
                idioma = idioma,
            )
        else:
            # Si el país no existe entonces se crea
            Pais.nuevo_pais(
                nombre = pais,
                union_europea = countries[pais]['union_europea'],
                prefijo_movil = countries[pais]['prefijo_movil'],
                codigo_iso_alfa2 = countries[pais]['codigo_iso_alfa2'],
                codigo_iso_alfa3 = countries[pais]['codigo_iso_alfa3'],
                codigo_iso_numerico = countries[pais]['codigo_iso_numerico'],
                moneda = moneda,
                idioma = idioma,
             )

# 4 - inicializar los datos del país Cuba (populate_cuba)
# Se utiliza para rellenar toda la información necesaria de Cuba como país de origen de los proveedores
def populate_cuba():
    cuba = globals.cuba
    # Si no se ha creado el país se intenta registrar
    if Pais.objects.filter(nombre = 'CUBA'):
        pais_object = Pais.objects.get(nombre='CUBA').modificar_pais(
            union_europea=cuba['Unión Europea'],
            prefijo_movil=cuba['Prefijo Móvil'],
            codigo_iso_alfa2=cuba['Código_ISO_Alfa2'],
            codigo_iso_alfa3=cuba['Código_ISO_Alfa3'],
            codigo_iso_numerico=cuba['Código_ISO_Numérico'],
            moneda=Moneda.objects.get(codigo_iso=cuba['Moneda']),
            idioma=Idioma.objects.get(codigo=cuba['Idioma']),
        )
    else:
        pais_object = Pais.nuevo_pais(
            nombre = 'CUBA',
            union_europea = cuba['Unión Europea'],
            prefijo_movil = cuba['Prefijo Móvil'],
            codigo_iso_alfa2 = cuba['Código_ISO_Alfa2'],
            codigo_iso_alfa3 = cuba['Código_ISO_Alfa3'],
            codigo_iso_numerico = cuba['Código_ISO_Numérico'],
            moneda = Moneda.objects.get(codigo_iso = cuba['Moneda']),
            idioma = Idioma.objects.get(codigo = cuba['Idioma']),
        )
    # Provincias
    for provincia in cuba['Provincias']:
        if Provincia.objects.filter(nombre = provincia['Nombre']):
            provincia_object = Provincia.objects.get(nombre = provincia['Nombre']).modificar_provincia(
                nombre = provincia['Nombre'],
                descripcion = provincia['Descripción'],
                pais = Pais.objects.get(nombre = 'CUBA')
            )
        else:
            provincia_object = Provincia.nueva_provincia(
                nombre = provincia['Nombre'],
                descripcion = provincia['Descripción'],
                pais = pais_object,
            )
        for municipio in provincia['Municipios']:
            if Municipio.objects.filter(nombre = municipio['Nombre'], provincia = provincia_object):
                municipio_object = Municipio.objects.get(
                    nombre = municipio['Nombre'],
                    provincia = provincia_object).modificar_municipio(
                    descripcion = municipio['Descripción']
                )
            else:
                municipio_object = Municipio.nuevo_municipio(
                    nombre = municipio['Nombre'],
                    descripcion = municipio['Descripción'],
                    provincia = provincia_object,
                )

def populate_provincias():
    for pais in cities:
        if len(pais) > 1:
            p = Pais.objects.get(codigo_iso_alfa2 = pais)
            provincias_pais = cities[pais]
            for provincia_pais in provincias_pais:
                if Provincia.objects.filter(nombre = provincia_pais):
                    pr = Provincia.objects.get(nombre = provincia_pais)
                    pr.modificar_provincia(
                        descripcion = None,
                        nombre = provincia_pais,
                        pais = p,
                    )
                else:
                    Provincia.nueva_provincia(
                        nombre = provincia_pais,
                        descripcion = None,
                        pais = p,
                    )

def populate_aeropuertos_cuba():
    codigos_iata = []
    for aeropuerto in aeropuertos_cuba:
        codigo_iata = aeropuerto.split(' ')[0]
        codigos_iata.append(codigo_iata)
        n_aeropuerto = Aeropuerto.nuevo_aeropuerto(
            codigo_iata = codigo_iata,
            info_completa = aeropuerto,
        )
        n_aeropuerto.cuba = True
        n_aeropuerto.save()

def populate_comisiones():
    for comision in comisiones:
        if Comision.objects.filter(precio = comision):
            c = Comision.objects.get(precio = comision)
            c.modificar_comision(
                precio = comision,
                comision = comisiones[comision],
            )
        else:
            Comision.nueva_comision(
                precio = comision,
                comision = comisiones[comision],
            )

def populate_intereses():
    for interes in globals.intereses:
        n_interes = Interes.nuevo_interes(
            nombre = interes,
        )

def populate_destinos():
    destinos = globals.destinos
    for destino in destinos:
        provincia = Provincia.objects.get(nombre = destino['provincia'])
        nombre = destino['nombre']
        intereses = list(Interes.objects.filter(nombre__in = destino['intereses'].split(',')))

        # Para la descripción leemos un fichero ubicado en "support/descripciones_destinos" con el nombre del destino
        doc = open('support/descripciones_destinos/%s.html' %(nombre), 'r')
        descripcion = doc.read()

        # Si el Destino que estoy registrando ya existe, se sobreescribe la información del mismo
        if Destino.objects.filter(nombre = nombre, provincia = provincia):
            m_destino = Destino.objects.get(nombre = nombre, provincia = provincia)
            m_destino.modificar_destino(
                descripcion = descripcion,
                intereses = intereses,
                provincia = provincia,
            )

        # Si el Destino no existe se crea un registro nuevo
        else:
            Destino.nuevo_destino(
                nombre = nombre,
                descripcion = descripcion,
                intereses = intereses,
                provincia = provincia,
            )

        doc.close()

def populate_fotos_destinos():
    fotos_path = 'support/fotos_destinos'

    # Lo primero es eliminar todas las Fotos de Destinos actuales
    for foto_destino in Foto_Destino.objects.all():
        foto_destino.eliminar_foto_destino()

    # Listamos todos los Destinos en la BD
    for destino in Destino.objects.all():
        print('Poblando %s' %(destino))
        # Para cada destino:
        # 1 - Determinamos el directorio donde podrían estar las imágenes relacionadas con este
        carpeta_fotos = '%s/%s' %(fotos_path, destino.nombre)

        # 2 - Creamos una lista con las fotos en el directorio
        if os.path.isdir(carpeta_fotos):
            for foto in os.listdir(carpeta_fotos):
                # 3 - Por cada foto de la lista creamos un nuevo objeto Foto_Destino y le asociamos la imagen
                n_foto_destino = Foto_Destino.objects.create(
                    destino = destino,
                    foto = None,
                )

                n_foto_destino.foto.save(foto, File(open('%s/%s' %(carpeta_fotos, foto), 'rb')))

                img_url = '%s/%s' % (os.getcwd(), n_foto_destino.foto.url)
                Foto_Servicio.procesar_foto_servicio(img_url)
        else:
            print('No se ha podido encontrar el directorio %s' %(carpeta_fotos))

def populate_tipos_alojamiento():
    tipos_alojamiento = globals.tipos_alojamiento
    for tipo_alojamiento in tipos_alojamiento:
        Tipo_Alojamiento.nuevo_tipo_alojamiento(
            tipo = tipo_alojamiento['tipo']
        )

def populate_impuestos():
    impuestos = globals.impuestos
    for impuesto in impuestos:
        Impuesto.nuevo_impuesto(
            nombre = impuesto['nombre'],
            porciento = Decimal(impuesto['porciento'],)
        )

def populate_tipos_cambio():
    # Como la moneda base que es el CUC es igual a efectos prácticos que el USD, se guardan todos los tipos de cambi respecto a este últlimo
    Tipo_Cambio.update_tipos_cambio()

# def populate_aeropuertos_mundo():
#     # Hace uso de la API de IATACodes para actualizar la información de todos los aeropuertos que pueden ser elegidos en el buscador de vuelos
#     # La versión gratuita de esta API es muy limitada, principalmente en cuanto a la información que devuelve de cada elemento. No se puede
#     # con una sola consulta obtener nombre de aeropuerto, codigo de aeropuerto, nombre de ciudad y de pais del aeropuerto; y estas son las 4 cosas
#     # que se necesitan para completar el modelo Aeropuerto_Mundo. La API de pago cuesta $99 al mes. De momento buscamos una alternativa gratuita
#     # para obtener la información necesaria. La estrategia sigue los siguientes pasos:
#     # 1 - Hacer uso de la búsqueda de ciudades para obtener TODAS las ciudades que devuelve la API
#     # 2 - Por cada ciudad, hacer uso del método de autocompletar, para a partir del código de ciudad, buscar el elemento airports_by_city" de la respuesta
#     #   En ese elemento viene una lista de Aeropuertos con código, nombre, y el nombre del país. Como ya tenemos la ciudad, entonces tenemos lo necesario
#     # IMPORTANTE!: Existe una limitación de llamadas en el tiempo para la versión gratuita de 250 por minuto y 2500 por hora, así que en el proceso
#     # espaciaremos las llamadas a dos segundos una de la siguiente. Será un proceso lento, pero se puede actualizar una o dos veces al mes y nos aporta
#     # toda la información que necesitamos para el modelo Aeropuerto_Mundo
#
#     # 1 - Obtener TODAS las Ciudades
#     all_cities = json.loads(requests.get('https://iatacodes.org/api/v6/cities?api_key=%s' %(globals.IATACode_APIKey), verify = False).__dict__['_content'].decode('utf-8'))['response']
#     time.sleep(2)
#
#     # 2 - Obtener TODOS los Países
#     all_countries = json.loads(requests.get('https://iatacodes.org/api/v6/countries?api_key=%s' %(globals.IATACode_APIKey), verify = False).__dict__['_content'].decode('utf-8'))['response']
#     time.sleep(2)
#
#     # 3 - Por cada ciudad, obtener la información necesaria:
#     # 3.1 - Nombre de la Ciudad
#     # 3.2 - Nombre del País
#     # 3.3 - Código IATA de los Aeropuertos de la Ciudad
#     for city in all_cities:
#         try:
#             # 3.1 - Nombre de la Ciudad
#             city_name = city['name']
#
#             # 3.2 - Nombre del País
#             country_name = None
#             for country in all_countries:
#                 if country['code'] == city['country_code']:
#                     country_name = country['name']
#                     break
#             if not country_name:
#                 continue
#
#             # Si llegamos a este punto es porque se han obtenido los nombres anteriores (ciudad y país)
#             # 3.3 - Código IATA de los Aeropuertos de la Ciudad
#             # Este paso tiene un porciento de posibilidad de error, ya que es un "truco" para poder seguir usando la API de forma Gratuita
#             # 3.3.1 - Hacemos una búsqueda de airports_by_city con el código de la ciudad y nos quedamos con aquellos aeropuertos conde el country_name coincida con el country_name que ya tenemos
#             airports_by_cities = json.loads(requests.get('https://iatacodes.org/api/v6/autocomplete?api_key=%s&query=%s' %(globals.IATACode_APIKey, city['code']), verify = False).__dict__['_content'].decode('utf-8'))['response']['airports_by_cities']
#             time.sleep(2)
#             airports_1 = []
#             for airport_by_city in airports_by_cities:
#                 if airport_by_city['country_name'] == country_name:
#                     airports_1.append(airport_by_city)
#
#             # 3.3.2 - Hacemos otra búsqueda igual a la anterior pero esta vez con el nombre de la ciudad en vez del código y también nos quedamos con los aeropuertos de iguales condiciones
#             airports_by_cities = json.loads(requests.get('https://iatacodes.org/api/v6/autocomplete?api_key=%s&query=%s' %(globals.IATACode_APIKey, city_name), verify = False).__dict__['_content'].decode('utf-8'))['response']['airports_by_cities']
#             time.sleep(2)
#             airports_2 = []
#             for airport_by_city in airports_by_cities:
#                 if airport_by_city['country_name'] == country_name:
#                     airports_2.append(airport_by_city)
#
#             # 3.3.3 - Nos quedamos con la intersección de ambos conjuntos
#             airports_city = []
#             for airport_1 in airports_1:
#                 if airport_1 in airports_2 and not airport_1 in airports_city \
#                         and not 'Railway' in airport_1['name'] \
#                         and not 'Bus Station' in airport_1['name'] \
#                         and not 'Ferry Port' in airport_1['name'] \
#                         and not 'Municipal' in airport_1['name'] \
#                         and not 'Heliport' in airport_1['name'] \
#                         and not 'Military' in airport_1['name']:
#                     airports_city.append(airport_1)
#             for airport_2 in airports_2:
#                 if airport_2 in airports_1 and not airport_2 in airports_city \
#                         and not 'Railway' in airport_2['name'] \
#                         and not 'Bus Station' in airport_2['name'] \
#                         and not 'Ferry Port' in airport_2['name'] \
#                         and not 'Municipal' in airport_2['name'] \
#                         and not 'Heliport' in airport_2['name'] \
#                         and not 'Military' in airport_2['name']:
#                     airports_city.append(airport_2)
#
#             for airport_city in airports_city:
#                 # Si encontramos un Aeropuerto cuyo código de ciudad y nombre de país coincidan con los datos que tenemos, entonces lo registramos
#                 airport_code = airport_city['code']
#                 airport_name = airport_city['name']
#                 country_name = airport_city['country_name']
#
#                 # 3 - Si encontramos un Aeropuerto con toda la información, la guardamos en nuestra Base de Datos
#                 n_aeropuerto_mundo = Aeropuerto_Mundo.nuevo_aeropuerto_mundo(
#                     codigo_iata = airport_code,
#                     nombre = airport_name,
#                     ciudad = city_name,
#                     pais = country_name,
#                 )
#
#             # Una vez analizada una ciudad, esperamos 2 segundos antes de hacer la próxima llamada
#             time.sleep(2)
#         except:
#             print('Ha habido un problema al registrar los Aeropuertos de la Ciudad "%s"' %(city['code']))

def populate_aeropuertos_mundo():
    codigos_iata = []
    for aeropuerto in aeropuertos_mundo:
        codigo_iata = aeropuerto.split(' ')[0]
        codigos_iata.append(codigo_iata)
        Aeropuerto.nuevo_aeropuerto(
            codigo_iata = codigo_iata,
            info_completa = aeropuerto
        )
    # Eliminamos cualquier Aeropuerto que no estuviera en la lista original
    for aeropuerto_mundo in Aeropuerto.objects.all():
        if not aeropuerto_mundo.codigo_iata in codigos_iata:
            aeropuerto_mundo.delete()

def populate_reglas_cancelacion():
    for regla_cancelacion in reglas_cancelacion:
        Regla_Cancelacion.nueva_regla_cancelacion(
            mas_de_x_dias = regla_cancelacion[0],
            menos_de_x_dias = regla_cancelacion[1],
            porciento_devolucion = regla_cancelacion[2],
        )


# Lanza todos los procesos de generación de datos
def populate_all():
    populate_impuestos()
    populate_monedas()
    populate_idiomas()
    populate_paises()
    populate_provincias()
    populate_cuba()
    populate_comisiones()
    populate_intereses()
    populate_destinos()
    populate_fotos_destinos()
    populate_tipos_alojamiento()
    populate_tipos_cambio()
    populate_aeropuertos_mundo()
    populate_aeropuertos_cuba()
    populate_reglas_cancelacion()