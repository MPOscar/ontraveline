function cambiar_uso_twilio_number() {
    obj_id = $(this).attr("id");
    $.ajax({
        url : "../cambiar_uso_twilio_number/"+obj_id,
        type : "GET",

        success : function(json) {
            if (json.en_uso){
                $('span.cambiar_uso_twilio_number').html('Usar').attr("class", "label label-sm label-warning cambiar_uso_twilio_number "+obj_id);
                $('span.cambiar_uso_twilio_number.'+obj_id).html('En uso').attr("class", "label label-sm label-success cambiar_uso_twilio_number "+obj_id);
            }
            else {
                $('span.cambiar_uso_twilio_number.'+obj_id).html('Usar').attr("class", "label label-sm label-warning cambiar_uso_twilio_number "+obj_id);
            }
        }
    });
}

$('.cambiar_uso_twilio_number').click(cambiar_uso_twilio_number);