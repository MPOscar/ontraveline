import datetime

from django import forms
from servicios.models import Municipio, Provincia, Tipo_Alojamiento

#_____________________________________________SERVICIOS______________________________________________________
DESDE = [
    (None, 'Desde'),
]

HASTA = [
    (None, 'Hasta'),
]
MONTHS = [
    (1, 'Enero'),
    (2, 'Febrero'),
    (3, 'Marzo'),
    (4, 'Abril'),
    (5, 'Mayo'),
    (6, 'Junio'),
    (7, 'Julio'),
    (8, 'Agosto'),
    (9, 'Septiembre'),
    (10, 'Octubre'),
    (11, 'Noviembre'),
    (12, 'Diciembre'),
]

class Add_Regla_Precio(forms.Form):
    fecha_desde = forms.ChoiceField(choices = DESDE + MONTHS, label = 'Desde', required = True, initial = 'Desde')
    fecha_hasta = forms.ChoiceField(choices = HASTA + MONTHS, label = 'Hasta', required = True, initial = 'Hasta')
    precio = forms.DecimalField(label = 'Precio', decimal_places = 2, required = True)

class Add_Indisponibilidad(forms.Form):
    fecha_desde = forms.DateField(label = 'Desde', required = True)
    fecha_hasta = forms.DateField(label = 'Hasta', required = True)

class Modificar_Regla_Precio(forms.Form):
    fecha_desde = forms.ChoiceField(choices = DESDE + MONTHS, label = 'Desde', required = True)
    fecha_hasta = forms.ChoiceField(choices = HASTA + MONTHS, label = 'Hasta', required = True)
    precio = forms.DecimalField(label = 'Precio', decimal_places = 2, required = True)

class URL_Video_Form(forms.Form):
    url_video = forms.URLField(label = 'URL Video Youtube', max_length = 255, required = True)

#_____________________________________________ALOJAMIENTOS___________________________________________________
# ALOJAMIENTO DATOS GENERALES
# Si la modalidad de alquiler seleccionada es "Por Habitación", no es necesaria más descripción del Alojamiento y se pasa a las Habitaciones
class Add_Alojamiento_Datos_Generales(forms.Form):
    acceso_discapacitados = forms.BooleanField(label = 'Acceso Discapacitados', initial = False, required = False)
    cantidad_habitaciones = forms.IntegerField(label = 'Habitaciones', required = True)
    codigo_postal = forms.CharField(label = 'Código Postal', max_length = 8, required = True)
    desayuno_cena = forms.BooleanField(label='Desayuno/Cena', initial=False, required=False)
    descripcion = forms.CharField(label = 'Descripción', max_length = 1024, required = False, widget = forms.Textarea)
    direccion = forms.CharField(label = 'Dirección', max_length = 128, required = True)
    internet = forms.BooleanField(label = 'Internet', initial = False, required = False)
    municipio = forms.ModelChoiceField(label = 'Municipio', queryset = Municipio.objects.order_by('nombre'), empty_label = 'Municipio', required = True)
    nombre = forms.CharField(label = 'Nombre', max_length = 64, required = True)
    parqueo = forms.BooleanField(label='Parqueo', initial = False, required = False)
    patio_terraza_balcon = forms.BooleanField(label = 'Patio/Terraza/Balcón', initial = False, required = False)
    permitido_fumar = forms.BooleanField(label = 'Permitido Fumar', initial = False, required = False)
    permitido_mascotas = forms.BooleanField(label = 'Permitido Mascotas', initial = False, required = False)
    permitido_ninnos = forms.BooleanField(label = 'Permitido Niños', initial = False, required = False)
    piscina = forms.BooleanField(label = 'Piscina', initial = False, required = False)
    provincia = forms.ChoiceField(label = 'Provincia', choices = [[None, 'Provincia']], required = True)
    tipo_alojamiento = forms.ModelChoiceField(label = 'Tipo de Alojamiento', queryset = Tipo_Alojamiento.objects.order_by('tipo'), empty_label = 'Tipo de Alojamiento', required = True)
    transporte_aeropuerto = forms.BooleanField(label = 'Transporte Aeropuerto', initial = False, required = False)

    def __init__(self, provincias_cuba, *args, **kwargs):
        super(Add_Alojamiento_Datos_Generales, self).__init__(*args, **kwargs)
        self.fields['provincia'].choices += provincias_cuba


# ALOJAMIENTO COMPLETO
# En caso de que la modalidad de alquiler sea "Completo" Se requieren más datos sobre las características del Alojamiento
class Add_Alojamiento_Completo(forms.Form):
    aire_acondicionado_central = forms.BooleanField(label = 'Aire Acondicionado Central', initial = False, required = False)
    cantidad_bannos = forms.IntegerField(label = 'Baños', required = True)
    capacidad = forms.IntegerField(label = 'Capacidad', required = True)
    cocina = forms.BooleanField(label = 'Cocina', initial = False, required = False)
    estereo = forms.BooleanField(label = 'Estereo', initial = False, required = False)
    lavadora = forms.BooleanField(label='Lavandería', initial=False, required=False)
    nevera_bar = forms.BooleanField(label = 'Nevera/Bar', initial = False, required = False)
    precio_base = forms.DecimalField(label = 'Precio base', decimal_places = 2, required = True)
    tv = forms.BooleanField(label = 'TV', initial = False, required = False)

# MODIFICAR ALOJAMIENTO (POR HABITACION)
class Modificar_Alojamiento(forms.Form):
    acceso_discapacitados = forms.BooleanField(label = 'Acceso para Discapacitados', initial = False, required = False)
    cantidad_habitaciones = forms.IntegerField(label = 'Habitaciones', required = True)
    codigo_postal = forms.CharField(label = 'Código Postal', max_length = 8, required = True)
    desayuno_cena = forms.BooleanField(label = 'Desayuno/Cena', initial = False, required = False)
    descripcion = forms.CharField(label = 'Descripción', max_length = 1024, required = False, widget = forms.Textarea)
    direccion = forms.CharField(label = 'Dirección Alojamiento', max_length = 128, required = True)
    internet = forms.BooleanField(label = 'Internet', initial = False, required = False)
    municipio = forms.ModelChoiceField(label = 'Municipio', queryset = Municipio.objects.order_by('nombre'), required = True)
    nombre = forms.CharField(label = 'Nombre', max_length = 128, required = True)
    patio_terraza_balcon = forms.BooleanField(label = 'Patio/Terraza/Balcón', initial = False, required=False)
    parqueo = forms.BooleanField(label = 'Parqueo', initial = False, required = False)
    permitido_fumar = forms.BooleanField(label = 'Permitido Fumar', initial = False, required = False)
    permitido_mascotas = forms.BooleanField(label = 'Permitido Mascotas', initial = False, required = False)
    permitido_ninnos = forms.BooleanField(label = 'Permitido Niños', initial = False, required = False)
    piscina = forms.BooleanField(label = 'Piscina', initial = False, required = False)
    provincia = forms.ChoiceField(label = 'Provincia', choices = [[None, 'Provincia']], required = True)
    tipo_alojamiento = forms.ModelChoiceField(label = 'Tipo de Alojamiento', queryset = Tipo_Alojamiento.objects.order_by('tipo'), empty_label = 'Tipo de Alojamiento', required = True)
    transporte_aeropuerto = forms.BooleanField(label = 'Transporte al Aeropuerto', initial = True, required = False)

    def __init__(self, provincias_cuba, *args, **kwargs):
        super(Modificar_Alojamiento, self).__init__(*args, **kwargs)
        self.fields['provincia'].choices += provincias_cuba

# MODIFICAR ALOJAMIENTO COMPLETO
class Modificar_Alojamiento_Completo(Modificar_Alojamiento):
    aire_acondicionado_central = forms.BooleanField(label = 'Aire Acondicionado Central', initial = False, required = False)
    cantidad_bannos = forms.IntegerField(label = 'Baños', required = True)
    capacidad = forms.IntegerField(label = 'Capacidad', required = True)
    cocina = forms.BooleanField(label = 'Cocina', initial = False, required = False)
    estereo = forms.BooleanField(label = 'Estéreo', initial = False, required = False)
    lavadora = forms.BooleanField(label = 'Lavadora', initial = False, required = False)
    nevera_bar = forms.BooleanField(label = 'Nevera/Bar', initial = False, required = False)
    precio_base = forms.IntegerField(label = 'Precio por Noche', required = True)
    tv = forms.BooleanField(label = 'TV', initial = False, required = False)

    def __init__(self, provincias_cuba, *args, **kwargs):
        super(Modificar_Alojamiento, self).__init__(*args, **kwargs)
        self.fields['provincia'].choices += provincias_cuba

# BUSCAR ALOJAMIENTOS POR HABITACIÓN
class Buscar_Alojamiento_Por_Habitacion(forms.Form):
    lugar = forms.CharField(label = 'Lugar', max_length = 64, required = False)
    fecha_entrada = forms.DateField(label = 'Fecha de Entrada', required = False)
    fecha_salida = forms.DateField(label = 'Fecha de Salida', required = False)
    huespedes = forms.IntegerField(label = 'Huéspedes', max_value = 6, required = False)

#_____________________________________________HABITACIONES___________________________________________________
# HABITACIÓN ALOJAMIENTO COMOPLETO
class Add_Habitacion_Alojamiento_Completo(forms.Form):
    aire_acondicionado = forms.BooleanField(label = 'Aire Acondicionado', initial = False, required = False)
    agua_caliente = forms.BooleanField(label = 'Agua Caliente', initial = False, required = False)
    nevera_bar = forms.BooleanField(label = 'Nevera/Bar', initial = False, required = False)
    camas_dobles = forms.IntegerField(label = 'Camas Dobles', max_value = 2, required = True)
    camas_individuales = forms.IntegerField(label = 'Camas Individuales', max_value = 2, required = True)
    balcon = forms.BooleanField(label = 'Balcón', initial = False, required = False)
    caja_fuerte = forms.BooleanField(label = 'Caja Fuerte', initial = False, required = False)
    tv = forms.BooleanField(label = 'TV', initial = False, required = False)
    estereo = forms.BooleanField(label = 'Estéreo', initial = False, required = False)
    ventanas = forms.BooleanField(label = 'Ventanas', initial = False, required = False)
    banno_independiente = forms.BooleanField(label = 'Baño Independiente', initial = False, required = False)

# HABITACIÓN ALOJAMIENTO POR HABITACIÓN
# Tiene todos los Campos de una Habitación de Alojamiento por Habitación, más otros únicos
class Add_Habitacion_Alojamiento_Por_Habitacion(Add_Habitacion_Alojamiento_Completo):
    precio_base = forms.DecimalField(label='Precio base', max_digits = 6, decimal_places = 2, required = True)
    capacidad = forms.IntegerField(label = 'Capacidad', max_value = 6, required = True)

# MODIFICAR HABITACIÓN ALOJAMIENTO COMOPLETO
class Modificar_Habitacion_Alojamiento_Completo(forms.Form):
    agua_caliente = forms.BooleanField(label = 'Agua Caliente', initial = False, required = False)
    aire_acondicionado = forms.BooleanField(label = 'Aire Acondicionado', initial = False, required = False)
    balcon = forms.BooleanField(label = 'Balcón', initial = False, required = False)
    caja_fuerte = forms.BooleanField(label = 'Caja Fuerte', initial = False, required = False)
    camas_dobles = forms.IntegerField(label = 'Camas Dobles', max_value = 2, required = True)
    camas_individuales = forms.IntegerField(label = 'Camas Individuales', max_value = 2, required = True)
    estereo = forms.BooleanField(label = 'Estéreo', initial = False, required = False)
    nevera_bar = forms.BooleanField(label = 'Nevera/Bar', initial = False, required = False)
    tv = forms.BooleanField(label = 'TV', initial = False, required = False)
    ventanas = forms.BooleanField(label = 'Ventanas', initial = False, required = False)

# MODIFICAR HABITACIÓN ALOJAMIENTO POR HABITACIÓN
# Tiene todos los Campos de una Habitación de Alojamiento por Habitación, más otros únicos
class Modificar_Habitacion_Alojamiento_Por_Habitacion(Modificar_Habitacion_Alojamiento_Completo):
    banno_independiente = forms.BooleanField(label='Baño Independiente', initial=False, required=False)
    capacidad = forms.IntegerField(label = 'Capacidad', max_value = 6, required = True)
    precio_base = forms.DecimalField(label = 'Precio base', max_digits = 6, decimal_places = 2, required = True)

# CONSULTAR DISPONIBILIDAD HABITACION ALOJAMIENTO POR HABITACIÓN
class Consultar_Disponibilidad_Alojamiento_Por_Habitacion(forms.Form):
    fecha_entrada = forms.DateField(label = 'Fecha de Entrada', required = True)
    fecha_salida = forms.DateField(label = 'Fecha de Salida', required = True)

    # def __init__(self, habitaciones = (), *args, **kwargs):
    #     super(Consultar_Disponibilidad_Alojamiento_Por_Habitacion, self).__init__(*args, **kwargs)
    #     for habitacion in habitaciones:
    #         self.fields["habitacion_%s" %(habitacion.id)] = forms.IntegerField(label = 'Adultos', required = False)
    #         self.fields["habitacion_%s_ninnos" %(habitacion.id)] = forms.IntegerField(label = 'Niños', required = False)

# CONSULTAR DISPONIBILIDAD HABITACION ALOJAMIENTO POR HABITACIÓN
class Consultar_Disponibilidad_Alojamiento_Completo(forms.Form):
    fecha_entrada = forms.DateField(label = 'Fecha de Entrada', required = True)
    fecha_salida = forms.DateField(label = 'Fecha de Salida', required = True)
    adultos = forms.IntegerField(label = 'Adultos', required = False)
    ninnos = forms.IntegerField(label = 'Niños', required = False)

# SUBIR FOTOS DE HABITACIONES
class Foto_Habitacion_Form(forms.Form):
    foto = forms.ImageField(label = 'Foto', required = False)

# SUBIR FOTOS DE HABITACIONES
class Foto_Servicio_Form(forms.Form):
    foto = forms.ImageField(label = 'Foto', required = False)

#_____________________________________________MOVIL___________________________________________________
# VERIFICAR MOVIL
class Movil_Form(forms.Form):
    numero = forms.IntegerField(label = 'Móvil', required = False)

# CODIGO DE VERIFICACION DEL MOVIL DEL USUARIO
class Verificar_Movil(forms.Form):
    codigo = forms.CharField(label = 'Código de Verificación', required = False)