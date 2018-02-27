from django.contrib import admin
from .models import Mensaje_Contacto, Testimonio, Aeropuerto

# Register your models here.
admin.site.register(Mensaje_Contacto)
admin.site.register(Testimonio)
admin.site.register(Aeropuerto)