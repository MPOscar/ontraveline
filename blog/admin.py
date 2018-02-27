from django.contrib import admin
from blog.models import Post, Categoria, Comentario_Post, Foto_Post, Like_Post, Video_Post, Vista_Post, Galeria_Blog

# Register your models here.
admin.site.register(Post)
admin.site.register(Categoria)
admin.site.register(Comentario_Post)
admin.site.register(Foto_Post)
admin.site.register(Like_Post)
admin.site.register(Video_Post)
admin.site.register(Vista_Post)
admin.site.register(Galeria_Blog)