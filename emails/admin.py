from django.contrib import admin
from emails.models import Email, Link_Activacion

# Register your models here.
admin.site.register(Email)
admin.site.register(Link_Activacion)