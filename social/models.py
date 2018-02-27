from django.db import models
import tweepy

class App_Twitter(models.Model):
    nombre = models.CharField('Nombre', max_length = 32, blank = True, null = True, unique = False)
    consumer_key = models.CharField('Consumer Key', max_length = 255, blank = True, null = True, unique = False)
    consumer_secret = models.CharField('Consumer Secret', max_length = 255, blank = True, null = True, unique = False)
    callback_url = models.URLField('Callback URL', max_length = 128, blank = True, null = True, unique = False)
    owner = models.CharField('Owner', max_length = 64, blank = True, null = True, unique = False)
    owner_id = models.CharField('Owner ID', max_length = 32, blank = True, null = True, unique = False)
    en_uso = models.BooleanField('En uso', blank = True, default = False)

    class Meta:
        verbose_name_plural = 'Apps Twitter'

    def __str__(self):
        return 'App Twitter'

class App_Facebook(models.Model):
    secret_key = models.CharField('Secret Key', max_length = 256, blank = True, null = True, unique = False)

    class Meta:
        verbose_name_plural = 'Apps Facebook'

    def __str__(self):
        return 'App Facebook'

class App_Google(models.Model):
    secret_key = models.CharField('Secret Key', max_length = 256, blank = True, null = True, unique = False)

    class Meta:
        verbose_name_plural = 'Apps Google'

    def __str__(self):
        return 'App Google'

class App_Instagram(models.Model):
    secret_key = models.CharField('Secret Key', max_length = 256, blank = True, null = True, unique = False)

    class Meta:
        verbose_name_plural = 'Apps Instagram'

    def __str__(self):
        return 'App Instagram'

class App_Linkedin(models.Model):
    secret_key = models.CharField('Secret Key', max_length = 256, blank = True, null = True, unique = False)

    class Meta:
        verbose_name_plural = 'Apps Linkedin'

    def __str__(self):
        return 'App Linkedin'

class Conector_Twitter(models.Model):
    access_token = models.CharField('Access Token', max_length = 255, blank = True, null = True, unique = False)
    access_token_secret = models.CharField('Access Token Secret', max_length = 255, blank = True, null = True, unique = False)
    usuario = models.ForeignKey('usuarios.Usuario', blank = True, null = True, unique = False, on_delete = models.CASCADE)
    token = models.CharField('Token', max_length = 256, blank = True, null = True, unique = False)
    app_twitter = models.ForeignKey(App_Twitter, blank = True, null = True, unique = False, on_delete = models.CASCADE)
    usuario_twitter = models.CharField('Usuario de Twitter', max_length = 64, blank = True, null = True, unique = False)
    fecha = models.DateField('Fecha Creación', blank = True, null = True, unique = False, auto_now_add = True)

    # Devuelve un objeto api de la conexión con la cuenta de un usuario
    def get_api(self):
        # Definiendo los parámetros de conexión
        consumer_key = self.app_twitter.consumer_key
        consumer_secret = self.app_twitter.consumer_secret
        access_token = self.access_token
        access_token_secret = self.access_token_secret

        # Estableciendo la conexión con la cuenta del cliente
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        # Instanciando la API para llevar a cabo las acciones deseadas
        api = tweepy.API(auth)
        return api

    # Devuelve True o False, en función de si existe conexión con la cuenta de Twitter del Usuario
    def check_client_access(self):
        api = self.get_api()
        try:
            api.verify_credentials()
            return True
        except:
            self.eliminar_twitter_conector()
            return False

    # Elimina un Conector de Twitter específico
    def eliminar_twitter_conector(self):
        self.delete()

    class Meta:
        verbose_name_plural = 'Conectores Twitter'

    def __str__(self):
        return 'Conector de Twitter para %s' %(self.usuario)

class Conector_Facebook(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', blank = False, null = False, unique = False, on_delete = models.CASCADE)
    token = models.CharField('Token', max_length = 256, blank = True, null = True, unique = False)

    class Meta:
        verbose_name_plural = 'Conectores Facebook'

    def __str__(self):
        return 'Conector de Facebook para %s' %(self.usuario)

class Conector_Google(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', blank = False, null = False, unique = False, on_delete = models.CASCADE)
    token = models.CharField('Token', max_length = 256, blank = True, null = True, unique = False)

    class Meta:
        verbose_name_plural = 'Conectores Google'

    def __str__(self):
        return 'Conector de Google para %s' %(self.usuario)

class Conector_Instagram(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', blank = False, null = False, unique = False, on_delete = models.CASCADE)
    token = models.CharField('Token', max_length = 256, blank = True, null = True, unique = False)

    class Meta:
        verbose_name_plural = 'Conectores Instagram'

    def __str__(self):
        return 'Conector de Instagram para %s' %(self.usuario)

class Conector_Linkedin(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', blank = False, null = False, unique = False, on_delete = models.CASCADE)
    token = models.CharField('Token', max_length = 256, blank = True, null = True, unique = False)

    class Meta:
        verbose_name_plural = 'Conectores Linkedin'

    def __str__(self):
        return 'Conector de Linkedin para %s' %(self.usuario)