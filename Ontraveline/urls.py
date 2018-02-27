from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    url(r'^', include('website.urls', namespace = 'website')),
    url(r'^admin/', admin.site.urls), # URL para el admin web
    url(r'^usuarios/', include('usuarios.urls', namespace = 'usuarios')),
    url(r'^servicios/', include('servicios.urls', namespace = 'servicios')),
    url(r'^mensajes/', include('mensajes.urls', namespace = 'mensajes')),
    url(r'^social/', include('social.urls', namespace = 'social')),
    url(r'^administracion/', include('administracion.urls', namespace = 'administracion')),
    url(r'^emails/', include('emails.urls', namespace = 'emails')),
    url(r'^pagos/', include('pagos.urls', namespace = 'pagos')),
    url(r'^blog/', include('blog.urls', namespace = 'blog')),
    url(r'^twilio/', include('twilio_app.urls', namespace = 'twilio')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)