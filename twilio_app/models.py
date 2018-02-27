from django.db import models
from django.db.models import Q
from twilio.rest import Client
from support.globals import *

class Twilio_Number(models.Model):
    numero = models.CharField('Número', max_length = 16, blank = False, null = False)
    sid = models.CharField('SID', max_length = 255, blank = False, null = False)
    en_uso = models.BooleanField('En uso', blank = True, default = False)

    def usar_twilio_number(self):
        # Se marca este número como "en uso" y todos los demás se desmarcan como tal

        for twilio_number in Twilio_Number.objects.filter(~Q(id = self.id)):
            twilio_number.en_uso = False
            twilio_number.save()
        self.en_uso = True
        self.save()

    def no_usar_twilio_number(self):
        # Se establece como False en atributo "en_uso" de un número de Twilio
        self.en_uso = False
        self.save()

    # Cambia el estado de "en_uso" de un número de Twilio
    def cambiar_uso_twilio_number(self):
        if self.en_uso:
            self.no_usar_twilio_number()
        else:
            self.usar_twilio_number()

    @classmethod
    def nuevo_twilio_number(cls, numero, sid):
        # Se comprueba que no haya ningún otro twilio_number con el mismo numero o sid
        if cls.objects.filter(numero = numero, sid = sid):
            message = 'Ya existe un Número de Twilio con los mismos datos (numero o sid)'
            print(message)
            return {
                'message': message,
            }
        else:
            n_twilio_number = cls.objects.create(
                numero = numero,
                sid = sid,
            )
            print('Se ha cereado correctamente el Número de Twilio %s' %(numero))
            return n_twilio_number

    # Modifica un Número de Twilio específico
    def modificar_twilio_number(self, numero, sid):
        # Se comprueba que no haya ningún otro twilio_number con el mismo numero o sid
        if self.objects.filter(numero = numero, sid = sid).filter(~Q(id = self.id)):
            message = 'Ya existe un Número de Twilio con los mismos datos (numero o sid)'
            print(message)
            return {
                'message': message,
            }
        else:
            self.numero = numero,
            self.sid = sid,
            self.save()
            print('Se ha modificado correctamente el Número de Twilio')
            return self

    # Eliminar Twilio Number
    def eliminar_twilio_number(self):
        self.delete()
        print('Se ha eliminado correctamente el Número de Twilio')


    class Meta:
        verbose_name_plural = 'Números de Twilio'

    def __str__(self):
        return self.numero

class Twilio_Client(models.Model):
    email = models.EmailField('E-mail', max_length = 64, blank = False, null = False, unique = True)
    account = models.CharField('Account', max_length = 64, blank = False, null = False, unique = True)
    token = models.CharField('Token', max_length = 64, blank = False, null = False, unique = True)
    en_uso = models.BooleanField('En uso', blank = False, default = False)

    # Envía un SMS al número indicado en el parámetro "to"
    def send_sms(self, to, message):
        client = Client(self.account, self.token)

        message = client.messages.create(
            to = to,
            from_ = Twilio_Number.objects.get(en_uso = True).numero,
            body = message,
        )

    @classmethod
    def nuevo_twilio_client(cls, email, account, token):
        # Se comprueba que no haya ningún otro cliente con el mismo token o la misma cuenta
        if cls.objects.filter(account = account, token = token):
            message = 'Ya existe un Cliente con los mismos datos (account o token)'
            print(message)
            return {
                'message': message,
            }
        else:
            n_twilio_client = cls.objects.create(
                email = email,
                account = account,
                token = token,
            )
            print('Se ha cereado correctamente un Cliente de Twilio para %s' %(cls.email))
            return n_twilio_client

    # Modifica un Cliente de Twilio específico
    def modificar_twilio_client(self, email, account, token):
        # Se comprueba que no haya ningún otro cliente con el mismo token o la misma cuenta
        if self.objects.filter(account = account, token = token).filter(~Q(id = self.id)):
            message = 'Ya existe un Cliente con los mismos datos (account o token)'
            print(message)
            return {
                'message': message,
            }
        else:
            self.email = email,
            self.account = account,
            self.token = token,
            self.save()
            print('Se ha modificado correctamente el Cliente de Twilio')
            return self

    # Eliminar Twilio Client
    def eliminar_twilio_client(self):
        self.delete()
        print('Se ha eliminado correctamente el Cliente de Twilio')


    class Meta:
        verbose_name_plural = 'Clientes Twilio'

    def __str__(self):
        return self.email

class Codigo_Verificacion(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', blank = False, null = False, unique = False, on_delete = models.CASCADE)
    movil = models.CharField('Móvil', max_length = 16, blank = False, null = False, unique = False)
    codigo = models.CharField('Código', max_length = 6, blank = False, null = False, unique = False)
    verificado = models.BooleanField('Verificado', blank = True, default = False)

    @classmethod
    # Verifica si el código indicado por el usuario
    def validate_codigo_usuario(cls, codigo, usuario):

        if cls.objects.filter(codigo = codigo, usuario = usuario, movil = usuario.movil, verificado = False):
            codigo_verificacion = cls.objects.get(codigo = codigo, usuario = usuario, movil = usuario.movil, verificado = False)
            codigo_verificacion.verificar_codigo()
            return True
        else:
            return False

    @classmethod
    def nuevo_codigo_verificacion(cls, usuario, codigo):
        # Debe comprobarse que no existe ningún código igual para el mismo usuario
        if cls.objects.filter(codigo = codigo, usuario = usuario):
            message = 'Ya existe el código %s para el usuario %s' %(codigo, usuario)
            return {
                'message': message,
            }
        else:
            # Al relacionar el móvil independientemente del usuario, garantizamos que no se pueda solicitar un código para un móvil
            # y cambiar este antes de validarlo, ya que en el proceso de verificación del código comprobaremos si el móvil que tiene
            # en ese momento es el mismo que tenía cuando se creó la solicitud de verificación
            n_codigo_verificacion = cls.objects.create(
                codigo = codigo,
                usuario = usuario,
                movil = usuario.movil,
            )
            print('Se ha creado correctamente el código %s para el usuario %s' %(codigo, usuario))
            return n_codigo_verificacion

    def verificar_codigo(self):
        self.verificado = True
        self.usuario.verificar_movil()
        self.save()
        print('Se ha verificado correctamente el código %s para el usuario %s' %(self.codigo, self.usuario))

    @classmethod
    # Genera un nuevo código de verificació de móvil de 6 dígitos
    def generar_codigo_verificacion_twilio(cls):
        return generate_random_twilio_code()

    class Meta:
        verbose_name_plural = 'Códigos de Verificación Twilio'

    def __str__(self):
        return 'Código para %s (%s)' %(self.usuario, self.codigo)

class Solicitud_Verificacion(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', blank = False, null = False, unique = False, on_delete = models.CASCADE)
    movil = models.CharField('Móvil', max_length = 16, blank = False, null = False, unique = False)
    fecha_hora_soilcitud = models.DateTimeField('Fecha y Hora de la Solicitud', blank = False, null = False, auto_now_add = True)

    @classmethod
    # Crea un nuevo registro de Solicitud de Verificación en Twilio
    def nueva_solicitud_verificacion(cls, usuario, movil):
        # Existe un número máximo de solicitudes de verificación para cada usuario, así se evita que un mismo usuario pueda hacer uso indiscriminado de un proceso que implica coste
        if len(cls.objects.filter(usuario = usuario)) >= 3:
            message = 'El usuario %s ha alcanzado el número máximo permitido de solicitudes de verificación de móvil'
            print(message)
            return {
                'message': message,
            }
        else:
            n_solicitud_verificacion = cls.objects.create(
                usuario = usuario,
                movil = movil,
            )
            print('Se ha creado correctamente la Solicitud de Verificación de %s para el móvil %s' %(usuario, movil))
            return n_solicitud_verificacion

    class Meta:
        verbose_name_plural = 'Solicitudes de verificación Twilio'

    def __str__(self):
        return 'Solicitud de %s para %s el %s' %(self.usuario, self.movil, self.fecha_hora_soilcitud)

