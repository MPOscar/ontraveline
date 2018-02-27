from django.contrib import admin
from twilio_app.models import Twilio_Client, Twilio_Number, Codigo_Verificacion, Solicitud_Verificacion

# Register your models here.
admin.site.register(Twilio_Client)
admin.site.register(Twilio_Number)
admin.site.register(Codigo_Verificacion)
admin.site.register(Solicitud_Verificacion)