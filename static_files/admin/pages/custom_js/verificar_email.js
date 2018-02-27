function verificar_email() {
    obj_id = $(this).attr("id");
    $.ajax({
        url : "../verificar_email/"+obj_id,
        type : "GET",

        success : function(json) {
            if (json.verificado_email){
                $('span.verificar_email.'+obj_id).html('Verificado').attr("class", "label label-sm label-success verificar_email "+obj_id);
            }
            else {
                $('span.verificar_email.'+obj_id).html('Pendiente').attr("class", "label label-sm label-danger verificar_email "+obj_id);
            }
        }
    });
}

$('.verificar_email').click(verificar_email);
