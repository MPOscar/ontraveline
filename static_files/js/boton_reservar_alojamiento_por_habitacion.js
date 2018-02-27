window.onload = (function() {
// El objetivo es mantener el botón de reservar desactivado mientras no haya al menos un adulto indicado por el usuario
// Se inicializa el botón desactivado
$("#reservar").attr("class","btn btn-primary btn-lg btn-block btn-lg disabled");

try{
    $(".adultos").on('keyup', function(){
        // Se determina la cantidad de adultos introducidos en el formulario
        var adultos = $(this).val();
        if (adultos.length > 0) {
            $("#reservar").attr("class","btn btn-primary btn-block btn-lg");
        }
        else {
            // Si el input está vacío, deshabilitamos el botón de reserva
            $("#reservar").attr("class","btn btn-primary btn-block btn-lg disabled");
        }
    }).keyup();
}catch(e){}});