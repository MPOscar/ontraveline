1 - CONFIGURACIÓN DE WKHTMLTOPDF EN CENTOS
=======================================================================================
# Instalacion de la libreria para Python
pip install wkhtmltopdf

# Descarga y manipulacion de los ficheros necesarios
sudo wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
sudo unxz wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
sudo tar -xvf wkhtmltox-0.12.4_linux-generic-amd64.tar

# Ubicacion en el directorio donde lo vamos a usar
sudo mv wkhtmltox/bin/* /usr/local/bin/

# limpiar los archivos descargados
sudo rm -rf wkhtmltox
sudo rm -f wkhtmltox-0.12.4_linux-generic-amd64.tar

Definir WHH2P_PATH = '/usr/local/bin/wkhtmltopdf'
=======================================================================================


2 - CAMBIOS EN LA CODIFICACION DE LA BD
=======================================================================================
La BD que se está usando en Desarrollo ha sido modificada la codificación para poder guardar ciertos caracteres.
Realizar esta modificación en las demás Bases de Datos (Producción):
a) ALTER DATABASE ontraveline CHARACTER SET utf8 COLLATE utf8_unicode_ci;
b) ALTER TABLE ontraveline.website_aeropuerto_mundo CONVERT TO CHARACTER SET utf8 COLLATE utf8_unicode_ci;
De manera general, se puede aplicar la configuración para alguna otra tabla que de problemas al guardar algunos tipos de caracteres
especialmente cuando tratemos con nombres de ciudades del mundo, etc.
=======================================================================================

3 - PRIMEROS PASOS
=======================================================================================
3.1 - Crear los ficheros settings__dev.py y settings__prod.py
3.2 - Si el entorno es de producción copiar settings__prod__gen.py para settings__prod.py y rellenar la información necesaria
O lo contrario en settings__dev si el entorno es desarrollo


4 - POBLAR LA BD CON LOS DATOS NECESARIOS
=======================================================================================
4.1 - Acceder por SSH al servidor de desarrollo, actualizar desde el repositorio web y activar el entorno virtual del proyecto
4.2 - Migrar (python manage.py migrate)
4.3 - Poblar la BD con los datos primarios:
    4.3.1 - python manage.py shell
    4.3.2 - >> from support import populate
    4.3.3 - >> populate.populate_all() (Aquí esperar a que se escriban todos los datos. Puede tardar un minuto o más)


5 - CREACIÓN DE LOS MODELOS DE APLICACIONES PARA APIs
=======================================================================================
5.1 - Paypal: Consultar las Apps de la cuenta business de Paypal que se vaya a utilizar (https://developer.paypal.com) y crear los dos modelos (sandbox y live) con las credenciales de la cuenta
5.2 - Twitter:
5.3 - Instagram
5.4 - LinkedIn
5.5 - Google