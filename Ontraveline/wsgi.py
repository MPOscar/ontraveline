"""
WSGI config for Ontraveline project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os, sys
from django.core.wsgi import get_wsgi_application

#------ CONFIGURACION WSGI PARA APACHE ------#
sys.path.append(os.getcwd())
sys.path.append('/opt/proyectos/Ontraveline/')
# Referencia (en Python) desde el path anterior al fichero settings.py
# Es importante hacerlo así, si hay varias instancias corriendo (en lugar de setdefaul

os.environ['DJANGO_SETTINGS_MODULE'] = 'Ontraveline.settings'
#os.environ.setdefault(“DJANGO_SETTINGS_MODULE”, “Ontraveline.settings”)

#prevenimos UnicodeEncodeError
os.environ.setdefault('LANG', 'en_US.UTF-8')
os.environ.setdefault('LC_ALL', 'en_US.UTF-8')

#activamos nuestro virtualenv
# activate_this = '/opt/virenvs/ontraveline/bin/activate_this.py'
# exec(activate_this, dict(__file__ = activate_this))

#obtenemos la aplicación
application = get_wsgi_application()
#------ FIN CONFIGURACION PARA APACHE ------#
