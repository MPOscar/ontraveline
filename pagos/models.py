from django.db import models
from support.globals import costo_gestion_cuc, impuesto_rate
from decimal import Decimal
import paypalrestsdk

class Paypal_App(models.Model):
    nombre = models.CharField('Nombre', max_length = 64, blank = False, null = False, unique = False)
    modo = models.CharField('Modo ("sandbox" o "live")', max_length = 7, blank = False, null = False, unique = False)
    mail_vendedor = models.EmailField('E-Mail vendedor', max_length = 64, blank = False, null = False, unique = False)
    client_id = models.CharField('Client ID', max_length = 80, blank = False, null = False, unique = True)
    client_secret = models.CharField('Client SECRET', max_length = 80, blank = False, null = False, unique = True)
    return_url = models.URLField('Return URL', max_length = 255, blank = False, null = False, unique = False)
    cancel_url = models.URLField('Cancel URL', max_length = 255, blank = False, null = False, unique = False)
    en_uso = models.BooleanField('En uso', blank = True, default = False)

    def create_payment(self, name, price, total):
        # Se configura la App con las credenciales y el modo de operativa
        paypalrestsdk.configure(
            {
                "mode": self.modo,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
        )

        # Se crea el objeto de Pago
        payment = paypalrestsdk.Payment(
            {
                "intent": "sale",

                "payer": {
                    "payment_method": "paypal",
                },

                "redirect_urls": {
                    "return_url": self.return_url,
                    "cancel_url": self.cancel_url,
                },

                "transactions": [
                    {
                        "item_list": {
                            "items": [
                                {
                                    "name": name,
                                    "sku": "item",
                                    "price": price,
                                    "currency": "EUR",
                                    "quantity": 1,
                                }
                            ]
                        },
                        "amount": {
                            "total": total,
                            "currency": "EUR",
                        },
                        "description": "This is the payment transaction description."
                    }
                ]
            }
        )

        # Se devuelve el objeto de pago creado y configurado configurado
        payment.create()
        return payment

    @classmethod
    def nueva_paypal_app(cls, nombre, modo, mail_vendedor, client_id, client_secret, return_url, cancel_url, en_uso = False):
        # Se comprueba que no exista ninguna otra App con el mismo client_id
        if cls.objects.filter(client_id = client_id):
            message = 'Ya existe una App de Paypal con el client_id: %s' %(client_id)
            print(message)
            return {
                'message': message,
            }
        # Se comprueba que no exista ninguna App de Paypal con el mismo client_secret
        if cls.objects.filter(client_secret = client_secret):
            message = 'Ya existe una App de Paypal con el client_secret: %s' %(client_secret)
            print(message)
            return {
                'message': message,
            }
        # Se comprueba que en caso de que se quiera registrar la App como "en_uso" no haya otra declarada como tal con el mismo "modo"
        if en_uso and cls.objects.filter(modo = modo, en_uso = True):
            message = 'Ya existe otra App en modo %s actualmente en uso' %(modo)
            print(message)
            return {
                'message': message,
            }
        # Si no hay problema con los criterios anteriores se registra la App
        n_paypal_app = cls.objects.create(
            nombre = nombre,
            modo = modo,
            mail_vendedor = mail_vendedor,
            return_url = return_url,
            cancel_url = cancel_url,
            client_id = client_id,
            client_secret = client_secret,
            en_uso = en_uso,
        )
        print('Se ha creado correctamente la App de Paypal %s' %(nombre))
        return n_paypal_app

    def modificar_paypal_app(self, nombre, modo, mail_vendedor, client_id, client_secret, return_url, cancel_url, en_uso):
        # todo: Añadir filtros
        self.nombre = nombre
        self.modo = modo
        self.mail_vendedor = mail_vendedor
        self.return_url = return_url
        self.cancel_url = cancel_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.en_uso = en_uso
        self.save()
        print('Se ha modificado correctamente la App de Paypal %s' %(nombre))
        return self

    @classmethod
    def get_payer_data(cls, payer):
        # Se extrae toda la información del objeto payer de la respuesta de Paypal...
        email = payer['payer_info']['email']
        first_name = payer['payer_info']['first_name']
        last_name = payer['payer_info']['last_name']
        pais_paypal = payer['payer_info']['country_code']
        provincia_paypal = payer['payer_info']['shipping_address']['state']
        direccion = payer['payer_info']['shipping_address']['line1']
        if 'line_2' in payer['payer_info']['shipping_address']:
            direccion += ' %s' % (payer['payer_info']['shipping_address']['line2'])
        ciudad = payer['payer_info']['shipping_address']['city']
        codigo_postal = payer['payer_info']['shipping_address']['postal_code']

        # ... y se devuelve como un Diccionario
        return {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'pais_paypal': pais_paypal,
            'provincia_paypal': provincia_paypal,
            'direccion': direccion,
            'ciudad': ciudad,
            'codigo_postal': codigo_postal,
        }

    def eliminar_paypal_app(self):
        self.delete()
        print('Se ha eliminado correctamente la App de Paypal')

    def usar_paypal_app(self):
        self.en_uso = True
        self.save()

    def no_usar_paypal_app(self):
        self.en_uso = False
        self.save()

    class Meta:
        verbose_name_plural = 'Paypal Apps'

    def __str__(self):
        return '%s (%s)' %(self.nombre, self.modo)

class Pago(models.Model):
    paypal_app = models.ForeignKey(Paypal_App, blank = False, null = False, unique = False, on_delete = models.CASCADE)
    reserva = models.ForeignKey('servicios.Reserva', blank = True, null = True, unique = False, on_delete = models.CASCADE)
    reserva_dict = models.TextField('Reserva (stores in session)', blank = True, null = True, unique = False)
    paypal_payment_id = models.CharField('ID Paypal Payment', max_length = 255, blank = False, null = False, unique = True, db_index = True)
    completado = models.BooleanField('Completado', blank = True, default = False)
    created_at = models.DateTimeField('Fecha y hora de creación', blank = False, null = False, auto_now_add = True)
    total_pagado_euros = models.DecimalField('Total Pagado €', max_digits = 6, decimal_places = 2, blank = True, null = True, unique = False)
    approval_url = models.URLField('URL de aprovación', max_length = 255, blank = False, null = False, unique = False)

    # Se desglosa el pago online en las partes que lo componen (en €)
    def distribucion_pago(self):
        # Lo primero es determinar el tipo de cambio que se usó cuando se realizó el pago
        # Para ello podemos dividir la cantidad pagada en € por la que habría sido en CUC según la Reserva
        tipo_cambio = Decimal(self.total_pagado_euros / (self.reserva.comision + Decimal(1.21) * costo_gestion_cuc))
        costo_gestion_euros = round(Decimal(costo_gestion_cuc * tipo_cambio), 2)
        impuesto_euros = round(costo_gestion_cuc * impuesto_rate, 2)
        comision_euros = self.total_pagado_euros - impuesto_euros - costo_gestion_euros
        return {
            'tipo_cambio': tipo_cambio,
            'costo_gestion_euros': costo_gestion_euros,
            'impuesto_euros': impuesto_euros,
            'comision_euros': comision_euros,
        }

    # Se crea un nuevo usuario a partir de una compra de usuario anónimo
    def create_new_user(self):
        payment = paypalrestsdk.Payment.find(self.paypal_payment_id)

    # Se ejecuta el pago en Paypal a través de la API una vez se ha obtenido autorización del cliente para hacer efectiva la transferencia de dinero
    def ejecutar_pago(self, PayerID):
        payment = paypalrestsdk.Payment.find(self.paypal_payment_id)
        execute_response = payment.execute({"payer_id": PayerID})

        if execute_response:
            # Si se ejecuta el pago en Paypal, entonces desencadenamos el proceso consecuente en nuestra parte
            self.set_completado()
            return payment.__data__
        else:
            return False

    # Define un pago como completado, y desencadena las acciones que de este hecho dependen
    def set_completado(self):
        # Se marca el pago como completado
        self.completado = True
        self.save()

    @classmethod
    def nuevo_pago(cls, paypal_app, reserva, reserva_dict, paypal_payment_id, total_pagado_euros, approval_url):
        # Se comprueba que no exista ningún otro pago registrado con el id del que se quiere registrar
        if cls.objects.filter(paypal_payment_id = paypal_payment_id):
            message = 'Ya existe un pago registrado con ID de Paypal: %s' %(paypal_payment_id)
            print(message)
            return {
                'message': message,
            }
        else:
            n_pago = cls.objects.create(
                paypal_app = paypal_app,
                reserva = reserva,
                reserva_dict = reserva_dict,
                paypal_payment_id = paypal_payment_id,
                total_pagado_euros = total_pagado_euros,
                approval_url = approval_url,
            )
            print('Se ha creado correctamente el pago %s' %(paypal_payment_id))
            return n_pago

    def eliminar_pago(self):
        self.delete()
        print('Se ha eliminado correctamente el Pago')

    class Meta:
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return self.paypal_payment_id