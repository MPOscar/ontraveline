from random import choice
from decimal import Decimal
import datetime
from django.conf import settings


alpha_base = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
numeric_base = '0123456789'
symbol_base = '!"$&()=?¿^+ç'
alpha_numeric_base = '%s%s' %(alpha_base, numeric_base)
alpha_numeric_symbol_base = '%s%s' %(alpha_numeric_base, symbol_base)

# Variables globales definidas para distinguir rutas en función del entorno de ejecución
def get_static_root():
    # Esta información debe ser consecuente con las variables STATIC_ROOT definidas en los settings__dev.py y settings__prod.py
    if settings.DEBUG:
        return 'static_files'
    else:
        return 'static'

# Convierte una fecha que esté como str en un datetime.date, considerando varias posibilidades de formato de entrada
def str_to_date(_str):
    if '-' in _str:
        splitted = _str.split('-')
    elif '/' in _str:
        splitted = _str.split('/')
    else:
        splitted = [_str[0:4], _str[4:6], _str[6:8]]
    year = int(splitted[0])
    month = int(splitted[1])
    day = int(splitted[2])
    return datetime.date(year, month, day)

def generate_random_activation_code():
    return '%s' %(''.join([choice(alpha_numeric_base) for i in range(30)]))

def generate_random_twilio_code():
    return ''.join([choice(numeric_base) for i in range(6)])

def generate_random_numeric_base(digits = 4):
    # Devuelve un número aleatorio de tantos dígitos como se indique en el argumento del método con "digits"
    return ''.join([choice(numeric_base) for i in range(digits)])

def generate_random_password(characters = 12):
    return ''.join([choice(alpha_numeric_symbol_base) for i in range(characters)])

# WKHTMLTOPDF CONF
# WKH2P_PATH = '/usr/local/bin/wkhtmltopdf'
if settings.DEBUG:
    WKH2P_PATH = '/usr/local/bin/wkhtmltox/bin/wkhtmltopdf'
else:
    WKH2P_PATH = '/usr/local/bin/wkhtmltopdf'

# API Key de Google Maps para visualizar los Mapas interactivos
# En la siguiente URL se accede a la vista de estadísticas de uso de la API en cuestión para la cuenta propietaria (erickmhq)
# https://console.cloud.google.com/apis/dashboard?project=amiable-webbing-180417&hl=es&duration=PT1H (Necesario logearse)
GMaps_APIKey = 'AIzaSyDikLKTov0oGslBQmjzpxqGAQfUCDK5QfE'

# API Key de IATA Codes para realizar consultas de Aeropuertos, ciudades, etc...
# http://iatacodes.org/
IATACode_APIKey = '0dc916f9-0ebb-4410-a01b-f947bb835e53'

# Establecemos una moneda por defecto para usar como referencia de pago en el sitio
codigo_iso_moneda_por_defecto = 'EUR'

# Costo de Gestión de reserva (en CUC)
costo_gestion_cuc = Decimal(10.00)

# Impuesto IVA (decimal)
impuesto_rate = Decimal(0.21)

# Diccionario para relacionar los meses con su orden en el año
meses = {
    '1': 'Enero',
    '2': 'Febrero',
    '3': 'Marzo',
    '4': 'Abril',
    '5': 'Mayo',
    '6': 'Junio',
    '7': 'Julio',
    '8': 'Agosto',
    '9': 'Septiembre',
    '10': 'Octubre',
    '11': 'Noviembre',
    '12': 'Diciembre',
}

cuba = {
    'Provincias': [
        {
            'Nombre': 'PINAR DEL RÍO',
            'Municipios': [
                {
                    'Nombre': 'Consolación del Sur',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Guane',
                    'Descripción': '',
                },
                {
                    'Nombre': 'La Palma',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Los Palacios',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Mantua',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Minas de Matahambre',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Pinar del Río',
                    'Descripción': '',
                },
                {
                    'Nombre': 'San Juan y Martínez',
                    'Descripción': '',
                },
                {
                    'Nombre': 'San Luis',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Sandino',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Viñales',
                    'Descripción': '',
                },
            ],
            'Descripción': '',
        },
        {
            'Nombre': 'ARTEMISA',
            'Municipios': [
                {
                    'Nombre': 'Mariel',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Guanajay',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Caimito',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Bauta',
                    'Descripción': '',
                },
                {
                    'Nombre': 'San Antonio de los Baños',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Güira de Melena',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Alquízar',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Artemisa',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Bahía Honda',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Candelaria',
                    'Descripción': '',
                },
                {
                    'Nombre': 'San Cristóbal',
                    'Descripción': '',
                },
            ],
            'Descripción': '',
        },
        {
            'Nombre': 'LA HABANA',
            'Municipios': [
                {
                    'Nombre': 'Arroyo Naranjo',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Boyeros',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Centro Habana',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Cerro',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Cotorro',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Diez de Octubre',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Guanabacoa',
                    'Descripción': '',
                },
                {
                    'Nombre': 'La Habana del Este',
                    'Descripción': '',
                },
                {
                    'Nombre': 'La Habana Vieja',
                    'Descripción': '',
                },                    {
                    'Nombre': 'La Lisa',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Marianao',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Playa',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Plaza de la Revolución',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Regla',
                    'Descripción': '',
                },
                {
                    'Nombre': 'San Miguel del Padrón',
                    'Descripción': '',
                },
            ],
            'Descripción': '',
        },
        {
            'Nombre': 'MAYABEQUE',
            'Municipios': [
                {
                    'Nombre': 'Bejucal',
                    'Descripción': '',
                },
                {
                    'Nombre': 'San José de las Lajas',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Jaruco',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Santa Cruz del Norte',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Madruga',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Nueva Paz',
                    'Descripción': '',
                },
                {
                    'Nombre': 'San Nicolás de Bari',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Güines',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Melena del Sur',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Batabanó',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Quivicán',
                    'Descripción': '',
                },
            ],
            'Descripción': '',
        },
        {
            'Nombre': 'MATANZAS',
            'Municipios': [
                {
                    'Nombre': 'Calimete',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Cárdenas',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Ciénaga de Zapata',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Colón',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Jagüey Grande',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Jovellanos',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Limonar',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Los Arabos',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Martí',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Matanzas',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Pedro Betancourt',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Perico',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Unión de Reyes',
                    'Descripción': '',
                },
            ],
            'Descripción': '',
        },
        {
            'Nombre': 'CIENFUEGOS',
            'Municipios': [
                {
                    'Nombre': 'Abreus',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Aguada de Pasajeros',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Cienfuegos',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Cruces',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Cumanayagua',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Lajas',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Palmira',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Rodas',
                    'Descripción': '',
                },
            ],
            'Descripción': '',
        },
        {
            'Nombre': 'VILLA CLARA',
            'Municipios': [
                {
                    'Nombre': 'Caibarién',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Camajuaní',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Cienfuegos',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Corralillo',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Encrucijada',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Manicaragua',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Placetas',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Quemado de Güines',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Ranchuelo',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Remedios',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Sagua la Grande',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Santa Clara',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Santo Domingo',
                    'Descripción': '',
                },
            ],
            'Descripción': '',
        },
        {
            'Nombre': 'SANCTI SPÍRITUS',
            'Municipios': [
                {
                    'Nombre': 'Sancti Spíritus',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Trinidad',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Cabaiguán',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Yaguajay',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Jatibonico',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Taguasco',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Fomento',
                    'Descripción': '',
                },
                {
                    'Nombre': 'La Sierpe',
                    'Descripción': '',
                },
            ],
            'Descripción': '',
        },
        {
            'Nombre': 'CIEGO DE ÁVILA',
            'Municipios': [
                {
                    'Nombre': 'Ciego de Ávila',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Morón',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Chambas',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Ciro Redondo',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Majagua',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Florencia',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Venezuela',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Baraguá',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Primero de Enero',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Bolivia',
                    'Descripción': '',
                },
            ],
            'Descripción': '',
        },
        {
            'Nombre': 'CAMAGÜEY',
            'Municipios': [
                {
                    'Nombre': 'Camagüey',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Guáimaro',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Nuevitas',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Céspedes',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Jimaguayú',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Sibanicú',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Esmeralda',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Minas',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Sierra de Cubitas',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Florida',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Najasa',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Vertientes',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Santa Cruz del Sur',
                    'Descripción': '',
                },
            ],
            'Descripción': '',
        },
        {
            'Nombre': 'LAS TUNAS',
            'Municipios': [
                {
                    'Nombre': 'Manatí',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Puerto Padre',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Jesús Menéndez',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Majibacoa',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Las Tunas',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Jobabo',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Colombia',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Amancio',
                    'Descripción': '',
                },
            ],
            'Descripción': '',
        },
        {
            'Nombre': 'GRANMA',
            'Municipios': [
                {
                    'Nombre': 'Bartolomé Masó',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Bayamo',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Buey Arriba',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Campechuela',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Cauto Cristo',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Guisa',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Jiguaní',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Manzanillo',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Media Luna',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Niquero',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Pilón',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Río Cauto',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Yara',
                    'Descripción': '',
                },
            ],
            'Descripción': '',
        },
        {
            'Nombre': 'HOLGUÍN',
            'Municipios': [
                {
                    'Nombre': 'Antilla',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Báguano',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Banes',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Cacocum',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Calixto García',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Cueto',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Frank País',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Jibara',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Holguín',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Mayarí',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Moa',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Rafael Freyre',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Tánamo',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Urbano Noris',
                    'Descripción': '',
                },
            ],
            'Descripción': '',
        },
        {
            'Nombre': 'SANTIAGO DE CUBA',
            'Municipios': [
                {
                    'Nombre': 'Contramaestre',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Guamá',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Mella',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Palma Soriano',
                    'Descripción': '',
                },
                {
                    'Nombre': 'San Luis',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Santiago de Cuba',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Segundo Frente',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Songo-La Maya',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Tercer Frente',
                    'Descripción': '',
                },
            ],
            'Descripción': '',
        },
        {
            'Nombre': 'GUANTÁNAMO',
            'Municipios': [
                {
                    'Nombre': 'Baracoa',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Caimanera',
                    'Descripción': '',
                },
                {
                    'Nombre': 'El Salvador',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Guantánamo',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Imías',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Maisí',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Manuel Tames',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Niceto Pérez',
                    'Descripción': '',
                },
                {
                    'Nombre': 'San Antonio del Sur',
                    'Descripción': '',
                },
                {
                    'Nombre': 'Yateras',
                    'Descripción': '',
                },
            ],
            'Descripción': '',
        },
        {
            'Nombre': 'ISLA DE LA JUVENTUD',
            'Municipios': [
                {
                    'Nombre': 'Isla de la Juventud',
                    'Descripción': '',
                },
            ],
            'Descripción': '',
        },
    ],
    'Unión Europea': False,
    'Prefijo Móvil': '53',
    'Código_ISO_Alfa2': 'CU',
    'Código_ISO_Alfa3': 'CUB',
    'Código_ISO_Numérico': '192',
    'Moneda': 'CUC',
    'Idioma': 'ES',
}

intereses = [
    'HISTORIA',
    'MUSEO',
    'SALSA',
    'PLAYA',
    'SHOPPING',
    'ACUARIO',
    'ARQUITECTURA',
    'MONUMENTO',
    'IGLESIA',
    'CATEDRAL',
    'CULTURA',
    'ZOOLÓGICO',
    'MÚSICA',
    'VIDA NOCTURNA',
    'GOLF',
    'BALNEARIO',
    'RESORT',
    'PARQUE',
    'ÁREA PROTEGIDA',
    'ALFARERÍA',
    'JARDÍN BOTÁNICO',
    'CLUB NÁUTICO',
    'CUEVA',
    'SENDERISMO',
    'CICLISMO',
    'PINTURA',
    'PREHISTORIA',
    'CUARTEL',
    'CHE GUEVARA',
    'MAUSOLEO',
    'ARRECIFES',
    'BUCEO',
    'PASO',
    'TESTUDINES',
    'IGUANA',
    'PESCA',
    'ESNÓRQUEL',
    'DELFINES',
    'TEATRO',
    'RÍO',
    'BALLET',
    'KITESURF',
    'JAZZ',
    'NATURALEZA',
    'CASCADA',
    'TIROLESA',
    'TURISMO ECOLÓGICO',
    'ESÓRQUEL',
    'JARDÍN',
    'COCODRILOS',
    'LAGUNA COSTERA',
    'SAFARI',
    'RESERVA NATURAL',
    'FARO',
    'EXCURSIONISMO',
    'MONTAÑA',
    'CAZA',
    'GRULLAS',
    'AGUAS TERMALES',
    'CASTILLO',
    'ARTE',
    'ESCULTURA',
    'BASÍLICA',
    'RESTAURANT',
    'PLAZA',
    'CONVENTO',
    'LUNA DE MIEL',
    'PUENTE',
]



destinos = [
    {'provincia': 'CAMAGÜEY', 'nombre': 'CAMAGÜEY', 'intereses': 'BALLET,HISTORIA,IGLESIA,CATEDRAL', 'descripcion': ''},
    {'provincia': 'CIEGO DE ÁVILA', 'nombre': 'CIEGO DE ÁVILA', 'intereses': 'TEATRO,JARDÍN,ZOOLÓGICO,HISTORIA', 'descripcion': ''},
    {'provincia': 'CIENFUEGOS', 'nombre': 'CIENFUEGOS', 'intereses': 'JARDÍN BOTÁNICO,CLUB NÁUTICO,PLAYA', 'descripcion': ''},
    {'provincia': 'GUANTÁNAMO', 'nombre': 'BARACOA', 'intereses': 'PLAYA,HISTORIA,RÍO,ESNÓRQUEL,MÚSICA', 'descripcion': ''},
    {'provincia': 'GUANTÁNAMO', 'nombre': 'GUANTÁNAMO', 'intereses': 'CULTURA,ÁREA PROTEGIDA,HISTORIA', 'descripcion': ''},
    {'provincia': 'HOLGUÍN', 'nombre': 'HOLGUÍN', 'intereses': 'DELFINES,PLAYA,VIDA NOCTURNA,GOLF', 'descripcion': ''},
    {'provincia': 'ISLA DE LA JUVENTUD', 'nombre': 'NUEVA GERONA', 'intereses': 'PLAYA,MUSEO,PARQUE', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'ACUARIO NACIONAL DE CUBA', 'intereses': 'ACUARIO', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'BAHÍA DE LA HABANA', 'intereses': 'HISTORIA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'CAPITOLIO DE LA HABANA', 'intereses': 'HISTORIA,ARQUITECTURA,MONUMENTO', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'CASTILLO DE LA PUNTA', 'intereses': 'CASTILLO,HISTORIA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'CASTILLO DE LA REAL FUERZA DE LA HABANA', 'intereses': 'CASTILLO,HISTORIA,ARQUITECTURA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'CASTILLO DE LOS TRES REYES DEL MORRO', 'intereses': 'CASTILLO,HISTORIA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'CATEDRAL DE LA HABANA', 'intereses': 'CATEDRAL,ARQUITECTURA,HISTORIA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'CEMENTERIO CRISTÓBAL COLÓN', 'intereses': 'MONUMENTO', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'COJÍMAR', 'intereses': 'PESCA,HISTORIA,MUSEO,PLAYA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'CONSERVATORIO DE SAN FRANCISCO DE ASÍS', 'intereses': 'CONVENTO,BASÍLICA,IGLESIA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'CRISTO DE LA HABANA', 'intereses': 'ESCULTURA,HISTORIA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'FINCA VIGÍA', 'intereses': 'MUSEO,CULTURA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'FORTALEZA DE SAN CARLOS DE LA CABAÑA', 'intereses': 'CHE GUEVARA,HISTORIA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'GRAN TEATRO DE LA HABANA', 'intereses': 'TEATRO,CULTURA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'LA BODEGUITA DEL MEDIO', 'intereses': 'RESTAURANT,HISTORIA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'LA HABANA', 'intereses': 'HISTORIA,MUSEO,SALSA,PLAYA,SHOPPING,ACUARIO,ARQUITECTURA,MONUMENTO,IGLESIA,CATEDRAL,CULTURA,ZOOLÓGICO,MÚSICA,MONUMENTO,VIDA NOCTURNA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'LA HABANA VIEJA', 'intereses': 'PASO,HISTORIA,ARQUITECTURA,MONUMENTO', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'MONUMENTO A JOSÉ MARTÍ', 'intereses': 'MONUMENTO,HISTORIA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'MUSEO DE LA REVOLUCIÓN', 'intereses': 'MUSEO,HISTORIA,ARQUITECTURA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'MUSEO NACIONAL DE BELLAS ARTES', 'intereses': 'MUSEO,ARTE,CULTURA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'MUSEO NACIONAL DE CIENCIAS NATURALES', 'intereses': 'MUSEO', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'MUSEO NAPOLEÓNICO', 'intereses': 'MUSEO', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'PALACIO DE LOS CAPITANES GENERALES', 'intereses': 'MUSEO,CULTURA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'PARQUE JOHN LENNON', 'intereses': 'PARQUE', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'PARQUE LENIN', 'intereses': 'PARQUE,NATURALEZA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'PASEO DEL PRADO', 'intereses': 'PASO,ARQUITECTURA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'PLAZA DE ARMAS', 'intereses': 'HISTORIA,MUSEO,PLAZA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'PLAZA DE LA CATEDRAL', 'intereses': 'CATEDRAL,ARQUITECTURA,HISTORIA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'PLAZA DE LA REVOLUCIÓN', 'intereses': 'CHE GUEVARA,JAZZ,MONUMENTO,HISTORIA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'PLAZA VIEJA', 'intereses': 'PLAZA,ARQUITECTURA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'UNIVERSIDAD DE LA HABANA', 'intereses': 'MONUMENTO,HISTORIA,CULTURA', 'descripcion': ''},
    {'provincia': 'LAS TUNAS', 'nombre': 'LAS TUNAS', 'intereses': 'VIDA NOCTURNA,PLAYA,HISTORIA,CULTURA', 'descripcion': ''},
    {'provincia': 'MATANZAS', 'nombre': 'BAHÍA DE COCHINOS', 'intereses': 'PLAYA,BUCEO,ESNÓRQUEL,MUSEO,CUEVA', 'descripcion': ''},
    {'provincia': 'MATANZAS', 'nombre': 'CÁRDENAS', 'intereses': 'MUSEO,HISTORIA,MONUMENTO,PLAYA', 'descripcion': ''},
    {'provincia': 'MATANZAS', 'nombre': 'DELFINARIO DE VARADERO', 'intereses': 'DELFINES,LUNA DE MIEL,PLAYA', 'descripcion': ''},
    {'provincia': 'MATANZAS', 'nombre': 'MATANZAS', 'intereses': 'CUEVA,TEATRO,PLAYA,SALSA,RÍO,HISTORIA', 'descripcion': ''},
    {'provincia': 'MATANZAS', 'nombre': 'PARQUE JOSONE', 'intereses': 'PARQUE', 'descripcion': ''},
    {'provincia': 'MATANZAS', 'nombre': 'PLAYA GIRÓN', 'intereses': 'PLAYA,ESNÓRQUEL,BUCEO,MUSEO,HISTORIA', 'descripcion': ''},
    {'provincia': 'MATANZAS', 'nombre': 'PUENTE DE BACUNAYAGUA', 'intereses': 'PUENTE', 'descripcion': ''},
    {'provincia': 'MATANZAS', 'nombre': 'VARADERO', 'intereses': 'PLAYA,GOLF,BALNEARIO,SHOPPING,RESORT,MÚSICA,VIDA NOCTURNA,PARQUE,ÁREA PROTEGIDA', 'descripcion': ''},
    {'provincia': 'PINAR DEL RÍO', 'nombre': 'MURAL DE LA PREHISTORIA', 'intereses': 'PREHISTORIA,PINTURA', 'descripcion': ''},
    {'provincia': 'PINAR DEL RÍO', 'nombre': 'PINAR DEL RÍO', 'intereses': 'CATEDRAL,MUSEO,HISTORIA', 'descripcion': ''},
    {'provincia': 'PINAR DEL RÍO', 'nombre': 'VIÑALES', 'intereses': 'CUEVA,SENDERISMO,CICLISMO,PINTURA,PREHISTORIA', 'descripcion': ''},
    {'provincia': 'SANCTI SPÍRITUS', 'nombre': 'SANCTI SPÍRITUS', 'intereses': 'IGLESIA,HISTORIA,MUSEO,NATURALEZA', 'descripcion': ''},
    {'provincia': 'SANTIAGO DE CUBA', 'nombre': 'BASÍLICA DE NUESTRA SEÑORA DE LA CARIDAD DEL COBRE', 'intereses': 'BASÍLICA', 'descripcion': ''},
    {'provincia': 'SANTIAGO DE CUBA', 'nombre': 'CUARTEL MONCADA', 'intereses': 'HISTORIA', 'descripcion': ''},
    {'provincia': 'SANTIAGO DE CUBA', 'nombre': 'PLAZA DE LA REVOLUCIÓN DE SANTIAGO DE CUBA', 'intereses': 'PLAZA,HISTORIA,MONUMENTO', 'descripcion': ''},
    {'provincia': 'SANTIAGO DE CUBA', 'nombre': 'SANTIAGO DE CUBA', 'intereses': 'PLAYA,MÚSICA,CATEDRAL,CUARTEL,CULTURA'},
    {'provincia': 'VILLA CLARA', 'nombre': 'MAUSOLEO DEL CHE GUEVARA', 'intereses': 'CHE GUEVARA', 'descripcion': ''},
    {'provincia': 'VILLA CLARA', 'nombre': 'SANTA CLARA', 'intereses': 'CHE GUEVARA,MAUSOLEO,MONUMENTO', 'descripcion': ''},
    {'provincia': 'SANTIAGO DE CUBA', 'nombre': 'BACONAO', 'intereses': 'PLAYA,PARQUE,ACUARIO,PREHISTORIA', 'descripcion': ''},
    {'provincia': 'GRANMA', 'nombre': 'BAYAMO', 'intereses': 'HISTORIA,IGLESIA,CATEDRAL,MUSEO', 'descripcion': ''},
    {'provincia': 'VILLA CLARA', 'nombre': 'CAIBARIÉN', 'intereses': 'PESCA,PLAYA,HISTORIA,ARQUITECTURA', 'descripcion': ''},
    {'provincia': 'CIEGO DE ÁVILA', 'nombre': 'CAYO GUILLERMO', 'intereses': 'PLAYA,KITESURF,PESCA,ESNÓRQUEL,BUCEO', 'descripcion': ''},
    {'provincia': 'CIENFUEGOS', 'nombre': 'CASTILLO DE JAGUA', 'intereses': 'CASTILLO', 'descripcion': ''},
    {'provincia': 'SANTIAGO DE CUBA', 'nombre': 'CASTILLO DE SAN PEDRO DE LA ROCA', 'intereses': 'CASTILLO,ARQUITECTURA,HISTORIA,MUSEO', 'descripcion': ''},
    {'provincia': 'CIEGO DE ÁVILA', 'nombre': 'CAYO COCO', 'intereses': 'PLAYA,RESORT,ARRECIFES,BUCEO', 'descripcion': ''},
    {'provincia': 'ISLA DE LA JUVENTUD', 'nombre': 'CAYO LARGO DEL SUR', 'intereses': 'PLAYA,TESTUDINES,BUCEO,IGUANA,PESCA', 'descripcion': ''},
    {'provincia': 'PINAR DEL RÍO', 'nombre': 'CAYO LEVISA', 'intereses': 'PLAYA', 'descripcion': ''},
    {'provincia': 'HOLGUÍN', 'nombre': 'CAYO SAETÍA', 'intereses': 'CAZA,RESERVA NATURAL,NATURALEZA', 'descripcion': ''},
    {'provincia': 'VILLA CLARA', 'nombre': 'CAYO SANTA MARÍA', 'intereses': 'PLAYA,ESNÓRQUEL,DELFINES,PESCA', 'descripcion': ''},
    {'provincia': 'SANTIAGO DE CUBA', 'nombre': 'CEMENTERIO SANTA IFIGENIA', 'intereses': 'MONUMENTO,HISTORIA', 'descripcion': ''},
    {'provincia': 'MATANZAS', 'nombre': 'CUEVAS DE BELLAMAR', 'intereses': 'CUEVA', 'descripcion': ''},
    {'provincia': 'HOLGUÍN', 'nombre': 'GIBARA', 'intereses': 'CUEVA,PLAYA,IGLESIA,HISTORIA,SAFARI', 'descripcion': ''},
    {'provincia': 'SANTIAGO DE CUBA', 'nombre': 'GRAN PIEDRA', 'intereses': 'JARDÍN BOTÁNICO,SAFARI,JARDÍN,PARQUE', 'descripcion': ''},
    {'provincia': 'SANTIAGO DE CUBA', 'nombre': 'GUAMÁ', 'intereses': 'COCODRILOS,LAGUNA COSTERA,CULTURA', 'descripcion': ''},
    {'provincia': 'HOLGUÍN', 'nombre': 'GUARDALAVACA', 'intereses': 'PLAYA,ESNÓRQUEL,VIDA NOCTURNA,BUCEO', 'descripcion': ''},
    {'provincia': 'SANCTI SPÍRITUS', 'nombre': 'IGLESIA PARROQUIAL MAYOR DEL ESPÍRITU SANTO', 'intereses': 'IGLESIA', 'descripcion': ''},
    {'provincia': 'MATANZAS', 'nombre': 'IGLESIA SANTA ELVIRA', 'intereses': 'IGLESIA', 'descripcion': ''},
    {'provincia': 'VILLA CLARA', 'nombre': 'JIBACOA', 'intereses': 'PLAYA,ESNÓRQUEL,PESCA,BUCEO,CUEVA', 'descripcion': ''},
    {'provincia': 'ARTEMISA', 'nombre': 'LAS TERRAZAS', 'intereses': 'TIROLESA,TURISMO ECOLÓGICO,CASCADA', 'descripcion': ''},
    {'provincia': 'GRANMA', 'nombre': 'MANZANILLO', 'intereses': 'PLAYA,SHOPPING,HISTORIA', 'descripcion': ''},
    {'provincia': 'PINAR DEL RÍO', 'nombre': 'MARÍA LA GORDA', 'intereses': 'PLAYA,ESNÓRQUEL,BUCEO,PESCA', 'descripcion': ''},
    {'provincia': 'CIEGO DE ÁVILA', 'nombre': 'MORÓN', 'intereses': 'COCODRILOS,VIDA NOCTURNA,PLAYA', 'descripcion': ''},
    {'provincia': 'CIENFUEGOS', 'nombre': 'PALACIO DE VALLE', 'intereses': 'ARQUITECTURA', 'descripcion': ''},
    {'provincia': 'CIENFUEGOS', 'nombre': 'PALACIO FERRER', 'intereses': 'ARQUITECTURA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'PARQUE CENTRAL', 'intereses': 'PARQUE', 'descripcion': ''},
    {'provincia': 'SANCTI SPÍRITUS', 'nombre': 'PARQUE CENTRAL CÉSPEDES', 'intereses': 'PARQUE', 'descripcion': ''},
    {'provincia': 'SANTIAGO DE CUBA', 'nombre': 'PARQUE CÉSPEDES', 'intereses': 'PARQUE', 'descripcion': ''},
    {'provincia': 'VILLA CLARA', 'nombre': 'PARQUE DEL TREN BLINDADO', 'intereses': 'MONUMENTO,HISTORIA', 'descripcion': ''},
    {'provincia': 'CAMAGÜEY', 'nombre': 'PARQUE IGNACIO AGRAMONTE', 'intereses': 'PARQUE,HISTORIA,MONUMENTO', 'descripcion': ''},
    {'provincia': 'CIENFUEGOS', 'nombre': 'PARQUE JOSÉ MARTÍ', 'intereses': 'PARQUE', 'descripcion': ''},
    {'provincia': 'HOLGUÍN', 'nombre': 'PARQUE NACIONAL ALEJANDRO DE HUMBOLDT', 'intereses': 'PARQUE,ÁREA PROTEGIDA,NATURALEZA', 'descripcion': ''},
    {'provincia': 'GRANMA', 'nombre': 'PARQUE NACIONAL DESEMBARCO DEL GRANMA', 'intereses': 'PARQUE,NATURALEZA', 'descripcion': ''},
    {'provincia': 'SANTIAGO DE CUBA', 'nombre': 'PARQUE NACIONAL TURQUINO', 'intereses': 'PARQUE,EXCURSIONISMO,MONTAÑA', 'descripcion': ''},
    {'provincia': 'PINAR DEL RÍO', 'nombre': 'PENÍNSULA DE GUANAHACABIBES', 'intereses': 'RESERVA NATURAL,CHE GUEVARA,FARO', 'descripcion': ''},
    {'provincia': 'SANTIAGO DE CUBA', 'nombre': 'PICO TURQUINO', 'intereses': 'MONTAÑA,SENDERISMO', 'descripcion': ''},
    {'provincia': 'SANCTI SPÍRITUS', 'nombre': 'PLAYA ANCÓN', 'intereses': 'ESÓRQUEL,PLAYA', 'descripcion': ''},
    {'provincia': 'MATANZAS', 'nombre': 'PLAYA LARGA', 'intereses': 'ESNÓRQUEL,PLAYA', 'descripcion': ''},
    {'provincia': 'HOLGUÍN', 'nombre': 'PLAYA PESQUERO', 'intereses': 'PLAYA', 'descripcion': ''},
    {'provincia': 'LA HABANA', 'nombre': 'PLAZA DE SAN FRANCISCO', 'intereses': 'IGLESIA,PLAZA', 'descripcion': ''},
    {'provincia': 'SANCTI SPÍRITUS', 'nombre': 'PLAZA MAYOR DE TRINIDAD', 'intereses': 'ARQUITECTURA,MUSEO,PLAZA', 'descripcion': ''},
    {'provincia': 'CAMAGÜEY', 'nombre': 'PLAZA SAN JUAN DE DIOS', 'intereses': 'PLAZA,HISTORIA', 'descripcion': ''},
    {'provincia': 'MATANZAS', 'nombre': 'RESERVA ECOLÓGICA DE VARAHICACOS', 'intereses': 'RESERVA NATURAL,NATURALEZA,PARQUE', 'descripcion': ''},
    {'provincia': 'VILLA CLARA', 'nombre': 'SAN JUAN DE LOS REMEDIOS', 'intereses': 'IGLESIA,CULTURA,PLAYA,MUSEO,HISTORIA', 'descripcion': ''},
    {'provincia': 'ARTEMISA', 'nombre': 'SOROA', 'intereses': 'CASCADA,JARDÍN,JARDÍN BOTÁNICO', 'descripcion': ''},
    {'provincia': 'VILLA CLARA', 'nombre': 'TEATRO DE LA CARIDAD', 'intereses': 'TEATRO,CULTURA', 'descripcion': ''},
    {'provincia': 'SANCTI SPÍRITUS', 'nombre': 'TOPE DE COLLANTES', 'intereses': 'PARQUE,SENDERISMO,NATURALEZA,CASCADA', 'descripcion': ''},
    {'provincia': 'SANCTI SPÍRITUS', 'nombre': 'TRINIDAD', 'intereses': 'PLAYA,SALSA,MUSEO,IGLESIA,ALFARERÍA', 'descripcion': ''},
    {'provincia': 'SANCTI SPÍRITUS', 'nombre': 'VALLE DE LOS INGENIOS', 'intereses': 'HISTORIA,GRULLAS,AGUAS TERMALES,CAZA,PESCA', 'descripcion': ''},
]

tipos_alojamiento = [
    {'tipo': 'Mansión'},
    {'tipo': 'Casa'},
    {'tipo': 'Apartamento'},
]

impuestos = [
    {'nombre': 'IVA Español', 'porciento': 0.21},
]