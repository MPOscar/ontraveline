function verificar_movil() {
    obj_id = $(this).attr("id");
    $.ajax({
        url : "../verificar_movil/"+obj_id,
        type : "GET",

        success : function(json) {
            if (json.verificado_movil){
                $('span.verificar_movil.'+obj_id).html('Verificado').attr("class", "label label-sm label-success verificar_movil "+obj_id);
            }
            else {
                $('span.verificar_movil.'+obj_id).html('Pendiente').attr("class", "label label-sm label-danger verificar_movil "+obj_id);
            }
        }
    });
}

$('.verificar_movil').click(verificar_movil);
