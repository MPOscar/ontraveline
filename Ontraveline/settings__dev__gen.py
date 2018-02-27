import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

ALLOWED_HOSTS = ['XXXX.XXXX.XXXX.XXXX', 'localhost', '[::1]']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",},
        'NAME': 'xxxxxxxxxxxxx',
        'USER': 'xxxxxxxxxxxxx',
        'PASSWORD': 'xxxxxxxxxxxx',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Esta es la ruta donde se deben buscar los ficheros estáticos para llevarlos a STATIC_ROOT cuando se hace collectstatic
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'xxxxxxxxxxxxx'),
)

# Esta es la ruta donde el servidor debe buscar los ficheros estáticos a servir
STATIC_ROOT = os.path.join(BASE_DIR, 'xxxxxxxxxxxxx')

# Esta es la ruta a donde se suben los archivos de los usuarios y demás medias
MEDIA_ROOT = os.path.join(BASE_DIR, 'xxxxxxxxxxxxx')