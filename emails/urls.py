from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^plantilla_register/$', views.plantilla_register, name = 'plantilla_register'),
    url(r'^pdf_reserva_alojamiento_completo/(?P<reserva_id>\d+)/$', views.pdf_reserva_alojamiento_completo, name = 'pdf_reserva_alojamiento_completo'),
    url(r'^pdf_reserva_alojamiento_completo_proveedor/(?P<reserva_id>\d+)/$', views.pdf_reserva_alojamiento_completo_proveedor, name = 'pdf_reserva_alojamiento_completo_proveedor'),
    url(r'^pdf_reserva_alojamiento_por_habitacion/(?P<reserva_id>\d+)/$', views.pdf_reserva_alojamiento_por_habitacion, name = 'pdf_reserva_alojamiento_por_habitacion'),
    url(r'^pdf_reserva_alojamiento_por_habitacion_proveedor/(?P<reserva_id>\d+)/$', views.pdf_reserva_alojamiento_por_habitacion_proveedor, name = 'pdf_reserva_alojamiento_por_habitacion_proveedor'),
    url(r'^pdf_cancelacion_reserva_alojamiento/(?P<reserva_id>\d+)/$', views.pdf_cancelacion_reserva_alojamiento, name = 'pdf_cancelacion_reserva_alojamiento'),
    url(r'^error_activacion/$', views.error_activacion, name = 'error_activacion'),
    url(r'^confirmar_email_usuario/(?P<codigo_activacion>\w+)/$', views.confirmar_email_usuario, name = 'confirmar_email_usuario'),
    url(r'^reenviar_email_confirmacion/(?P<usuario_id>\d+)/$', views.reenviar_email_confirmacion, name = 'reenviar_email_confirmacion'),
    # url(r'^logout/$', views.logout_view, name = 'logout_view'),
    # url(r'^perfil_usuario/$', views.perfil_usuario, name = 'perfil_usuario'),
    # url(r'^cambiar_estado_proveedor/(?P<usuario_id>\d+)/$', views.cambiar_estado_proveedor, name = 'cambiar_estado_proveedor'),
    # url(r'^cambiar_estado_activo/(?P<usuario_id>\d+)/$', views.cambiar_estado_activo, name = 'cambiar_estado_activo'),
    # url(r'^cambiar_estado_admin/(?P<usuario_id>\d+)/$', views.cambiar_estado_admin, name = 'cambiar_estado_admin'),
    # url(r'^eliminar_usuario/(?P<usuario_id>\d+)/$', views.eliminar_usuario, name = 'eliminar_usuario'),
    # url(r'^eliminar_foto_perfil/(?P<usuario_id>\d+)/$', views.eliminar_foto_perfil, name = 'eliminar_foto_perfil'),
]