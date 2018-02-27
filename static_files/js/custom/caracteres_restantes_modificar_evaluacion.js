var textarea_modificar_evaluacion = $('textarea#modificar_evaluacion');
var span_caracteres_restantes_modificar_evaluacion = $('span#caracteres_restantes_modificar_evaluacion');
var button_confirmar_modificar_evaluacion = $('button#confirmar_modificar_evaluacion');
var caracteres_requeridos = 100;

function validar_caracteres_restantes(){
    var caracteres_escritos = textarea_modificar_evaluacion.val().length;
    var caracteres_restantes = caracteres_requeridos - caracteres_escritos;

    if (caracteres_restantes > -1) {
        span_caracteres_restantes_modificar_evaluacion.text('  ' + caracteres_restantes);
    }
    else {
        span_caracteres_restantes_modificar_evaluacion.text('  0');
    }

    if (caracteres_restantes > 0) {
        button_confirmar_modificar_evaluacion.prop("disabled",true);
    }
    else {
        button_confirmar_modificar_evaluacion.prop("disabled",false);
    }
}

$(document).ready(function() {
    // Se vacía el Textarea
    // textarea_modificar_evaluacion.val(textarea_modificar_evaluacion.val().replace('                        ', ''));

    // Se inicializa el formulario y los valores según lo que hay escrito al principio (nada)
    validar_caracteres_restantes();

    // Cada vez que presione y suete una tecla, se analiza la cantidad de caracteres y se habilita o no el submit del formulario
    // Siempre se muestra la información de cuántos caracteres faltan para que se habilite el submit
    textarea_modificar_evaluacion.keyup(validar_caracteres_restantes);
});