from django.db import models

class Mensaje_Contacto(models.Model):
    nombre = models.CharField('Nombre', max_length = 64, blank = True, null = True, unique = False)
    email = models.EmailField('E-Mail', max_length = 64, blank = False, null = False, unique = False)
    message = models.CharField('Mensaje', max_length = 1024, blank = False, null = False)

    @classmethod
    def nuevo_mensaje_contacto(cls, nombre, email, message):
        n_mensaje_contacto = cls.objects.create(
            nombre = nombre,
            email = email,
            message = message,
        )
        return n_mensaje_contacto

    class Meta:
        verbose_name_plural = 'Mensajes de Contacto'

    def __str__(self):
        return 'Mensaje de %s' %(self.email)

class Testimonio(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', blank = False, null = False, unique = False, on_delete = models.CASCADE)
    testimonio = models.CharField('Testimonio', max_length = 255, blank = False, null = False, unique = False)
    mostrar = models.BooleanField('Mostrar', blank = True, default = False)

    @classmethod
    def nuevo_testimonio(cls, usuario, testimonio):
        n_testimonio = cls.objects.create(
            usuario = usuario,
            testimonio = testimonio,
        )
        return n_testimonio

    class Meta:
        verbose_name_plural = 'Testimonios'

    def __str__(self):
        return 'Testimonio de %s' %(self.usuario)

class Aeropuerto(models.Model):
    codigo_iata = models.CharField('Código IATA', max_length = 5, blank = False, null = False, unique = True, db_index = True)
    info_completa = models.CharField('Nombre', max_length = 255, blank = True, null = True, unique = False)
    cuba = models.BooleanField('Cuba', blank = True, default = False)

    @classmethod
    def nuevo_aeropuerto(cls, codigo_iata, info_completa):
        # Se comprueba que no exista ningún aeropuerto registrado en este modelo con el mismo código IATA
        if cls.objects.filter(codigo_iata = codigo_iata):
            message = 'Ya existe un Aeropuerto con código IATA %s' %(codigo_iata)
            print(message)
            return {
                'message': message,
            }
        else:
            n_aeropuerto = cls.objects.create(
                codigo_iata = codigo_iata,
                info_completa = info_completa,
            )
            print('Se ha creado correctamente el Aeropuerto %s' %(info_completa))
            return n_aeropuerto

    class Meta:
        verbose_name_plural = 'Aeropuertos'

    def __str__(self):
        return self.info_completa
