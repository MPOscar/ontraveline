function activar() {
    obj_id = $(this).attr("id");
    $.ajax({
        url : "../activar_usuario/"+obj_id,
        type : "GET",

        success : function(json) {
            if (json.activado){
                // activado es un diccionario que retorna de la vista
                $('span.activar.'+obj_id).html('Activo').attr("class", "label label-sm label-success activar "+obj_id);
                // Lo anterior se lee como "Todos los elementos de etiqueta span, que incluyan "activar" en la class y que el id sea obj_id
            }
            else {
                $('span.activar.'+obj_id).html('Inactivo').attr("class", "label label-sm label-danger activar "+obj_id);
            }
        }
    });
}

$('.activar').click(activar);
