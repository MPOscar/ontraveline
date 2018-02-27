from django.contrib import admin
from usuarios.models import Usuario, Foto_Licencia_Actividad, Codigo_Recovery_Password

# Register your models here.
admin.site.register(Usuario)
admin.site.register(Foto_Licencia_Actividad)
admin.site.register(Codigo_Recovery_Password)