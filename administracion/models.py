from django.db import models

class Impuesto(models.Model):
    nombre = models.CharField('Nombre', max_length = 16, blank = False, null = False, unique = True)
    porciento = models.DecimalField('Porciento', max_digits = 4, decimal_places = 2, blank = False, null = False, unique = False)

    @classmethod
    def nuevo_impuesto(cls, nombre, porciento):
        if not cls.objects.filter(nombre = nombre):
            n_impuesto = cls.objects.create(
                nombre = nombre,
                porciento = porciento,
            )
            print('Se ha registrado correctamente el impuesto %s' %(n_impuesto))
            return n_impuesto
        else:
            print('Ya existe un impuesto con nombre %s' %(nombre))
            return None

    def eliminar(self):
        self.delete()

    class Meta:
        verbose_name_plural = 'Impuestos'

    def __str__(self):
        return '%s (%s)' %(self.nombre, self.porciento)


