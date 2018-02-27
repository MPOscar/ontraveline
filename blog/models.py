from django.db import models
from django.db.models import Count
from servicios.models import Foto_Servicio
import os, shutil

# FOTOS DE SERVICIOS
def posts_photos_directory(instance, filename):
    return 'usuarios/{0}/posts_photos/{1}/{2}'.format(
        instance.post.autor.id,
        instance.post.id,
        filename,
    )

class Categoria(models.Model):
    nombre = models.CharField('Nombre', max_length = 128, blank = False, null = False, unique = True)
    descripcion = models.CharField('Descripción', max_length = 255, blank = False, null = False, unique = False)

    @classmethod
    def nueva_categoria(cls, nombre, descripcion):
        # Comprobamos que no exista ninguna categoría con el mismo nombre
        if cls.objects.filter(nombre = nombre):
            message = 'Ya existe una categoría llamada %s' %(nombre)
            print(message)
            return {
                'message': message,
            }
        else:
            n_categoria = cls.objects.create(
                nombre = nombre,
                descripcion = descripcion,
            )
            print('Se ha creado correctamente la Categoría %s' %(nombre))
            return n_categoria

    def modificar_categoria(self, nombre, descripcion):
        # Se comprueba que no haya ninguna categoría con el nombre nuevo que se le quiere poner a la categoría a modificar
        if self.objects.filter(nombre = nombre):
            message = 'Ya existe una categoría llamada %s' %(nombre)
            print(message)
            return {
                'message': message,
            }
        else:
            self.nombre = nombre
            self.descripcion = descripcion
            self.save()
            return self

    def eliminar_categoria(self):
        self.delete()
        print('Se ha eliminado correctamente la categoria')

    class Meta:
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre

class Post(models.Model):
    titulo = models.CharField('Título', max_length = 255, blank = False, null = False, unique = True)
    descripcion = models.CharField('Descripción', max_length = 1024, blank = False, null = False)
    texto = models.TextField('Texto', max_length = 32768, blank = False, null = False)
    categorias = models.ManyToManyField(Categoria, blank = True)
    fecha_post = models.DateTimeField('Fecha de Creación', blank = False, null = False, unique = False, auto_now_add = True)
    autor = models.ForeignKey('usuarios.Usuario', blank = False, null = False, unique = False, on_delete = models.CASCADE)

    @classmethod
    # Devuelve un listado de Posts cuyos mes y año de publicación coincidan con los parámetros que se indican en los argumentos
    def get_posts_mes(cls, year, month):
        posts_mes = []
        for post in cls.objects.order_by('fecha_post'):
            if post.fecha_post.year == year and post.fecha_post.month == month:
                posts_mes.append(post)
        return posts_mes

    @classmethod
    # Devuelve un listado de Posts ordenados por cantidad de veces que han sido vistos
    def get_posts_populares(cls, cantidad = 5):
        return cls.objects.annotate(vistas = Count('vista_post')).order_by('-vistas')[:cantidad]

    @classmethod
    def nuevo_post(cls, titulo, descripcion, texto, categorias, autor):
        # Comprobamos que no exista ninguna categoría con el mismo titulo
        if cls.objects.filter(titulo = titulo):
            message = 'Ya existe un Post llamado %s' % (titulo)
            print(message)
            return {
                'message': message,
            }
        else:
            n_post = cls.objects.create(
                titulo = titulo,
                descripcion = descripcion,
                texto = texto,
                autor = autor,
            )
            for categoria in categorias:
                n_post.categorias.add(categoria)
            n_post.save()
            print('Se ha creado correctamente el Post %s' % (titulo))
            return n_post

    def modificar_post(self, titulo, descripcion, texto, categorias, autor):
        # Se comprueba que no haya ningún Post con el título nuevo que se le quiere poner al Post sin modificar
        if self.objects.filter(titulo = titulo):
            message = 'Ya existe un Post titulado %s' % (titulo)
            print(message)
            return {
                'message': message,
            }
        else:
            self.titulo = titulo
            self.descripcion = descripcion
            self.texto = texto
            self.autor = autor

            # Si alguna de las categorías que se le asocian al Post no las tiene, se le añade
            for categoria in categorias:
                if categoria not in self.categorias:
                    self.categorias.add(categoria)
            # Así mismo, si hay alguna categoría asociada al Post que no esté en la lista que se pasa, se elimina
            for categoria in list(self.categorias):
                if not categoria in categorias:
                    self.categorias.remove(categoria)

            # Se guardan los cambios y se devuelve el objeto modificado
            self.save()
            return self

    def eliminar_categoria(self):
        self.delete()
        print('Se ha eliminado correctamente la categoria')

    def eliminar_post(self):
        fotos_post = self.foto_post_set.all()
        for foto_post in fotos_post:
            foto_post.eliminar_foto_post()

    class Meta:
        verbose_name_plural = 'Posts'

    def __str__(self):
        return self.titulo

class Vista_Post(models.Model):
    post = models.ForeignKey(Post, blank = False, null = False, unique = False, on_delete = models.DO_NOTHING)
    usuario = models.ForeignKey('usuarios.Usuario', blank = False, null = False, unique = False, on_delete = models.CASCADE)
    fecha_vista = models.DateTimeField('Fecha de la Vista', blank = False, null = False, unique = False, auto_now_add = True)

    @classmethod
    def nueva_vista_post(cls, post, usuario, fecha_vista):
        # Una vista es obviada para un usuario en una publicación el mismo día
        if not cls.objects.filter(
            post = post,
            usuario = usuario,
            fecha_vista__year = fecha_vista.year,
            fecha_vista__month = fecha_vista.month,
            fecha_vista__day = fecha_vista.day,
        ):
            n_vista_post = cls.objects.create(
                post = post,
                usuario = usuario,
                fecha_vista = fecha_vista,
            )
            print('Se ha creado correctamente la vista al Post %s por el usuario %s' %(post, usuario))
            return n_vista_post
        else:
            return None

    def eliminar_vista_post(self):
        self.delete()
        print('Se ha eliminado correctamente la vista al Post')

    class Meta:
        verbose_name_plural = 'Vistas Posts'

    def __str__(self):
        return 'Vista de %s el %s por %s' %(self.post, self.fecha_vista, self.usuario)

class Comentario_Post(models.Model):
    post = models.ForeignKey(Post, blank = False, null = False, unique = False, on_delete = models.DO_NOTHING)
    usuario = models.ForeignKey('usuarios.Usuario', blank = False, null = False, unique = False, on_delete = models.CASCADE)
    comentario = models.TextField('Comentario', max_length = 32768, blank = False, null = False)
    fecha_comentario = models.DateTimeField('Fecha del Comentario', blank = False, null = False, unique = False, auto_now_add = True)
    en_respuesta_a = models.IntegerField('En respuesta a (ID del Comentario)', blank = True, null = True, unique = False)
    editado = models.BooleanField('Editado', blank = True, default = False)

    def marcar_como_editado(self):
        self.editado = True
        self.save()
        print('Se ha marcado correctamente el %s como "Editado"' %(self))

    @classmethod
    def nuevo_comentario_post(cls, post, usuario, comentario, fecha_comentario, en_respuesta_a):
        n_comentario_post = cls.objects.create(
            post = post,
            usuario = usuario,
            comentario = comentario,
            fecha_comentario = fecha_comentario,
            en_respuesta_a = en_respuesta_a,
        )
        print('Se ha creado correctamente el comentario de %s al Post %s' %(usuario, post))
        return n_comentario_post

    def eliminar(self):
        # Eliminar un Comentario eliminará todos los Comentarios que se hayan hecho en respuesta al primero
        for comentario_respuesta in self.objects.filter(en_respuesta_a = self.id):
            comentario_respuesta.delete()
            print('Se ha eliminado correctamente un comentario en respuesta al que se desea eliminar')
        # Una vez eliminados todos los comentarios respuesta, se elimina el comentario original
        self.delete()
        print('Se ha eliminado correctamente el comentario')

    @classmethod
    # Devuelve una lista de Comentarios de más reciente a más viejo, limitados a la cantidad indicada en el parámetro "cantidad"
    def get_ultimos_comentarios(cls, cantidad):
        return cls.objects.order_by('-fecha_comentario')[:cantidad]

    class Meta:
        verbose_name_plural = 'Comentarios Posts'

    def __str__(self):
        return 'Comentario al Post %s el %s por %s' %(self.post, self.fecha_comentario, self.usuario)

class Like_Post(models.Model):
    post = models.ForeignKey(Post, blank = False, null = False, unique = False, on_delete = models.DO_NOTHING)
    usuario = models.ForeignKey('usuarios.Usuario', blank = False, null = False, unique = False, on_delete = models.CASCADE)
    fecha_like = models.DateTimeField('Fecha del Like', blank = False, null = False, unique = False, auto_now_add = True)

    class Meta:
        verbose_name_plural = 'Likes'

    def __str__(self):
        return 'Like al post %s el %s por %s' %(self.post, self.fecha_like, self.usuario)

class Video_Post(models.Model):
    titulo = models.CharField('Título', max_length = 64, blank = True, null = True, unique = False)
    descripcion = models.CharField('Descripción', max_length = 256, blank = True, null = True, unique = False)
    url = models.URLField('URL', max_length = 128, blank = False, null = False, unique = True)
    post = models.ForeignKey(Post, blank = False, null = False, unique = False, on_delete = models.CASCADE)

    @classmethod
    def nuevo_video_post(cls, titulo, descripcion, url, post):
        # Comprobamos que no exista ningún video almacenado con la misma url asociado al mismo post(se trataría del mismo)
        # La url suele estar en la forma: https://www.youtube.com/embed/<CODIGO-VIDEO>
        if cls.objects.filter(url = url, post = post):
            message = 'Ya existe un video asociado al post "%s" con url: "%s"' %(post, url)
            print(message)
            return {
                'message': message,
            }
        else:
            n_video_post = cls.objects.create(
                titulo = titulo,
                descripcion = descripcion,
                url = url,
                post = post,
            )
            print('Se ha creado correctamente el video %s asociado al post %s' %(titulo, post))
            return n_video_post

    class Meta:
        verbose_name_plural = 'Videos de Posts'

    def __str__(self):
        return 'Video del Post %s' %(self.post)

class Foto_Post(models.Model):
    post = models.ForeignKey(Post, blank = False, null = False, unique = False, on_delete = models.CASCADE)
    foto = models.ImageField('Foto Servicio', upload_to = posts_photos_directory, blank = True, null = True)

    @classmethod
    def nueva_foto_post(cls, post, foto):
        n_foto_post = cls.objects.create(
            post = post,
            foto = foto,
        )

        # Procesar la imagen almacenada
        img_url = '%s/%s' %(os.getcwd(), n_foto_post.foto.url)
        Foto_Servicio.procesar_foto_post(img_url)

        # Siempre que se crea una nueva foto de Post se le añade a la Galería del Blog, si hay alguna en uso
        if Galeria_Blog.objects.filter(en_uso = True):
            galeria_blog = Galeria_Blog.objects.get(en_uso = True)
            galeria_blog.annadir_foto_galeria(n_foto_post)

        return n_foto_post

    def eliminar_foto_post(self):
        # Siempre que se elimine una foto de un Post se eliminará también de la Galería del Blog
        if Galeria_Blog.objects.filter(en_uso = True):
            galeria_blog = Galeria_Blog.objects.get(en_uso = True)
            if self in galeria_blog.fotos_posts.all():
                galeria_blog.eliminar_foto_galeria(self)

        # Se elimina el archivo de imagen relacionado con la foto del Post
        self.foto.delete()
        # Antes de eliminar el Objeto de Foto, debe comprobarse si es la última foto existente del Post.
        # Si es así, se debe eliminar el directorio que contenía las fotos
        posts_photos_path = '%s/media/usuarios/%s/posts_photos/%s' %(os.getcwd(), self.post.autor.id, self.post.id)
        if not os.listdir(posts_photos_path):
            shutil.rmtree(posts_photos_path)
        # Si no queda ningún Post con imágenes, se elimina también el directorio "posts_photos"
        posts_photos_path = '%s/media/usuarios/%s/posts_photos' %(os.getcwd(), self.post.autor.id)
        if not os.listdir(posts_photos_path):
            shutil.rmtree(posts_photos_path)

        self.delete()

class Galeria_Blog(models.Model):
    fotos_posts = models.ManyToManyField(Foto_Post, blank = True)
    en_uso = models.BooleanField('En uso', blank = True, default = True)

    @classmethod
    def nueva_galeria_blog(cls, fotos_posts):
        # Se verifica que no haya ninguna Galería de Blog en Uso y si es así, la nueva será creada con "en_uso" = False
        if cls.objects.filter(en_uso = True):
            en_uso = False
        else:
            en_uso = True
        n_galeria_blog = cls.objects.create(
            en_uso = en_uso,
        )
        print('Se ha creado correctamente la Galería del Blog')

        # Luego de creada la Galería, se le asocian las fotos que se hayan indicado (si es el caso)
        for foto_post in fotos_posts:
            n_galeria_blog.fotos_posts.add(foto_post)
            print('Una Foto del Post %s ha sido añadida a la Galería del Blog' %(foto_post.post))
        n_galeria_blog.save()

    def modificar_galeria(self, fotos_posts):
        # Si alguna de las fotos que se le asocian a la Galeria no las tiene, se le añade
        for foto in fotos_posts:
            if foto not in self.fotos_posts:
                self.fotos_posts.add(foto)
        # Así mismo, si hay alguna categoría asociada al Post que no esté en la lista que se pasa, se elimina
        for foto in list(self.fotos_posts):
            if not foto in fotos_posts:
                self.fotos_posts.remove(foto)

    def annadir_foto_galeria(self, foto_post):
        self.fotos_posts.add(foto_post)
        self.save()
        print('Se ha añadido correctamente la foto a la Galería')
        return self

    def eliminar_foto_galeria(self, foto_post):
        self.fotos_posts.remove(foto_post)
        self.save()
        print('Se ha eliminado correctamente la foto de la Galería')
        return self

    def eliminar_galeria_blog(self):
        self.delete()
        print('Se ha eliminado correctamente la Galería del Blog')

    class Meta:
        verbose_name_plural = 'Galerías del Blog'

    def __str__(self):
        return 'Galería del Blog'

