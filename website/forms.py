from django import forms
import datetime

from servicios.models import Provincia, Municipio, Destino

class Contacto_Form(forms.Form):
    nombre = forms.CharField(label = 'Nombre', max_length = 64, required = False)
    email = forms.EmailField(label = 'E-Mail', max_length = 64, required = True)
    message = forms.CharField(label = 'Mensaje', max_length = 1024, widget = forms.Textarea, required = True)
    # captcha = ReCaptchaField()

class Buscar_Alojamientos(forms.Form):
    provincia = forms.ModelChoiceField(label = 'Provincia', queryset = Provincia.objects.order_by('nombre'), required = False, initial = 'Provincia')
    municipio = forms.ModelChoiceField(label = 'Municipio', queryset = Municipio.objects.order_by('provincia__nombre', 'nombre'), required = False, initial = 'Municipio')
    destino = forms.ModelChoiceField(label = 'Destino', queryset = Destino.objects.order_by('nombre'), required = False, initial = 'Destino')
    entrada = forms.DateField(label = 'Entrada', required = False)
    salida = forms.DateField(label = 'Salida', required = False)
    huespedes = forms.IntegerField(label = 'Huéspedes', required = False)
    habitaciones = forms.IntegerField(label = 'Habitaciones', required = False)

HUESPEDES = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
)

ORDENAR_POR = (
    ('nombre_asc', 'Nombre (A - Z)'),
    ('nombre_desc', 'Nombre (Z - A)'),
    ('precio_asc', 'Precio (Asc)'),
    ('precio_desc', 'Precio (Desc)'),
    ('provincia_asc', 'Provincia (Asc)'),
    ('provincia_desc', 'Provincia (Desc)'),
    ('municipio_asc', 'Municipio (Asc)'),
    ('municipio_desc', 'Municipio (Desc)'),
    ('opinion_asc', 'Opinion (Asc)'),
    ('opinion_desc', 'Opinion (Desc)'),
    ('popularidad_asc', 'Reservas (Asc)'),
    ('popularidad_desc', 'Reservas (Desc)'),
    ('habitaciones_asc', 'Habitaciones (Asc)'),
    ('habitaciones_desc', 'Habitaciones (Desc)'),
)

class Buscar_Alojamientos_Por_Habitacion(forms.Form):
    # Filtro principal de Alojaientos
    lugar = forms.CharField(label = 'Dónde', max_length = 64, required = False)
    fecha_entrada = forms.DateField(label = 'Entrada', required = False, initial = datetime.date.today() + datetime.timedelta(days = 2))
    fecha_salida = forms.DateField(label = 'Salida', required = False, initial = datetime.date.today() + datetime.timedelta(days = 9))
    huespedes = forms.ChoiceField(label = 'Huéspedes', choices = HUESPEDES)

    # características generales del Alojamiento
    rating_1_estrella = forms.BooleanField(label = '1 estrella', required = False, initial = False)
    rating_2_estrellas = forms.BooleanField(label = '2 estrellas', required = False, initial = False)
    rating_3_estrellas = forms.BooleanField(label = '3 estrellas', required = False, initial = False)
    rating_4_estrellas = forms.BooleanField(label = '4 estrellas', required = False, initial = False)
    rating_5_estrellas = forms.BooleanField(label = '5 estrellas', required = False, initial = False)

    acceso_discapacitados = forms.BooleanField(label = 'Acceso Discapacitados', initial = False, required = False)
    desayuno_cena = forms.BooleanField(label = 'Desayuno/Cena', initial = False, required = False)
    internet = forms.BooleanField(label = 'Internet', initial = False, required = False)
    parqueo = forms.BooleanField(label = 'Parqueo', initial = False, required = False)
    patio_terraza_balcon = forms.BooleanField(label = 'Patio/Terraza/Balcón', initial = False, required = False)
    permitido_fumar = forms.BooleanField(label = 'Permitido Fumar', initial = False, required = False)
    permitido_mascotas = forms.BooleanField(label = 'Permitido Mascotas', initial = False, required = False)
    permitido_ninnos = forms.BooleanField(label = 'Permitido Niños', initial = False, required = False)
    piscina = forms.BooleanField(label = 'Piscinas', initial = False, required = False)
    transporte_aeropuerto = forms.BooleanField(label = 'Transporte Aeropuerto', initial = False, required = False)
    # Posibles Tipos de Alojamiento (Ver estructura y registros del modelo: servicios/models.py/Tipo_Alojamiento
    casa = forms.BooleanField(label = 'Casa', required = False, initial = False)
    apartamento = forms.BooleanField(label = 'Apartamento', required = False, initial = False)
    mansion = forms.BooleanField(label = 'Mansión', required = False, initial = False)

    aire_acondicionado = forms.BooleanField(label = 'Aire Acondicionado', initial = False, required = False)
    agua_caliente = forms.BooleanField(label = 'Agua Caliente', initial = False, required = False)
    nevera_bar = forms.BooleanField(label = 'Nevera/Bar', initial = False, required = False)
    balcon = forms.BooleanField(label = 'Balcón', initial = False, required = False)
    caja_fuerte = forms.BooleanField(label = 'Caja Fuerte', initial = False, required = False)
    tv = forms.BooleanField(label = 'TV', initial = False, required = False)
    estereo = forms.BooleanField(label = 'Estéreo', initial = False, required = False)
    ventanas = forms.BooleanField(label = 'Ventanas', initial = False, required = False)
    banno_independiente = forms.BooleanField(label = 'Baño Independiente', initial = False, required = False)

    ordenar_por = forms.ChoiceField(label = 'Ordenar por', choices = ORDENAR_POR, required = False, widget = forms.Select(attrs={'onchange': 'this.form.submit();'}))
    rango_precio = forms.CharField(label = 'Rango de Precios', max_length = 256, required = False)

    # precio_max y precio_min se pueden tratar como dos Inputs, pero intentaremos usar el selector deslizable del template original

class Buscar_Alojamientos_Completos(forms.Form):
    # Filtro principal de Alojaientos
    lugar = forms.CharField(label = 'Dónde', max_length = 64, required = False)
    fecha_entrada = forms.DateField(label = 'Entrada', required = False, initial = datetime.date.today() + datetime.timedelta(days = 2))
    fecha_salida = forms.DateField(label = 'Salida', required = False, initial = datetime.date.today() + datetime.timedelta(days = 9))
    huespedes = forms.ChoiceField(label = 'Huéspedes', choices = HUESPEDES)

    # características generales del Alojamiento
    rating_1_estrella = forms.BooleanField(label = '1 estrella', required = False, initial = False)
    rating_2_estrellas = forms.BooleanField(label = '2 estrellas', required = False, initial = False)
    rating_3_estrellas = forms.BooleanField(label = '3 estrellas', required = False, initial = False)
    rating_4_estrellas = forms.BooleanField(label = '4 estrellas', required = False, initial = False)
    rating_5_estrellas = forms.BooleanField(label = '5 estrellas', required = False, initial = False)

    acceso_discapacitados = forms.BooleanField(label = 'Acceso Discapacitados', initial = False, required = False)
    aire_acondicionado = forms.BooleanField(label = 'Aire Acondicionado', initial = False, required = False)
    cantidad_habitaciones = forms.IntegerField(label = 'Cantidad de Habitaciones', required = False)
    cocina = forms.BooleanField(label = 'Cocina', initial = False, required = False)
    desayuno_cena = forms.BooleanField(label='Desayuno/Cena', initial=False, required=False)
    internet = forms.BooleanField(label = 'Internet', initial = False, required = False)
    parqueo = forms.BooleanField(label = 'Parqueo', initial = False, required = False)
    patio_terraza_balcon = forms.BooleanField(label = 'Patio/Terraza/Balcón', initial = False, required = False)
    permitido_fumar = forms.BooleanField(label = 'Permitido Fumar', initial = False, required = False)
    permitido_mascotas = forms.BooleanField(label = 'Permitido Mascotas', initial = False, required = False)
    permitido_ninnos = forms.BooleanField(label = 'Permitido Niños', initial = False, required = False)
    piscina = forms.BooleanField(label = 'Piscinas', initial = False, required = False)
    transporte_aeropuerto = forms.BooleanField(label = 'Transporte Aeropuerto', initial = False, required = False)
    # Posibles Tipos de Alojamiento (Ver estructura y registros del modelo: servicios/models.py/Tipo_Alojamiento
    casa = forms.BooleanField(label = 'Casa', required = False, initial = False)
    apartamento = forms.BooleanField(label = 'Apartamento', required = False, initial = False)
    mansion = forms.BooleanField(label = 'Mansión', required = False, initial = False)
    agua_caliente = forms.BooleanField(label = 'Agua Caliente', initial = False, required = False)
    nevera_bar = forms.BooleanField(label = 'Nevera/Bar', initial = False, required = False)
    balcon = forms.BooleanField(label = 'Balcón', initial = False, required = False)
    caja_fuerte = forms.BooleanField(label = 'Caja Fuerte', initial = False, required = False)
    tv = forms.BooleanField(label = 'TV', initial = False, required = False)
    estereo = forms.BooleanField(label = 'Estéreo', initial = False, required = False)
    lavadora = forms.BooleanField(label = 'Lavadora', initial = False, required = False)

    ordenar_por = forms.ChoiceField(label = 'Ordenar por', choices = ORDENAR_POR, required = False, widget = forms.Select(attrs={'onchange': 'this.form.submit();'}))
    rango_precio = forms.CharField(label = 'Rango de Precios', max_length = 256, required = False)

