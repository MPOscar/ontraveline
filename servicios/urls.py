from django.conf.urls import url
from servicios import views

urlpatterns = [
    #_______________________Alojamientos_____________________
    url(r'^add_alojamiento/$', views.add_alojamiento, name = 'add_alojamiento'),
    url(r'^add_alojamiento_completo/(?P<alojamiento_sin_finalizar_id>\d+)/$', views.add_alojamiento_completo, name = 'add_alojamiento_completo'),
    url(r'^administrar_alojamiento/(?P<alojamiento_id>\d+)/$', views.administrar_alojamiento, name = 'administrar_alojamiento'),
    url(r'^eliminar_alojamiento/(?P<alojamiento_id>\d+)/$', views.eliminar_alojamiento, name = 'eliminar_alojamiento'),
    url(r'^eliminar_alojamiento_sin_finalizar/(?P<alojamiento_sin_finalizar_id>\d+)/$', views.eliminar_alojamiento_sin_finalizar, name = 'eliminar_alojamiento_sin_finalizar'),
    url(r'^modificar_alojamiento_completo/(?P<alojamiento_id>\d+)/$', views.modificar_alojamiento_completo, name = 'modificar_alojamiento_completo'),
    url(r'^modificar_alojamiento_por_habitacion/(?P<alojamiento_id>\d+)/$', views.modificar_alojamiento_por_habitacion, name = 'modificar_alojamiento_por_habitacion'),
    url(r'^evaluaciones_servicio/(?P<servicio_id>\d+)/$', views.evaluaciones_servicio, name = 'evaluaciones_servicio'),
    url(r'^checkout_alojamiento_por_habitacion/(?P<reserva_id>\d+)/$', views.checkout_alojamiento_por_habitacion, name = 'checkout_alojamiento_por_habitacion'),
    url(r'^checkout_alojamiento_por_habitacion_servicio/(?P<servicio_id>\d+)/$', views.checkout_alojamiento_por_habitacion, name = 'checkout_alojamiento_por_habitacion_servicio'),
    url(r'^checkout_alojamiento_completo/(?P<reserva_id>\d+)/$', views.checkout_alojamiento_completo, name = 'checkout_alojamiento_completo'),
    url(r'^checkout_alojamiento_completo_servicio/(?P<servicio_id>\d+)/$', views.checkout_alojamiento_completo, name = 'checkout_alojamiento_completo_servicio'),
    url(r'^get_lat_lng/(?P<alojamiento_id>\d+)/$', views.get_lat_lng, name = 'get_lat_lng'),
    url(r'^get_data_alojamientos/$', views.get_data_alojamientos, name = 'get_data_alojamientos'),

    #______________________Habitaciones______________________
    url(r'^add_habitacion_alojamiento_por_habitacion/(?P<alojamiento_id>\d+)/$', views.add_habitacion_alojamiento_por_habitacion, name = 'add_habitacion_alojamiento_por_habitacion'),
    url(r'^add_habitacion_alojamiento_completo/(?P<alojamiento_id>\d+)/$', views.add_habitacion_alojamiento_completo, name = 'add_habitacion_alojamiento_completo'),
    url(r'^fotos_habitacion/(?P<habitacion_id>\d+)/$', views.fotos_habitacion, name = 'fotos_habitacion'),
    url(r'^administrar_habitacion_alojamiento_por_habitacion/(?P<habitacion_id>\d+)/$', views.administrar_habitacion_alojamiento_por_habitacion, name = 'administrar_habitacion_alojamiento_por_habitacion'),
    url(r'^modificar_habitacion_alojamiento_por_habitacion/(?P<habitacion_id>\d+)/$', views.modificar_habitacion_alojamiento_por_habitacion, name = 'modificar_habitacion_alojamiento_por_habitacion'),
    url(r'^modificar_habitacion/(?P<habitacion_id>\d+)/$', views.modificar_habitacion, name = 'modificar_habitacion'),
    url(r'^eliminar_habitacion/(?P<habitacion_id>\d+)/$', views.eliminar_habitacion, name = 'eliminar_habitacion'),
    url(r'^add_habitacion_carro/(?P<habitacion_id>\d+)/$', views.add_habitacion_carro, name = 'add_habitacion_carro'),
    url(r'^eliminar_foto_habitacion/(?P<foto_habitacion_id>\d+)/$', views.eliminar_foto_habitacion, name = 'eliminar_foto_habitacion'),
    url(r'^cerrar_habitacion/(?P<habitacion_id>\d+)/$', views.cerrar_habitacion, name = 'cerrar_habitacion'),
    url(r'^abrir_habitacion/(?P<habitacion_id>\d+)/$', views.abrir_habitacion, name = 'abrir_habitacion'),

    #______________________Servicios______________________
    url(r'^fotos_servicio/(?P<servicio_id>\d+)/$', views.fotos_servicio, name = 'fotos_servicio'),
    url(r'^video_servicio/(?P<servicio_id>\d+)/$', views.video_servicio, name = 'video_servicio'),
    url(r'^eliminar_video_servicio/(?P<servicio_id>\d+)/$', views.eliminar_video_servicio, name = 'eliminar_video_servicio'),
    url(r'^administrar_servicio/(?P<servicio_id>\d+)/$', views.administrar_servicio, name = 'administrar_servicio'),
    url(r'^eliminar_foto_servicio/(?P<foto_servicio_id>\d+)/$', views.eliminar_foto_servicio, name = 'eliminar_foto_servicio'),
    url(r'^detalles_alojamiento/(?P<alojamiento_id>\d+)/$', views.detalles_alojamiento, name = 'detalles_alojamiento'),
    url(r'^administrar_reglas_precio/(?P<elemento>\w+)/(?P<id>\d+)/$', views.administrar_reglas_precio, name = 'administrar_reglas_precio'),
    url(r'^administrar_disponibilidades/(?P<elemento>\w+)/(?P<id>\d+)/$', views.administrar_disponibilidades, name = 'administrar_disponibilidades'),
    url(r'^detalles_alojamiento_por_habitacion/(?P<alojamiento_id>\d+)/$', views.detalles_alojamiento_por_habitacion, name = 'detalles_alojamiento_por_habitacion'),
    url(r'^detalles_alojamiento_completo/(?P<alojamiento_id>\d+)/$', views.detalles_alojamiento_completo, name = 'detalles_alojamiento_completo'),
    url(r'^add_favorito/(?P<servicio_id>\d+)/$', views.add_favorito, name = 'add_favorito'),
    url(r'^servicio_cerrado/(?P<servicio_id>\d+)/$', views.servicio_cerrado, name = 'servicio_cerrado'),
    url(r'^cerrar_servicio/(?P<servicio_id>\d+)/$', views.cerrar_servicio, name = 'cerrar_servicio'),
    # url(r'^checkout/(?P<reserva_id>\d+)/$', views.checkout, name = 'checkout'),
    url(r'^eliminar_reserva/(?P<reserva_id>\d+)/$', views.eliminar_reserva, name = 'eliminar_reserva'),
    url(r'^cancelar_reserva/(?P<reserva_id>\d+)/$', views.cancelar_reserva, name = 'cancelar_reserva'),
    url(r'^eliminar_favorito/(?P<servicio_id>\d+)/$', views.eliminar_favorito, name = 'eliminar_favorito'),
    url(r'^activar_regla_precio/(?P<regla_precio_id>\d+)/$', views.activar_regla_precio, name = 'activar_regla_precio'),
    url(r'^desactivar_regla_precio/(?P<regla_precio_id>\d+)/$', views.desactivar_regla_precio, name = 'desactivar_regla_precio'),
    url(r'^eliminar_regla_precio/(?P<regla_precio_id>\d+)/$', views.eliminar_regla_precio, name = 'eliminar_regla_precio'),
    url(r'^eliminar_indisponibilidad/(?P<indisponibilidad_id>\d+)/$', views.eliminar_indisponibilidad, name = 'eliminar_indisponibilidad'),
    url(r'^eliminar_reserva_sesion/(?P<timestamp>\w+)/$', views.eliminar_reserva_sesion, name = 'eliminar_reserva_sesion'),
    url(r'^mis_servicios/$', views.mis_servicios, name = 'mis_servicios'),
    url(r'^mis_favoritos/$', views.mis_favoritos, name = 'mis_favoritos'),
    url(r'^mis_reservas/$', views.mis_reservas, name = 'mis_reservas'),
    url(r'^cart/$', views.cart, name = 'cart'),
    url(r'^tabla_comisiones/$', views.tabla_comisiones, name = 'tabla_comisiones'),
    url(r'^informacion_comercial/$', views.informacion_comercial, name = 'informacion_comercial'),
    url(r'^onlinetravel/$', views.onlinetravel, name = 'onlinetravel'),
    url(r'^get_municipios_provincia/(?P<provincia_id>\d+)/$', views.get_municipios_provincia, name = 'get_municipios_provincia'),
    url(r'^abrir_servicio/(?P<servicio_id>\d+)/$', views.abrir_servicio, name = 'abrir_servicio'),

    #______________________Recorridos______________________
    url(r'^administrar_recorrido/(?P<recorrido_id>\d+)/$', views.administrar_recorrido, name = 'administrar_recorrido'),

    #______________________Taxis______________________
    url(r'^administrar_taxi/(?P<taxi_id>\d+)/$', views.administrar_taxi, name = 'administrar_taxi'),

    #______________________Packs______________________
    url(r'^administrar_pack/(?P<pack_id>\d+)/$', views.administrar_pack, name = 'administrar_pack'),

]