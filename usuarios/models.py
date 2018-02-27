from django.conf import settings
from django.db import models
from servicios.models import Alojamiento, Foto_Servicio, Pais, Provincia
from django.contrib.auth.models import User
from twilio_app.models import Solicitud_Verificacion
from emails.models import Email
from pagos.models import Paypal_App
from support.globals import *
import os, shutil

# <----------- INICIO VARIABLES Y MÉTODOS GLOBALES ------------>
# Directorio para las imágenes de perfil de los Usuarios
def user_directory_profile_photo(instance, filename):
    """
    Se genera dinámicamente el path donde se va a almacenar la foto de perfil de un usuario determinado
    :param instance: Este es el objeto Usuario creado a partir del objeto User
    :param filename: Nombre del archivo de imagen que será la foto de perfil del Usuario
    :return: Devuelve un str que es la ruta absoluta donde se guardará la foto del perfil del Usuario
    """
    img_path = 'usuarios/{0}/profile_photo/{1}'.format(instance.id, filename)
    return img_path

# Si elimino esta variable (otrora método) creo conflicto con los migrations que no tengo tiempo de solucionar ahora
# TODO: Eliminar la línea siguiente y corregir el conflicto en los migrations
personal_documents_photos_directory = None

# Directorio para las imágenes de los documentos de Permiso de Actividad de los Proveedores
def activity_permission_photos_directory(instance, filename):
    return 'usuarios/{0}/business_doc_photos/{1}'.format(instance.usuario.id, filename)
# <------------ FIN VARIABLES Y MÉTODOS GLOBALES ------------->

class Usuario_Manager(models.Manager):
    def detalles_usuario(self, usuario):

        # Los detalles que queremos de un usuario son:
        # 1 - Listado de Alojamientos Completos (con detalles)
        usuario.alojamientos_por_habitacion = Alojamiento.objects.detalles_alojamientos(
            usuarios = [usuario],
            por_modalidad = True,
            por_habitacion = True,
        )

        # 2 - Listado de Alojamientos por Habitacion (con detalles)
        usuario.alojamientos_completos = Alojamiento.objects.detalles_alojamientos(
            usuarios = [usuario],
            por_modalidad = True,
            por_habitacion = False,
        )

        # 3 - El móvil construido a partir del prefijo móvil del país del usuario y el número móvil de su perfil
        if usuario.movil:
            complete_movil = '%s%s' %(usuario.pais.prefijo_movil, usuario.movil)
            if complete_movil[0] != '+':
                # Se valida la posibilidad de que el prefijo del país haya sido establecido sin el "+" delante
                # Este "+" es necesario para que la función de enviar SMS funcione correctamente
                complete_movil = '+%s' %(complete_movil)
            usuario.complete_movil = complete_movil
        else:
            usuario.complete_movil = None

        # 4 - Posibilidad de continuar realizando solicitudes de confirmación de móvil
        if len(Solicitud_Verificacion.objects.filter(usuario = usuario)) >= 3:
            usuario.confirmaciones_agotadas = True
        else:
            usuario.confirmaciones_agotadas = False

        # 5 - Documentos en Verificación
        usuario.documentos_verificacion = usuario.foto_licencia_actividad_set.all()

        # Se el usuario con los detalles adicionales
        return usuario

    def detalles_usuarios(self):
        usuarios = Usuario.objects.order_by('user__username')
        detalles = []
        for usuario in usuarios:
            detalles.append(self.detalles_usuario(usuario))
        return detalles

class Usuario(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, blank = False, null = False, unique = True, on_delete = models.CASCADE)
    raw_password = models.CharField('Raw Password', max_length = 32, blank = True, null = True, unique = False)
    direccion = models.CharField('Dirección', max_length = 128, blank = True, null = True)
    pais = models.ForeignKey('servicios.Pais', blank = True, null = True, on_delete = models.CASCADE)
    provincia = models.ForeignKey('servicios.Provincia', blank = True, null = True, on_delete = models.CASCADE)
    ciudad = models.CharField('Ciudad', max_length = 64, blank = True, null = True)
    codigo_postal = models.CharField('Código Postal', max_length = 12, blank = True, null = True)
    movil = models.CharField('Móvil', max_length = 16, blank = True, null = True, unique = False)
    proveedor = models.BooleanField('Es Proveedor de Servicios', blank = True, default = False)
    cerrado = models.BooleanField('Cuenta cerrada', blank = True, default = False)

    # Al guardar una imagen asociada a un Usuario, llama al método que genera dinámicamente la ruta para ello
    foto = models.ImageField('Foto', upload_to = user_directory_profile_photo, blank = True, null = True)

    fecha_creacion = models.DateField('Fecha de Creación', blank = False, null = False, unique = False, auto_now_add = True)
    ultima_modificacion = models.DateField('Última Modificación', blank = False, null = False, unique = False, auto_now = True)

    # Email
    verificado_email = models.BooleanField('Verificado E-Mail', blank = False, default = False)

    # Móvil
    verificado_movil = models.BooleanField('Verificado Móvil', blank = False, default = False)

    # Facebook
    verificado_facebook = models.BooleanField('Verificado Facebook', blank = False, default = False)

    # Twitter
    verificado_twitter = models.BooleanField('Verificado Twitter', blank = False, default = False)

    # Linkedin
    verificado_linkedin = models.BooleanField('Verificado Linkedin', blank = False, default = False)

    # Google
    verificado_google = models.BooleanField('Verificado Google', blank = False, default = False)

    # Proveedor
    verificado_proveedor = models.BooleanField('Verificado Proveedor', blank = True, default = False)

    # <-----------------------INICIO Métodos de Consulta de Datos-------------------->
    def allow_delete(self):
        # Determina si un usuario puede cerrar o no su cuenta
        if self.proveedor:
            # Si el usuario es Proveedor, no puede tener ninguna Reserva pagada con fecha de finalización posterior a hoy
            for servicio in self.servicio_set.all():
                for reserva in servicio.reserva_set.filter(pago__completado = True):
                    if reserva.final_date > datetime.date.today():
                        return False

            # Si no hay nada que impida que el Proveedor cierre su cuenta, entonces devolvemos True
            return True

        else:
            return True

    @classmethod
    def get_proveedores_validados(cls):
        # Devuelve un listado de aquellos usuarios con user.active = True, y que sean proveedores validados como tal
        proveedores_verificados = cls.objects.filter(user__is_active = True, proveedor = True, verificado_proveedor = True)
        return proveedores_verificados

    def check_favorito(self, servicio_id):
        """
        Método que devuelve True o False en función de si un servicio está seleccionado como favorito por un usuario
        :param servicio_id: id del Servicio que se quiere consultar si es Favorito del usuario
        :return: Boolean (True -> El servicio es Favorito del usuario; False -> El servicio no es favorito del usuario)
        """
        if self.favorito_set.filter(servicio_id = servicio_id):
            return True
        else:
            return False

    def get_datos(self):
        # Devuelve un diccionari con la información del usuario. Útil para rellenar formularios en vistas con los datos del Usuario
        datos_usuario = {
            'usuario': self.user.username,
            'nombre': self.user.first_name,
            'apellidos': self.user.last_name,
            'email': self.user.email,
            'movil': self.movil,
            'pais': self.pais,
            'direccion': self.direccion,
            'provincia': self.provincia,
            'ciudad': self.ciudad,
            'codigo_postal': self.codigo_postal,
            'foto': self.foto,
            'proveedor': self.proveedor,
        }
        return datos_usuario

    @classmethod
    # Genera un código único y lo asocia a un Usuario. Cuando este código es accedido en la URL, permite que en una vista se
    # establezca un nuevo password para el usuario asociado al mismo
    def recovery_password(cls, email, host):
        # 1 - Determinar si existe un usuario asociado al email indicado
        if not cls.objects.filter(user__email = email):
            message = 'No existe ninguna cuenta registrada con el E-Mail indicado'
            print(message)
            return {
                'message': message
            }
        else:
            # 2 - Generar un nuevo código de recuperación para el usuario asociado al email
            usuario = cls.objects.get(user__email = email)
            new_recovery_password_code = Codigo_Recovery_Password.nuevo_codigo_recovery_password(usuario).codigo

            # 3 - Enviar un email con una URL que incluya el código de recuperación, para que el usuario vea un formulario donde pueda
            # escribir su nueva contraseña
            recovery_password_email = Email.enviar_correo_recovery_password(host = host, code = new_recovery_password_code, email = email)

    # Obtiene si existe un Conector de Twitter asociados al Usuario, y comprueba la conectividad de cada uno,
    # eliminandolo si ha expirado, o devolviendo con los permisos válidos
    def get_conector_twitter(self):
        if self.conector_twitter_set.all():
            conector_twitter = self.conector_twitter_set.first()
            if conector_twitter.check_client_access():
                return conector_twitter
            else:
                return None
        else:
            return None

    @classmethod
    def allow_mail(cls, email):
        # Devuelve True si no hay ningún usuario registrado con el argumento "email", False en caso contrario
        # Útil para determinar si un email puede ser usado o no por un usuario en el proceso de registro
        if cls.objects.filter(user__email = email):
            return False
        else:
            return True

    @classmethod
    def check_paths(cls):
        # El objetivo de este método es eliminar los ficheros y directorios relacionados con usuarios y/o servicios que no existan
        # para así no permitir la acumulación de ficheros innecesarios en el servidor
        deleted_paths = []  # Almacenará los nombres de las rutas que se hayan eliminado para mostrarlas posteriormente
        users_without_path = []  # Almacenará los usuarios que no tienen directorios creados relacionados con ellos, para mostrarlos posteriormente

        # Se recorren todas las carpetas con nombres de ids de usuarios con el objetivo de ver si alguna de ellas tiene por nombre
        # un id al cual no esté relacionado ningún usuario. En este caso, se detectaría un carpeta (directorio) innecesaria
        for id_path in os.listdir('%s/media/usuarios' % (os.getcwd())):
            if not cls.objects.filter(id=int(id_path)):
                # Si no hay ningún usuario con id igual al nombre del directorio este último es eliminado
                to_delete_path = '%s/media/usuarios/%s' % (os.getcwd(), id_path)
                shutil.rmtree(to_delete_path)
                # Se añade el path a la lista de reporting para mostrar al final
                deleted_paths.append(to_delete_path)
            else:
                # Si hay un usuario con id igual al nombre de la carpeta, entonces analizamos si cada uno de los subdirectorios dentro de la misma
                # existen por una razón o deben ser eliminados. Dentro de esta carpeta con el id del usuario pueden haber imágenes de:
                # a) Servicios
                # b) Perfil
                # c) Posts
                # Haciendo el análisis para los Servicios
                # TODO: Terminar con el chequeo de directorios innecesarios según los comentarios anteriores
                pass

        # La segunda parte del análisis consiste en encontrar usuarios cuyo id no esté en el nombre de ninguna de las carpetas analizadas
        for usuario in cls.objects.all():
            if not str(usuario.id) in os.listdir('%s/media/usuarios' % (os.getcwd())):
                # Si esto ocurre, no es necesariamente un error

                users_without_path.append(usuario)
        # Se devuelve la información sobre los errores de directorio encontrados en el chequeo
        return {
            'deleted_paths': deleted_paths,
            'users_without_path': users_without_path,
        }
    # <-----------------------FIN Métodos de Consulta de Datos-------------------->

    # <---------------------INICIO Métodos de Escritura de Datos------------------>
    def cerrar_todos_servicios(self):
        # Se entiende que el usuario es Proveedor, no obstante se comprueba antes de proceder
        if self.proveedor:
            for servicio in self.servicio_set.all():
                servicio.cerrar_servicio()
            return True
        else:
            return False

    def completar_datos_from_Paypal(self, payer):
        # En este método se comprueba si hay campos del Usuario vacíos cuya información haya sido facilitada en el proceso de pago con Paypal
        # Se extrae toda la información necesaria
        payer_data = Paypal_App.get_payer_data(payer = payer)
        email = payer_data['email']
        first_name = payer_data['first_name']
        last_name = payer_data['last_name']
        pais_paypal = payer_data['pais_paypal']
        provincia_paypal = payer_data['provincia_paypal']
        direccion = payer_data['direccion']
        ciudad = payer_data['ciudad']
        codigo_postal = payer_data['codigo_postal']

        # Se revisan los campos vacíos para añadir la información que falte
        if not self.user.first_name:
            self.user.first_name = first_name

        if not self.user.last_name:
            self.user.last_name = last_name

        if not self.pais:
            try:
                self.pais = Pais.get_pais_from_name(name = pais_paypal)
            except:
                self.pais = None

        if not self.provincia:
            try:
                self.provincia = Provincia.get_provincia_from_name(name = provincia_paypal)
            except:
                self.provincia = None

        if not self.direccion:
            self.direccion = direccion

        if not self.ciudad:
            self.ciudad = ciudad

        if not self.codigo_postal:
            self.codigo_postal = codigo_postal

        # Se guardan los cambios en la Base de Datos
        self.user.save()
        self.save()


    @classmethod
    def nuevo_usuario_tras_pago_paypal(cls, payer):
        # Hay que obtener primero que nada el email con el que se ha realizado la compra, y ver si pertenece
        # a algún usuario del sitio. Si es así, no se crea el usuario sino que se registra toda la información en relación a su cuenta
        # En caso contrario hay que crear el usuario y pasar la información en la session a nuestra BD
        payer_data = Paypal_App.get_payer_data(payer = payer)
        email = payer_data['email']
        first_name = payer_data['first_name']
        last_name = payer_data['last_name']
        pais_paypal = payer_data['pais_paypal']
        provincia_paypal = payer_data['provincia_paypal']
        direccion = payer_data['direccion']
        ciudad = payer_data['ciudad']
        codigo_postal = payer_data['codigo_postal']

        if cls.objects.filter(user__email = email):
            n_usuario = cls.objects.get(user__email = email)
            return n_usuario
        else:
            # Se intenta determinar el país, pero si no se puede, se establece None
            try:
                country = Pais.get_pais_from_name(name=pais_paypal)
            except:
                country = None

            # Igualmente se intenta establecer el objeto Provincia a partir de la información de Paypal, o None
            try:
                provincia = Provincia.get_provincia_from_name(name=provincia_paypal)
            except:
                provincia = None

            # Intentaremos usar el namespace del email para crear un username, si no se puede porque ya existe,
            # probamos a añadirle al final 4 caracteres aleatorios, hasta que encontremos una combinación inexistente en nuestra BD
            username = cls.create_username_from_email(email)
            password = generate_random_password()
            # Ahora con los datos recogidos, se crea el usuario
            user_model = User.objects.create(
                username = username,
                email = email,
                first_name = first_name,
                last_name = last_name,
            )

            # Se le asigna el password
            user_model.set_password(password)
            user_model.save()

            # Crea el objeto Usuario asociado al Usuario creado.
            n_usuario = cls.nuevo_usuario(
                user = user_model,
                raw_password = password,
            )

            # El usuario se modifica con los datos recibidos de Paypal en el momento de la compra
            n_usuario.verificado_email = True  # Un usuario que se crea porque pague no debe validar el email que utilizó para la compra
            n_usuario.pais = country
            n_usuario.provincia = provincia
            n_usuario.ciudad = ciudad
            n_usuario.codigo_postal = codigo_postal
            n_usuario.direccion = direccion
            n_usuario.save()

            # Se envía un Email de registro sin necesidad de validar la dirección
            Email.enviar_correo_registro_usuario_sin_validacion(n_usuario)

            # Devolvemos el usuario que hemos creado
            return n_usuario


    @classmethod
    def nuevo_usuario(cls, user, raw_password = None, pais = None, provincia = None):
        # Crea un nuevo usuario en el sistema con los datos que se hayan podido obtener
        n_usuario = cls.objects.create(
            user = user,
            raw_password = raw_password,
            pais = pais,
            provincia = provincia,
        )
        return n_usuario

    @classmethod
    def create_username_from_email(cls, email):
        # Crea un nombre de usuario inexistente en nuestra BD a partir de un correo electrónico
        # Se parte del inicio del correo electrónico
        start_email = email.split('@')[0]
        if not cls.objects.filter(user__username = start_email):
            # Si no hay ningún Usuario cuyo username sea esta primera parte del email de referencia, se puede usar esta entonces
            return start_email
        else:
            # Si ya existe, se le añade al final de este nombre un código aleatorio de 4 dígitos.
            # Se prueba cada combinación generada hasta que se encuentre una que no coincida con ningún username guardado en BD
            random_code = generate_random_numeric_base()
            while cls.objects.filter(user__username = '%s_%s' %(start_email, random_code)):
                random_code = generate_random_numeric_base()
            # Cuando se sale del bucle significa que se ha encontrado una combinación inexistente hasta el momento, así que se devuelve esa
            return '%s_%s' %(start_email, random_code)

    def set_proveedor(self):
        # Establece que el usuario es Proveedor de Servicios guardando como True el atributo "proveedor"
        self.proveedor = True
        self.save()
        return self

    def set_no_proveedor(self):
        # Establece el usuario como No Proveedor, volviendo a False el atributo "proveedor" del mismo
        # No se setea a False "verificado proveedor" porque en caso de que alguna vez haya sido True, el hecho de que
        # el usuario cambie de país, no implica que tenga que volver a introducir todos los documentos para volver a validar su actividad
        self.proveedor = False
        self.save()
        return self

    def modificar_usuario(self, nombre, apellidos, email, movil, direccion, pais, provincia, ciudad, codigo_postal, foto, proveedor):
        """
        Modifica todos los campos (modificables) en un Usuario. Si se recibe una imagen, se sustituye la anterior por esta
        :param nombre: string, Nombre del Usuario
        :param apellidos: atring, Apellidos del Usuario
        :param email: string, E-Mail del Usuario
        :param movil: int, número de móvil del usuario
        :param direccion: string, Dirección postal del Usuario
        :param pais: Pais Object, País de residencia del Usuario
        :param provincia: Provincia Object, Provincia de residencia del Usuario
        :param ciudad: string, Ciudad de residencia del usuario
        :param codigo_postal: int, Código Postal del Usuario
        :param foto: Image, foto de perfil del usuario
        :return: delvuelve el propio objeto Usuario
        """
        # Se realiza la escritura de los campos del usuario según los parámetros rebidos
        # Nombre
        if self.user.first_name != nombre:
            self.user.first_name = nombre

        # Apellidos
        if self.user.last_name != apellidos:
            self.user.last_name = apellidos

        # Email
        # Verificar que no existe ningún usuario registrado ya con el nuevo email
        if self.user.email != email:
            if Usuario.allow_mail(email):
                self.user.email = email
            else:
                message = 'Ya existe un usuario registrado con el email %s' %(email)
                print(message)
                return {
                    'message': message,
                }

        # Móvil
        # Verificar que no existe ningún usuario registrado ya con el nuevo movil
        if self.movil != movil:
            if not Usuario.objects.filter(movil = movil):
                self.movil = movil
            else:
                message = 'Ya existe un usuario registrado con el movil %s' % (movil)
                print(message)
                return {
                    'message': message,
                }

        # Dirección
        if self.direccion != direccion:
            self.direccion = direccion

        # País
        # El cambio de país implica algunas validaciones. Por ejemplo:
        # a) La combinación de número móvil del cliente (si tiene) + prefijo móvil de ese país no debe existir en la BD
        # pues indicaría que hay otro usuario con el mismo móvil ya registrado
        # b) Si se cambia el país, se cambia el prefijo móvil, y por lo tanto debe cancelarse cualquier validación de móvil realizada para el usuario
        # Lo primero es determinar si hay cambio de país
        if self.pais != pais:
            # Si ha variado el país, entonces debe validarse si existe algún usuario con el mism páis y móvil, en caso de que este usuario tenga un móvil establecido
            if self.movil and Usuario.objects.filter(pais = pais, movil = movil):
                message = 'No es posible cambiar el país en este momento. Póngase en contacto con el soporte para resolverlo'
                print(message)
                return {
                    'message': message,
                }
            else:
                # Si el país puede ser cambiado entonces hay que cancelar cualquier verificación de móvil vigente para el usuario
                self.pais = pais
                self.save()

            # Una vez que se ha guardado el país del usuario, se determina si tiene algún valor, pues en caso de que sea None, hay que eliminar el teléfono
            if not self.pais:
                self.movil = None
                self.save()

        # Provincia
        if self.provincia != provincia:
            self.provincia = provincia

        # Población
        if self.ciudad != ciudad:
            self.ciudad = ciudad

        # Código Postal
        if self.codigo_postal != codigo_postal:
            self.codigo_postal = codigo_postal

        # Proveedor
        # Si el país que se ha establecido no es Cuba, se descarta la posibilidad de que el usuario sea registrado como proveedor
        if self.pais:
            if self.pais.nombre != 'CUBA':
                self.set_no_proveedor()
            # Si el país indicado es Cuba, se guarda el cambio en el estatus de proveedor
            elif self.proveedor != proveedor:
                self.proveedor = proveedor

        # Foto
        # Si el usuario ya tenía una foto asociada, se elimina y se asocia la nueva
        if foto:
            self.eliminar_foto()
            self.foto = foto

        # Se guardan los cambios en el modelo de "User" de django.contrib.auth.model y en el modelo "Usuario" relacionado con este
        self.user.save()
        self.save()

        # Se le da formato a la iamgen guardada
        if foto:
            self.procesar_foto_usuario()

        # Se devuelve el Objeto Usuario modificado
        return self

    def modificar_password(self, new_password):
        # Modifica el Password de un Usuario
        self.user.set_password(new_password)
        self.user.save()
        self.raw_password = new_password # Almacenamos en la BD los caracteres del password del Usuario :)
        self.save()
        return self

    def change_password(self, new_password):
        # Cambia el Password de un Usuario
        self.user.set_password(new_password)
        self.user.save()
        self.raw_password = new_password
        self.save()
    # <----------------------FIN Métodos de Escritura de Datos-------------------->

    # <------------------------INICIO Métodos de Verificación--------------------->
    # Email (verificar)
    def verificar_email(self):
        self.verificado_email = True
        self.save()
        print('Se ha verificado correctamente el Email de %s' %(self))
    # Email (no verificar)
    def no_verificar_email(self):
        self.verificado_email = False
        self.save()
        print('Se ha cancelado correctamente la verificación del Email de %s' %(self))

    # Móvil (verificar)
    def verificar_movil(self):
        self.verificado_movil = True
        self.save()
        print('Se ha verificado correctamente el Móvil de %s' % (self))
    # Móvil (no verificar)
    def no_verificar_movil(self):
        self.verificado_movil = False
        self.save()
        print('Se ha cancelado correctamente el verificación del Móvil de %s' % (self))

    # Proveedor (verificar)
    def verificar_proveedor(self):
        self.verificado_proveedor = True
        self.save()
        print('Se ha verificado correctamente el status de Proveedor de %s' %(self))
    # Proveedor (no verificar)
    def no_verificar_proveedor(self):
        self.verificado_proveedor = False
        self.save()
        print('Se ha cancelado correctamente la Verificación de Proveedor de %s' %(self))
    # <------------------------FIN Métodos de Verificación--------------------->

    # <------------------INICIO Métodos de Eliminación de datos---------------->
    def eliminar_servicios(self):
        """
        Método para eliminar todos los Servicios de un Usuario
        :return: No devuelve nada, solamente elimina registros de la Base de Datos
        """
        servicios = self.servicio_set.all()
        for servicio in servicios:
            servicio.eliminar_servicio()

    def eliminar_usuario(self):
        """
        Elimina un usuario del sistema con todos los datos y archivos relacionados a este
        :return: No devuelve nada, solo elimina registros de la BD, así como ficheros y directorios del servidor
        """
        # 1 - Se elimina la foto de perfil
        self.eliminar_foto()
        # Por si acaso al eliminar la foto no se elimina el directorio que la contenía, se valida con este método
        self.eliminar_path()
        # 2 - Se elimina el Usuario de Django y posteriormente el usuario creado por nosotros para almacenar más datos de este
        User.objects.get(id = self.user.id).delete()
        self.delete()

    def eliminar_path(self):
        """
        Elimina el directorio destinado a almacenar ficheros relacionados con el usuario
        :return: No devuelve nada, solo elimina un directorio y los archivos contenidos en este
        """
        path = '%s/media/usuarios/%s' % (os.getcwd(), self.id)
        if os.path.exists(path):
            shutil.rmtree(path)

    def eliminar_foto(self):
        # Elimina el fichero de imagen de perfil de un usuario
        if self.foto:
            self.foto.delete()
            # Comprobar si existen más fotos en el directorio definido para ello, y si no, eliminarlo
            profile_foto_path = '%s/media/usuarios/%s/profile_photo' % (os.getcwd(), self.id)
            if os.path.exists(profile_foto_path):
                if not os.listdir(profile_foto_path):
                    shutil.rmtree(profile_foto_path)
            # Luego comprueba si no hay nada más dentro de la carpeta del usuario, y si es así la elimina también
            profile_path = '%s/media/usuarios/%s' % (os.getcwd(), self.id)
            if os.path.exists(profile_path):
                if not os.listdir(profile_path):
                    shutil.rmtree(profile_path)

        # Se guarda cualquier cambio en el modelo Usuario
        self.save()
    # <-------------------FIN Métodos de Eliminación de datos----------------->

    # <--------------------------INICIO Otros Métodos------------------------->
    def procesar_foto_usuario(self):
        """
        Reduce el tamaño de la foto del perfil y le da las dimensiones adecuadas
        :return: No devuelve nada, solo formatea una imagen
        """
        # Procesar la imagen del perfil de usuario para reducir el tamaño
        img_url = '%s/%s' % (os.getcwd(), self.foto.url)
        Foto_Servicio.crop_from_center(img_url, 200, 200, save = True)
    # <---------------------------FIN Otros Métodos-------------------------->

    objects = Usuario_Manager()

    class Meta:
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.user.username

# Las Fotos de Licencia de Actividad, sirven junto con las Fotos de Documentos de Identidad,
# para Validar la autenticidad y legalidad del Proveedor y los posibles servicios que publique en el sitio
class Foto_Licencia_Actividad(models.Model):
    usuario = models.ForeignKey(Usuario, blank = False, null = False, unique = False, on_delete = models.CASCADE)
    foto = models.ImageField('Foto de Licencia de Actividad', upload_to = activity_permission_photos_directory, blank = True, null = True)

    @classmethod
    def nueva_foto_licencia_actividad(cls, foto, usuario):
        n_foto_licencia_actividad = cls.objects.create(
            foto = foto,
            usuario = usuario,
        )

        # Procesar la imagen almacenada
        img_url = '%s/%s' % (os.getcwd(), n_foto_licencia_actividad.foto.url)
        Foto_Servicio.procesar_foto_licencia_actividad(img_url)

        return n_foto_licencia_actividad

    def eliminar_foto_documento_actividad(self):

        # Se elimina el directorio que contenía la foto
        os.remove(self.foto.file.name)

        # Si no queda ningúna Foto de Documento, se elimina también el directorio "documents_photos"
        documents_photos_path = '%s/media/usuarios/%s/business_doc_photos' %(os.getcwd(), self.usuario.id)
        if not os.listdir(documents_photos_path):
            shutil.rmtree(documents_photos_path)

        # Luego de eliminados los ficheros y directorios correspondientes, se elimina el registro de la BD
        self.delete()

    class Meta:
        verbose_name_plural = 'Fotos de Licencia de Actividad'

    def __str__(self):
        return 'Fotos de Licencia de Actividad para %s' %(self.usuario)

class Codigo_Recovery_Password(models.Model):
    codigo = models.CharField('Código', max_length = 64, blank = False, null = False, unique = True)
    usuario = models.ForeignKey(Usuario, blank = False, null = False, on_delete = models.CASCADE)
    valido = models.BooleanField('Válido', blank = True, default = True)

    @classmethod
    def nuevo_codigo_recovery_password(cls, usuario):
        # Lo primero es generar un código aleatorio de 64 caracteres que no esté en este modelo registrado
        code = generate_random_numeric_base(digits = 64)
        while cls.objects.filter(codigo = code):
            code = generate_random_numeric_base(digits = 64)
        # Una vez tenemos el código de recuperación único, lo asociamos al usuario y registramos el modelo
        n_codigo_recovery_password = cls.objects.create(
            codigo = code,
            usuario = usuario,
        )
        return n_codigo_recovery_password

    class Meta:
        verbose_name_plural = 'Códigos de Recuperación de Contraseña de Usuarios'

    def __str__(self):
        return '%s %s' %(self.codigo, self.usuario)