function verificado_proveedor() {
    obj_id = $(this).attr("id");
    $.ajax({
        url : "../verificado_proveedor/"+obj_id,
        type : "GET",

        success : function(json) {
            if (json.verificado_proveedor){
                if (json.proveedor) {
                    $('span.verificado_proveedor.'+obj_id).html('Verificado').attr("class", "label label-sm label-success verificado_proveedor "+obj_id);
                }
                else {
                    $('span.verificado_proveedor.'+obj_id).hide()
                }
            }
            else {
                if (json.proveedor) {
                    $('span.verificado_proveedor.'+obj_id).html('No Verificado').attr("class", "label label-sm label-warning verificado_proveedor "+obj_id);
                }
                else {
                    $('span.verificado_proveedor.'+obj_id).hide()
                }
            }
        }
    });
}

$('.verificado_proveedor').click(verificado_proveedor);