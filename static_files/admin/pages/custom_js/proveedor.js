function proveedor() {
    obj_id = $(this).attr("id");
    $.ajax({
        url : "../proveedor/"+obj_id,
        type : "GET",

        success : function(json) {
            if (json.proveedor){
                $('span.proveedor.'+obj_id).html('Proveedor').attr("class", "label label-sm label-success proveedor "+obj_id);
                $('span.verificado_proveedor.'+obj_id).html('No Verificado').attr("class", "label label-sm label-warning verificado_proveedor "+obj_id).show();
            }
            else {
                $('span.proveedor.'+obj_id).html('No Proveedor').attr("class", "label label-sm label-info proveedor "+obj_id);
                $('span.verificado_proveedor.'+obj_id).hide();
            }
        }
    });
}

$('.proveedor').click(proveedor);