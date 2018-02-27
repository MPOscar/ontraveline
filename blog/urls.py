from django.conf.urls import url
from blog import views

urlpatterns = [
    url(r'^index/$', views.blog, name = 'index'),
    url(r'^galeria_blog/$', views.galeria_blog, name = 'galeria_blog'),
    url(r'^post/(?P<post_id>\w+)/$', views.blog, name = 'post'),
    url(r'^categoria/(?P<categoria_id>\w+)/$', views.blog, name = 'categoria'),
    # url(r'^single_&_word/(?P<word>\w+)/$', views.view, name = 'single_&_word'),
]