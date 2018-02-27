from django.contrib import admin
from social.models import Conector_Facebook, Conector_Google, Conector_Instagram, Conector_Linkedin,\
    App_Facebook, App_Google, App_Instagram, App_Linkedin

# Register your models here.
# admin.site.register(Conector_Twitter)
admin.site.register(Conector_Facebook)
admin.site.register(Conector_Google)
admin.site.register(Conector_Instagram)
admin.site.register(Conector_Linkedin)
# admin.site.register(App_Twitter)
admin.site.register(App_Facebook)
admin.site.register(App_Google)
admin.site.register(App_Instagram)
admin.site.register(App_Linkedin)