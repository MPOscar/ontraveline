from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from support import globals
from servicios.models import Alojamiento, Servicio, Reserva
import pdfkit
from os.path import basename

class Link_Activacion(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', blank = False, null = False, on_delete = models.CASCADE)
    link = models.URLField('Link Activación', max_length = 255, blank = False, null = False, unique = True)
    fecha_creacion = models.DateField('Fecha de creación', blank = False, null = False, unique = False, default = timezone.now)
    valido = models.BooleanField('Valido', blank = True, default = True)
    activado = models.BooleanField('Activado', blank = True, default = False)

    @classmethod
    # Crea un nuevo link de Activación para enviar a un usuario por mail una vez se ha registrado en el sistema
    def nuevo_link_activacion(cls, usuario, codigo_activacion, host):
        # Se garantiza que no haya dos links de activación con el mismo code, pues estos debes ser unívocos para cada usuario
        # Con 62 caracteres alfanuméricos y una longitud de 30 hay 2.21 x 10^53 combinaciones, así que nunca se agotarán
        while cls.objects.filter(link__contains = codigo_activacion):
            codigo_activacion = globals.generate_random_activation_code()

        # En este punto tenemos un código de activación que no se encontrará en ningún link de Activación de nuestra BD
        # Si ya existe un link para el usuario, entonces, este se pone como inválido y se genera uno nuevo
        for link in cls.objects.filter(usuario = usuario):
            link.valido = False
            link.save()

        url_base = 'http://%s/emails/confirmar_email_usuario' %(host)

        # En este punto tenemos:
        # a) un código de activación único
        # b) una URL de base a la que añadirle al final el código de Activación
        # c) la certeza de que si había algún otro link de Activación para el usuario, este se ha desactivado y no será usable

        # Se crea el nuevo Link de Activación
        n_link_activacion = cls.objects.create(
            usuario = usuario,
            # El link en la unión de la URL base con el código de Activación
            link = '/'.join([url_base, codigo_activacion]),
        )

        # Siempre se creará un link de Activación
        print('Se ha creado correctamente el link de activación para %s' %(usuario))
        return n_link_activacion

    # Marca un link de activación como Activado
    def activar(self):
        # Cuando se Activa un link por un usuario ya no puede volver a ser usado jamás
        self.activado = True
        self.valido = False
        self.save()
        print('Se ha activado correctamente el link para %s' %(self.usuario))

    # Elimina un link de activación
    def eliminar_link_activacion(self):
        self.delete()
        print('Se ha eliminado correctamente el link de activación')

    # Genera un nuevo link de activación
    @classmethod
    def generar_link_activacion(cls, usuario, host):
        # El código de Activación de obtiene de una función que lo genera con caracteres alfanuméricos aleatoriamente mezclados
        codigo_activacion = globals.generate_random_activation_code()

        # Se crea el link de Activación a partir del código de Activación y el usuario para el que se ha generado
        n_link_activacion = Link_Activacion.nuevo_link_activacion(
            usuario = usuario,
            codigo_activacion = codigo_activacion,
            host = host,
        )

        # Se devuelve el link de Activación que se ha creado
        return n_link_activacion

    class Meta:
        verbose_name_plural = 'Links de Activación'

    def __str__(self):
        return 'Link de Activación para %s' %(self.usuario)

class Email(models.Model):
    asunto = models.CharField('Asunto', max_length = 255, blank = False, null = False, unique = False)
    cuerpo = models.TextField('Cuerpo', blank = True, null = True, unique = False)
    remitente = models.CharField('Remitente', max_length = 64, blank = False, null = False, unique = False)
    destinatarios = models.CharField('Destinatarios', max_length = 4096, blank = False, null = False)
    fecha_envio = models.DateTimeField('Fecha y Hora de envio', blank = False, null = False, unique = False, auto_now_add = True)

    @classmethod
    def enviar_correo_recovery_password(cls, host, code, email):
        # 1 - Construir la URL que debe seguir el usuario
        url = 'http://%s/usuarios/recovery_password/%s' %(host, code)

        # 2 - Se definen las partes y el contenido del email
        asunto = 'Recuperar contraseña Ontraveline'
        remitente = 'contact@ontraveline.com'

        context = {
            'url': url,
        }
        destinatarios = [email, ]
        plantilla = 'emails/plantillas/recovery_password.html'
        imagenes = ['emails/templates/emails/imagenes_emails/logotipo_ontraveline.png', ]

        # 3 - Se llama a una función genérica que envía el email
        cls.enviar_correo(
            asunto = asunto,
            destinatarios = destinatarios,
            remitente = remitente,
            context = context,
            plantilla = plantilla,
            imagenes = imagenes,
        )

    @classmethod
    def enviar_correo_cuenta_cerrada(cls, usuario):
        # 1 - Se definen las partes y el contenido del email
        asunto = 'Su cuenta en Ontraveline ha sido cerrada'
        remitente = 'contact@ontraveline.com'

        context = {
            'usuario': usuario,
        }

        destinatarios = [usuario.user.email, ]
        plantilla = 'emails/plantillas/cuenta_cerrada.html'
        imagenes = ['emails/templates/emails/imagenes_emails/logotipo_ontraveline.png', ]

        # 2 - Se llama a una función genérica que envía el email
        cls.enviar_correo(
            asunto = asunto,
            destinatarios = destinatarios,
            remitente = remitente,
            context = context,
            plantilla = plantilla,
            imagenes = imagenes,
        )

    @classmethod
    # Envía un Correo al usuario que ha realizado una Reserva de Alojamiento. Se consideran los dos tipos de alquiler de Alojamiento
    def enviar_correo_cancelacion_reserva_alojamiento(cls, host, reserva_id):

        # 1 - Generar el PDF que se enviará adjunto por correo
        reserva = Reserva.objects.detalles_reserva(id = reserva_id)
        usuario = reserva.usuario

        # Características y configuración del PDF
        options = {
            'page-size': 'A4',
            'encoding': 'UTF-8'
        }
        config = pdfkit.configuration(wkhtmltopdf = globals.WKH2P_PATH)

        # Se general el PDF
        pdfkit.from_url(host + '/emails/pdf_cancelacion_reserva_alojamiento/%s' %(reserva_id), 'media/comprobantes_cancelacion_reserva/%s_C.pdf' %(reserva.codigo_reserva), configuration = config, options = options)

        # 2 - Crear el Email, adjuntar el PDF y enviarlo a la dirección del usuario que ha realizado la reserva
        # Aquí se definen todas las particularidades del Email que se quiere enviar
        asunto = 'Detalles de Cancelación de Reserva'
        remitente = 'contact@ontraveline.com'
        context = {
            'username': usuario.user.username,
        }

        destinatarios = [usuario.user.email, ]
        plantilla = 'emails/plantillas/cancelacion_reserva.html'
        imagenes = ['emails/templates/emails/imagenes_emails/logotipo_ontraveline.png', ]
        ficheros_adjuntos = ['media/comprobantes_cancelacion_reserva/%s_C.pdf' %(reserva.codigo_reserva), ]

        # Se llama a una función genérica que envía el email
        cls.enviar_correo(
            asunto = asunto,
            destinatarios = destinatarios,
            remitente = remitente,
            context = context,
            plantilla = plantilla,
            imagenes = imagenes,
            ficheros_adjuntos = ficheros_adjuntos,
        )

    @classmethod
    # Envía un Correo al usuario que ha realizado una Reserva de Alojamiento. Se consideran los dos tipos de alquiler de Alojamiento
    def enviar_correo_reserva_alojamiento(cls, host, reserva_id):

        # 1 - Generar el PDF que se enviará adjunto por correo
        # ID del usuario que realiza a reserva para conformar el nombre del PDF con la combinación unívoca del ID del Usuario y de la Reserva
        reserva = Reserva.objects.get(id=reserva_id)
        usuario = reserva.usuario

        # Características y configuración del PDF
        options = {
            'page-size': 'A4',
            'encoding': 'UTF-8'
        }
        config = pdfkit.configuration(wkhtmltopdf = globals.WKH2P_PATH)

        # En función de la modalidad de alquiler del Alojamiento se usa una vista u otra para generar el contenido del PDF
        if reserva.servicio.alojamiento.por_habitacion:
            pdfkit.from_url(host + '/emails/pdf_reserva_alojamiento_por_habitacion/%s' %(reserva_id), 'media/comprobantes_reserva/%s.pdf' %(reserva.codigo_reserva), configuration = config, options = options)
        else:
            pdfkit.from_url(host + '/emails/pdf_reserva_alojamiento_completo/%s' %(reserva_id), 'media/comprobantes_reserva/%s.pdf' %(reserva.codigo_reserva), configuration = config, options = options)

        # 2 - Crear el Email, adjuntar el PDF y enviarlo a la dirección del usuario que ha realizado la reserva
        # Aquí se definen todas las particularidades del Email que se quiere enviar
        asunto = 'Detalles de la Reserva'
        remitente = 'contact@ontraveline.com'
        context = {
            'username': usuario.user.username,
        }

        destinatarios = [usuario.user.email, ]
        plantilla = 'emails/plantillas/comprobante_reserva.html'
        imagenes = ['emails/templates/emails/imagenes_emails/logotipo_ontraveline.png', ]
        ficheros_adjuntos = ['media/comprobantes_reserva/%s.pdf' %(reserva.codigo_reserva), ]

        # Se llama a una función genérica que envía el email
        cls.enviar_correo(
            asunto = asunto,
            destinatarios = destinatarios,
            remitente = remitente,
            context = context,
            plantilla = plantilla,
            imagenes = imagenes,
            ficheros_adjuntos = ficheros_adjuntos,
        )

    @classmethod
    # Envía un Correo al usuario que ha realizado una Reserva de Alojamiento. Se consideran los dos tipos de alquiler de Alojamiento
    def enviar_correo_reserva_alojamiento_proveedor(cls, host, reserva_id):

        # 1 - Generar el PDF que se enviará adjunto por correo
        # ID del usuario que realiza a reserva para conformar el nombre del PDF con la combinación unívoca del ID del Usuario y de la Reserva
        reserva = Reserva.objects.get(id = reserva_id)

        # Características y configuración del PDF
        options = {
            'page-size': 'A4',
            'encoding': 'UTF-8'
        }
        config = pdfkit.configuration(wkhtmltopdf = globals.WKH2P_PATH)

        # En función de la modalidad de alquiler del Alojamiento se usa una vista u otra para generar el contenido del PDF
        if reserva.servicio.alojamiento.por_habitacion:
            pdfkit.from_url(
                host + '/emails/pdf_reserva_alojamiento_por_habitacion_proveedor/%s' %(reserva_id),
                'media/comprobantes_reserva/%s_P.pdf' %(reserva.codigo_reserva),
                configuration = config,
                options = options
            )
        else:
            pdfkit.from_url(
                host + '/emails/pdf_reserva_alojamiento_completo_proveedor/%s' %(reserva_id),
                'media/comprobantes_reserva/%s_P.pdf' %(reserva.codigo_reserva),
                configuration = config,
                options = options
            )

        # 2 - Crear el Email, adjuntar el PDF y enviarlo a la dirección del usuario que ha realizado la reserva
        # Aquí se definen todas las particularidades del Email que se quiere enviar
        asunto = '¡¡Enhorabuena, tu Alojamiento ha sido reservado!!'
        remitente = 'contact@ontraveline.com'
        context = {
            'user': reserva.servicio.usuario.user,
        }

        destinatarios = [reserva.servicio.usuario.user.email, ]
        plantilla = 'emails/plantillas/comprobante_reserva_proveedor.html'
        imagenes = ['emails/templates/emails/imagenes_emails/logotipo_ontraveline.png', ]
        ficheros_adjuntos = ['media/comprobantes_reserva/%s_P.pdf' % (reserva.codigo_reserva), ]

        # Se llama a una función genérica que envía el email
        cls.enviar_correo(
            asunto=asunto,
            destinatarios=destinatarios,
            remitente=remitente,
            context=context,
            plantilla=plantilla,
            imagenes=imagenes,
            ficheros_adjuntos=ficheros_adjuntos,
        )

    @classmethod
    # Envía un email a un usuario recién registrado sin necesidad que se valide dicha dirección de email (sin código de verificación)
    def enviar_correo_registro_usuario_sin_validacion(cls, usuario):
        destinatarios = [usuario.user.email, ]
        asunto = 'Bienvenido a Ontraveline'
        remitente = 'contact@ontraveline.com'
        context = {
            'first_name': usuario.user.first_name,
            'username': usuario.user.username,
            'password': usuario.raw_password,
        }
        plantilla = 'emails/plantillas/register_sin_validacion.html'
        imagenes = ['emails/templates/emails/imagenes_emails/logotipo_ontraveline.png', ]

        # Se llama a una función genérica que envía el email
        cls.enviar_correo(
            asunto = asunto,
            destinatarios = destinatarios,
            remitente = remitente,
            context = context,
            plantilla = plantilla,
            imagenes = imagenes,
        )

    @classmethod
    # Método que se llama para enviar un email a un usuario recién registrado
    def enviar_correo_registro_usuario(cls, usuario, host):
        # Destinatarios ha de ser una lista de strings donde cada uno es una dirección de correo electrónico
        # En este tipo de email de confirmación de registro debe ser uno solo

        # 1 - Ya que el usuario se acaba de registrar con el email al que vamos a enviar e link de activación, a través de este podemos obtener el objeto usuario
        destinatarios = [usuario.user.email,]

        # Lo primero es generar un código de activación para el usuario recién registrado
        link_activacion = Link_Activacion.generar_link_activacion(usuario = usuario, host = host)

        # Aquí se definen todas las particularidades del Email que se quiere enviar
        asunto = 'Bienvenido a Ontraveline'
        remitente = 'contact@ontraveline.com'
        context = {
            'username': usuario.user.username,
            'link_activacion': link_activacion.link,
            'static_root': globals.get_static_root(),
        }
        plantilla = 'emails/plantillas/register.html'
        # TODO: Suspendido temporalmente hasta arreglar error de apache que no encuentra el fichero
        # imagenes = ['%s/img/imagenes_emails/logotipo_ontraveline.png' %globals.get_static_root(),]

        # Se llama a una función genérica que envía el email
        cls.enviar_correo(
            asunto = asunto,
            destinatarios = destinatarios,
            remitente = remitente,
            context = context,
            plantilla = plantilla,
            # TODO: Suspendido temporalmente hasta arreglar error de apache que no encuentra el fichero
            # imagenes = imagenes,
        )

    @classmethod
    # Método genérico que se encarga de enviar un email
    def enviar_correo(cls, asunto, destinatarios, remitente, context, plantilla, imagenes = None, ficheros_adjuntos = None):
        html_content = render_to_string(plantilla, context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(asunto, text_content, remitente, destinatarios)
        msg.attach_alternative(html_content, "text/html")
        msg.mixed_subtype = 'related'

        # El siguiente "for" permite adjuntar las imágenes como parte del texto del correo, y no ajuntas como ficheros en este
        # La lista que recorre el for, debe contener los nombres (rutas incluidas) de las imágenes a enviar.
        # Posteriormente estas son llamadas en el template de plantilla HTML que conforma el cuerpo del correo
        if imagenes:
            for imagen in imagenes:
                # fp = open(os.path.join(os.path.dirname(__file__), imagen), 'rb')
                fp = open(imagen, 'rb')
                msg_img = MIMEImage(fp.read())
                fp.close()
                msg_img.add_header('Content-ID', '<{}>'.format(imagen))
                msg.attach(msg_img)

        # Adjuntando los ficheros adjuntos que se indiquen en el argumento del método
        if ficheros_adjuntos:
            for fichero_adjunto in ficheros_adjuntos or []:
                with open(fichero_adjunto, "rb") as f:
                    part = MIMEApplication(
                        f.read(),
                        Name = basename(fichero_adjunto)
                    )
                # After the file is closed
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(fichero_adjunto)
                msg.attach(part)

        # Se envía el correo
        msg.send()

        # Luego de enviar el correo se registra el envío
        n_email = Email.nuevo_email(
            asunto = asunto,
            cuerpo = html_content,
            remitente = remitente,
            destinatarios = destinatarios
        )


    @classmethod
    def nuevo_email(cls, asunto, cuerpo, remitente, destinatarios):
        n_email = cls.objects.create(
            asunto = asunto,
            cuerpo = cuerpo,
            remitente = remitente,
            destinatarios = str(destinatarios)
        )
        return n_email

    class Meta:
        verbose_name_plural = 'Emails'

    def __str__(self):
        return 'Email para %s destinatario(s) enviado por %s el %s con asunto: "%s"' %(len(self.destinatarios.split(',')), self.remitente, self.fecha_envio.strftime('%d-%m-%Y'), self.asunto)