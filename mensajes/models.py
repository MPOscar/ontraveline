from django.db import models

class Mensaje_Cliente(models.Model):
    nombre = models.CharField('Nombre', max_length = 64, blank = False, null = False, unique = False)
    email = models.EmailField('E-Mail', max_length = 64, blank = False, null = False, unique = False)
    mensaje = models.CharField('Mensaje', max_length = 1024, blank = False, null = False, unique = False)
    created_at = models.DateTimeField('Fecha y Hora', blank = False, null = False, unique = False, auto_now_add = True)

    @classmethod
    def nuevo_mensaje_contacto(cls, nombre, email, mensaje):
        n_mensaje_contacto = cls.objects.create(
            nombre = nombre,
            email = email,
            mensaje = mensaje,
        )
        return n_mensaje_contacto

    class Meta:
        verbose_name_plural = 'Mensajes de Contacto'

    def __str__(self):
        return 'Mensaje de %s el %s' %(self.email, self.created_at)