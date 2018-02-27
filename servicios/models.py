from decimal import Decimal
from django.db.models import Q
from django.db import models
from forex_python.converter import CurrencyRates
from PIL import Image, ImageEnhance
import os, shutil, datetime, random
from support.globals import *
from pagos.models import Pago

class Idioma(models.Model):
    nombre = models.CharField('Nombre', max_length = 32, blank = False, null = False, unique = False)
    codigo = models.CharField('Código', max_length = 3, blank = True, null = True, unique = False)

    @classmethod
    def nuevo_idioma(cls, nombre, codigo):
        n_idioma = cls.objects.create(
            nombre = nombre,
            codigo = codigo,
        )
        return n_idioma

    def modificar_idioma(self, nombre):
        self.nombre = nombre
        self.save()
        return self

    def eliminar(self):
        self.delete()
    class Meta:
        verbose_name_plural = 'Idiomas'

    def __str__(self):
        return self.codigo

class Moneda(models.Model):
    codigo_iso = models.CharField('Código ISO', max_length = 3, blank = False, null = False, unique = False)
    menu = models.BooleanField('Mostrar en Menú', blank = True, default = False)

    @classmethod
    # Devuelve el objeto moneda que debe mostrarse para cada usuario por defecto al abrir la Web.
    # Si se le indica el id de la moneda, lo obtiene de la Base de Datos; en caso contrario, lo toma de la configuración en uso
    def get_user_moneda(cls, moneda_id):
        if moneda_id:
            return cls.objects.get(id = moneda_id)
        else:
            # Se establece el Euro como moneda por defecto
            return Moneda.objects.get(codigo_iso = 'EUR')

    @classmethod
    # Añade una nueva moneda
    def nueva_moneda(cls, codigo_iso, menu):
        # Comprueba que no exista ninguna moneda guardada con el mismo nombre ni el mismo codigo_iso
        if cls.objects.filter(codigo_iso = codigo_iso):
            print('Ya existe una moneda con código ISO %s' %(codigo_iso))
        else:
            n_moneda = cls.objects.create(
                codigo_iso = codigo_iso,
                menu = menu,
            )
            print('Se ha creado correctamente la moneda %s' %(codigo_iso))
            return n_moneda

    # Comprueba que los nuevos valores de nombre o código ISO no correcponden con ninguno de los almacenados hasta ahora
    def modificar_moneda(self, codigo_iso, menu):
        self.codigo_iso = codigo_iso
        self.menu = menu
        self.save()
        print('Se ha modificado correctamente la moneda %s' %(self.codigo_iso))
        return self

    @classmethod
    # Define una moneda a partis de la configuración establecida en globals.py
    def get_moneda_por_defecto(cls):
        return cls.objects.get(codigo_iso = codigo_iso_moneda_por_defecto)

    def eliminar(self):
        self.delete()

    class Meta:
        verbose_name_plural = 'Monedas'

    def __str__(self):
        return self.codigo_iso

# Definición de la variable global de configuración del sitio
# conf = Configuracion.get_configuracion_en_uso()

'''
Los países se clasifican fundamentalmente en función de si pertenecen o no a la Unión Europea. Sin tener en cuenta si la Empresa
Magestree opera bajo el Régimen de Operador Intracomunitario, lo usual sería cobrar IVA sobre los precios que facturase a los
países que pertenezcan a la UE, y no cobrarlo en caso contrario.
'''
class Pais(models.Model):
    nombre = models.CharField('País', max_length = 128, blank = False, null = False, unique = True)
    union_europea = models.BooleanField('Unión Europea', blank = True, default = False)
    prefijo_movil = models.CharField('Prefijo Móvil', max_length = 8, blank = True, null = True, unique = False)
    codigo_iso_alfa2 = models.CharField('Código ISO Alfa-2', max_length = 2, blank = True, null = True, unique = False)
    codigo_iso_alfa3 = models.CharField('Código ISO Alfa-3', max_length = 10, blank = True, null = True, unique = False)
    codigo_iso_numerico = models.CharField('Código ISO Numérico', max_length = 8, blank = True, null = True, unique = False)
    moneda = models.ForeignKey(Moneda, blank = True, null = True, unique = False, on_delete = models.CASCADE)
    idioma = models.ForeignKey(Idioma, blank = True, null = True, unique = False, on_delete = models.CASCADE)

    def eliminar_pais(self):
        # Antes de eliminar un país, es necesario verificar que no sea Cuba. Cuba no se puede eliminar sin más de la BD
        # ya que es muy probable que existan Servicios asociados a este país
        if self.nombre == 'CUBA':
            print('No se puede eliminar Cuba de esta manera de la Base de Datos, por favor acceda a la Interfaz de administración de Django')
            return None
        else:
            # Se eliminan todas las provincias asociadas al país
            for provincia in self.provincia_set.all():
                provincia.eliminar_provincia()
            print('Se ha eliminado correctamente el país %s' %(self.nombre))
            self.delete()

    @classmethod
    # Devuelve un país con codigo_iso_alfa2 igual al parámetro name, de lo contrario, devuelve None
    def get_pais_from_name(cls, name):
        # Intentamos encontrar un país que coincida con el parámetro "name" en alguno de sus atributos
        # 1 - codigo_iso_alfa2:
        if cls.objects.filter(codigo_iso_alfa2 = name):
            return cls.objects.get(codigo_iso_alfa2 = name)
        else:
            return None

    @classmethod
    # Devuelve el objeto moneda que debe mostrarse para cada usuario por defecto al abrir la Web.
    # Si se le indica el id de la moneda, lo obtiene de la Base de Datos; en caso contrario, lo toma de la configuración en uso
    def get_user_pais(cls, pais_id):
        if pais_id:
            return cls.objects.get(id = pais_id)
        else:
            # Se establece España como país por defecto
            return Pais.objects.get(nombre = 'SPAIN')

    @classmethod
    # Crea un nuevo registro de País en el Sistema
    def nuevo_pais(cls, nombre, union_europea, prefijo_movil, codigo_iso_alfa2, codigo_iso_alfa3, codigo_iso_numerico, moneda, idioma):
        # Verificar si no existe un país con los mismos datos únicos
        if cls.objects.filter(nombre = nombre):
            print('Ya existe un país con nombre: %s' %(nombre))
            return None
        else:
            n_pais = cls.objects.create(
                nombre = nombre,
                union_europea = union_europea,
                prefijo_movil = prefijo_movil,
                codigo_iso_alfa2 = codigo_iso_alfa2,
                codigo_iso_alfa3 = codigo_iso_alfa3,
                codigo_iso_numerico = codigo_iso_numerico,
                moneda = moneda,
                idioma = idioma,
            )
            print('Se ha creado correctamente el País %s' %(n_pais))
            return n_pais

    def modificar_pais(self, union_europea, prefijo_movil, codigo_iso_alfa2, codigo_iso_alfa3, codigo_iso_numerico, moneda, idioma):
        self.union_europea = union_europea
        self.prefijo_movil = prefijo_movil
        self.codigo_iso_alfa2 = codigo_iso_alfa2
        self.codigo_iso_alfa3 = codigo_iso_alfa3
        self.codigo_iso_numerico = codigo_iso_numerico
        self.moneda = moneda
        self.idioma = idioma
        self.save()
        print('Se ha modificado correctamente el País %s' %(self))
        return self

    class Meta:
        verbose_name_plural = 'Países'

    def __str__(self):
        return self.nombre

# class

class Comision(models.Model):
    precio = models.DecimalField('Precio', max_digits = 6, decimal_places = 2, blank = True, null = True, unique = False)
    comision = models.DecimalField('Comisión', max_digits = 6, decimal_places = 2, blank = True, null = True, unique = False)

    @classmethod
    def nueva_comision(cls, precio, comision):
        # Ha de verificarse que no existe un registro de comisión para el precio indicado
        if cls.objects.filter(precio = precio):
            print('Ya existe una comisión establecida para el precio %s' %(precio))
            return None

        else:
            n_comision = cls.objects.create(
                precio = precio,
                comision = comision,
            )
            print('Se ha creado correctamente una comisión para %s CUC de %s' %(precio, comision))
            return n_comision

    # Modifica los datos de una comisión en particular
    def modificar_comision(self, precio, comision):
        self.precio = precio
        self.comision = comision
        self.save()
        print('Se ha modificado correctamente la comisión para %s' %(self.precio))

    @classmethod
    # Devuelve el valor de comisión para un precio determinado
    def get_comision(cls, precio):
        return cls.objects.filter(precio__gte = precio).order_by('precio')[0].comision

    class Meta:
        verbose_name_plural = 'Comisiones'

    def __str__(self):
        return 'Comisión para %s (%s)' %(self.precio, self.comision)

# Devuelve las provincias con uana lista de sus municipios asociados
class Provincia_Manager(models.Manager):
    def incluir_municipios(self):
        provincias = Provincia.objects.order_by('nombre')
        provincias_con_municipios = []
        for provincia in provincias:
            provincia.municipios = provincia.municipio_set.order_by('nombre')
            provincias_con_municipios.append(provincia)
        return provincias_con_municipios

class Provincia(models.Model):
    nombre = models.CharField('Provincia', max_length = 128, blank = False, null = False, unique = False)
    descripcion = models.CharField('Descripción', max_length = 1024, blank = True, null = True, unique = False)
    pais = models.ForeignKey(Pais, blank = False, null = False, unique = False, on_delete = models.CASCADE)

    @classmethod
    # Devuelve una provincia con un nombre coincidente de alguna manera con el parámetro "name". En caso contrario devuelve None
    def get_provincia_from_name(cls, name):
        if cls.objects.filter(nombre = name):
            return cls.objects.get(nombre = name)
        elif cls.objects.filter(nombre = name.upper()):
            return cls.objects.get(nombre = name.upper())
        elif cls.objects.filter(nombre = name.lower()):
            return cls.objects.get(nombre = name.lower())
        elif cls.objects.filter(nombre = name.capitalize()):
            return cls.objects.get(nombre = name.capitalize())
        else:
            return None

    @classmethod
    # Crea una nueva Provincia
    def nueva_provincia(cls, nombre, descripcion, pais):
        if cls.objects.filter(nombre = nombre, pais = pais):
            print('Ya existe una provincia con nombre %s en el país %s' %(cls.nombre, cls.pais))
            return None
        else:
            n_provincia = cls.objects.create(
                nombre = nombre,
                descripcion = descripcion,
                pais = pais,
            )
            print('Se ha creado correctamente la provincia %s en el país %s' %(nombre, pais))
            return n_provincia

    # Modifica una Provincia determinada.
    def modificar_provincia(self, descripcion, nombre, pais):
        self.nombre = nombre
        self.descripcion = descripcion
        self.pais = pais
        self.save()
        print('Se ha modificado correctamente la provincia %s del país %s' %(self.nombre, self.pais))
        return self

    def eliminar_provincia(self):
        # Se eliminan todos los municipios relacionados con la Provincia
        municipios = self.municipio_set.all()
        for municipio in municipios:
            municipio.eliminar_municipio()
        print('Se ha eliminado correctamente la Provincia %s del país %s' %(self.nombre, self.pais))
        self.delete()

    # Object Manager de Provincia
    objects = Provincia_Manager()

    class Meta:
        verbose_name_plural = 'Provincias'

    def __str__(self):
        return self.nombre

class Municipio(models.Model):
    nombre = models.CharField('Municipio', max_length = 32, blank = False, null = False, unique = False)
    descripcion = models.CharField('Descripción', max_length = 1024, blank = True, null = True, unique = False)
    provincia = models.ForeignKey(Provincia, blank = False, null = False, unique = False, on_delete = models.CASCADE)

    @classmethod
    def nuevo_municipio(cls, nombre, descripcion, provincia):
        if cls.objects.filter(nombre = nombre, provincia = provincia):
            print('Ya existe un Minucipio con nombre %s en la Provincia %s' %(cls.nombre, cls.provincia))
            return None
        else:
            n_municipio = cls.objects.create(
                nombre = nombre,
                descripcion = descripcion,
                provincia = provincia,
            )
            print('Se ha creado correctamente el municipio %s en la provincia %s' %(nombre, provincia))
            return n_municipio

    def modificar_municipio(self, descripcion):
        self.descripcion = descripcion
        self.save()
        return self

    def eliminar_municipio(self):
        print('Se ha eliminado correctamente el municipio %s de la provincia %s del país %s' %(self.nombre, self.provincia, self.provincia.pais))
        self.delete()

    class Meta:
        verbose_name_plural = 'Municipios'

    def __str__(self):
        return self.nombre

class Interes(models.Model):
    nombre = models.CharField('Interés', max_length = 64, blank = False, null = False, unique = True)

    @classmethod
    # Crea un nuevo Interés en la BD
    def nuevo_interes(cls, nombre):
        # Comprobando que no existe ningún interés con ese nombre
        if cls.objects.filter(nombre = nombre):
            print('Ya existe un interés con nombre %s' %(nombre))
            return None
        else:
            n_interes = cls.objects.create(
                nombre = nombre
            )
            print('Se ha creado correctamente el interés con nombre %s' %(nombre))
            return n_interes

    # Modifica un interés en particular
    def modificar_interes(self, nombre):
        # Comprueba que no existe ningún interés con el nuevo valor de nombre que se quiere asignar a este Interés
        if self.objects.filter(nombre = nombre):
            print('Ya existe un interés con nombre %s' %(nombre))
            return None
        else:
            self.nombre = nombre
            self.save()
            print('Se ha modificado correctamente el Interés')
            return self

    # Elimina un interés en particular
    def eliminar(self):
        self.delete()
        print('Se ha eliminado correctamente el Interés')

    class Meta:
        verbose_name_plural = 'Intereses'

    def __str__(self):
        return self.nombre

class Destino_Manager(models.Manager):
    # En este método se define el criterio de ponderación para los Destinos así como la cantidad de estos que se desea devolver
    # Los posibles criterios son:
    # 1 - intereses: Es más importante el destino que más intereses tenga relacionados
    # 2 - ??
    def mas_importantes(self, criterio = 'intereses', cantidad = 10):
        # Obteniendo todos los destinos
        destinos = Destino.objects.order_by('nombre')

        if criterio == 'intereses':
            destinos_ordenados = []
            # Ordenamiento de los Destinos según el criterio especificado
            # 1 - Determinar el destino con más intereses y ver cuántos son
            # 2 - En una iteración decreciente ir llenando la lista con los destinos que tengan tantos intereses relacionados como el número de turno de la iteración
            max_interses = -1
            for destino in destinos:
                if len(destino.intereses.all()) > max_interses:
                    max_interses = len(destino.intereses.all())

            destinos_excluidos = []
            for intereses in range(max_interses + 1).__reversed__():
                if len(destinos_ordenados) < cantidad:
                    for destino in destinos:
                        if not destino in destinos_excluidos:
                            if len(destino.intereses.all()) == intereses:
                                destinos_ordenados.append(destino)
                                destinos_excluidos.append(destino)
                else:
                    return destinos_ordenados[:10]
            return destinos_ordenados[:10]
        else:
            return destinos

'''
Los Destinos son lugares de Interés que pueden estar en cualquier localización y se pueden asociar a cualquier servicio por cercanía.
Así mismo un destino puede ser perfectamente un criterio de búsqueda de servicios, si este es el objetivo principal de la búsqueda.
'''
class Destino(models.Model):
    nombre = models.CharField('Nombre', max_length = 64, blank = False, null = False, unique = True)
    descripcion = models.TextField('Descripcion', blank = True, null = True, unique = False)
    intereses = models.ManyToManyField(Interes, blank = True, unique = False)
    provincia = models.ForeignKey(Provincia, blank = True, null = True, unique = False, on_delete = models.CASCADE)

    @classmethod
    def get_destinos_populares(cls):
        # Los destinos populares son aquellos con los cuales están relacionados los Alojamientos que más reservas han tenido
        destinos_populares = {}
        for destino in cls.objects.all():
            reservas_provincia = len(Reserva.objects.filter(servicio__alojamiento__provincia = destino.provincia))
            destinos_populares[destino] = reservas_provincia
        # En este putno tenemos un diccionario con la forma:{<Destino1>:A, <Destino2>:B, ...}
        # La idea es ordenar los elementos de este diccionario con el criterio de los values que son las reservas de Alojamientos en las provincias del Destino
        items = destinos_populares.items()
        ordenados = sorted(items, key = lambda x: x[1])
        return ordenados

    # Devuelve una lista de Alojamientos (Con detalles) que se encuentren en la provincia del Destino
    def get_alojamientos_cercanos(self):
        return Alojamiento.objects.detalles_alojamientos(provincia = self.provincia)


    @classmethod
    # Crea un nuevo Destino en nuestra BD
    def nuevo_destino(cls, nombre, descripcion, intereses, provincia):
        # Comprueba que no exista ya guardado un Destino con el mismo nombre en la misma provincia
        if cls.objects.filter(nombre = nombre, provincia = provincia):
            print('Ya existe un Destino con nombre %s en la provincia %s' %(nombre, provincia))
            return None
        else:
            n_destino = cls.objects.create(
                nombre = nombre,
                descripcion = descripcion,
                provincia = provincia,
            )
            for interes in intereses:
                n_destino.intereses.add(interes)
            n_destino.save()
            print('Se ha creado correctamente el destino %s' %(n_destino.nombre))
            return n_destino

    def modificar_destino(self, descripcion, intereses, provincia):
        self.descripcion = descripcion
        self.provincia = provincia

        # Primero se eliminan todos los Intereses
        for interes in self.intereses.all():
            self.intereses.remove(interes)

        # Después se añaden uno a uno los intereses
        for interes in intereses:
            self.intereses.add(interes)

        # Se guardan los cambios
        self.save()

        print('Se ha modificado correctamente el destino %s' % (self.nombre))
        return self

    # Elimina un Destino de la BD
    def eliminar(self):
        self.delete()

    # Definición del Object Manager
    objects = Destino_Manager()

    class Meta:
        verbose_name_plural = 'Destinos'

    def __str__(self):
        return self.nombre

# class Servicio_Manager(models.Manager):
#     def detalles_servicios(self, servicios_ids = None):
#         # Se definen todos los Servicios que van a ser devueltos en función de los filtros en el argumento del método
#         servicios = Servicio.objects.order_by('nombre')
#
#         # Filtrado
#         if servicios_ids:
#             servicios = servicios.filter(id__in = servicios_ids)
#
#         # Adición de detalles
#         detalles_servicios = []
#         for servicio in servicios:
#             detalles_servicio = self.detalles_servicio(
#                 servicio_id = servicio.id,
#             )
#             detalles_servicios.append(detalles_servicio)
#
#         # Devolución de la lista de servicios filtrados y con detalles
#         return detalles_servicios
#
#     def detalles_servicio(self, servicio_id, tamanno_muestra_evaluaciones = 3):
#         # Se determina el Servicio del que se requiere información Adicional
#         servicio = Servicio.objects.get(id = servicio_id)
#
#         # La lista de detalles a añadir al Servicio son:
#         # 1 - evaluaciones
#         servicio.evaluaciones = servicio.evaluacion_set.order_by('-fecha')
#
#         # 2 - evaluaciones_muestra: Ùltimas Evaluaciones registradas
#         servicio.muestra_evaluaciones = servicio.evaluaciones[:tamanno_muestra_evaluaciones]
#
#         # 3 - cantidad_evaluaciones
#         servicio.cantidad_evaluaciones = len(servicio.evaluaciones)
#
#         # 4 - cantidad_evaluaciones_muestra
#         servicio.cantidad_evaluaciones_muestra = len(servicio.muestra_evaluaciones)
#
#         # 5 - Precio Mínimo y Precio Máximo
#         # Aquí puede haber variaciones en caso de que el Servicio sea un Alojamiento, y particularmente si se alquila por Habitaciones
#         # En ese caso no existe un precio máximo y mínimo del Servicio sino de la Habitación
#         if servicio.alojamiento and servicio.alojamiento.por_habitacion:
#             if servicio.alojamiento.por_habitacion:
#                 servicio.precio_minimo, servicio.precio_maximo = servicio.alojamiento.precios_extremos_alojamiento_por_habitacion()
#             else:
#                 # Si el alojamiento se alquila completo el precio mínimo es el menor de los precios según las reglas de precio del Servicio
#                 servicio.precio_minimo, servicio.precio_maximo = servicio.precios_extremos_alojamiento_completo()
#         else:
#             # todo: Si en el futuro hay variaciones en el cálculo o el diseño de precios para otros servicios, añadiríamos elif aquí...
#             servicio.precio_minimo, servicio.precio_maximo = servicio.precios_extremos_alojamiento_completo()
#
#         # 5 - Promedio de Evaluaciones
#         evaluaciones_recomendado = 0
#         evaluaciones_bueno = 0
#         evaluaciones_promedio = 0
#         evaluaciones_pobre = 0
#         evaluaciones_terrible = 0
#         puntuaciones = []
#         for evaluacion in servicio.evaluaciones:
#             puntuaciones.append(evaluacion.evaluacion)
#             if evaluacion.evaluacion == 5:
#                 evaluaciones_recomendado += 1
#             elif evaluacion.evaluacion == 4:
#                 evaluaciones_bueno += 1
#             elif evaluacion.evaluacion == 3:
#                 evaluaciones_promedio += 1
#             elif evaluacion.evaluacion == 2:
#                 evaluaciones_pobre += 1
#             else:
#                 evaluaciones_terrible += 1
#         cantidad_puntuaciones = len(puntuaciones)
#         if cantidad_puntuaciones == 0:
#             servicio.promedio_evaluaciones = None
#             servicio.promedio_clientes_recomendado = 0
#             servicio.promedio_clientes_bueno = 0
#             servicio.promedio_clientes_promedio = 0
#             servicio.promedio_clientes_pobre = 0
#             servicio.promedio_clientes_terrible = 0
#         else:
#             promedio_puntuaciones = sum(puntuaciones) / cantidad_puntuaciones
#             servicio.promedio_evaluaciones = promedio_puntuaciones
#             servicio.promedio_clientes_recomendado = evaluaciones_recomendado / cantidad_puntuaciones * 100
#             servicio.promedio_clientes_bueno = evaluaciones_bueno / cantidad_puntuaciones * 100
#             servicio.promedio_clientes_promedio = evaluaciones_promedio / cantidad_puntuaciones * 100
#             servicio.promedio_clientes_pobre = evaluaciones_pobre / cantidad_puntuaciones * 100
#             servicio.promedio_clientes_terrible = evaluaciones_terrible / cantidad_puntuaciones * 100
#
#             # Cantidades de cada tipo de Evaluación
#             servicio.cantidad_evaluaciones_recomendado = evaluaciones_recomendado
#             servicio.cantidad_evaluaciones_bueno = evaluaciones_bueno
#             servicio.cantidad_evaluaciones_promedio = evaluaciones_promedio
#             servicio.cantidad_evaluaciones_pobre = evaluaciones_pobre
#             servicio.cantidad_evaluaciones_terrible = evaluaciones_terrible
#
#         # 6 - rating: Estrellas que representan el Promedio de Evaluaciones
#         servicio.rating = Evaluacion.promedio_evaluaciones(servicio)
#
#         # 7 - reservas
#         servicio.reservas = servicio.reserva_set.order_by('initial_date')
#
#         # 8 - cantidad_reservas
#         servicio.cantidad_reservas = len(servicio.reservas)
#
#         # 9 - ultima_reserva
#         if servicio.reservas:
#             servicio.ultima_reserva = servicio.reservas[::-1][0]
#         else:
#             servicio.ultima_reserva = None
#
#         # 10 - Fotos
#         # Hay que determinar si el Servicio es un Alojamiento, y si lo es, comprobar si se alquila Completo o Por Habitacion
#         # Solo en el caso que sea un Alojamiento que se alquile Por Habitaciones, las fotos serán la suma de las fotos de cada Habitacion
#         # En todos los demás casos, será todas las fotos de los objetos Foto_Servicio relacionados con este Servicio
#         servicio.fotos = []
#         if servicio.alojamiento:
#             alojamiento = Alojamiento.objects.detalles_alojamiento(id_alojamiento = servicio.alojamiento.id)
#             if servicio.alojamiento.por_habitacion:
#                 for habitacion in alojamiento.habitaciones_asociadas:
#                     for foto in habitacion.foto_habitacion_set.all():
#                         servicio.fotos.append(foto)
#             else:
#                 for foto in servicio.foto_servicio_set.all():
#                     servicio.fotos.append(foto)
#         else:
#             for foto in servicio.foto_servicio_set.all():
#                 servicio.fotos.append(foto)
#
#         # 11 - cantidad_fotos
#         servicio.cantidad_fotos = len(servicio.fotos)
#
#         # 12 - Reglas de Precio
#         servicio.reglas_precio = servicio.regla_precio_set.order_by('fecha_desde')
#
#         # Se devuelve el servicio con la información adicional añadida
#         return servicio

'''
Un servicio es el elemento jerárquicamente superior de todos los elementos que se comercializan en el Sitio. Contiene
los elementos comunes a todo tipo de servicios ofrecidos.
'''
class Servicio(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', blank = False, null = False, unique = False, on_delete = models.CASCADE)
    nombre = models.CharField('Nombre', max_length = 64, blank = False, null = False, unique = False)
    descripcion = models.CharField('Descripción', max_length = 1024, blank = False, null = False, unique = False)
    email = models.EmailField('E-Mail Servicio', max_length = 64, blank = True, null = True, unique = False)
    movil = models.CharField('Móvil', max_length = 16, blank = True, null = True, unique = False)
    sitio_web = models.URLField('Sitio Web', max_length = 128, blank = True, null = True, unique = False)
    max_fotos = models.IntegerField('Máximo de Fotos permitidas', blank = False, null = False, unique = False, default = 8)
    fecha_creacion = models.DateTimeField('Fecha de Creación', blank = False, null = False, unique = False, auto_now_add = True)
    moneda = models.ForeignKey(Moneda, blank = True, null = True, unique = False, on_delete = models.DO_NOTHING)
    precio_base = models.DecimalField('Precio Base', max_digits = 6, decimal_places = 2, blank = True, null = True, unique = False)
    url_video = models.URLField('URL Video', max_length = 255, blank = True, null = True, unique = False)
    destacado = models.BooleanField('Destacado', blank = True, default = False)
    cerrado = models.BooleanField('Cerrado', blank = True, default = False)
    visualizaciones = models.PositiveIntegerField('Visualizaciones', blank = True, null = True, unique = False, default = 0)

    # Incrementa en una unidad la cantidad de visualizaciones del Servicio
    def new_visualization(self):
        self.visualizaciones += 1
        self.save()

    def cerrar_servicio(self):
        # Cierra el Servicio y se analizan las implicaciones. Por ejemplo:
        # Si el Servicio es un Alojamiento por Habitación, se cierran también las Habitaciones del mismo
        self.cerrado = True
        self.save()

        if self.alojamiento:
            if self.alojamiento.por_habitacion:
                for habitacion in self.alojamiento.habitacion_set.all():
                    habitacion.cerrar_habitacion()

    # Devuelve True o False, en función de si el Servicio puede ser eliminado por el Proveedor del mismo
    def allow_delete(self):
        # Esta capacidad está determinada al menos por si el Servicio ha sido reservado en el pasado. Si es el caso,
        # el proveedor no puede eliminarlo de la Base de Datos, solo "cerrarlo" para que no sea visible en los resultados de búsqueda
        for reserva in self.reserva_set.all():
            if reserva.pago_set.filter(completado = True):
                return False

        # Si se llega a este punto es porque ninguna reserva asociada al Servicio (en caso de existir) tiene algún pago completado relacionado
        return True

    # Devuelve True o False en función de si el Servicio puede ser Cerrado por el Proveedor
    def allow_close(self):
        # Un alojamiento no puede ser cerrado, si en caso de tener reservas pagadas, la fecha actual es anterior a alguna de las fechas de entrada de las reservas pagadas
        for reserva in self.reserva_set.all():
            if reserva.pago_set.filter(completado = True):
                if datetime.date.today() < reserva.initial_date:
                    return False

        # Si se llega a este punto es porque ninguna reserva asociada al Servicio (en caso de existir) tiene algún pago completado relacionado
        # y además su fecha de inicio es posterior a hoy
        return True


    # Guarda el campo url_video asociado a un Servicio a partir de una URL de un video de Youtube
    def set_url_video(self, url_video):
        if 'youtube.com' in url_video:
            # Caso que el video sea de Youtube
            video_code = url_video.split('watch?v=')[1]
            embed_url = 'https://www.youtube.com/embed/%s' %(video_code)
            self.url_video = embed_url
            self.save()
            return self

        else:
            message = 'El video debe ser de Youtube'
            print(message)
            return {
                'message': message,
            }

    # Elimina la URL del video asociado al servicio
    def eliminar_url_video(self):
        self.url_video = None
        self.save()

    # Devuelve el precio más bajo entre el precio de base y todos los precios de las reglas asociadas a este servicio
    def precios_extremos_alojamiento_completo(self):
        reglas_precio = self.regla_precio_set.filter(activa = True).order_by('precio')
        if reglas_precio:
            precio_minimo = reglas_precio[0].precio
            precio_maximo = reglas_precio[::-1][0].precio
            return precio_minimo, precio_maximo
        else:
            # Si no hay reglas de Precios, ambos precios extremos son el Precio Base establecido
            return self.precio_base, self.precio_base

    # Devuelve True, si el Servicio o la Habitación estñan disponibles en un rango de fechas determinado
    def check_disponibilidad(self, fecha_entrada, fecha_salida, habitacion = None):
        if not habitacion:
            indisponibilidades = self.indisponibilidad_set.all()
        else:
            indisponibilidades = habitacion.indisponibilidad_set.all()
        for indisponibilidad in indisponibilidades:
            # Las dos posibilidades para que la indisponibilidad afecte el período solicitado son:
            # 1 - que la fecha de entrada se encuentre entre las fechas de la indisponibilidad (incluida la fecha de entrada)
            # 2 - que la fecha de salida se encuentre entre las fechas de la indisponibilidad (incluida la fecha de salida)
            if fecha_entrada >= indisponibilidad.fecha_desde and fecha_entrada <= indisponibilidad.fecha_hasta:
                return False
            elif fecha_salida >= indisponibilidad.fecha_desde and fecha_salida <= indisponibilidad.fecha_hasta:
                return False

        # Si se han analizado todas las indisponibilidades y en ningún caso han coincidido las fechas, se devuelve True entonces
        return True

    @classmethod
    # Devuelve una lista de ids de los Servicios asociados a Alojamientos que cumplen o no con una condición de tipo de modalidad de alquiler
    def get_ids_alojamientos(cls, por_habitacion = 'null'):
        ids_alojamientos = []
        for alojamiento in Alojamiento.objects.all():
            if por_habitacion != 'null':
                if alojamiento.por_habitacion == por_habitacion:
                    ids_alojamientos.append(int(alojamiento.servicio.id))
            else:
                ids_alojamientos.append(int(alojamiento.servicio.id))
        return ids_alojamientos


    def get_precio_fechas(self, fecha_entrada, fecha_salida, habitacion = None):
        # Determinar el precio total (sumatoria de precios) para todos los días de un período para un Servicio o Habitación
        # A partir del período de tiempo determinar todos los días involucrados y calcular y acumular el precio para cada día
        precio_fechas = 0
        for dia in range(1, (fecha_salida - fecha_entrada).days + 1):
            precio_fechas += self.get_precio_fecha(fecha_entrada + datetime.timedelta(days = dia), habitacion)
        return precio_fechas

    def get_precio_fecha(self, fecha, habitacion = None):
        """
        Calcula el precio del Servicio o Habitación para un día en particular
        :param fecha: datetime.date que determina el día para el que se quiere saber el precio de un Servicio o Habitación
        :return: decimal, que es el precio de este Servicio o Habitación en el día indicado
        """
        # Hay que ubicar la fecha en alguno de los rangos de reglas de precio creadas. Si se encuentra, entonces obtener el precio para esa feche
        mes = fecha.month

        # Se obtienen todas las reglas de precio para el Servicio o la Habitación que se requiere (según sea el caso)
        if habitacion:
            reglas_precio = Regla_Precio.objects.filter(habitacion = habitacion)
        else:
            reglas_precio = Regla_Precio.objects.filter(servicio = self)

        # Si existe alguna regla de precio, debe analizarse si incluye algún mes del período que se quiere comprobar
        if reglas_precio:
            for regla_precio in reglas_precio:
                meses_regla_precio = Regla_Precio.obtener_numeros_meses_periodo(regla_precio.fecha_desde, regla_precio.fecha_hasta)
                if mes in meses_regla_precio:
                    return regla_precio.precio
        # Si no se encuentra coincidencia en ninguno de los meses de las reglas existentes, se devuelve el precio base de la Habitación
        if habitacion:
            return habitacion.habitacion_alojamiento_por_habitacion.precio_base
        else:
            return self.precio_base

    def get_precio_comision_fechas(self, fecha_entrada, fecha_salida, habitacion = None):
        """
        Calcula el precio de un Servicio para un núemro determinado de días, según las reglas de precio establecidas para el mismo
        Devuelve también el acumulado de comisión
        :param fecha_entrada: datetime.date, indica la fecha de entrada a consumir el servicio
        :param fecha_salida: datetime.date, indica la fecha de salida de consumir el servicio
        :return: dicemal, que es el total del precio del servicio para los días indicados
        """
        # 1 - Crear la lista de días en los que se va a consumir el servicio
        days = []
        # Debemos considerar la posibilidad que los argumentos de fecha_entrada y fecha_salida, lleguen en formato str de la manera: "AAAA-MM-DD"
        # En ese caso, debemos convertirlos a datetime.date, para poder realizar las operaciones con fechas necesarias
        if isinstance(fecha_entrada, str):
            fecha_entrada = str_to_date(fecha_entrada)
        if isinstance(fecha_salida, str):
            fecha_salida = str_to_date(fecha_salida)

        for day in range(0, (fecha_salida - fecha_entrada).days):
            days.append(fecha_entrada + datetime.timedelta(days = day))

        # 2 - Una vez se tienen todos los días, se calcula el precio de cada uno de manera independiente
        precio = 0
        comision = 0
        for day in days:
            precio_dia = self.get_precio_fecha(day, habitacion)
            precio += precio_dia
            comision += Comision.get_comision(precio_dia)

        # 3 - Devolver el precio y la comisión totales para este Servicio
        return precio, comision

    @classmethod
    def get_servicios_alojamientos_por_habitacion(cls):
        alojamientos = Alojamiento.objects.detalles_alojamientos(
            activos = True,
            por_modalidad = True,
            por_habitacion = True,
        )
        servicios_alojamientos_por_habitacion = []
        for alojamiento in alojamientos:
            servicios_alojamientos_por_habitacion.append(alojamiento.servicio)

        return servicios_alojamientos_por_habitacion

    @classmethod
    def get_servicios_alojamientos_completos(cls):
        alojamientos = Alojamiento.objects.detalles_alojamientos(
            activos = True,
            por_modalidad = True,
            por_habitacion = False,
        )
        servicios_alojamientos_completos = []
        for alojamiento in alojamientos:
            servicios_alojamientos_completos.append(alojamiento.servicio)

        return servicios_alojamientos_completos

    def get_fotos_servicio(self):
        """
        Obtener todas las Fotos relacionadas con un Servicio
        :return: Devuelve un listado de Objetos Foto_Servicio
        """
        return self.foto_servicio_set.all()

    def eliminar_path(self):
        """
        Elimina el directorio donde se almacenan las imágenes de un Servicio
        :return: No devuelve nada
        """
        path = '%s/media/usuarios/%s/services_photos/%s' % (os.getcwd(), self.usuario.id, self.id)
        if os.path.exists(path):
            shutil.rmtree(path)

    # Devuelve un número entre 1 y 5, que es el promedio de evaluaciones para un servicio dado
    def get_promedio_evaluaciones(self, entero = False):
        evaluaciones = self.evaluacion_set.all()
        if evaluaciones:
            suma_evaluaciones = 0
            for evaluacion in evaluaciones:
                suma_evaluaciones += evaluacion.evaluacion
            promedio_evaluaciones = suma_evaluaciones / len(evaluaciones)
            if entero:
                # Se devuelve un Entero del 1 al 5
                return int(round(promedio_evaluaciones, 0))
            else:
                # Se devuelve un Decimal del 1 al 5
                return Decimal(promedio_evaluaciones)
        else:
            return None

    # Modifica un Servicio determinado
    def modificar_servicio(self, nombre, descripcion, precio_base):
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio_base = precio_base
        self.save()
        print('Se ha modificado correctamente el Servicio %s' %(self))
        return self

    # Devuelve el precio mínimo para un Servicio
    def precio_minimo_reglas(self):
        reglas_precio_servicio = self.regla_precio_set.filter(activa = True).order_by('precio')
        if reglas_precio_servicio:
            menor_precio = reglas_precio_servicio[0].precio
            return menor_precio
        else:
            return None

    # Devuelve una lista de listas donde cada una contiene o fotos del servicio o n string
    def get_photos_rows(self, columns):
        max_fotos = range(self.max_fotos)
        fotos_servicio = self.foto_servicio_set.all()
        cantidad_fotos_servicio = len(fotos_servicio)
        show_fotos = []
        for foto in max_fotos:
            if cantidad_fotos_servicio <= foto:
                show_fotos.append(None)
            else:
                show_fotos.append(fotos_servicio[foto])
        l = 0
        r = columns
        rows = []
        while len(show_fotos[l:r]) == columns:
            rows.append(show_fotos[l:r])
            l += columns
            r += columns
        if len(show_fotos[l:r]) > 0:
            rows.append(show_fotos[l:r])
        return rows

    @classmethod
    # Crea un nuevo Servicio
    def nuevo_servicio(cls, usuario, nombre, descripcion, precio_base = None, email = None, sitio_web = None):
        # Por defecto los datos de contacto de los Servicios son los datos de contacto de los Usuarios que los proveen
        if not email:
            email = usuario.user.email

        # Por defecto se ha establecido que la moneda base para los servicios es el CUC
        if not Moneda.objects.filter(codigo_iso = 'CUC'):
            Moneda.nueva_moneda(
                codigo_iso = 'CUC',
                menu = True,
            )

        # Se valida que el usuario no tenga otro servicio con el mismo nombre
        if cls.objects.filter(usuario = usuario, nombre = nombre):
            print('Ya existe un Servicio para %s con nombre %s' %(usuario, nombre))
            return None
        else:
            n_servicio = cls.objects.create(
                descripcion = descripcion,
                email = email,
                movil = usuario.movil,
                nombre = nombre,
                sitio_web = sitio_web,
                usuario = usuario,
                precio_base = precio_base,
            )
            print('Se ha creado correctamente el Servicio %s para %s' %(nombre, usuario))
            return n_servicio

    @classmethod
    # Devuelve el listado de Servicios relacionados con un usuario en específico
    def get_servicios_usuario(cls, usuario):
        servicios = usuario.servicio_set.order_by('nombre')
        return servicios

    def eliminar_servicio(self):
        # Lo primero es determinar qué clase de Servicio es, y en función de eso, llamar al método que corresponde en el modelo que sea
        # 1 - Probando si se trata de un Alojamiento
        if self.alojamiento:
            self.alojamiento.eliminar_alojamiento()

        # todo: Añadir los demás casos de servicios (elif...)

        # Finalmente se elimina el Servicio
        self.delete()


    # ======== Métodos generales que no deseo tener en módulos independientes, los colocamos al final del model Servicio ======= #
    @classmethod
    def compare_strings(cls, string_1, string_2):
        # Se analiza si ambos strings son idénticos. En caso que lo sean se devuelve True y no se hace más análisis
        if string_1.lower() == string_2.lower():
            return True
        # Si no tienen el mismo largo, la única posibilidad que se consideren relacionadas requiere que la diferencia sea de una sola letra
        elif abs(len(string_1) - len(string_2)) == 1:
            # Si la diferencia es de una sola letra, entonces es necesario que la letra faltante se encuentre al final o al inicio de la palabra
            if len(string_1) > len(string_2):
                if string_2.lower() in string_1.lower():
                    return True
                else:
                    return False
            elif string_1.lower() in string_2.lower():
                return True
            else:
                return False
        # Este es el caso en que las palabras no son iguales, pero tienen igual número de caracteres
        # Solo será True la respuesta, en caso de que difieran en un solo caracter
        elif len(string_1) == len(string_2):
            errores = 0
            for char in range(len(string_1)):
                if not string_1[char] == string_2[char]:
                    errores += 1
                    if errores > 1:
                        return False
            # Si llega a este punto sin salir del método implica que ambos strings tienen como máximo un caracter de diferencia
            return True
        # Este es el caso en que los strings no son iguales, y la diferencia en la cantidad de caracteres es de más de uno.
        else:
            return False

    # objects = Servicio_Manager()

    class Meta:
        verbose_name_plural = 'Servicios'

    def __str__(self):
        return '%s de %s' %(self.nombre, self.usuario)

'''
El tipo de alojamiento es un atributo del Alojamiento y sirve para clasificarlo según sunaturaleza constructiva. Puede ser:
Casa, Apartamento o Mansión; siendo esta última una casa más grande, lujosa y confortable que las primeras.
'''
class Tipo_Alojamiento(models.Model):
    tipo = models.CharField('Tipo de Alojamiento', max_length = 64, blank = False, null = False, unique = True)

    @classmethod
    def nuevo_tipo_alojamiento(cls, tipo):
        n_tipo_alojamiento = cls.objects.create(
            tipo = tipo,
        )
        print('Se ha creado correctamente el tipo de Alojamiento: "%s"' %(cls.tipo))
        return n_tipo_alojamiento

    class Meta:
        verbose_name_plural = 'Tipos de Alojamientos'

    def __str__(self):
        return self.tipo


class Alojamiento_Manager(models.Manager):
    # Este método devuelve una lista con los Alojamientos y detalles extra pero de un usuario en particular
    def detalles_alojamientos(
            self,
            cerrado = False, # -----------------> ¿? - Si == True, devolverá INCLUSO los Alojamientos cerrados, si es False, no devolverá los Alojamientos cerrados
            acceso_discapacitados = False, # --> 10 - Si == True, solo devolverá los Alojamientos que tengan Acceso para discapacitados
            activos = False, # ----------------> 02 - Si == True, solo devolverá los Alojamientos que estñen activos
            agua_caliente = False, # ----------> 24 -
            aire_acondicionado = False, # -----> 23 -
            alojamientos_ids = (), # ----------> 06 - Devuelve solo un grupo de Alojamientos especificados, requiere una lista de ids de los Alojamientos deseados
            apartamento = False, # ------------> 20 - Si == True, solo devolverá los Alojamientos en los que el Tipo sea Apartamento
            balcon = False, # -----------------> 26 -
            banno_independiente = False, # ----> 31 -
            casa = False, # -------------------> 21 - Si == True, solo devolverá los Alojamientos en los que el Tipo sea Casa
            caja_fuerte = False, # ------------> 27 -
            con_habitaciones = False, # -------> 03 - Si == True, solo devolverá Alojamientos con al menos una habitación
            desayuno_cena = False, # ----------> 11 - Si == True, solo devolverá los Alojamientos en los que se ofrezcan servicios de desayuno/cena
            estereo = False, # ----------------> 29 -
            favoritos = (), # -----------------> 33 - Sólo devolverá loa alojamientos de los cuales los ids de sus servicios se encuentren en la lista "favoritos"
            fechas_huespedes = (), # ----------> 08 - Devuelve los Alojamientos que estén disponibles en un rango de fechasy puedan admitir la cantidad de huéspedes indicada
            internet = False, # ---------------> 12 - Si == True, solo devolverá los Alojamientos en los que sea posible acceder a Internet
            limit = False, # ------------------> XX - Si es diferente de False, debe ser un entero, y limita los registros a devolver (la cantidad de ellos)
            lugar = None, # -------------------> 07 - Devuelve solo los Alojamientos que estén relacionados con un lugar explícito
            mansion = False, # ----------------> 22 - Si == True, solo devolverá los Alojamientos en los que el Tipo sea Mansión
            nevera_bar = False, # -------------> 25 -
            parqueo = False, # ----------------> 13 - Si == True, solo devolverá los Alojamientos en los que exista disponibilidad de parqueo
            patio_terraza_balcon = False, # ---> 14 - Si == True, solo devolverá los Alojamientos en los que existan patio, terraza o balcón
            permitido_fumar = False, # --------> 15 - Si == True, solo devolverá los Alojamientos en los que se permita fumar
            permitido_mascotas = False, # -----> 16 - Si == True, solo devolverá los Alojamientos en los que se permitan tener mascotas
            permitido_ninnos = False, # -------> 17 - Si == True, solo devolverá los Alojamientos en los que se permitan niños
            piscina = False, # ----------------> 18 - Si == True, solo devolverá los Alojamientos en los que exista piscina
            por_habitacion = True, # ----------> 05 - Devuelve los Alojamientos según la modalidad de Alquiler (por habitacion si == True, o completo si == False)
            por_modalidad = False, # ----------> 04 - Si == True, hará caso del argumento "por_habitacion", si no, lo obviará y no tendrá en cuenta la modalidad de alquiler
            rango_precio = None, # ------------> 32 -
            rating_1_estrella = False,
            rating_2_estrellas = False,
            rating_3_estrellas = False,
            rating_4_estrellas = False,
            rating_5_estrellas = False,
            transporte_aeropuerto = False, #--> 19 - Si == True, solo devolverá los Alojamientos en los que se brinde servicio de transporte desde y hacia el Aeropuerto
            tv = False, #---------------------> 28 -
            ventanas = False, #---------------> 30 -
            usuarios = (), # ------------------> 01 - Solo devolverá los Alojamientos para un grupo de usuarios en específico
            cantidad_habitaciones = False,
            cocina = False,
            lavadora = False,
            provincia = None,

            # "ordered" (abajo de los comentarios), puede tomar los valores:
            # 01. nombre_asc (Variante por Defecto)
            # 02. nombre_desc
            # 03. precio_asc
            # 04. precio_desc
            # 05. provincia_asc
            # 06. provincia_desc
            # 07. municipio_asc
            # 08. municipio_desc
            # 09. opinion_asc
            # 10. opinion_desc
            # 11. popularidad_asc
            # 12. popularidad_desc
            # 13. habitaciones_asc
            # 14. habitaciones_desc
            ordered = 'nombre_asc',
    ):

        # Se comienza con el filtrado de los Alojamientos, según los parámetros establecidos
        # Se asume que no hay elementos de restricción, y se obtienen todos los Alojamientos
        alojamientos = Alojamiento.objects.all()

        # ¿? - cerrado
        if not cerrado:
            alojamientos = alojamientos.filter(servicio__cerrado = False)

        # 01 - usuarios
        if usuarios:
            alojamientos = alojamientos.filter(servicio__usuario__in = usuarios)

        # 33 - favoritos
        if favoritos:
            alojamientos = alojamientos.filter(servicio__id__in = favoritos)

        # 03 - con_habitaciones
        # Hacer una lista con todos los ids de los Alojamientos asociados a todas las Habitaciones existentes
        # No incluir los alojoamientos cuyos ids no se encuentren en esa lista
        ids_alojamientos_con_habitaciones = Habitacion.get_ids_alojamientos()
        if con_habitaciones:
            alojamientos = alojamientos.filter(id__in = ids_alojamientos_con_habitaciones)

        # 04 - por_modalidad
        # Si por_modalidad == True, se aplicará el filtro siguiente en consecuencia con la modalidad de alquiler del Alojamiento

        # 05 - por_habitacion
        if por_modalidad:
            if por_habitacion:
                alojamientos = alojamientos.filter(por_habitacion = True)
            else:
                alojamientos = alojamientos.filter(por_habitacion = False)

        # 06 - alojamientos_ids
        if alojamientos_ids:
            alojamientos = alojamientos.filter(id__in = alojamientos_ids)

        # 07 - lugar
        if lugar:
            ids_alojamientos_lugar = Alojamiento.filtrado_lugar(lugar)
            alojamientos = alojamientos.filter(id__in = ids_alojamientos_lugar)

        # 08 - fechas
        if fechas_huespedes:
            # fechas_huespedes debe ser una lista de dos fechas y una cantidad de huéspedes: "fecha_entrada", "fecha_salida" y "huespedes"
            if len(fechas_huespedes) == 3:
                fecha_entrada = fechas_huespedes[0]
                fecha_salida = fechas_huespedes[1]
                huespedes = fechas_huespedes[2]
                ids_alojamientos_fechas_huespedes = Alojamiento.filtrado_fechas_huespedes(fecha_entrada, fecha_salida, huespedes)
                alojamientos = alojamientos.filter(id__in = ids_alojamientos_fechas_huespedes)
            else:
                print('fechas debe ser una lista con dos objetos datetime.date ordenados cronológicamente y un objeto int')

        # 10 - acceso_discapacitados
        if acceso_discapacitados:
            alojamientos = alojamientos.filter(acceso_discapacitados = True)

        # 11 - desayuno_cena
        if desayuno_cena:
            alojamientos = alojamientos.filter(desayuno_cena = True)

        # 12 - internet
        if internet:
            alojamientos = alojamientos.filter(internet = True)

        # 13 - parqueo
        if parqueo:
            alojamientos = alojamientos.filter(parqueo = True)

        # 14 - patio_terraza_balcon
        if patio_terraza_balcon:
            alojamientos = alojamientos.filter(patio_terraza_balcon = True)

        # 15 - permitido_fumar
        if permitido_fumar:
            alojamientos = alojamientos.filter(permitido_fumar = True)

        # 16 - permitido_mascotas
        if permitido_mascotas:
            alojamientos = alojamientos.filter(permitido_mascotas = True)

        # 17 - permitido_ninnos
        if permitido_ninnos:
            alojamientos = alojamientos.filter(permitido_ninnos = True)

        # 18 - piscina
        if piscina:
            alojamientos = alojamientos.filter(piscina = True)

        # 19 - transporte_aeropuerto
        if transporte_aeropuerto:
            alojamientos = alojamientos.filter(transporte_aeropuerto = True)

        # 20 - apartamento
        if apartamento:
            alojamientos = alojamientos.filter(tipo_alojamiento__tipo = 'Apartamento')

        # 21 - casa
        if casa:
            alojamientos = alojamientos.filter(tipo_alojamiento__tipo = 'Casa')

        # 22 - mansion
        if mansion:
            alojamientos = alojamientos.filter(tipo_alojamiento__tipo = 'Mansión')

        # 23 - aire_acondicionado
        if aire_acondicionado:
            alojamientos = alojamientos.filter(Q(habitacion__aire_acondicionado = True) | Q(alojamiento_completo__aire_acondicionado_central = True))

        # 24 - agua_caliente
        if agua_caliente:
            alojamientos = alojamientos.filter(habitacion__agua_caliente = True)

        # 25 - nevera_bar
        if nevera_bar:
            alojamientos = alojamientos.filter(Q(habitacion__nevera_bar = True) | Q(alojamiento_completo__nevera_bar = True))

        # 26 - balcon
        if balcon:
            alojamientos = alojamientos.filter(habitacion__balcon = True)

        # 27 - caja_fuerte
        if caja_fuerte:
            alojamientos = alojamientos.filter(habitacion__caja_fuerte = True)

        # 28 - tv
        if tv:
            alojamientos = alojamientos.filter(Q(habitacion__tv = True) | Q(alojamiento_completo__tv = True))

        # 29 - estereo
        if estereo:
            alojamientos = alojamientos.filter(Q(habitacion__estereo = True) | Q(alojamiento_completo__estereo = True))

        # 30 - ventanas
        if ventanas:
            alojamientos = alojamientos.filter(habitacion__ventanas = True)

        # 31 - banno_independiente
        if banno_independiente:
            alojamientos = alojamientos.filter(habitacion__habitacion_alojamiento_por_habitacion__banno_independiente = True)

        # Cocina
        if cocina:
            alojamientos = alojamientos.filter(alojamiento_completo__cocina = True)

        # Lavadora
        if lavadora:
            alojamientos = alojamientos.filter(alojamiento_completo__lavadora = True)

        # Provincia
        if provincia:
            alojamientos = alojamientos.filter(provincia = provincia)

        # Una vez obtenidos los Alojamientos que cumplen con las condiciones de los parámetros del método. Se ordenan según se requiere y se le añade la información extra
        if ordered == 'nombre_asc':
            alojamientos = alojamientos.order_by('servicio__nombre')
        elif ordered == 'nombre_desc':
            alojamientos = alojamientos.order_by('-servicio__nombre')
        elif ordered == 'precio_asc':
            alojamientos = alojamientos.order_by('habitacion__habitacion_alojamiento_por_habitacion__precio_base')
        elif ordered == 'precio_desc':
            alojamientos = alojamientos.order_by('-habitacion__habitacion_alojamiento_por_habitacion__precio_base')
        elif ordered == 'provincia_asc':
            alojamientos = alojamientos.order_by('provincia__nombre')
        elif ordered == 'provincia_desc':
            alojamientos = alojamientos.order_by('-provincia__nombre')
        elif ordered == 'municipio_asc':
            alojamientos = alojamientos.order_by('municipio__nombre')
        elif ordered == 'municipio_desc':
            alojamientos = alojamientos.order_by('-municipio__nombre')
        elif ordered == 'opinion_asc':
            alojamientos = alojamientos.order_by('servicio__evaluacion__evaluacion')
        elif ordered == 'opinion_desc':
            alojamientos = alojamientos.order_by('-servicio__evaluacion__evaluacion')
        elif ordered == 'popularidad_asc':
            alojamientos = alojamientos.order_by('servicio__reserva')
        elif ordered == 'popularidad_desc':
            alojamientos = alojamientos.order_by('-servicio__reserva')
        # elif ordered == 'habitaciones_asc':
        #     alojamientos = alojamientos.order_by('hab')
        # elif ordered == 'habitaciones_desc':
        #     alojamientos = alojamientos.order_by('habitaciones_desc')

        # XX - limit
        if limit:
            alojamientos = alojamientos[:limit]

        # Cuando se han determinado los Alojamientos a devolver y se han ordenado como se necesita, entonces se procede a añadirles la información adicional
        detalles_alojamientos = []
        for alojamiento in alojamientos:
            # Si se ha pasado en los argumentos del método el parámetro "activos", requiere que solo los Alojamientos en condiciones puedan ser mostrados
            # Estas condiciones son que tengan al menos una Habitación con Fotos y precio si se alquila por habitación, o al menos
            # una foto si el Alojamiento se alquila completlo
            if activos:
                if not alojamiento.servicio.cerrado:
                    check_pic = False
                    usuario = alojamiento.servicio.usuario
                    if usuario.pais:
                        if usuario.pais.codigo_iso_alfa2 == 'CU':
                            if usuario.proveedor and usuario.verificado_proveedor:
                                if alojamiento.por_habitacion:
                                    for habitacion in alojamiento.habitacion_set.all():
                                        if habitacion.foto_habitacion_set.all():
                                            # Si entra en este if es porque hay al menos una Habitación con Foto
                                            check_pic = True
                                            break
                                else:
                                    if alojamiento.servicio.foto_servicio_set.all():
                                        # Si se entra en este if es porque tiene al menos una foto
                                        check_pic = True

                    # Sólo si el Alojamiento puede ser mostrado a los usuarios, se añade a los Alojamientos a devolver
                    if check_pic:
                        detalles_alojamiento = self.detalles_alojamiento(alojamiento.id)
                        detalles_alojamientos.append(detalles_alojamiento)

            # En caso que los Alojamientos no tengan que estar "activos" (Pueden ser mostrados a los usuarios), se obvian todas las validaciones de fotos
            else:
                detalles_alojamiento = self.detalles_alojamiento(alojamiento.id)
                detalles_alojamientos.append(detalles_alojamiento)

        # Hay algunos filtros que solo se pueden ejecutar tras haber añadido la información adicional a los alojamientos
        if cantidad_habitaciones:
            alojamientos_filtrados = []
            for alojamiento in detalles_alojamientos:
                if alojamiento.cantidad_habitaciones >= cantidad_habitaciones:
                    alojamientos_filtrados.append(alojamiento)
            detalles_alojamientos = alojamientos_filtrados

        # 09 - filtro_rating
        if True in [rating_1_estrella, rating_2_estrellas, rating_3_estrellas, rating_4_estrellas, rating_5_estrellas]:
            alojamientos_filtrados = []
            for alojamiento in detalles_alojamientos:
                # Con esto obtengo un entero entre 1 y 5 equivalente al promedio redondeado de las evaluaciones del Alojamiento
                rating_alojamiento = alojamiento.servicio.get_promedio_evaluaciones(entero = True)
                if rating_alojamiento:
                    # Se seleccionan solo los Alojamientos que coincidan con el promedio de evaluación seleccionado
                    if rating_alojamiento == 1 and rating_1_estrella:
                        alojamientos_filtrados.append(alojamiento)
                    elif rating_alojamiento == 2 and rating_2_estrellas:
                        alojamientos_filtrados.append(alojamiento)
                    elif rating_alojamiento == 3 and rating_3_estrellas:
                        alojamientos_filtrados.append(alojamiento)
                    elif rating_alojamiento == 4 and rating_4_estrellas:
                        alojamientos_filtrados.append(alojamiento)
                    elif rating_alojamiento == 5 and rating_5_estrellas:
                        alojamientos_filtrados.append(alojamiento)
            detalles_alojamientos = alojamientos_filtrados

        # 32 - rango_precio
        if rango_precio:
            minimo = int(round(float(rango_precio.split(';')[0]), 2))
            maximo = int(round(float(rango_precio.split(';')[1]), 2))
            alojamientos_filtrados = []
            for alojamiento in detalles_alojamientos:
                if alojamiento.precio_minimo >= minimo and alojamiento.precio_maximo <= maximo:
                    alojamientos_filtrados.append(alojamiento)
            detalles_alojamientos = alojamientos_filtrados

        return detalles_alojamientos

    # Este método devuelve un único Alojamiento con más detalles que los que aportan sus atributos originales.
    # El parámetro que se necesita es el id del Alojamiento del que se quieren tener los datos
    def detalles_alojamiento(self, id_alojamiento):
        # 1 - Determinando los Alojamientos del usuario en cuestión
        alojamiento = Alojamiento.objects.get(id = id_alojamiento)

        # 2 - Obteniendo la información adicional y añadiéndola al objeto de Alojamiento

        # 2.4 - Habitaciones
        alojamiento.habitaciones_asociadas = alojamiento.habitacion_set.all()
        alojamiento.cantidad_habitaciones_asociadas = len(alojamiento.habitaciones_asociadas)
        alojamiento.orden_habitacion = alojamiento.cantidad_habitaciones_asociadas + 1
        alojamiento.add_habitacion = alojamiento.check_add_habitacion()

        # 2.6 - Modalidad de alquiler
        if alojamiento.por_habitacion:
            alojamiento.modalidad_alquiler = 'por Habitación'
        else:
            alojamiento.modalidad_alquiler = 'Completo'

        # 2.7 - Precio Mínimo y Precio Máximo
        if alojamiento.por_habitacion:
            # Si el Alojamiento se alquila por Habitaciones, el precio mínimo es el menor de los precios de todas las habitaciones
            # Y el precio máximo es el mayor de todos los precios de todas las habitaciones
            # Este resultado contempla las reglas de precios de las Habitaciones del Alojamiento
            # El método precios_extremos del modelo Alojamiento devuelve una lista con dos precios de forma: [precio_minimo, precio_maximo]
            precio_minimo, precio_maximo = alojamiento.precios_extremos_alojamiento_por_habitacion()
        else:
            # Si el alojamiento se alquila completo el precio mínimo es el menor de los precios según las reglas de precio del Alojamiento
            precio_minimo, precio_maximo = alojamiento.alojamiento_completo.precios_extremos_alojamiento_completo()
        # Se asocian ambos precios extremos al Alojamiento por Habitacion
        alojamiento.precio_minimo = precio_minimo
        alojamiento.precio_maximo = precio_maximo

        # 2.8 - Fotos
        alojamiento.fotos = []
        # Si el Alojamiento se alquila por Habitaciones, Todas las fotos de las habitaciones, se muestran como fotos de este
        if alojamiento.por_habitacion:
            for habitacion in alojamiento.habitaciones_asociadas:
                for foto in habitacion.foto_habitacion_set.all():
                    alojamiento.fotos.append(foto)
        # Si el Alojamiento se alquila completo, las fotos de este son las fotos del Servicio relacionado
        else:
            for foto in alojamiento.servicio.foto_servicio_set.all():
                alojamiento.fotos.append(foto)
        alojamiento.cantidad_fotos = len(alojamiento.fotos)

        # 2.9 - Alojamientos similares cercanos
        alojamientos_cercanos = Alojamiento.objects.filter(Q(provincia = alojamiento.provincia, municipio = alojamiento.municipio, por_habitacion = alojamiento.por_habitacion) & ~Q(servicio__usuario = alojamiento.servicio.usuario))
        alojamiento.alojamientos_cercanos = alojamientos_cercanos

        # 1 - evaluaciones
        alojamiento.evaluaciones = alojamiento.servicio.evaluacion_set.order_by('-fecha')

        # Muestra de evaluaciones
        alojamiento.muestra_evaluaciones = alojamiento.evaluaciones[:3]

        # 3 - cantidad_evaluaciones
        alojamiento.cantidad_evaluaciones = len(alojamiento.evaluaciones)

        # 5 - Promedio de Evaluaciones
        evaluaciones_recomendado = 0
        evaluaciones_bueno = 0
        evaluaciones_promedio = 0
        evaluaciones_pobre = 0
        evaluaciones_terrible = 0
        puntuaciones = []
        for evaluacion in alojamiento.evaluaciones:
            puntuaciones.append(evaluacion.evaluacion)
            if evaluacion.evaluacion == 5:
                evaluaciones_recomendado += 1
            elif evaluacion.evaluacion == 4:
                evaluaciones_bueno += 1
            elif evaluacion.evaluacion == 3:
                evaluaciones_promedio += 1
            elif evaluacion.evaluacion == 2:
                evaluaciones_pobre += 1
            else:
                evaluaciones_terrible += 1
        cantidad_puntuaciones = len(puntuaciones)
        if cantidad_puntuaciones == 0:
            alojamiento.promedio_evaluaciones = None
            alojamiento.promedio_clientes_recomendado = None
            alojamiento.promedio_clientes_bueno = None
            alojamiento.promedio_clientes_promedio = None
            alojamiento.promedio_clientes_pobre = None
            alojamiento.promedio_clientes_terrible = None
        else:
            promedio_puntuaciones = sum(puntuaciones) / cantidad_puntuaciones
            alojamiento.promedio_evaluaciones = promedio_puntuaciones
            alojamiento.promedio_clientes_recomendado = evaluaciones_recomendado / cantidad_puntuaciones * 100
            alojamiento.promedio_clientes_bueno = evaluaciones_bueno / cantidad_puntuaciones * 100
            alojamiento.promedio_clientes_promedio = evaluaciones_promedio / cantidad_puntuaciones * 100
            alojamiento.promedio_clientes_pobre = evaluaciones_pobre / cantidad_puntuaciones * 100
            alojamiento.promedio_clientes_terrible = evaluaciones_terrible / cantidad_puntuaciones * 100

            # Cantidades de cada tipo de Evaluación
            alojamiento.cantidad_evaluaciones_recomendado = evaluaciones_recomendado
            alojamiento.cantidad_evaluaciones_bueno = evaluaciones_bueno
            alojamiento.cantidad_evaluaciones_promedio = evaluaciones_promedio
            alojamiento.cantidad_evaluaciones_pobre = evaluaciones_pobre
            alojamiento.cantidad_evaluaciones_terrible = evaluaciones_terrible

        # 6 - rating: Estrellas que representan el Promedio de Evaluaciones
            alojamiento.rating = Evaluacion.promedio_evaluaciones(alojamiento.servicio)

        # 7 - reservas
        alojamiento.reservas = alojamiento.servicio.reserva_set.order_by('initial_date')

        # 8 - cantidad_reservas
        alojamiento.cantidad_reservas = len(alojamiento.reservas)

        # 9 - ultima_reserva
        if alojamiento.reservas:
            alojamiento.ultima_reserva = alojamiento.reservas[::-1][0]
        else:
            alojamiento.ultima_reserva = None

        # Devolviendo los Alojamientos con los datos adicionales añadidos
        return alojamiento

'''
Los Alojamientos se clasifican según su modalidad de Alquiler: "Por Habitación" o "Completo". Cada Alojamiento va relacionado
a un único Servicio. Los Alojamientos pueden tener relacionados a ellos múltiples Habitaciones. Si el Alojamiento se alquila
por habitación, entonces cada Habitación relacionado a este es a su vez relacionada con un Servicio independiente.
'''
class Alojamiento(models.Model):
    acceso_discapacitados = models.BooleanField('Acceso para Discapacitados', blank = True, default = False)
    cantidad_habitaciones = models.IntegerField('Cantidad de Habitaciones', blank = False, null = False, unique = False)
    codigo_postal = models.CharField('Código Postal', max_length = 8, blank = False, null = False, unique = False)
    desayuno_cena = models.BooleanField('Desayuno/Cena', blank = True, default = False)
    direccion = models.CharField('Dirección Alojamiento', max_length = 128, blank = False, null = False, unique = False)
    latitud_gmaps = models.CharField('Latitud GMaps', max_length = 32, blank = True, null = True, unique = False)
    longitud_gmaps = models.CharField('Longitud GMaps', max_length = 32, blank = True, null = True, unique = False)
    internet = models.BooleanField('Internet', blank=False, unique=False)
    municipio = models.ForeignKey(Municipio, blank = True, null = True, unique = False, on_delete = models.DO_NOTHING)
    pais = models.ForeignKey(Pais, blank = False, null = False, unique = False, on_delete = models.DO_NOTHING)
    patio_terraza_balcon = models.BooleanField('Patio/Terraza/Balcón', blank = False, unique = False)
    parqueo = models.BooleanField('Parqueo', blank = False, unique = False)
    permitido_fumar = models.BooleanField('Permitido Fumar', blank = False, unique = False)
    permitido_mascotas = models.BooleanField('Permitido Mascotas', blank = False, unique = False)
    permitido_ninnos = models.BooleanField('Permitido Niños', blank = True, default = False)
    piscina = models.BooleanField('Piscina', blank = True, default = False)
    por_habitacion = models.BooleanField('Por Habitación', blank = True, default = True, unique = False)
    provincia = models.ForeignKey(Provincia, blank = False, null = False, unique = False, on_delete = models.DO_NOTHING)
    servicio = models.OneToOneField(Servicio, blank = False, null = False, on_delete = models.CASCADE)
    tipo_alojamiento = models.ForeignKey(Tipo_Alojamiento, blank = False, null = False, unique = False, on_delete = models.DO_NOTHING)
    transporte_aeropuerto = models.BooleanField('Transporte al Aeropuerto', blank = False, unique = False)

    # Devuelve una lista de enteros crecientes con paso 1, tan larga como habitaciones tenga el alojamiento.
    # Por ejemplo, si el Alojamiento tiene 4 habitaciones, devolverá la lista: [1, 2, 3, 4]
    # def range_habitaciones(self):
    @classmethod
    def get_agrupados_evaluacion(cls, alojamientos):
        # Se definen las listas vacías que formarán el diccionario
        alojamientos_5_estrellas = []
        alojamientos_4_estrellas = []
        alojamientos_3_estrellas = []
        alojamientos_2_estrellas = []
        alojamientos_1_estrellas = []

        # Se agrupan los alojamientos según su promedio de Evaluaciones
        for alojamiento in alojamientos:
            promedio_evaluaciones = alojamiento.servicio.get_promedio_evaluaciones()
            if promedio_evaluaciones:
                promedio_evaluaciones_alojamiento = round(promedio_evaluaciones)
                if promedio_evaluaciones_alojamiento == 5:
                    alojamientos_5_estrellas.append(alojamiento)
                elif promedio_evaluaciones_alojamiento == 4:
                    alojamientos_4_estrellas.append(alojamiento)
                elif promedio_evaluaciones_alojamiento == 3:
                    alojamientos_3_estrellas.append(alojamiento)
                elif promedio_evaluaciones_alojamiento == 2:
                    alojamientos_2_estrellas.append(alojamiento)
                elif promedio_evaluaciones_alojamiento == 1:
                    alojamientos_1_estrellas.append(alojamiento)

        # Se forma el diccionario con los grupos de alojamientos
        alojamientos_evaluacion = {
            '5_estrellas': alojamientos_5_estrellas,
            '4_estrellas': alojamientos_4_estrellas,
            '3_estrellas': alojamientos_3_estrellas,
            '2_estrellas': alojamientos_2_estrellas,
            '1_estrellas': alojamientos_1_estrellas,
        }

        # Se devuelve el diccionario con los Alojamientos agrupados por promedio de evaluaciones
        return alojamientos_evaluacion

    @classmethod
    def get_agrupados_caracteristicas(cls, alojamientos):
        aire_acondicionado = []
        agua_caliente = []
        caja_fuerte = []
        tv = []
        balcon = []
        acceso_discapacitados = []
        desayuno_cena = []
        internet = []
        parqueo = []
        patio_terraza_balcon = []
        permitido_fumar = []
        permitido_mascotas = []
        permitido_ninnos = []
        piscina = []
        transporte_aeropuerto = []
        apartamento = []
        casa = []
        mansion =  []
        cocina = []
        nevera_bar = []
        lavadora = []
        estereo = []
        ventanas = []
        banno_independiente = []


        # Se agrupan los alojamientos según sus características
        # Algunas características pueden aparecer tanto en la descripción del Alojamiento como en la descripción de las habitaciones.
        # En estos casos se valida cualquiera de los dos escenarios
        # Los casos son:
        # 1 - Aire Acondicionado: El alojamiento ccompleto tiene "aire acondicionado central" y el alojamiento por habitacion, sus habitaciones "aire acondicionado"
        # 2 - Estereo: Tanto el Alojamiento completo como las habitaciones tienen el atributo "estereo"
        # 3 - TV: Tanto el Alojamiento completo como las habitaciones tienen el atributo "tv"
        # 4 - Nevera Bar: Tanto el Alojamiento completo como las habitaciones tienen el atributo "nevera bar"
        for alojamiento in alojamientos:
            # a) acceso_discapacitados
            if alojamiento.acceso_discapacitados:
                acceso_discapacitados.append(alojamiento)
            # b) desayuno_cena
            if alojamiento.desayuno_cena:
                desayuno_cena.append(alojamiento)
            # c) internet
            if alojamiento.internet:
                internet.append(alojamiento)
            # d) parqueo
            if alojamiento.parqueo:
                parqueo.append(alojamiento)
            # e) patio_terraza_balcon
            if alojamiento.patio_terraza_balcon:
                patio_terraza_balcon.append(alojamiento)
            # f) permitido_fumar
            if alojamiento.permitido_fumar:
                permitido_fumar.append(alojamiento)
            # g) permitido_mascotas
            if alojamiento.permitido_mascotas:
                permitido_mascotas.append(alojamiento)
            # h) permitido_ninnos
            if alojamiento.permitido_ninnos:
                permitido_ninnos.append(alojamiento)
            # i) piscina
            if alojamiento.piscina:
                piscina.append(alojamiento)
            # j) transporte_aeropuerto
            if alojamiento.transporte_aeropuerto:
                transporte_aeropuerto.append(alojamiento)

            # Características de los Alojamientos Completos
            if not alojamiento.por_habitacion:
                # k) aire_acondicionado
                if alojamiento.alojamiento_completo.aire_acondicionado_central:
                    aire_acondicionado.append(alojamiento)
                # l) tv
                if alojamiento.alojamiento_completo.tv:
                    tv.append(alojamiento)
                # m) cocina
                if alojamiento.alojamiento_completo.cocina:
                    cocina.append(alojamiento)
                # n) nevera_bar
                if alojamiento.alojamiento_completo.nevera_bar:
                    nevera_bar.append(alojamiento)
                # ñ) lavadora
                if alojamiento.alojamiento_completo.lavadora:
                    lavadora.append(alojamiento)
                # o) estereo
                if alojamiento.alojamiento_completo.estereo:
                    estereo.append(alojamiento)
            else:
                habitaciones_alojamiento = alojamiento.habitacion_set.all()
                for habitacion in habitaciones_alojamiento:
                    # k) aire_acondicionado
                    if habitacion.aire_acondicionado:
                        if not alojamiento in aire_acondicionado:
                            aire_acondicionado.append(alojamiento)
                    # p) agua_caliente
                    if habitacion.agua_caliente:
                        if not alojamiento in agua_caliente:
                            agua_caliente.append(alojamiento)
                    # n) nevera_bar
                    if habitacion.nevera_bar:
                        if not alojamiento in nevera_bar:
                            nevera_bar.append(alojamiento)
                    # q) balcon
                    if habitacion.balcon:
                        if not alojamiento in balcon:
                            balcon.append(alojamiento)
                    # r) caja_fuerte
                    if habitacion.caja_fuerte:
                        if not alojamiento in caja_fuerte:
                            caja_fuerte.append(alojamiento)
                    # l) tv
                    if habitacion.tv:
                        if not alojamiento in tv:
                            tv.append(alojamiento)
                    # o) estereo
                    if habitacion.estereo:
                        if not alojamiento in estereo:
                            estereo.append(alojamiento)
                    # s) ventanas
                    if habitacion.ventanas:
                        if not alojamiento in ventanas:
                            ventanas.append(alojamiento)
                    # t) banno_independiente
                    if habitacion.habitacion_alojamiento_por_habitacion.banno_independiente:
                        if not alojamiento in banno_independiente:
                            banno_independiente.append(alojamiento)
            # u) apartamento
            if alojamiento.tipo_alojamiento.tipo == 'Apartamento':
                apartamento.append(alojamiento)
            # v) casa
            elif alojamiento.tipo_alojamiento.tipo == 'Casa':
                casa.append(alojamiento)
            # w) mansion
            elif alojamiento.tipo_alojamiento.tipo == 'Mansión':
                mansion.append(alojamiento)

        # Se forma el diccionario con los grupos de alojamientos
        alojamientos_caracteristicas = {
            'acceso_discapacitados': acceso_discapacitados, # ---- a)
            'desayuno_cena': desayuno_cena, # -------------------- b)
            'internet': internet, # ------------------------------ c)
            'parqueo': parqueo, # -------------------------------- d)
            'patio_terraza_balcon': patio_terraza_balcon, # ------ e)
            'permitido_fumar': permitido_fumar, # ---------------- f)
            'permitido_mascotas': permitido_mascotas, # ---------- g)
            'permitido_ninnos': permitido_ninnos, # -------------- h)
            'piscina': piscina, # -------------------------------- i)
            'transporte_aeropuerto': transporte_aeropuerto, # ---- j)
            'aire_acondicionado': aire_acondicionado, # ---------- k)
            'tv': tv, # ------------------------------------------ l)
            'cocina': cocina, # ---------------------------------- m)
            'nevera_bar': nevera_bar, # -------------------------- n)
            'lavadora': lavadora, # ------------------------------ ñ)
            'estereo': estereo, # -------------------------------- o)
            'agua_caliente': agua_caliente, # -------------------- p)
            'balcon': balcon, # ---------------------------------- q)
            'caja_fuerte': caja_fuerte, # ------------------------ r)
            'ventanas': ventanas, # ------------------------------ s)
            'banno_independiente': banno_independiente, # -------- t)
            'apartamento': apartamento, # ------------------------ u)
            'casa': casa, # -------------------------------------- v)
            'mansion': mansion, # -------------------------------- w)
        }

        # Se devuelve el diccionario con los Alojamientos agrupados por características
        return alojamientos_caracteristicas

    # Devuelve una lista de Habitaciones asociadas a este Alojamiento, que se encuentran disponibles en la totalidad de un rango de tiempo
    def get_habitaciones_disponibles(self, fecha_entrada, fecha_salida):
        # 1 - Obtener todas las Habitaciones asociadas al Alojamiento
        # 2 - Ir mirando una a una si las fechas indicadas se solapan con el período de tiempo de la indisponibilidad
        # 3 - La Habitación que no tenga indisponibilidad en las fechas indicadas, añadirla a una lista de habitaciones disponibles
        habitaciones = self.habitacion_set.all()
        habitaciones_disponibles = []
        for habitacion in habitaciones:
            if self.servicio.check_disponibilidad(fecha_entrada, fecha_salida, habitacion):
                # Si la Habitación está disponible para esas fechas se obtiene de paso el precio total en las mismas
                habitacion.precio_fechas = self.servicio.get_precio_fechas(fecha_entrada, fecha_salida, habitacion)
                habitaciones_disponibles.append(habitacion)
        return habitaciones_disponibles

    @classmethod
    def get_alojamientos_disponibles(cls, fecha_entrada, fecha_salida):
        alojamientos = cls.objects.filter(servicio__activo = True)
        alojamientos_disponibles = []
        for alojamiento in alojamientos:
            if alojamiento.servicio.check_disponibilidad(fecha_entrada, fecha_salida):
                alojamientos_disponibles.append(alojamiento)
        return alojamientos_disponibles

    @classmethod
    # Devuelve los Alojamientos donde al menos una Habitación está disponible entre las dos fechas indicadas y su capacidad es mayor o igual que el parametro huéspedes
    def filtrado_fechas_huespedes(cls, fecha_entrada, fecha_salida, huespedes):
        alojamientos_fechas_huespedes = []
        # Se analiza cada habitación de cada alojamiento. Si al menos una habitación cumple con las condiciones se añade a la lista de resultados positivos
        alojamientos = cls.objects.all()
        for alojamiento in alojamientos:
            if alojamiento.por_habitacion:
                for habitacion in alojamiento.habitacion_set.all():
                    if alojamiento.servicio.check_disponibilidad(fecha_entrada, fecha_salida, habitacion):
                        if habitacion.habitacion_alojamiento_por_habitacion.capacidad >= huespedes:
                            alojamientos_fechas_huespedes.append(alojamiento.id)
                            # Si un alojamiento cumple con todas las condiciones para pasar el filtro inmediatamente se pasa al siguiente sin analizar más de este
                            break
            else:
                if alojamiento.servicio.check_disponibilidad(fecha_entrada, fecha_salida):
                    if alojamiento.alojamiento_completo.capacidad >= huespedes:
                        alojamientos_fechas_huespedes.append(alojamiento.id)

        return alojamientos_fechas_huespedes

    @classmethod
    # Devuelve una lista ids de Alojamientos que se relacionan con un lugar
    def filtrado_lugar(cls, lugar):
        ids_alojamientos_lugar = []
        for alojamiento in cls.objects.all():
            # Filtrar por lugar lleva tres análisis:
            # 1 - Si la Provincia coincide
            # 2 - Si el Municipio coincide
            # 3 - Si la Provincia contiene algun destino que coincide
            # Provincia...
            if Servicio.compare_strings(alojamiento.provincia.nombre, lugar):
                ids_alojamientos_lugar.append(alojamiento.id)
                continue
            # Municipio...
            if Servicio.compare_strings(alojamiento.municipio.nombre, lugar):
                ids_alojamientos_lugar.append(alojamiento.id)
                continue
            # Destinos...
            # Selecciona todos los destinos que se encuentran en la Provincia del Alojamiento
            for destino in alojamiento.provincia.destino_set.all():
                if Servicio.compare_strings(destino.nombre, lugar):
                    ids_alojamientos_lugar.append(alojamiento.id)
                    break

        # Devuelve los resultados obtenidos
        return ids_alojamientos_lugar

    @classmethod
    # Crea el nuevo Alojamiento y su Servicio Asociado
    def nuevo_alojamiento(
        cls, acceso_discapacitados, cantidad_habitaciones, codigo_postal, desayuno_cena, descripcion, direccion,
        latitud, longitud, internet, municipio, nombre, pais, parqueo, patio_terraza_balcon, permitido_fumar, permitido_mascotas,
        permitido_ninnos, piscina, por_habitacion, provincia, tipo_alojamiento, transporte_aeropuerto, usuario, precio_base = None
    ):
        # Determinar si no existe un Alojamiento con ese nombre para el mismo usuario ya
        if cls.objects.filter(servicio__usuario = usuario, servicio__nombre = nombre):
            print('Ya existe un Alojamiento con nombre %s para %s' % (nombre, usuario))
            return None
        else:
            # 1 - Crear el servicio
            n_servicio = Servicio.nuevo_servicio(
                descripcion = descripcion,
                nombre = nombre,
                usuario = usuario,
                precio_base = precio_base,
            )
            # 2 - Si se pudo crear el servicio, entonces se crea el Alojamiento
            if n_servicio:
                n_alojamiento = cls.objects.create(
                    acceso_discapacitados = acceso_discapacitados,
                    cantidad_habitaciones = cantidad_habitaciones,
                    codigo_postal = codigo_postal,
                    desayuno_cena = desayuno_cena,
                    direccion = direccion,
                    latitud_gmaps = latitud,
                    longitud_gmaps = longitud,
                    internet = internet,
                    municipio = municipio,
                    pais = pais,
                    parqueo = parqueo,
                    patio_terraza_balcon = patio_terraza_balcon,
                    permitido_fumar = permitido_fumar,
                    permitido_mascotas = permitido_mascotas,
                    permitido_ninnos = permitido_ninnos,
                    piscina = piscina,
                    por_habitacion = por_habitacion,
                    provincia = provincia,
                    servicio = n_servicio,  # Se relaciona el Servicio creado con el Alojamiento que se va a crear
                    tipo_alojamiento = tipo_alojamiento,
                    transporte_aeropuerto = transporte_aeropuerto,
                )
                print('Se ha creado un alojamiento para %s con nombre %s' % (usuario, nombre))
                return n_alojamiento
            else:
                print('No se ha podido crear el servicio para el alojamiento %s' % (nombre))
                return None

    def modificar_alojamiento(
        self, acceso_discapacitados, cantidad_habitaciones, codigo_postal, desayuno_cena, descripcion, direccion,
        internet, municipio, nombre, parqueo, patio_terraza_balcon, permitido_fumar, permitido_mascotas,
        permitido_ninnos, piscina, precio_base, provincia, tipo_alojamiento, transporte_aeropuerto, latitud, longitud
    ):
        # Modificar el Servicio
        m_servicio = self.servicio.modificar_servicio(nombre = nombre, descripcion = descripcion, precio_base = precio_base)

        # Modificar el Alojamiento
        # Si se ha podido modificar el Servicio relacionado con el Alojamiento
        if m_servicio:
            self.acceso_discapacitados = acceso_discapacitados
            self.cantidad_habitaciones = cantidad_habitaciones
            self.codigo_postal = codigo_postal
            self.desayuno_cena = desayuno_cena
            self.direccion = direccion
            self.internet = internet
            self.municipio = municipio
            self.parqueo = parqueo
            self.patio_terraza_balcon = patio_terraza_balcon
            self.permitido_fumar = permitido_fumar
            self.permitido_mascotas = permitido_mascotas
            self.permitido_ninnos = permitido_ninnos
            self.piscina = piscina
            self.provincia = provincia
            self.tipo_alojamiento = tipo_alojamiento
            self.transporte_aeropuerto = transporte_aeropuerto
            self.latitud_gmaps = latitud
            self.longitud_gmaps = longitud
            self.servicio.save()
            self.save()
            print('Se ha modificado correctamente el Alojamiento %s' %(self))
            return self
        # Si no se ha podido modificar previamente el Servicio, no se prosigue con la Modificación
        else:
            print('No se ha podido modificar el Alojamiento %s por no haber podido modificar el Servicio relacionado' %(self))
            return None

    # Definir el precio mínimo de un Alojamiento que se alquila por Habitaciones
    def precios_extremos_alojamiento_por_habitacion(self):
        if self.habitacion_set.all():
            habitaciones = self.habitacion_set.order_by('alojamiento__servicio__nombre')
            precios_minimos = []
            precios_maximos = []
            for habitacion in habitaciones:
                precios_extremos = habitacion.habitacion_alojamiento_por_habitacion.precios_extremos()
                precios_minimos.append(precios_extremos[0])
                precios_maximos.append(precios_extremos[1])
            return min(precios_minimos), max(precios_maximos)
        else:
            return None, None

    # Verifica que se puedan seguir añadiendo Habitaciones al Alojamiento
    def check_add_habitacion(self):
        cantidad_habitaciones_creadas = len(self.habitacion_set.all())
        if self.cantidad_habitaciones > cantidad_habitaciones_creadas:
            return True
        else:
            return False

    # Elimina de la BD un Alojamiento en particular
    def eliminar_alojamiento(self):
        if not self.por_habitacion:
            self.alojamiento_completo.eliminar_alojamiento_completo()
        else:
            # Eliminar un Alojamiento por Habitaciones implica, eliminar las habitaciones con todas las fotos y directorios
            # y posteriormente eliminar el Alojamiento en sí.
            habitaciones = self.habitacion_set.all()
            for habitacion in habitaciones:
                habitacion.eliminar_habitacion()
            self.delete()

    objects = Alojamiento_Manager()

    class Meta:
        verbose_name_plural = 'Alojamientos'

    def __str__(self):
        return self.servicio.nombre

'''
Un Alojamiento Completo es un Alojamiento que se alquila en su totalidad. Es decir, no se alquilan sus habitaciones por
separado sino el Alojamiento en sí. Normalmente tiene un precio más caro que una Habitación independiente y además, puede
tener asociadas habitaciones, pero estas no constituyen servicios en sí, ni tienen precios independientes.
En este caso son simples elementos descriptivos del Alojamiento.
'''
class Alojamiento_Completo(models.Model):
    alojamiento = models.OneToOneField(Alojamiento, blank = False, null = False, unique = False, on_delete = models.CASCADE)
    aire_acondicionado_central = models.BooleanField('Aire Acondicionado Central', blank = True, unique = False, default = False)
    cantidad_bannos = models.IntegerField('Cantidad de Baños', blank = False, null = False, unique = False)
    capacidad = models.IntegerField('Capacidad', blank = False, null = False, unique = False)
    cocina = models.BooleanField('Cocina', blank = True, unique = False, default = False)
    estereo = models.BooleanField('Estéreo', blank = True, unique = False, default = False)
    lavadora = models.BooleanField('Lavadora', blank = True, unique = False, default = False)
    nevera_bar = models.BooleanField('Nevera/Bar', blank = True, unique = False, default = False)
    tv = models.BooleanField('TV', blank = True, unique = False, default = False)

    def eliminar_alojamiento_completo(self):
        # Eliminar un Alojamiento Completo implica eliminar todas las fotos y directorios asociados a este
        fotos_alojamiento = self.alojamiento.servicio.get_fotos_servicio()
        for foto_alojamiento in fotos_alojamiento:
            foto_alojamiento.eliminar_foto_servicio()
        # Una vez eliminadas las imágenes y los directorios relacionados con el servicio, se eliminan las Habitaciones del mismo
        habitaciones_alojamiento = self.alojamiento.habitacion_set.all()
        for habitacion_alojamiento in habitaciones_alojamiento:
            habitacion_alojamiento.eliminar_habitacion()
        # Cuando ya se han eliminado todas las imágenes, directorios y habitaciones de un alojamiento, entonces se elimina el Alojamiento, con su Servicio
        self.alojamiento.servicio.delete()

    @classmethod
    def nuevo_alojamiento_completo(
            cls, acceso_discapacitados, aire_acondicionado_central, cantidad_bannos, cantidad_habitaciones, capacidad, cocina,
            codigo_postal, desayuno_cena, descripcion, direccion, estereo, internet, lavadora, municipio, nevera_bar, nombre, pais,
            parqueo, patio_terraza_balcon, permitido_fumar, permitido_mascotas, permitido_ninnos, piscina, por_habitacion,
            precio_base, provincia, tipo_alojamiento, transporte_aeropuerto, tv, usuario, latitud, longitud
    ):
        # 1 - Crear el Alojamiento
        n_alojamiento = Alojamiento.nuevo_alojamiento(
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
            precio_base = precio_base,
            provincia = provincia,
            tipo_alojamiento = tipo_alojamiento,
            transporte_aeropuerto = transporte_aeropuerto,
            usuario = usuario,
        )
        # 2 - Si se ha podido crear el Alojamiento, entonces crear el Alojamiento Completo
        if n_alojamiento:
            n_alojamiento_completo = cls.objects.create(
                alojamiento = n_alojamiento,
                aire_acondicionado_central = aire_acondicionado_central,
                cantidad_bannos = cantidad_bannos,
                capacidad = capacidad,
                cocina = cocina,
                estereo = estereo,
                lavadora = lavadora,
                nevera_bar = nevera_bar,
                tv = tv,
            )
            print('Se ha creado correctamente el Alojamiento Completo: %s' %(n_alojamiento_completo.alojamiento.servicio.nombre))
            return n_alojamiento_completo
        else:
            print('No se ha podido crear el Alojamiento Completo para %s' %(usuario))
            return None

    def modificar_alojamiento_completo(
        self, acceso_discapacitados, aire_acondicionado_central, cantidad_bannos, cantidad_habitaciones, capacidad, cocina,
        codigo_postal, desayuno_cena, descripcion, direccion, estereo, internet, lavadora, municipio, nevera_bar, nombre,
        parqueo, patio_terraza_balcon, permitido_fumar, permitido_mascotas, permitido_ninnos, piscina,
        precio_base, provincia, tipo_alojamiento, transporte_aeropuerto, tv, latitud, longitud
    ):
        # Se modifica el Alojamiento
        m_alojamiento = self.alojamiento.modificar_alojamiento(
            acceso_discapacitados = acceso_discapacitados,
            cantidad_habitaciones = cantidad_habitaciones,
            codigo_postal = codigo_postal,
            desayuno_cena = desayuno_cena,
            descripcion = descripcion,
            direccion = direccion,
            internet = internet,
            municipio = municipio,
            nombre = nombre,
            parqueo = parqueo,
            patio_terraza_balcon = patio_terraza_balcon,
            permitido_fumar = permitido_fumar,
            permitido_mascotas = permitido_mascotas,
            permitido_ninnos = permitido_ninnos,
            piscina = piscina,
            precio_base = precio_base,
            provincia = provincia,
            tipo_alojamiento = tipo_alojamiento,
            transporte_aeropuerto = transporte_aeropuerto,
            latitud = latitud,
            longitud = longitud,
        )
        # Se modifica el Alojamiento Completo
        # Si se ha podido modificar el Alojamiento relacionado con el Alojamiento Completo
        if m_alojamiento:
            self.aire_acondicionado_central = aire_acondicionado_central
            self.cantidad_bannos = cantidad_bannos
            self.capacidad = capacidad
            self.cocina = cocina
            self.estereo = estereo
            self.lavadora = lavadora
            self.nevera_bar = nevera_bar
            self.tv = tv
            self.save()
            print('Se ha modificado correctamente el Alojamiento Completo %s' %(self))
            return self
        else:
            print('No se ha podido modificar el Alojamiento Completo %s' %(self))
            return None

    # Devuelve el precio más bajo entre el precio de base y todos los precios de las reglas asociadas a este alojamiento
    def precios_extremos_alojamiento_completo(self):
        reglas_precio = self.alojamiento.servicio.regla_precio_set.filter(activa = True).order_by('precio')
        if reglas_precio:
            precio_minimo = reglas_precio[0].precio
            precio_maximo = reglas_precio[::-1][0].precio
            return precio_minimo, precio_maximo
        else:
            # Si no hay reglas de Precios, el Precio Base es el mínimo establecido
            return self.alojamiento.servicio.precio_base, self.alojamiento.servicio.precio_base

    class Meta:
        verbose_name_plural = 'Alojamientos Completos'

    def __str__(self):
        return self.alojamiento.servicio.nombre

class Habitacion_Manager(models.Manager):
    def detalles_habitaciones(
            self,
            ids_habitaciones = (),
            ordered = 'nombre_asc',
            cerrada = False,
    ):
        habitaciones = Habitacion.objects.all()

        # Se aplican los filtros establecidos
        if not cerrada:
            habitaciones = habitaciones.filter(cerrada = False)

        if ids_habitaciones:
            habitaciones = habitaciones.filter(id__in = ids_habitaciones)

        # Se ordena según los requerimientos
        if ordered == 'nombre_asc':
            habitaciones = habitaciones.order_by('alojamiento__servicio__nombre')

        # Se añade la información adicional
        habitaciones_detalles = []
        for habitacion in habitaciones:
            habitacion_detalles = self.detalles_habitacion(habitacion.id)
            habitaciones_detalles.append(habitacion_detalles)

        return habitaciones_detalles

    def detalles_habitacion(self, id_habitacion):
        habitacion = Habitacion.objects.get(id = id_habitacion)

        # FOTOS
        fotos = habitacion.foto_habitacion_set.all()
        habitacion.fotos = fotos

        # ALOJAMIENTO
        alojamiento_detalles = Alojamiento.objects.detalles_alojamiento(id_alojamiento = habitacion.alojamiento.id)
        habitacion.alojamiento_detalles = alojamiento_detalles

        return habitacion


class Habitacion(models.Model):
    agua_caliente = models.BooleanField('Agua Caliente', blank = True, unique = False)
    aire_acondicionado = models.BooleanField('Aire Acondicionado', blank = True, unique = False)
    alojamiento = models.ForeignKey(Alojamiento, blank = False, null = False, unique = False, on_delete = models.CASCADE)
    balcon = models.BooleanField('Balcón', blank = True, unique = False)
    caja_fuerte = models.BooleanField('Caja Fuerte', blank = True, unique = False)
    camas_dobles = models.IntegerField('Camas Dobles', blank = False, null = False, unique = False)
    camas_individuales = models.IntegerField('Camas Individuales', blank = False, null = False, unique = False)
    estereo = models.BooleanField('Estéreo', blank = True, unique = False)
    max_fotos = models.IntegerField('Máximo de fotos permitidas', blank = False, null = False, unique = False, default = 5)
    nevera_bar = models.BooleanField('Nevera/Bar', blank = True, unique = False)
    tv = models.BooleanField('TV', blank = True, unique = False)
    ventanas = models.BooleanField('Ventanas', blank = True, unique = False)
    cerrada = models.BooleanField('Cerrada', blank = True, default = False, unique = False)

    def cerrar_habitacion(self):
        self.cerrada = True
        self.save()

    # Devuelve True o False, en función de si la Habitación puede ser eliminada por el Proveedor del Alojamiento asociado
    def allow_delete(self):
        # Esta capacidad está determinada al menos por si la Habitación ha sido reservado en el pasado. Si es el caso,
        # el proveedor no puede eliminarlo de la Base de Datos, solo "cerrarlo" para que no sea visible en los resultados de búsqueda
        for reserva_habitacion in self.reserva_habitacion_set.all():
            if reserva_habitacion.reserva.pago_set.filter(completado = True):
                return False
        return True

    # Devuelve True o False en función de si el Servicio puede ser Cerrado por el Proveedor
    def allow_close(self):
        # Un alojamiento no puede ser cerrado, si en caso de tener reservas pagadas, la fecha actual es anterior a alguna de las fechas de entrada de las reservas pagadas
        for reserva_habitacion in self.reserva_habitacion_set.all():
            if reserva_habitacion.reserva.pago_set.filter(completado = True):
                if datetime.date.today() < reserva_habitacion.reserva.initial_date:
                    return False

        # Si se llega a este punto es porque ninguna reserva asociada al Servicio (en caso de existir) tiene algún pago completado relacionado
        # y además su fecha de inicio es posterior a hoy
        return True

    # Devuelve True o False en función de si la Habitación puede ser eliminada por el Proveedor del Alojamiento
    def allow_delete_habitacion(self):
        # El criterio para definir si una habitación puede ser eliminada o no es si pertenece a un Alojamiento que ha tenido al menos una Reserva Pagada
        for reserva_habitacion in self.reserva_habitacion_set.all():
            if reserva_habitacion.reserva.pago_set.filter(completado = True):
                return False
        return True

    @classmethod
    # Devuelve una lista de Habitaciones que corresponden con todas las habitaciones de los Alojamientos que se indiquen como parametro del método
    # alojoamientos debe ser una lista de objetos Alojamiento
    def get_habitaciones_alojamientos(cls, alojamientos = ()):
        habitaciones_alojamientos = []
        for alojamiento in alojamientos:
            for habitacion_alojamiento in alojamiento.habitacion_set.all():
                if not habitacion_alojamiento in habitaciones_alojamientos:
                    habitaciones_alojamientos.append(habitacion_alojamiento)
        return habitaciones_alojamientos

    @classmethod
    # Devuelve una lista con los ids de los Alojamientos asociados a todas las habitaciones existentes
    def get_ids_alojamientos(cls):
        ids_alojamientos = []
        for habitacion in cls.objects.all():
            if habitacion.alojamiento.id not in ids_alojamientos:
                ids_alojamientos.append(habitacion.alojamiento.id)
        return ids_alojamientos


    @classmethod
    # Crea una nueva Habitación
    def nueva_habitacion(
            cls, alojamiento, aire_acondicionado, agua_caliente, nevera_bar,
            camas_dobles, camas_individuales, balcon, caja_fuerte, tv, estereo, ventanas
    ):
        n_habitacion = cls.objects.create(
            agua_caliente = agua_caliente,
            aire_acondicionado = aire_acondicionado,
            alojamiento = alojamiento,
            balcon = balcon,
            caja_fuerte = caja_fuerte,
            camas_dobles = camas_dobles,
            camas_individuales = camas_individuales,
            estereo = estereo,
            nevera_bar = nevera_bar,
            tv = tv,
            ventanas = ventanas,
        )
        if n_habitacion:
            return n_habitacion
        else:
            print('No se ha podido crear la habitación')
            return None

    # Modifica una Habitación que pertenece a un Alojamiento que se renta en su totalidad
    def modificar_habitacion(self, agua_caliente, aire_acondicionado, balcon, caja_fuerte, camas_dobles, camas_individuales, estereo, nevera_bar, tv, ventanas):
        self.agua_caliente = agua_caliente
        self.aire_acondicionado = aire_acondicionado
        self.balcon = balcon
        self.caja_fuerte = caja_fuerte
        self.camas_dobles = camas_dobles
        self.camas_individuales = camas_individuales
        self.estereo = estereo
        self.nevera_bar = nevera_bar
        self.tv = tv
        self.ventanas = ventanas
        self.save()
        return self

    def eliminar_habitacion(self):
        # Primero se comprueba si el Alojamiento al que pertenece la Habitación se alquila Completo o por Habitaciones
        if self.alojamiento.por_habitacion:
            # Si se alquila por habitaciones, entonces hay que eliminar todas las posibles fotos y carpetas asociadas a la Habitación
            fotos_habitacion = self.foto_habitacion_set.all()
            for foto_habitacion in fotos_habitacion:
                foto_habitacion.eliminar_foto_habitacion()
        # Se elimina si aún existe el directorio para las fotos de la Habitación
        self.eliminar_path()
        # Despues de eliminar si es necesario el directorio donde se almacenabas las, se elimina el objeto Habitación
        self.delete()

    def eliminar_path(self):
        path = '%s/media/usuarios/%s/rooms_photos/%s' % (os.getcwd(), self.alojamiento.servicio.usuario.id, self.id)
        if os.path.exists(path):
            shutil.rmtree(path)

    objects = Habitacion_Manager()

    class Meta:
        verbose_name_plural = 'Habitaciones'

    def __str__(self):
        return 'Habitación de %s' %(self.alojamiento)

class Habitacion_Alojamiento_Por_Habitacion(models.Model):
    banno_independiente = models.BooleanField('Baño Independiente', blank = True, unique = False)
    capacidad = models.IntegerField('Capacidad', blank=False, null=False, unique=False, default=3)
    habitacion = models.OneToOneField(Habitacion, blank = False, null = False, unique = False, on_delete = models.CASCADE)
    precio_base = models.DecimalField('Precio por Noche', max_digits = 6, decimal_places = 2, blank = False, null = False, unique = False)

    # Modifica una Habitación que pertenece a un Alojamiento que se alquila por habitaciones
    def modificar_habitacion_alojamiento_por_habitacion(
            self, agua_caliente, aire_acondicionado, balcon, banno_independiente, caja_fuerte, camas_dobles,
            camas_individuales, capacidad, estereo, nevera_bar, precio_base, tv, ventanas
    ):
        # Modificamos los datos de la Habitación
        self.habitacion.agua_caliente = agua_caliente
        self.habitacion.aire_acondicionado = aire_acondicionado
        self.habitacion.balcon = balcon
        self.habitacion.caja_fuerte = caja_fuerte
        self.habitacion.camas_dobles = camas_dobles
        self.habitacion.camas_individuales = camas_individuales
        self.habitacion.estereo = estereo
        self.habitacion.nevera_bar = nevera_bar
        self.habitacion.tv = tv
        self.habitacion.ventanas = ventanas
        self.habitacion.save()

        # Modificamos los datos de la Habitación de Alojamiento por Habitación
        self.banno_independiente = banno_independiente
        self.capacidad = capacidad
        self.precio_base = precio_base
        self.save()

        # Devuelve la Habitación
        return self.habitacion

    # Determina el precio Actual en función del Precio Base y las Reglas de Precio Establecidas
    def precio_actual(self):
        # 1 - Determinar las Reglas de Precio asociadas a esta Habitación
        reglas_precio = self.habitacion.regla_precio_set.filter(activa = True)
        if not reglas_precio:
            # Si no hay Reglas de Precio para esta habitación, el precio de la misma es el Precio Base
            return self.precio_base
        else:
            # En caso de que haya reglas de precio, se determina cuál está vigente
            regla_precio = reglas_precio[0]
            return regla_precio.precio

    # Devuelve el precio extremo de una Habitación en particular
    # Puede ser el máximo o el mínimo. El parámetro tipo puede ser: "precio" (Devuelve el mínimo), ó "-precio" (Devuelve el máximo)
    def precios_extremos(self):
        reglas_precio = self.habitacion.regla_precio_set.filter(activa = True).order_by('precio')
        if reglas_precio:
            precio_minimo_reglas = reglas_precio[0].precio
            precio_maximo_reglas = reglas_precio[::-1][0].precio
            return min(self.precio_base, precio_minimo_reglas), max(self.precio_base, precio_maximo_reglas)
        else:
            return self.precio_base, self.precio_base

    # Devuelve el menos de los precios establecidos para una Habitación
    def precio_minimo(self):
        return self.precios_extremos()[0]

    # Devuelve el menos de los precios establecidos para una Habitación
    def precio_maximo(self):
        return self.precios_extremos()[1]

    @classmethod
    # Crea una nueva Habitación para un Alojamiento por Habitación
    def nueva_habitacion_alojamiento_por_habitacion(
            cls, alojamiento, aire_acondicionado, banno_independiente, agua_caliente, nevera_bar, capacidad,
            camas_dobles, camas_individuales, balcon, caja_fuerte, tv, estereo, ventanas, precio_base
    ):
        # Valida que no se puedan crear mas habitaciones que las que el usuario ha indicado en la variable "cantidad_habitaciones" de su alojamiento
        cantidad_habitaciones_declaradas = alojamiento.cantidad_habitaciones
        cantidad_habitaciones_creadas = len(alojamiento.habitacion_set.all())
        if cantidad_habitaciones_creadas >= cantidad_habitaciones_declaradas:
            print('Ya se han creado %s habitaciones de %s declaradas en el Alojamiento' %(cantidad_habitaciones_creadas, cantidad_habitaciones_declaradas))
            return None
        else:
            # Verificar que el Alojamiento no ha alcanzado el número máximo de habitaciones declaradas por el usuario
            if alojamiento.check_add_habitacion():
                # Se crea la habitación genérica
                n_habitacion = Habitacion.nueva_habitacion(
                    agua_caliente = agua_caliente,
                    aire_acondicionado = aire_acondicionado,
                    alojamiento = alojamiento,
                    balcon = balcon,
                    caja_fuerte = caja_fuerte,
                    camas_dobles = camas_dobles,
                    camas_individuales = camas_individuales,
                    estereo = estereo,
                    nevera_bar = nevera_bar,
                    tv = tv,
                    ventanas = ventanas,
                )
                if n_habitacion:
                    # Se crea la habitación para este tipo de Alojamiento y se asocia a la habitación genérica ya creada
                    n_habitacion_alojamiento_por_habitacion = cls.objects.create(
                        banno_independiente = banno_independiente,
                        capacidad = capacidad,
                        habitacion = n_habitacion,
                        precio_base = precio_base,
                    )
                    if n_habitacion_alojamiento_por_habitacion:
                        return n_habitacion_alojamiento_por_habitacion
                    else:
                        print('Se ha creado la Habitación con id = %s, pero no se ha podido crear la habitación para este tipo de alojamiento' %(n_habitacion))
                        return None
                else:
                    print('No se ha podido crear la habitación genérica')
                    return None
            else:
                print('Ya no se pueden crear más habitaciones para el %s' %(alojamiento.alojamiento_por_habitacion))
                return None


    class Meta:
        verbose_name_plural = 'Habitaciones de Alojamientos por Habitación'

    def __str__(self):
        return 'Habitación de %s' %(self.habitacion.alojamiento)

class Regla_Precio(models.Model):
    fecha_desde = models.CharField('Desde', blank = False, null = False, unique = False, max_length = 10)
    fecha_hasta = models.CharField('Hasta', blank = False, null = False, unique = False, max_length = 10)
    precio = models.DecimalField('Precio', max_digits = 6, decimal_places = 2, blank = False, null = False, unique = False)
    activa = models.BooleanField('Activa', blank = True, default = True)

    # Los elementos con precios son los Servicios y las Habitaciones de los Alojamientos por Habitación
    servicio = models.ForeignKey(Servicio, blank = True, null = True, unique = False, on_delete = models.CASCADE)
    habitacion = models.ForeignKey(Habitacion, blank = True, null = True, unique = False, on_delete = models.CASCADE)

    @classmethod
    def obtener_numeros_meses_periodo(cls, mes_inicial, mes_final):
        # El primer paso es encontrar el los meses en el diccionario y obtener sus claves
        desde, hasta = None, None
        for mes in meses:
            if mes_inicial == meses[mes]:
                desde = int(mes)
            if mes_final == meses[mes]:
                hasta = int(mes)

        if desde < hasta:
            periodo = list(range(desde, hasta + 1))
        elif desde > hasta:
            periodo = list(range(desde, 13)) + list(range(1, hasta + 1))
        else:
            periodo = [desde]

        return periodo

    def activar_regla_precio(self):
        self.activa = True
        self.save()

    def desactivar_regla_precio(self):
        self.activa = False
        self.save()

    def cambiar_activacion_regla_precio(self):
        self.activa = not self.activa
        self.save()

    @classmethod
    def get_regla_precio(cls, servicio, fecha):
        return cls.objects.filter(servicio=servicio, fecha_desde__lte=fecha, fecha_hasta__gte=fecha)

    @classmethod
    def nueva_regla_precio(cls,fecha_desde, fecha_hasta, precio, servicio = None, habitacion = None):
        # 1 - Se debe garantizar que al menos haya indicado un servicio o una Habitación
        if not servicio and not habitacion:
            message = 'Debe indicar al menos un Servicio o una Habitación para añadir una regla a sus precios'
            print(message)
            return {'message': message}

        # 2 - También debe garantizarse que no se solapen meses entre las reglas de precio de una misma habitación o servicio
        if servicio:
            reglas_precio = servicio.regla_precio_set.all()
        elif habitacion:
            reglas_precio = habitacion.regla_precio_set.all()
        else:
            reglas_precio = None

        if reglas_precio:
            meses_incluidos_en_reglas = []
            for regla_precio in reglas_precio:
                meses_incluidos_en_reglas += Regla_Precio.obtener_numeros_meses_periodo(
                    mes_inicial = regla_precio.fecha_desde,
                    mes_final = regla_precio.fecha_hasta,
                )
            meses_periodo_nuevo = Regla_Precio.obtener_numeros_meses_periodo(
                mes_inicial = fecha_desde,
                mes_final = fecha_hasta,
            )
            for mes_periodo_nuevo in meses_periodo_nuevo:
                if mes_periodo_nuevo in meses_incluidos_en_reglas:
                    message = '%s ya ha sido incluido en una regla de precio anterior. No se pueden definir más de una regla para un mismo mes' %(meses[str(mes_periodo_nuevo)])
                    print(message)
                    return {'message': message}

        # 3 - Si ningun mes del período propuesto coincide con ningún mes de alguna de las reglas ya creadas, entonces se puede crear la nueva regla
        n_regla_precio = cls.objects.create(
            fecha_desde = fecha_desde,
            fecha_hasta = fecha_hasta,
            precio = precio,
            servicio = servicio,
            habitacion = habitacion,
        )
        if servicio:
            elemento = servicio
        elif habitacion:
            elemento = habitacion
        else:
            elemento = None
        if elemento:
            print('Se ha creado correctamente la Regla de precio para %s' % (elemento))
            return n_regla_precio
        else:
            message = 'Debe indicar al menos un Servicio o una Habitación para añadir una regla a sus precios'
            print(message)
            return {'message':  message}

    def modificar_regla_precio(self, fecha_desde, fecha_hasta, precio):
        # 2 - Debe garantizarse que no se solapen meses entre las reglas de precio de una misma habitación o servicio
        if self.servicio:
            reglas_precio = self.servicio.regla_precio_set.filter(~Q(id = self.id))
        elif self.habitacion:
            reglas_precio = self.habitacion.regla_precio_set.filter(~Q(id = self.id))
        else:
            reglas_precio = None

        if reglas_precio:
            meses_incluidos_en_reglas = []
            for regla_precio in reglas_precio:
                meses_incluidos_en_reglas += Regla_Precio.obtener_numeros_meses_periodo(
                    mes_inicial=regla_precio.fecha_desde,
                    mes_final=regla_precio.fecha_hasta,
                )
            meses_periodo_nuevo = Regla_Precio.obtener_numeros_meses_periodo(
                mes_inicial=fecha_desde,
                mes_final=fecha_hasta,
            )
            for mes_periodo_nuevo in meses_periodo_nuevo:
                if mes_periodo_nuevo in meses_incluidos_en_reglas:
                    message = '%s ya ha sido incluido en una regla de precio anterior. No se pueden definir más de una regla para un mismo mes' % (
                    meses[str(mes_periodo_nuevo)])
                    print(message)
                    return {'message': message}

        # 3 - Si ningun mes del período propuesto coincide con ningún mes de alguna de las reglas ya creadas, entonces se puede modificar la regla
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.precio = precio
        self.save()
        return self

    # Elimina una Regla de Precio de Servicio definida
    def eliminar_regla_precio(self):
        self.delete()

    class Meta:
        verbose_name_plural = 'Reglas de Precio'

    def __str__(self):
        if self.servicio:
            elemento = self.servicio
        else:
            elemento = self.habitacion
        return 'Regla de Precio de %s' %(elemento)

class Recorrido(models.Model):
    servicio = models.OneToOneField(Servicio, blank = False, null = False, on_delete = models.CASCADE)
    pax = models.IntegerField('Pax', blank = False, null = False, unique = False)
    precio = models.DecimalField('Precio', max_digits = 8, decimal_places = 2, blank = False, null = False, unique = False)
    provincia_origen = models.ForeignKey(Provincia, blank = False, null = False, unique = False, on_delete = models.DO_NOTHING, related_name = 'recorrido_provincia_origen')
    provincias = models.ManyToManyField(Provincia, blank = False, unique = False, related_name = 'recottido_provincias')

    class Meta:
        verbose_name_plural = 'Recorrido'

    def __str__(self):
        return 'Recorrido de %s' % (self.servicio.usuario)

class Excursion(models.Model):
    recorrido = models.OneToOneField(Recorrido, blank = False, null = False, on_delete = models.CASCADE)
    hora_inicio = models.TimeField('Hora de Inicio', blank = True, null = True, unique = False)
    hora_fin = models.TimeField('Hora de Fin', blank = True, null = True, unique = False)
    municipio_origen = models.ForeignKey(Municipio, blank = True, null = True, unique = False, on_delete = models.DO_NOTHING)
    provincia_destino = models.ForeignKey(Provincia, blank = False, null = False, unique = False, on_delete = models.DO_NOTHING, related_name = 'excursion_provincia_destino')

    @classmethod
    def get_excursiones_usuario(cls, usuario):
        escursiones_usuario = cls.objects.filter(recorrido__servicio__usuario = usuario)
        return escursiones_usuario

    class Meta:
        verbose_name_plural = 'Excursiones'

    def __str__(self):
        return 'Excursión de %s' % (self.recorrido.servicio.usuario)

class CityTour(models.Model):
    recorrido = models.OneToOneField(Recorrido, blank = False, null = False, on_delete = models.CASCADE)
    hora_inicio = models.TimeField('Hora de Inicio', blank = True, null = True, unique = False)
    hora_fin = models.TimeField('Hora de Fin', blank = True, null = True, unique = False)

    @classmethod
    def get_citytours_usuario(cls, usuario):
        citytours_usuario = cls.objects.filter(recorrido__servicio__usuario = usuario)
        return citytours_usuario

    class Meta:
        verbose_name_plural = 'CityTours'

    def __str__(self):
        return 'CityTour de %s' %(self.recorrido.servicio.usuario)

class Tour(models.Model):
    recorrido = models.OneToOneField(Recorrido, blank = False, null = False, on_delete = models.CASCADE)
    duracion_dias = models.IntegerField('Duración en días', blank = False, null = False)

    @classmethod
    def get_tours_usuario(cls, usuario):
        tours_usuario = cls.objects.filter(recorrido__servicio__usuario = usuario)
        return tours_usuario

    class Meta:
        verbose_name_plural = 'Tours'

    def __str__(self):
        return 'Tour de %s' %(self.recorrido.servicio.usuario)

class Marca(models.Model):
    nombre = models.CharField('Nombre', max_length = 64, blank = False, null = False, unique = True)
    descripcion = models.CharField('Descripción', max_length = 1024, blank = False, null = False, unique = False)

    class Meta:
        verbose_name_plural = 'Marcas'

    def __str__(self):
        return self.nombre

class Taxi(models.Model):
    servicio = models.OneToOneField(Servicio, blank = False, null = False, on_delete = models.CASCADE)
    marca = models.ForeignKey(Marca, blank = True, null = True, unique = False, on_delete = models.DO_NOTHING)
    modelo = models.CharField('Modelo', max_length = 32, blank = True, null = True, unique = False)
    precio = models.DecimalField('Precio diario', blank = False, null = False, unique = False, max_digits = 8, decimal_places = 2)

    @classmethod
    # Devuelve una lista de taxis asociados a un usuario
    def get_taxis_usuario(cls, usuario):
        taxis_usuaio = cls.objects.filter(servicio__usuario = usuario)
        return taxis_usuaio

    class Meta:
        verbose_name_plural = 'Taxis'

    def __str__(self):
        return self.servicio.nombre

class Estado_Servicio(models.Model):
    estado = models.CharField('Estado del Servicio', max_length = 32, blank = False, null = False, unique = True)
    descripcion = models.CharField('Descripción', max_length = 1024, blank = True, null = True)

    class Meta:
        verbose_name_plural = 'Posibles Estados de los Servicios'

    def __str__(self):
        return self.estado

class Reserva_Manager(models.Manager):
    def detalles_reservas(self, completada, usuario):
        reservas = Reserva.objects.order_by('initial_date')
        if completada:
            reservas = reservas.filter(pago__completado = True)
        if usuario:
            reservas = reservas.filter(usuario = usuario)
        reservas_servicios = []
        for reserva in reservas:
            reservas_servicios.append(self.detalles_reserva(id = reserva.id))
        return reservas_servicios


    def detalles_reserva(self, id, reserva_servicio = None):
        """
        Método para obtener información extra de la Reserva. Puede ser llamado cuando reserva un usuario autenticado o uno anónimo
        La diferencia consistirá en que si se llama desde la reservación por parte de un usuario anónimo, el id de la Reserva creada será None
        mientras que se pasará un diccionario con la información de una Reserva de Servicio en el parámetro "reserva".
        Siendo esto al revés en caso de que la reserva la esté realizando un usuario autenticado en el sistema
        :param id: El id de una Reserva de Servicio previamente creada. Se pasa si el usuario que crea la reserva está autenticado
        :param reserva: Un diccionario con información de Reserva de Servicio con la forma: {'servicio_id': alojamiento.servicio.id, 'alojamiento_id': alojamiento.id, 'initial_date': fecha_entrada, 'final_date': fecha_salida}
        :return: Devolverá un objeto Reserva de Servicio con información adicional, o bien el diccionario reserva recibido si el usuario no está autenticado
        """
        # Días de la semana de initial y final date
        dicdias = {
            'MONDAY': 'Lunes',
            'TUESDAY': 'Martes',
            'WEDNESDAY': 'Miercoles',
            'THURSDAY': 'Jueves',
            'FRIDAY': 'Viernes',
            'SATURDAY': 'Sabado',
            'SUNDAY': 'Domingo',
        }

        if id:
            # Este es el caso en que la Reserva la está realizando un usuario autenticado
            reserva = Reserva.objects.get(id = id)

            cantidad_noches = (reserva.final_date - reserva.initial_date).days
            initial_date_week = dicdias[reserva.initial_date.strftime('%A').upper()]
            final_date_week = dicdias[reserva.final_date.strftime('%A').upper()]
            reserva.cantidad_noches = cantidad_noches
            reserva.initial_date_week = initial_date_week
            reserva.final_date_week = final_date_week
            reserva.costo_gestion = costo_gestion_cuc
            reserva.impuestos = round(reserva.costo_gestion * impuesto_rate, 2)
            reserva.total_a_pagar = reserva.costo_gestion + reserva.precio_servicio + reserva.impuestos
            reserva.pago_online = reserva.comision + reserva.costo_gestion + reserva.impuestos
            reserva.pago_offline = reserva.total_a_pagar - reserva.pago_online
            if reserva.servicio.alojamiento:
                reserva.tipo_servicio = 'Alojamiento'
            elif reserva.servicio.recorrido:
                reserva.tipo_servicio = 'Recorrido'
            elif reserva.servicio.taxi:
                reserva.tipo_servicio = 'Taxi'
            elif reserva.servicio.pack:
                reserva.tipo_servicio = 'Pack'
            else:
                reserva.tipo_servicio = 'Not Defined'
            # Características de cancelación de la Reserva
            dias_restantes = (reserva.initial_date - datetime.date.today()).days
            # Para determinar el porciento de devolución, hay que ubicar la reserva en uno de los cuatro grupos temporales posibles.
            # a) Más del mínimo de días necesarios para que la devolución sea del 100%
            # b) Entre dicho mínimo de días y el máximo necesario para que la devolución sea de un porciento menor, pero mayor que el descuento máximo
            # c) Menos que dicho máximo, pero anterior al día de la reserva
            # d) El día de la Reserva
            # Se entiende que hay solo 4 grupos de distribución para las devoluciones por cancelaciones, así que se pueden identificar por el orden del porciento de devolución
            reglas_cancelacion = Regla_Cancelacion.objects.order_by('-porciento_devolucion')

            reserva.dias_restantes = dias_restantes
            for i in range(0, len(reglas_cancelacion)):
                if reglas_cancelacion[i].mas_de_x_dias and reglas_cancelacion[i].menos_de_x_dias:
                    if dias_restantes > reglas_cancelacion[i].mas_de_x_dias and dias_restantes < reglas_cancelacion[i].menos_de_x_dias:
                        reserva.porciento_devolucion = reglas_cancelacion[i].porciento_devolucion
                        break
                elif reglas_cancelacion[i].mas_de_x_dias:
                    if dias_restantes > reglas_cancelacion[i].mas_de_x_dias:
                        reserva.porciento_devolucion = reglas_cancelacion[i].porciento_devolucion
                        break
                elif reglas_cancelacion[i].menos_de_x_dias:
                    if dias_restantes < reglas_cancelacion[i].menos_de_x_dias:
                        reserva.porciento_devolucion = reglas_cancelacion[i].porciento_devolucion
                        break
                else:
                    reserva.porciento_devolucion = 0
                    break

            # Cantidad a devolver si cancelación
            # Se considera que una Reserva guardada en la BD no tiene que te tener un Pago asociado
            if reserva.pago_set.all():
                # En caso que la Reserva tenga un Pago asociado, se entiende que es unico
                reserva.pago = reserva.pago_set.first()
                # Se realiza una distribución en € de las partes que conforman el total del pago online realizado por el cliente
                distribucion_pago = reserva.pago.distribucion_pago()
                reserva.tipo_cambio = distribucion_pago['tipo_cambio'] # El Tipo de Cambio utilizado el día que se realizó el pago
                reserva.costo_gestion_euros = distribucion_pago['costo_gestion_euros'] # Parte del pago online que corresponde al Costo de Gestión de Ontraveline
                reserva.impuesto_euros = distribucion_pago['impuesto_euros'] # Parte del pago online que corresponde a los impuestos sobre el Costo de Gestión
                reserva.comision_euros = distribucion_pago['comision_euros'] # Parte del Pago online que se factura al Proveedor. Es la Comisión para este y la Pre-reserva para el Cliente
                reserva.total_reembolso = round(reserva.comision_euros * reserva.porciento_devolucion / Decimal(100), 2) # Cantidad a devolver en caso de Cancelación
                reserva.link_descarga_comprobante = '/media/comprobantes_reserva/%s.pdf' % (reserva.codigo_reserva)
                reserva.link_descarga_comprobante_cancelacion = '/media/comprobantes_cancelacion_reserva/%s_C.pdf' % (reserva.codigo_reserva)
            else:
                # En caso que no se haya realizado Pago en relación a la Reserva, se le asocian los atributos en None, para que puedan al menos ser llamados
                # Aunque no existe al momento motivo como para que sean llamados si no ha sido realizado algún pago para dicha Reserva
                reserva.pago = None
                reserva.tipo_cambio = None
                reserva.costo_gestion_euros = None
                reserva.impuesto_euros = None
                reserva.comision_euros = None
                reserva.total_reembolso = None
                reserva.link_descarga_comprobante = None
                reserva.link_descarga_comprobante_cancelacion = None

            # Si la reserva es cancelable o no
            if reserva.cancelacion_reserva_set.all():
                reserva.cancelable = False
            else:
                reserva.cancelable = True

            # Si la reserva es evaluable o no. Para que lo sea, el día actual debe ser posterior a la fecha de finalización de la reserva
            # Además no se puede haber cancelado la Reserva ni haber sido evaluado el servicio con anterioridad por le mismo usuario en relación a dicha reserva
            today = datetime.date.today()
            final_date = reserva.final_date
            cancelable = reserva.cancelable
            if today > final_date and cancelable and not reserva.evaluacion_set.all():
                reserva.evaluable = True
            else:
                reserva.evaluable = False

            return reserva
        else:
            # Este es el caso en que la Reserva la está realizando un usuario anónimo (no autenticado en el sistema)
            reserva_servicio['cantidad_noches'] = (reserva_servicio['final_date'] - reserva_servicio['initial_date']).days
            reserva_servicio['initial_date_week'] = dicdias[reserva_servicio['initial_date'].strftime('%A').upper()]
            reserva_servicio['final_date_week'] = dicdias[reserva_servicio['final_date'].strftime('%A').upper()]
            reserva_servicio['costo_gestion'] = costo_gestion_cuc
            reserva_servicio['impuestos'] = round(costo_gestion_cuc * impuesto_rate, 2)
            return reserva_servicio

class Reserva(models.Model):
    servicio = models.ForeignKey(Servicio, blank = False, null = False, unique = False, on_delete = models.CASCADE)
    initial_date = models.DateField('Fecha de Inicio', blank = False, null = False, unique = False)
    final_date = models.DateField('Fecha de Fin', blank = False, null = False, unique = False)
    usuario = models.ForeignKey('usuarios.Usuario', blank = False, null = False, unique = False, on_delete = models.CASCADE)
    precio_servicio = models.DecimalField('Precio', max_digits = 6, decimal_places = 2, blank = True, null = True, unique = False)
    comision = models.DecimalField('Comisión', max_digits = 6, decimal_places = 2, blank = True, null = True, unique = False)
    fecha_creacion = models.DateField('Fecha de creación', blank = False, null = False, unique = False, auto_now_add = True)
    ninnos = models.IntegerField('Niños', blank = True, null = True, unique = False)
    adultos = models.IntegerField('Adultos', blank = True, null = True, unique=False)
    codigo_reserva = models.CharField('Código de Reserva', max_length = 255, blank = True, null = True, unique = False)

    @classmethod
    # A partir de un diccionadio con datos de una reserva (usualmente alojada en la session) se crean y modifican los correspondientes registros en BD
    def crear_reserva_from_session(cls, usuario, reserva_dict):
        # Lo primero que hacemos con la Reserva es determinar el Pago asociado. No puede haber una Reserva sin Pago asociado
        pago = Pago.objects.get(reserva_dict__contains = reserva_dict['timestamp'])

        # Una vez identificamos el pago, entonces creamos el objeto Reserva a partir de la información del diccionario almacenado en el carro
        # Es posible que haya Alojamientos Completos y Por Habitación. Para los Alojamientos por Habitación, también se crean Reservas de Habitaciones

        alojamiento = Alojamiento.objects.get(id = reserva_dict['alojamiento_id'])
        # Si el Alojamiento se alquila Completo:
        if not alojamiento.por_habitacion:
            n_reserva = cls.nueva_reserva_servicio(
                servicio = alojamiento.servicio,
                initial_date = reserva_dict['initial_date'],
                final_date = reserva_dict['final_date'],
                usuario = usuario,
                precio_servicio = reserva_dict['precio_servicio'],
                ninnos = reserva_dict['ninnos'],
                adultos = reserva_dict['adultos'],
                comision = reserva_dict['comision'],
            )
            pago.reserva_dict = None
            pago.reserva = n_reserva
            pago.save()

        # Si el Alojamiento se alquila por Habitaciones
        else:
            # Primero se crea el objeto de Reserva y luego los objetos de Reservas de Habitaciones
            n_reserva = Reserva.nueva_reserva_servicio(
                servicio = alojamiento.servicio,
                initial_date = reserva_dict['initial_date'],
                final_date = reserva_dict['final_date'],
                usuario = usuario,
                precio_servicio = reserva_dict['precio_servicio'],
                comision = reserva_dict['comision'],
            )

            pago.reserva_dict = None
            pago.reserva = n_reserva
            pago.save()

            # Ahora detectamos cada reserva de habitación existente en el diccionario reserva_dict
            # y creamos un objeto de Reserva de Habitación para cada una
            for element in reserva_dict:
                # Solo las reservas de Habitaciones son diccionarios con key = ID de la Habitación
                if isinstance(reserva_dict[element], dict):

                    habitacion = Habitacion.objects.get(id = element)
                    precio, comision = habitacion.alojamiento.servicio.get_precio_comision_fechas(
                        fecha_entrada = reserva_dict['initial_date'],
                        fecha_salida = reserva_dict['final_date'],
                        habitacion = habitacion,
                    )

                    n_reserva_habitacion = Reserva_Habitacion.nueva_reserva_habitacion(
                        reserva = n_reserva,
                        habitacion = Habitacion.objects.get(id = element),
                        ninnos = reserva_dict[element]['ninnos'],
                        adultos = reserva_dict[element]['adultos'],
                        precio = precio,
                        comision = comision,
                    )

        # Devolvemos el objeto de Reserva creado
        return n_reserva

    @classmethod
    # Devuelve una lista de Reservas que no están completadas aún
    def get_reservas_incompletas(cls):
        return cls.objects.filter(completada = False)

    # Define el precio de una Reserva a partir de los precios de las Habitaciones que la conforman
    # Este método es únicamente válido en las Reservas de Alojamientos que se alquilan por Habitación
    def set_precio_from_habitaciones(self):
        precio_total = 0
        comision = 0
        for reserva_habitacion in self.reserva_habitacion_set.all():
            precio_total += reserva_habitacion.precio
            comision += reserva_habitacion.comision

        self.precio_servicio = precio_total
        self.comision = comision
        self.save()

    @classmethod
    def get_available_order(cls):
        # El objetivo es generar un código de Reserva compuesto por: 'YYYYMMDD###' donde '###' es un número aleatorio entre 111 y 999
        today = datetime.date.today()
        randint = random.randint(111, 999)
        # Este código debe ser único para cada Reserva, así que mientras haya alguna Reserva con un código igual al que acabamos de generar
        # (cosa improbable) seguimos generando nuevos códigos hasta que encontremos uno que no exista
        while cls.objects.filter(codigo_reserva = '%s%s%s%s' %(str(today.year), str(today.month).zfill(2), str(today.day).zfill(2), randint)):
            randint = random.randint(111, 999)
        # Si salimos del bucle quiere decir que hemos encontrado un código que no está asociado a ninguna Reserva
        codigo_reserva = '%s%s%s%s' %(today.year, str(today.month).zfill(2), str(today.day).zfill(2), randint)
        return codigo_reserva

    @classmethod
    def get_reservas_pendientes(cls):
        return cls.objects.filter(completada = False)

    def eliminar_reserva(self):
        # Hay que determinar si la Reserva tiene algunas Reservas de Habitaciones Asociadas y eliminarlas primero
        if self.reserva_habitacion_set.all():
            for reserva_habitacion in self.reserva_habitacion_set.all():
                reserva_habitacion.eliminar_reserva_habitacion()

        # Después que no haya ninguna dependencia "suelta", se elimina la Reserva
        self.delete()

    @classmethod
    # Crea una nueva Reserva de Servicio
    def nueva_reserva_servicio(cls, servicio, initial_date, final_date, usuario, precio_servicio = None, ninnos = None, adultos = None, comision = None):
        n_reserva_servicio = cls.objects.create(
            servicio = servicio,
            initial_date = initial_date,
            final_date = final_date,
            usuario = usuario,
            precio_servicio = precio_servicio,
            ninnos = ninnos,
            adultos = adultos,
            comision = comision,
            codigo_reserva = Reserva.get_available_order(),
        )
        return n_reserva_servicio

    def set_completada(self):
        # Poner el atributo: "completada" a True
        self.completada = True
        self.save()

    objects = Reserva_Manager()

    class Meta:
        verbose_name_plural = 'Reservas de Servicios'

    def __str__(self):
        return 'Reserva de %s' %(self.servicio)


class Reserva_Habitacion_Manager(models.Manager):
    def detalles_reservas_habitaciones(self, reserva_servicio):
        reservas_habitaciones = []
        for reserva_habitacion in reserva_servicio.reserva_habitacion_set.all():
            reservas_habitaciones.append(self.detalles_reserva_habitacion(reserva_habitacion))

        return reservas_habitaciones

    def detalles_reserva_habitacion(self, reserva_habitacion):
        pass

class Reserva_Habitacion(models.Model):
    reserva = models.ForeignKey(Reserva, blank = False, null = False, unique = False, on_delete = models.CASCADE)
    habitacion = models.ForeignKey(Habitacion, blank = False, null = False, unique = False, on_delete = models.CASCADE)
    ninnos = models.IntegerField('Niños', blank = True, null = True, unique = False)
    adultos = models.IntegerField('Adultos', blank=True, null=True, unique=False)
    precio = models.DecimalField('Precio', max_digits=6, decimal_places=2, blank=True, null=True, unique=False)
    comision = models.DecimalField('Comisión', max_digits=6, decimal_places=2, blank=True, null=True, unique=False)

    def eliminar_reserva_habitacion(self):
        self.delete()

    def precio_total(self):
        # Devuelve la suma del precio más la comisión de una Reserva de Habitación
        return self.precio + self.comision

    @classmethod
    def nueva_reserva_habitacion(cls, reserva, habitacion, ninnos, adultos, precio, comision):
        n_reserva_habitacion = cls.objects.create(
            reserva = reserva,
            habitacion = habitacion,
            ninnos = ninnos,
            adultos = adultos,
            precio = precio,
            comision = comision,
        )

        return n_reserva_habitacion

    objects = Reserva_Habitacion_Manager()

    class Meta:
        verbose_name_plural = 'Reservas de Habitaciones'

    def __str__(self):
        return 'Reserva de %s' %(self.habitacion)


class Alojamiento_sin_finalizar(models.Model):
    # Datos Generales
    acceso_discapacitados = models.BooleanField('Acceso para Discapacitados', blank = True, default = False)
    cantidad_habitaciones = models.IntegerField('Cantidad de Habitaciones', blank = True, null = True, unique = False)
    codigo_postal = models.CharField('Código Postal', max_length = 8, blank = True, null = True, unique = False)
    desayuno_cena = models.BooleanField('Desayuno/Cena', blank = True, default = False)
    descripcion = models.CharField('Descripción', max_length = 1024, blank = True, null = True, unique = False)
    direccion = models.CharField('Dirección', max_length = 128, blank = True, null = True, unique = False)
    latitud = models.CharField('Latitud GMaps', max_length = 32, blank = True, null = True, unique = False)
    longitud = models.CharField('Longitud GMaps', max_length = 32, blank = True, null = True, unique = False)
    internet = models.BooleanField('Internet', blank = True, default = False)
    municipio = models.ForeignKey(Municipio, blank = True, null = True, on_delete = models.CASCADE)
    nombre = models.CharField('Nombre', max_length = 64, blank = True, null = True, unique = False)
    pais = models.ForeignKey(Pais, blank = True, null = True, unique = False, on_delete = models.CASCADE)
    parqueo = models.BooleanField('Parqueo', blank = True, default = False)
    patio_terraza_balcon = models.BooleanField('Patio/Terraza/Balcón', blank = True, default = False)
    permitido_fumar = models.BooleanField('Permitido Fumar', blank = True, default = False)
    permitido_mascotas = models.BooleanField('Permitido Mascotas', blank = True, default = False)
    permitido_ninnos = models.BooleanField('Permitido Niños', blank = True, default = False)
    piscina = models.BooleanField('Piscina', blank = True, default = False)
    por_habitacion = models.BooleanField('Por Habitación', blank = True, default = True)
    provincia = models.ForeignKey(Provincia, blank = True, null = True, on_delete = models.CASCADE)
    tipo_alojamiento = models.ForeignKey(Tipo_Alojamiento, blank = True, null = True, unique = False, on_delete = models.CASCADE)
    transporte_aeropuerto = models.BooleanField('Transporte Aeropuerto', blank = True, default = False)
    usuario = models.ForeignKey('usuarios.Usuario', blank = True, null = True, unique = False, on_delete = models.CASCADE)

    @classmethod
    # Creación del Alojamiento e incorporación de los Datos Generales del mismo. Este método es llamado en el paso 1 del proceso de registro de un Alojamiento
    def nuevo_alojamiento_sin_finalizar(
        cls, acceso_discapacitados, cantidad_habitaciones, codigo_postal, desayuno_cena, descripcion, direccion, latitud, longitud,
        internet, municipio, nombre, pais, parqueo, patio_terraza_balcon, permitido_fumar, permitido_mascotas,
        permitido_ninnos, piscina, por_habitacion, provincia, tipo_alojamiento, transporte_aeropuerto, usuario
    ):
        if cls.objects.filter(usuario = usuario):
            print('El usuario %s tiene un Alojamiento sin Finalizar. Debe finalizarlo antes de iniciar el proceso de registrar otro')
            return None
        else:
            n_alojamiento_sin_finalizar = cls.objects.create(
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
            return n_alojamiento_sin_finalizar

    # incorporación de los Servicios y características a un Alojamiento Incompleto. Es llamado en el paso 2 del proceso de creación del Alojamiento
    def add_servicios_alojamiento_por_habitacion(self, internet, patio_terraza_balcon, parqueo, permitido_fumar, permitido_mascotas, transporte_aeropuerto):
        self.internet = internet
        self.patio_terraza_balcon = patio_terraza_balcon
        self.parqueo = parqueo
        self.permitido_fumar = permitido_fumar
        self.permitido_mascotas = permitido_mascotas
        self.transporte_aeropuerto = transporte_aeropuerto
        self.save()
        return self

    @classmethod
    # Elimina todos los Alojamientos sin finalizar existentes
    def eliminar_alojamientos_sin_finalizar(cls):
        alojamientos_sin_finalizar = cls.objects.all()
        for alojamiento_sin_finalizar in alojamientos_sin_finalizar:
            alojamiento_sin_finalizar.delete()

    class Meta:
        verbose_name_plural = 'Alojamientos sin finalizar'

    def __str__(self):
        return 'Alojamiento de %s sin finalizar' %(self.usuario)

# FOTOS DE SERVICIOS
def services_photos_directory(instance, filename):
    return 'usuarios/{0}/services_photos/{1}/{2}'.format(
        instance.servicio.usuario.id,
        instance.servicio.id,
        filename,
    )

# FOTOS DE HABITACIONES
def rooms_photos_directory(instance, filename):
    return 'usuarios/{0}/rooms_photos/{1}/{2}'.format(
        instance.habitacion.alojamiento.servicio.usuario.id,
        instance.habitacion.id,
        filename,
    )

# FOTOS DE Destinos
def destinations_photos_directory(instance, filename):
    return 'destinos/{0}/{1}'.format(
        instance.destino.id,
        filename,
    )

class Evaluacion(models.Model):
    servicio = models.ForeignKey(Servicio, blank = False, null = False, unique = False, on_delete = models.CASCADE)
    reserva = models.ForeignKey(Reserva, blank = True, null = True, unique = False, on_delete = models.CASCADE)
    titulo = models.CharField('Título', max_length = 64, blank = True, null = True, unique = False)
    evaluacion = models.IntegerField('Evaluación', blank = False, null = False, unique = False, default = 0)
    comentario = models.CharField('Comentario', max_length = 1024, blank = True, null = True, unique = False)
    usuario = models.ForeignKey('usuarios.Usuario', blank = False, null = False, unique = False, on_delete = models.CASCADE)
    fecha = models.DateTimeField('Fecha', blank = False, null = False, unique = False, auto_now_add = True)

    # Si un comentario es más largo que una cantidad de caracteres determinada, se devuelve en dos partes
    # Útil para mostrar vistas previas de publicaciones o textos largos
    def comentario_dividido(self):
        largo_primera_parte = 50
        primera_parte = self.comentario[:largo_primera_parte]
        if len(primera_parte) == len(self.comentario):
            return [self.comentario, None]
        else:
            return [self.comentario[:largo_primera_parte], self.comentario[largo_primera_parte:]]

    # Devuelve la combinación de estrellas para una Evaluación según su puntuación
    def evaluacion_estrellas(self):
        rating = []
        for value in range(self.evaluacion):
            rating.append('fa-star')
        while len(rating) < 5:
            rating.append('fa-star-o')
        return rating

    @classmethod
    # Devuelve la combinación de estrellas de un Servicio según el promedio de todas las puntuaciones de sus evaluaciones
    def promedio_evaluaciones(cls, servicio):
        evaluaciones_servicio = cls.objects.filter(servicio = servicio)
        if evaluaciones_servicio:
            # Una vez obtenidos todos los objetos Evaluación, se construye la estructura de estrellas que representa su promedio
            acumulado = 0
            rating = []
            for evaluacion_servicio in evaluaciones_servicio:
                acumulado += evaluacion_servicio.evaluacion
            if acumulado == 0:
                rating = ['fa-star-o', 'fa-star-o', 'fa-star-o', 'fa-star-o', 'fa-star-o']
            else:
                promedio_evaluaciones = acumulado / len(evaluaciones_servicio)
                entero = int(promedio_evaluaciones)
                decimal = abs(promedio_evaluaciones) - abs(entero)
                # Se añaden tantos "True" como unidades completas haya.
                for star in range(entero):
                    rating.append('fa-star')
                # Para determinar si el sobrante decimal implica media, una o ninguna estrella, se sigue la sgte lógica:
                if decimal > 0.25 and decimal < 0.75:
                    rating.append('fa-star-half-o')
                elif decimal > 0.75:
                    rating.append('fa-star')
                # Completamos con 5 estrellas la puntuación
                while len(rating) < 5:
                    rating.append('fa-star-o')
            return rating
        else:
            return None

    @classmethod
    def nueva_evaluacion(cls, servicio, reserva, usuario, evaluacion, titulo, comentario):
        # Se valida que la evaluación es un número entre 1 y 5
        if int(evaluacion) > 0 and int(evaluacion) < 6:
            # También se valida que no exista ya una evaluación del mismo usuario con la misma reserva
            if cls.objects.filter(usuario = usuario, reserva = reserva):
                message = 'Ya el usuario %s ha evaluado el servicio en relación a la %s' %(usuario, reserva)
                print(message)
                return {
                    'message': message,
                }
            else:
                n_evaluacion = cls.objects.create(
                    servicio = servicio,
                    reserva = reserva,
                    usuario = usuario,
                    evaluacion = int(evaluacion),
                    titulo = titulo,
                    comentario = comentario,
                )
                return n_evaluacion
        else:
            message = 'La evaluación debe ser un número entre 1 y 5'
            print(message)
            return {
                'message': message,
            }

    def modificar_evaluacion(self, evaluacion, titulo, comentario):
        # Se valida que la evaluación es un número entre 1 y 5
        if int(evaluacion) > 0 and int(evaluacion) < 6:
            self.evaluacion = int(evaluacion)
            self.titulo = titulo
            self.comentario = comentario
            self.save()
            print('Se ha modificado correctamente la Evaluación')
            return self
        else:
            message = 'La evaluación debe ser un número entre 1 y 5 (ambos incluídos)'
            print(message)
            return {
                'message': message,
            }

    class Meta:
        verbose_name_plural = 'Evaluaciones'

    def __str__(self):
        return 'Evaluación para %s' %(self.servicio)

class Foto_Destino(models.Model):
    destino = models.ForeignKey(Destino, blank = False, null = False, unique = False, on_delete = models.CASCADE)
    foto = models.ImageField('Foto Servicio', upload_to = destinations_photos_directory, blank = True, null = True)

    @classmethod
    def nueva_fotodestino(cls, destino, foto):
        n_foto_destino = cls.objects.create(
            destino = destino,
            foto = foto,
        )

        # Procesar la imagen almacenada
        img_url = '%s/%s' % (os.getcwd(), n_foto_destino.foto.url)
        Foto_Servicio.procesar_foto_post(img_url)

        return n_foto_destino

    def eliminar_foto_destino(self):
        # Se elimina el archivo de imagen relacionado con la foto del Destino
        self.foto.delete()
        # Antes de eliminar el Objeto de Foto, debe comprobarse si es la última foto existente del Destino.
        # Si es así, se debe eliminar el directorio que contenía las fotos
        destinations_photos_path = '%s/media/destinos/%s' %(os.getcwd(), self.destino.id)
        if os.path.exists(destinations_photos_path):
            if not os.listdir(destinations_photos_path):
                shutil.rmtree(destinations_photos_path)
        # Si no queda ningún Destino con imágenes, se elimina también el directorio "destinations_photos"
        # destinations_photos_path = '%s/media/destinos/%s' %(os.getcwd(), self.destino.id)
        # if not os.listdir(destinations_photos_path):
        #     shutil.rmtree(destinations_photos_path)
        self.delete()

    class Meta:
        verbose_name_plural = 'Fotos de Destinos'

    def __str__(self):
        return 'Foto de %s' %(self.destino)


class Foto_Servicio(models.Model):
    servicio = models.ForeignKey(Servicio, blank = False, null = False, unique = False, on_delete = models.CASCADE)
    foto = models.ImageField('Foto Servicio', upload_to = services_photos_directory, blank = True, null = True)

    @classmethod
    def nueva_foto_servicio(cls, servicio, foto):
        # Se valida que se pueden añadir más Fotos al Servicio en cuestión
        if len(servicio.foto_servicio_set.all()) >= servicio.max_fotos:
            print('Se ha alcanzado el número máximo de fotos posibles a añadir para este Servicio')
            return None
        else:
            n_foto_servicio = cls.objects.create(
                servicio = servicio,
                foto = foto,
            )

            # Procesar la imagen almacenada
            img_url = '%s/%s' % (os.getcwd(), n_foto_servicio.foto.url)
            Foto_Servicio.procesar_foto_servicio(img_url)

            # Si un servicio tiene al menos una foto, se marca como activo. Esta es una de las dos condiciones para que un
            # Servicio sea visible a lo clientes. La otra condición es que el usuario que lo ha creado sea proveedor y esté verificado como tal
            servicio.activo = True
            servicio.save()

            return n_foto_servicio

    def eliminar_foto_servicio(self):
        # Se elimina el archivo de imagen relacionado con la foto del Servicio
        self.foto.delete()
        # Antes de eliminar el Objeto de Foto, debe comprobarse si es la última foto existente del Servicio.
        # Si es así, se debe eliminar el directorio que contenía las fotos
        service_photos_path = '%s/media/usuarios/%s/services_photos/%s' %(os.getcwd(), self.servicio.usuario.id, self.servicio.id)
        if not os.listdir(service_photos_path):
            shutil.rmtree(service_photos_path)

            # Quizás redundantemente, verificamos que hay un solo registro de Foto de Servicio asociado al Servicio al que pertenece esta foto
            # Esto quiere decir, que se está a punto de eliminar la última foto, y el servicio debe ser marcado como activo = False
            if len(self.servicio.foto_servicio_set.all() == 1):
                self.servicio.activo = False
                self.save()

        # Si no queda ningún Servicio con imágenes, se elimina también el directorio "services_photos"
        services_photos_path = '%s/media/usuarios/%s/services_photos' %(os.getcwd(), self.servicio.usuario.id)
        if not os.listdir(services_photos_path):
            shutil.rmtree(services_photos_path)
        self.delete()

    # Inserta una marca de agua en una foto
    @classmethod
    def reduce_opacity(cls, im, opacity):
        """Returns an image with reduced opacity."""
        assert opacity >= 0 and opacity <= 1
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        else:
            im = im.copy()
        alpha = im.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        im.putalpha(alpha)
        return im

    @classmethod
    def insert(cls, im, mark):
        """Adds a watermark to an image."""
        mark = cls.reduce_opacity(mark, 0.4)
        # create a transparent layer the size of the image and draw the
        # watermark in that layer.
        layer = Image.new('RGBA', im.size, (0, 0, 0, 0))

        # scale, but preserve the aspect ratio
        ratio = min(
            float(im.size[0]) / mark.size[0], float(im.size[1]) / mark.size[1])
        w = int(mark.size[0] * ratio / 2)
        h = int(mark.size[1] * ratio / 2)
        mark = mark.resize((w, h))
        layer.paste(mark, (int((im.size[0] - w) / 2), int((im.size[1] - h) / 2)))

        # composite the watermark with the layer
        return Image.composite(layer, im, layer)

    @classmethod
    def watermark(cls, im_url, mark_url):
        im = Image.open(im_url).convert('RGB')
        mark = Image.open(mark_url)
        ##    watermark(im, mark, 'tile', 0.5).save("fin.jpg")
        cls.insert(im, mark).save(im_url)

    ##    watermark(im, mark, (100, 100), 0.5).save("fin.jpg")

    # Convierte una imagen a 800x600 y recorta a partir del centro de la imagen tomando el 100% de la menor dimensión
    # Esto reduce y estandariza las imágenes que almacenamos de los Servicios y usuarios
    @classmethod
    def crop_from_center(cls, image_url, width, height, save=False):
        image_file = Image.open(image_url)
        # 1 - Detectar el mayor de los lados para adaptarlo al marco deseado
        w, h = image_file.size
        if w > h:
            r_factor = h / height
        else:
            r_factor = w / width

        # 2 - Redimensionar la imagen al marco
        resized_img = image_file.resize((int(round(w / r_factor, 0)), int(round(h / r_factor, 0))), Image.ANTIALIAS)

        # 3 - Seleccionar el fragmento de la imagen centrado deseado
        croped_img = resized_img.crop(((resized_img.width / 2 - width / 2), (resized_img.height / 2 - height / 2),
                                       # Coordenadas de inicio de recorte (x, y)
                                       (resized_img.width / 2 - width / 2) + width, (
                                       resized_img.height / 2 - height / 2) + height))  # Coordenadas de fin de recorte (x, y)
        if save:
            croped_img.save(image_url)

        # 4 - Devolver la imagen modificada
        return croped_img

    @classmethod
    def procesar_foto_servicio(cls, img_url):
        """
        Formatea una imagen para asociarla a un Servicio o una Habitación. El formateo consiste en reducirle el tamaño,
        las dimensiones, e imprimirle una marca de agua con el logo de Ontraveline.
        :param img_url: str que define el path donde se encuentra la imagen que hay que procesar
        :return: No devuelve nada, solo formatea la imagen guardada
        """
        mark_url = '%s/static_files/img/backgrounds/mark.png' % (os.getcwd())
        # 1 - Se reduce a 800 x 600
        cls.crop_from_center(img_url, 800, 600, save = True)
        # 2 - Se le imprime la marca de agua de Ontraveline
        cls.watermark(img_url, mark_url)

    @classmethod
    # Con este método se establecen las medidas de una imagen a partir de su centro, garantizando incluir siempre la dimensión más pequeña
    def procesar_foto_post(cls, img_url):
        cls.crop_from_center(img_url, 1200, 500, save = True)

    @classmethod
    # Este método reduce el peso de la imagen sin atender a las dimensiones de la misma y manteniendo la proporción
    def procesar_foto_documento_personal(cls, img_url):
        while os.path.getsize(img_url) > 300 * 1024:
            imagen = Image.open(img_url, mode = 'r')
            width, height = imagen.size
            imagen = imagen.resize((int(width * 92 / 100), int(height * 92 / 100)), Image.ANTIALIAS)
            imagen.save(img_url)

    @classmethod
    def procesar_foto_licencia_actividad(cls, img_url):
        # El tratamiento es el mismo para una imagen de Documento Personal que para una Imagen de Licencia de Actividad
        cls.procesar_foto_documento_personal(img_url)

    class Meta:
        verbose_name_plural = 'Fotos de Servicios'

    def __str__(self):
        return 'Foto de %s' %(self.servicio)

class Foto_Habitacion(models.Model):
    habitacion = models.ForeignKey(Habitacion, blank = False, null = False, unique = False, on_delete = models.CASCADE)
    foto = models.ImageField('Foto Habitacion', upload_to = rooms_photos_directory, blank = True, null = True)

    def eliminar_foto_habitacion(self):
        """
        Elimina una foto de Habitación
        :return: No devuelve nada, simplemente elimina registros de la BD, ficheros de fotos, y de ser necesario un directorio
        """
        # Se elimina el archivo de imagen relacionado con la foto de la Habitación
        self.foto.delete()
        # Antes de eliminar el Objeto Foto de Habitación, debe comprobarse si es la última foto existente de la Habitación.
        # Si es así, se debe eliminar el directorio que contenía las fotos
        habitacion_photos_path = '%s/media/usuarios/%s/rooms_photos/%s' %(os.getcwd(), self.habitacion.alojamiento.servicio.usuario.id, self.habitacion.id)
        if not os.listdir(habitacion_photos_path):
            shutil.rmtree(habitacion_photos_path)
        habitaciones_photos_path = '%s/media/usuarios/%s/rooms_photos' %(os.getcwd(), self.habitacion.alojamiento.servicio.usuario.id)
        if not os.listdir(habitaciones_photos_path):
            shutil.rmtree(habitaciones_photos_path)
        self.delete()

    @classmethod
    def nueva_foto_habitacion(cls, habitacion, foto):
        # Se valida que se pueden añadir más Fotos a la Habitación en cuestión
        if len(habitacion.foto_habitacion_set.all()) >= habitacion.max_fotos:
            print('Se ha alcanzado el número máximo de fotos posibles a añadir para esta Habitación')
            return None
        elif not habitacion.alojamiento.por_habitacion:
            print('No se pueden añadir fotos a Habitaciones de Alojamientos que se alquilan completos')
            return None
        else:
            n_foto_habitacion = cls.objects.create(
                habitacion = habitacion,
                foto = foto,
            )

            # Procesar la imagen almacenada
            img_url = '%s/%s' % (os.getcwd(), n_foto_habitacion.foto.url)
            Foto_Servicio.procesar_foto_servicio(img_url)

            return n_foto_habitacion

    class Meta:
        verbose_name_plural = 'Fotos de Habitaciones'

    def __str__(self):
        return 'Foto de %s' %(self.habitacion)

class Pack(models.Model):
    servicio = models.OneToOneField(Servicio, blank = False, null = False, on_delete = models.CASCADE)

    class Meta:
        verbose_name_plural = 'Packs'

    def __str__(self):
        return 'Foto de %s' %(self.servicio)

class Indisponibilidad(models.Model):
    fecha_desde = models.DateField('Fecha Inicio', blank = False, null = False, unique = False)
    fecha_hasta = models.DateField('Fecha Fin', blank = False, null = False, unique = False)

    # Los elementos con precios son los Servicios y las Habitaciones de los Alojamientos por Habitación
    servicio = models.ForeignKey(Servicio, blank = True, null = True, unique = False, on_delete = models.CASCADE)
    habitacion = models.ForeignKey(Habitacion, blank = True, null = True, unique = False, on_delete = models.CASCADE)

    @classmethod
    def nueva_indisponibilidad(cls, fecha_desde, fecha_hasta, servicio, habitacion):
        if servicio:
            for indisponibilidad in cls.objects.filter(servicio = servicio):
                if not indisponibilidad.fecha_hasta < fecha_desde or indisponibilidad.fecha_desde > fecha_hasta:
                    message = 'Hay una fecha en el período indicado entre %s y %s que coincide con una indisponibilidad ya registrada para este Servicio entre el %s y el %s' %(fecha_desde, fecha_hasta, indisponibilidad.fecha_desde, indisponibilidad.fecha_hasta)
                    print(message)
                    return {'message': message}

            # Debe validarse también que la fecha_desde sea anterior o igual a la fecha_hasta
            if fecha_desde > fecha_hasta:
                message = 'La fecha de inicio del período de indisponibilidad (%s) debe ser anterior o igual a la fecha de fin (%s)' %(fecha_desde, fecha_hasta)
                print(message)
                return {'message': message}

            # Si se llega a este punto es porque ninguna de las fechas de indisponibilidades registradas para los Servicios se solapan con las fechas inidicadas en los parámetros del método
            n_indisponibilidad = cls.objects.create(
                servicio = servicio,
                fecha_desde = fecha_desde,
                fecha_hasta = fecha_hasta,
            )
            print('Se ha registrado una indisponibilidad para %s del %s al %s' %(servicio, fecha_desde, fecha_hasta))
            return n_indisponibilidad
        elif habitacion:
            for indisponibilidad in cls.objects.filter(habitacion = habitacion):
                if not indisponibilidad.fecha_hasta < fecha_desde or indisponibilidad.fecha_desde > fecha_hasta:
                    print('Hay una fecha en el período indicado entre %s y %s que coincide con una indisponibilidad ya registrada para esta Habitación entre el %s y el %s' %(fecha_desde, fecha_hasta, indisponibilidad.fecha_desde, indisponibilidad.fecha_hasta))
                    return None
            # Si se llega a este punto es porque ninguna de las fechas de indisponibilidades registradas para las Habitaciones se solapan con las fechas inidicadas en los parámetros del método
            n_indisponibilidad = cls.objects.create(
                habitacion = habitacion,
                fecha_desde = fecha_desde,
                fecha_hasta = fecha_hasta,
            )
            print('Se ha registrado una indisponibilidad para %s del %s al %s' %(habitacion, fecha_desde, fecha_hasta))
            return n_indisponibilidad

    def modificar_indisponibilidad(self, fecha_desde, fecha_hasta):
        # 2 - Debe garantizarse que no se solapen días entre los períodos de indisponibilidad de una misma habitación o servicio
        if self.servicio:
            indisponibilidades = self.servicio.indisponibilidad_set.filter(~Q(id = self.id))
        elif self.habitacion:
            indisponibilidades = self.habitacion.indisponibilidad_set.filter(~Q(id = self.id))
        else:
            indisponibilidades = None

        if indisponibilidades:
            for indisponibilidad in indisponibilidades:
                if indisponibilidad.fecha_desde < fecha_desde and indisponibilidad.fecha_hasta > fecha_desde or indisponibilidad.fecha_hasta > fecha_hasta and indisponibilidad.fecha_desde < fecha_hasta:
                    message = 'Ya existe un período de indisponibilidad con fechas incluidas entre %s y %s' %(fecha_desde, fecha_hasta)
                    print(message)
                    return {'message': message}

        # Llegado a este punto no hay ningún problema en guardar la Indisponibilidad con las nuevas fechas
        # 3 - Si ningun día del período propuesto coincide con ningún día de alguna de las indisponibilidades ya creadas, entonces se puede modificar la indisponibilidad
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.save()
        return self

    # Elimina una indisponibilidad de Habitacion
    def eliminar_indisponibilidad(self):
        self.delete()

    class Meta:
        verbose_name_plural = 'Indisponibilidades de Alojamientos'

    def __str__(self):
        if self.servicio:
            elemento = self.servicio
        else:
            elemento = self.habitacion
        return 'Indisponibilidad de %s del %s al %s' %(elemento, self.fecha_desde, self.fecha_hasta)

class Favorito(models.Model):
    servicio = models.ForeignKey(Servicio, blank = False, null = False, unique = False, on_delete = models.CASCADE)
    usuario = models.ForeignKey('usuarios.Usuario', blank = True, null = True, unique = False, on_delete = models.CASCADE)
    fecha = models.DateField('Fecha de Registro', blank = False, null = False, unique = False, auto_now_add = True)

    @classmethod
    def get_favoritos(cls, usuarios = ()):
        favoritos = []
        if usuarios:
            for usuario in usuarios:
                favoritos_usuario = usuario.favorito_set.all()
                for favorito_usuario in favoritos_usuario:
                    favoritos.append(favorito_usuario.servicio.id)
        return favoritos

    @classmethod
    def nuevo_favorito(cls, servicio, usuario):
        # Se comprueba que el usuario ya no tenga este servicio como Favorito
        # if cls.objects.filter(servicio = servicio, user = user):
        #     print('El usuario %s ya tiene a %s como Favorito' %(user, servicio))
        #     return None
        # else:
        n_favorito = cls.objects.create(
            servicio = servicio,
            usuario = usuario,
        )
        print('Se ha registrado correctamente %s com Favorito de %s' %(servicio, usuario))
        return n_favorito

    def eliminar_favorito(self):
        self.delete()
        print('Se ha eliminad correctamente el %s' %(self))

    class Meta:
        verbose_name_plural = 'Favoritos'

    def __str__(self):
        return 'Favorito'

class Tipo_Cambio(models.Model):
    moneda_1 = models.ForeignKey(Moneda, blank = False, null = False, unique = False, related_name = 'moneda_1', on_delete = models.CASCADE)
    moneda_2 = models.ForeignKey(Moneda, blank = False, null = False, unique = False, related_name = 'moneda_2', on_delete = models.CASCADE)
    tipo_cambio = models.DecimalField('Tipo de Cambio', blank = False, null = False, unique = False, max_digits = int(20), decimal_places = int(10))

    @classmethod
    def get_tipo_cambio(cls, moneda_2):
        # Devuelve el tipo de cambio ya sea que se haya actualizado o el que había en la BD
        return cls.objects.get(moneda_2 = moneda_2, moneda_1__codigo_iso = 'USD').tipo_cambio

    @classmethod
    def update_tipos_cambio(cls):
        c = CurrencyRates()
        for moneda_1 in Moneda.objects.filter(menu = True):
            for moneda_2 in Moneda.objects.filter(menu = True).filter(~Q(id = moneda_1.id)):
                if moneda_1.codigo_iso != 'CUC' and moneda_2.codigo_iso != 'CUC':
                    try:
                        rate = c.get_rate(moneda_1.codigo_iso, moneda_2.codigo_iso)
                        if cls.objects.filter(moneda_1 = moneda_1, moneda_2 = moneda_2):
                            tc = cls.objects.get(moneda_1 = moneda_1, moneda_2 = moneda_2)
                            tc.modificar_tipo_cambio(
                                tipo_cambio = rate,
                            )
                        else:
                            tc = cls.nuevo_tipo_cambio(
                                moneda_1 = moneda_1,
                                moneda_2 = moneda_2,
                                tipo_cambio = rate,
                            )
                    except:
                        print('No existen datos de origen para el cambio %s / %s' % (moneda_1, moneda_2))


    @classmethod
    # Ejecutar esta tarea periódicamente e independuente del front para mantener actualizados lo tipos de cambio
    def update_tipo_cambio(cls):
        c = CurrencyRates()
        for moneda in Moneda.objects.filter(menu = True):
            print('Actualizando %s...' %(moneda))
            if moneda.codigo_iso not in ['USD', 'CUC']:
                if True:
                    rate = c.get_rate('USD', moneda.codigo_iso)
                    if cls.objects.filter(moneda_2 = moneda):
                        tc = cls.objects.get(moneda_2 = moneda)
                        tc.modificar_tipo_cambio(
                            tipo_cambio = rate,
                        )
                    else:
                        tc = cls.nuevo_tipo_cambio(
                            moneda_1 = Moneda.objects.get(codigo_iso = 'USD'),
                            moneda_2 = moneda,
                            tipo_cambio = rate,
                        )
                else:
                    print('No existen datos de origen para el cambio USD / %s' %(moneda))
                    pass
            else:
                print('La relación USD / %s = 1 siempre' %(moneda))

    @classmethod
    def nuevo_tipo_cambio(cls, moneda_1, moneda_2, tipo_cambio):
        if cls.objects.filter(moneda_1 = moneda_1, moneda_2 = moneda_2):
            print('Ya existe el Tipo de Cambio %s / %s' %(moneda_1, moneda_2))
            return None
        else:
            n_tipo_cambio = cls.objects.create(
                moneda_1 = moneda_1,
                moneda_2 = moneda_2,
                tipo_cambio = tipo_cambio,
            )
            print('Se ha creado correctamente el Tipo de Cambio %s / %s' %(moneda_1, moneda_2))
            return n_tipo_cambio

    def modificar_tipo_cambio(self, tipo_cambio):
        self.tipo_cambio = tipo_cambio
        self.save()
        print('Se ha modificado correctamente el Tipo de Cambio %s / %s' %(self.moneda_1, self.moneda_2))
        return self

    class Meta:
        verbose_name_plural = 'Tipos de Cambio'

    def __str__(self):
        return '%s / %s' %(self.moneda_1, self.moneda_2)

class Regla_Cancelacion(models.Model):
    mas_de_x_dias = models.IntegerField('Más de (X) días de antelación', blank = True, null = True, unique = False)
    menos_de_x_dias = models.IntegerField('Menos de (X) días de antelación', blank = True, null = True, unique = False)
    porciento_devolucion = models.DecimalField('Porciento de Devolución de la Pre-Reserva', max_digits = 5, decimal_places = 2, blank = True, null = True, unique = False)

    @classmethod
    def nueva_regla_cancelacion(cls, mas_de_x_dias, menos_de_x_dias, porciento_devolucion):
        n_regla_cancelacion = cls.objects.create(
            mas_de_x_dias = mas_de_x_dias,
            menos_de_x_dias = menos_de_x_dias,
            porciento_devolucion = porciento_devolucion,
        )

        print('Se ha creado correctamente la Regla de Cancelación para menos de %s días y más de %s' %(menos_de_x_dias, mas_de_x_dias))
        return n_regla_cancelacion


    class Meta:
        verbose_name_plural = 'Reglas de Cancelación'

    def __str__(self):
        if self.menos_de_x_dias and self.mas_de_x_dias:
            return 'Entre %s y %s días: Se devuelve el %s porciento' %(self.mas_de_x_dias + 1, self.menos_de_x_dias - 1, self.porciento_devolucion)
        elif self.menos_de_x_dias:
            return 'Menos de %s días: Se devuelve el %s porciento' %(self.menos_de_x_dias, self.porciento_devolucion)
        elif self.mas_de_x_dias:
            return 'Más de %s días: Se devuelve el %s porciento' %(self.mas_de_x_dias, self.porciento_devolucion)

class Cancelacion_Reserva(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete = models.CASCADE)
    fecha = models.DateTimeField('Fecha y Hora de Cancelación', blank = False, null = False, unique = False, auto_now_add = True)
    motivo = models.CharField('Motivo de Cancelación', max_length = 255, blank = False, null = False, unique = False)
    cantidad_reembolso_euros = models.DecimalField('Cantidad Reembolsada (€)', max_digits = 6, decimal_places = 2, blank = False, null = False, unique = False)

    @classmethod
    def nueva_cancelacion_reserva(cls, reserva, motivo, cantidad_reembolso_euros):
        # Se comprueba que la Reserva que se pretende cancelar no tiene ya ninguna cancelación relacionada anteriormente
        if cls.objects.filter(reserva = reserva):
            message = 'Ya existe una Cancelación para %s' %(reserva)
            print(message)
            return {
                'message': message,
            }
        else:
            n_cancelacion_reserva = cls.objects.create(
                reserva = reserva,
                motivo = motivo,
                cantidad_reembolso_euros = cantidad_reembolso_euros,
            )
            print('Se ha creado correctamente la %s' %(n_cancelacion_reserva))
            return n_cancelacion_reserva


    class Meta:
        verbose_name_plural = 'Cancelación de Reservas'

    def __str__(self):
        return 'Cancelación de %s' %self.reserva