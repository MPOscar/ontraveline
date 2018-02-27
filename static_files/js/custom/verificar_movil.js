function check_code() {
    var input_code = $('#codigo_sms_verificar');
    var code = input_code.val();
    var user_id = input_code.attr('name');

    if (input_code.val().length > 5) {
        $.ajax({
            url : "/twilio/check_sms_code/"+code+"/"+user_id,
            type : "GET",

            success : function(json) {
                if (json.valido){
                    $('#codigo_sms_verificar').attr('disabled','disabled');
                    window.location.reload();
                    // $('input#codigo_sms_verificar').hide();
                    // $('input#estado_movil').hide();
                    // $('span#estado_movil').show();
                }
            }
        });
    }
}

$(document).ready(function() {
    // Cuenta la cantidad de caracteres en el input cada vez que se introduce un nuevo valor
    $('div#validando').hide();
    $('#codigo_sms_verificar').keyup(check_code);
});
