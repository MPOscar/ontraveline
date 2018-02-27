from django.shortcuts import render
from servicios.views import custom_context
from blog.models import Post, Categoria, Comentario_Post, Galeria_Blog
from blog.forms import Blog_Form
import datetime

# Create your views here.
def blog(request, categoria_id = None, post_id = None):

    posts = Post.objects.order_by('fecha_post')
    post, categoria = None, None

    # Validamos el escenario de búsqueda a través del buscador del blog
    if request.method == 'POST':
        form = Blog_Form(request.POST)
        if form.is_valid():
            # Obtenemos el criterio de búsqueda del usuario
            buscar = form.cleaned_data['search']

            # Obtenemos una de los Posts que responden al criterio de búsqueda
            posts = Post.objects.filter(titulo__contains = buscar)

    else:
        form = Blog_Form()
        if post_id:
            posts = posts.filter(id = post_id)
            post = posts[0]
        if categoria_id:
            categoria = Categoria.objects.get(id = categoria_id)
            p = []
            for i in posts:
                if categoria in i.categorias.all():
                    p.append(i)
            posts = p

    # Categorías
    categorias = Categoria.objects.order_by('nombre')

    # Posts populares
    posts_populares = Post.get_posts_populares(cantidad = 4)

    # Últimos comentarios
    ultimos_comentarios = Comentario_Post.get_ultimos_comentarios(cantidad = 4)

    # Meses para otras publicaciones
    today = datetime.date.today()
    month = today.month
    year = today.year
    fechas_otras_publicaciones = []
    for i in range(10):
        if month > 1:
            month -= 1
        else:
            year -= 1
            month = 12
        if Post.get_posts_mes(year, month):
            fechas_otras_publicaciones.append([year, month])

    # Galería del Blog
    if Galeria_Blog.objects.filter(en_uso = True):
        galeria_blog = Galeria_Blog.objects.get(en_uso = True)
    else:
        galeria_blog = []

    context = {
        'posts': posts,
        'categorias': categorias,
        'posts_populares': posts_populares,
        'ultimos_comentarios': ultimos_comentarios,
        'fechas_otras_publicaciones': fechas_otras_publicaciones,
        'galeria_blog': galeria_blog,
        'post_': post,
        'categoria_': categoria,
        'form': form,
    }
    context.update(custom_context(request))
    return render(request, 'blog/index.html', context)

def galeria_blog(request):
    galeria = Galeria_Blog.objects.get(en_uso = True)
    context = {
        'galeria': galeria,
    }
    context.update(custom_context(request))
    return render(request, 'blog/galeria.html', context)