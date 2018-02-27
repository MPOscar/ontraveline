var textarea_motivo_cancelacion = $('textarea#motivo_cancelacion');
var span_caracteres_restantes = $('span#caracteres_restantes');
var button_confirmar_cancelacion = $('button#confirmar_cancelacion');
var caracteres_requeridos = 100;

function validar_caracteres_restantes(){
    var caracteres_escritos = textarea_motivo_cancelacion.val().length;
    var caracteres_restantes = caracteres_requeridos - caracteres_escritos;

    if (caracteres_restantes > -1) {
        span_caracteres_restantes.text('  ' + caracteres_restantes);
    }
    else {
        span_caracteres_restantes.text('  0');
    }

    if (caracteres_restantes > 0) {
        button_confirmar_cancelacion.prop("disabled",true);
    }
    else {
        button_confirmar_cancelacion.prop("disabled",false);
    }
}

$(document).ready(function() {
    // Se vacía el Textarea
    textarea_motivo_cancelacion.val('');

    // Se inicializa el formulario y los valores según lo que hay escrito al principio (nada)
    validar_caracteres_restantes();

    // Cada vez que presione y suete una tecla, se analiza la cantidad de caracteres y se habilita o no el submit del formulario
    // Siempre se muestra la información de cuántos caracteres faltan para que se habilite el submit
    textarea_motivo_cancelacion.keyup(validar_caracteres_restantes);
});