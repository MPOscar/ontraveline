from django.conf.urls import url
from administracion import views

urlpatterns = [
    url(r'^dashboard/$', views.dashboard, name = 'dashboard'),
    url(r'^administrar_usuarios/$', views.administrar_usuarios, name = 'administrar_usuarios'),
    url(r'^administrar_twilio_numbers/$', views.administrar_twilio_numbers, name = 'administrar_twilio_numbers'),
    url(r'^add_usuario/$', views.add_usuario, name = 'add_usuario'),
    url(r'^add_twilio_client/$', views.add_twilio_client, name = 'add_twilio_client'),
    url(r'^add_twilio_number/$', views.add_twilio_number, name = 'add_twilio_number'),
    url(r'^administrar_alojamientos/$', views.administrar_alojamientos, name = 'administrar_alojamientos'),
    url(r'^add_alojamiento/$', views.add_alojamiento, name = 'add_alojamiento'),
    url(r'^administrar_destinos/$', views.administrar_destinos, name = 'administrar_destinos'),
    url(r'^administrar_twilio_clients/$', views.administrar_twilio_clients, name = 'administrar_twilio_clients'),
    url(r'^datos_prueba/$', views.datos_prueba, name = 'datos_prueba'),
    url(r'^add_destino/$', views.add_destino, name = 'add_destino'),
    url(r'^modificar_usuario/(?P<usuario_id>\d+)/$', views.modificar_usuario, name = 'modificar_usuario'),
    url(r'^modificar_twilio_client/(?P<twilio_client_id>\d+)/$', views.modificar_twilio_client, name = 'modificar_twilio_client'),
    url(r'^modificar_twilio_number/(?P<twilio_number_id>\d+)/$', views.modificar_twilio_number, name = 'modificar_twilio_number'),
    url(r'^eliminar_twilio_client/(?P<eliminar_twilio_client>\d+)/$', views.eliminar_twilio_client, name = 'eliminar_twilio_client'),
    url(r'^eliminar_twilio_number/(?P<eliminar_twilio_number>\d+)/$', views.eliminar_twilio_number, name = 'eliminar_twilio_number'),
    url(r'^activar_usuario/(?P<usuario_id>\d+)/$', views.activar_usuario, name = 'activar_usuario'),
    url(r'^verificar_email/(?P<usuario_id>\d+)/$', views.verificar_email, name = 'verificar_email'),
    url(r'^usar_twilio_number/(?P<twilio_number_id>\d+)/$', views.usar_twilio_number, name = 'usar_twilio_number'),
    url(r'^cambiar_uso_twilio_number/(?P<twilio_number_id>\d+)/$', views.cambiar_uso_twilio_number, name = 'cambiar_uso_twilio_number'),
    url(r'^verificar_movil/(?P<usuario_id>\d+)/$', views.verificar_movil, name = 'verificar_movil'),
    url(r'^proveedor/(?P<usuario_id>\d+)/$', views.proveedor, name = 'proveedor'),
    url(r'^verificado_proveedor/(?P<usuario_id>\d+)/$', views.verificado_proveedor, name = 'verificado_proveedor'),
]