from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/$', views.login_view, name = 'login_view'),
    url(r'^logout/$', views.logout_view, name = 'logout_view'),
    url(r'^perfil_usuario/$', views.perfil_usuario, name = 'perfil_usuario'),
    url(r'^cambiar_estado_proveedor/(?P<usuario_id>\d+)/$', views.cambiar_estado_proveedor, name = 'cambiar_estado_proveedor'),
    url(r'^cerrar_cuenta_usuario/(?P<usuario_id>\d+)/$', views.cerrar_cuenta_usuario, name = 'cerrar_cuenta_usuario'),
    url(r'^cambiar_estado_activo/(?P<usuario_id>\d+)/$', views.cambiar_estado_activo, name = 'cambiar_estado_activo'),
    url(r'^cambiar_estado_admin/(?P<usuario_id>\d+)/$', views.cambiar_estado_admin, name = 'cambiar_estado_admin'),
    url(r'^eliminar_usuario/(?P<usuario_id>\d+)/$', views.eliminar_usuario, name = 'eliminar_usuario'),
    url(r'^eliminar_foto_perfil/(?P<usuario_id>\d+)/$', views.eliminar_foto_perfil, name = 'eliminar_foto_perfil'),
    url(r'^centro_verificacion_datos/$', views.centro_verificacion_datos, name = 'centro_verificacion_datos'),
    url(r'^forgot_password/$', views.forgot_password, name = 'forgot_password'),
    url(r'^verificar_movil/(?P<usuario_id>\d+)/$', views.verificar_movil, name = 'verificar_movil'),
    url(r'^documentos_verificacion_actividad/(?P<usuario_id>\d+)/$', views.documentos_verificacion_actividad, name = 'documentos_verificacion_actividad'),
    url(r'^eliminar_foto_documento_actividad/(?P<foto_documento_actividad_id>\d+)/$', views.eliminar_foto_documento_actividad, name = 'eliminar_foto_documento_actividad'),
    url(r'^get_provincias_pais/(?P<pais_id>\d+)/$', views.get_provincias_pais, name = 'get_provincias_pais'),
    url(r'^recovery_password/(?P<code>\w+)/$', views.recovery_password, name = 'recovery_password'),
]