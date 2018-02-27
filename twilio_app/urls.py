from django.conf.urls import url
from twilio_app import views

urlpatterns = [
    url(r'^check_sms_code/(?P<code>\d+)/(?P<usuario_id>\d+)/$', views.check_sms_code, name = 'check_sms_code'),
]