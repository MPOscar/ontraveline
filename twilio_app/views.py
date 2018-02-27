from django.shortcuts import render, HttpResponse
from twilio_app.models import Codigo_Verificacion
from usuarios.models import Usuario
from django.contrib.auth.decorators import login_required
import json

# Create your views here.
@login_required
def check_sms_code(request, code, usuario_id):
    # Obtenemos el Objeto usuario para pasar el método que comprueba la validez del código analizado
    usuario = Usuario.objects.get(id = usuario_id)

    valido = Codigo_Verificacion.validate_codigo_usuario(
        codigo = code,
        usuario = usuario,
    )

    resultado = {
        'valido': valido,
    }

    return HttpResponse(json.dumps(resultado), content_type = 'application/json')