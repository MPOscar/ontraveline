from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(r'^index/$', views.index, name = 'index'),
    url(r'^home/$', views.index, name = 'index'),
    url(r'^inicio/$', views.index, name = 'index'),
    url(r'^contacto/$', views.contacto, name = 'contacto'),
    url(r'^temporalmente_indisponible/$', views.temporalmente_indisponible, name = 'temporalmente_indisponible'),
    url(r'^terminos_de_uso/$', views.terminos_de_uso, name = 'terminos_de_uso'),
    url(r'^condiciones_legales/$', views.condiciones_legales, name = 'condiciones_legales'),
    url(r'^politica_de_privacidad_de_datos/$', views.politica_de_privacidad_de_datos, name = 'politica_de_privacidad_de_datos'),
    url(r'^contacto/$', views.contacto, name = 'contacto'),
    url(r'^sobre_nosotros/$', views.sobre_nosotros, name = 'sobre_nosotros'),
    url(r'^ofreces_servicios/$', views.ofreces_servicios, name = 'ofreces_servicios'),
    url(r'^servicios/$', views.servicios, name = 'servicios'),
    url(r'^buscar_recorridos/$', views.buscar_recorridos, name = 'buscar_recorridos'),
    url(r'^buscar_taxis/$', views.buscar_taxis, name = 'buscar_taxis'),
    url(r'^buscar_paquetes/$', views.buscar_paquetes, name = 'buscar_paquetes'),
    url(r'^set_currency/(?P<moneda>\w+)/$', views.set_currency, name = 'set_currency'),
    url(r'^destino/(?P<destino_id>\d+)/$', views.destino, name = 'destino'),
    url(r'^search/(?P<elemento>\w+)/$', views.search, name = 'search'),

    url(r'^buscar_alojamientos_por_habitacion/$', views.buscar_alojamientos_por_habitacion, name = 'buscar_alojamientos_por_habitacion'),
    url(r'^buscar_alojamientos_completos/$', views.buscar_alojamientos_completos, name = 'buscar_alojamientos_completos'),
    url(r'^buscar_excursiones/$', views.buscar_excursiones, name = 'buscar_excursiones'),
    url(r'^buscar_citytours/$', views.buscar_citytours, name = 'buscar_citytours'),
    url(r'^buscar_tours/$', views.buscar_tours, name = 'buscar_tours'),
    url(r'^buscar_destinos/$', views.buscar_destinos, name = 'buscar_destinos'),
    url(r'^como_funciona/$', views.como_funciona, name = 'como_funciona'),
    url(r'^blog/$', views.blog, name = 'blog'),
    url(r'^get_destinos/$', views.get_destinos, name = 'get_destinos'),
    url(r'^get_aeropuertos_mundo/$', views.get_aeropuertos_mundo, name = 'get_aeropuertos_mundo'),
    url(r'^get_destinos_provincias_municipios_alojamientos/$', views.get_destinos_provincias_municipios_alojamientos, name = 'get_destinos_provincias_municipios_alojamientos'),

    # PRUEBAS
    url(r'^pruebas_html/$', views.pruebas_html, name = 'pruebas_html'),
]