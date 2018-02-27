from django.contrib import admin
from pagos.models import Paypal_App, Pago

# Register your models here.
admin.site.register(Paypal_App)
admin.site.register(Pago)