from django.conf.urls import url
from pagos import views

urlpatterns = [
    url(r'^transaccion_exitosa/$', views.transaccion_exitosa, name = 'transaccion_exitosa'),
    url(r'^transaccion_error/$', views.transaccion_error, name = 'transaccion_error'),
    url(r'^reserva_confirmada/(?P<pago_id>\d+)/$', views.reserva_confirmada, name = 'reserva_confirmada'),

    # url(r'^single/$', views.view, name = 'single'),
    # url(r'^single_&_number/(?P<number>\d+)/$', views.view, name = 'single_&_number'),
    # url(r'^single_&_word/(?P<word>\w+)/$', views.view, name = 'single_&_word'),
]