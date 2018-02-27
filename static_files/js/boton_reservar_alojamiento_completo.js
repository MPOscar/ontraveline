window.onload = (function(){
// El objetivo es mantener el botón de reservar desactivado mientras no haya al menos un adulto indicado por el usuario
// Se inicializa el botón desactivado
$("#reservar").attr("class","btn btn-primary btn-block btn-lg disabled");

try{
    $("#ninnos").on('keyup', function(){
        // Se determina la cantidad de niños introducidos en el formulario
        var ninnos = $(this).val();
        var adultos = $("#adultos").val();
        if (ninnos.length > 0) {
            if (ninnos > 0) {
                if (adultos > 0) {
                    $("#reservar").attr("class","btn btn-primary btn-block btn-lg");
                }
                else {
                    $("#reservar").attr("class","btn btn-primary btn-block btn-lg disabled");
                }
            }
            else {
                if (adultos > 0) {
                    $("#reservar").attr("class","btn btn-primary btn-block btn-lg");
                }
                else {
                    $("#reservar").attr("class","btn btn-primary btn-block btn-lg disabled");
                }
            }
        }
        else {
            if (adultos.length > 0) {
                $("#reservar").attr("class","btn btn-primary btn-block btn-lg");
            }
            else {
                $("#reservar").attr("class","btn btn-primary btn-block btn-lg disabled");
            }
        }
    }).keyup();

    $("#adultos").on('keyup', function(){
        // Se determina la cantidad de adultos introducidos en el formulario
        var adultos = $(this).val();
        if (adultos.length > 0) {
            if (adultos > 0) {
                $("#reservar").attr("class","btn btn-primary btn-block btn-lg");
            }
            else {
                $("#reservar").attr("class","btn btn-primary btn-block btn-lg disabled");
            }
        }
        else {
            // Si el input está vacío, deshabilitamos el botón de reserva
            $("#reservar").attr("class","btn btn-primary btn-block btn-lg disabled");
        }
    }).keyup();

}catch(e){}});