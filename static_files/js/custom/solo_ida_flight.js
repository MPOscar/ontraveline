var solo_ida_link = $('#solo_ida_link');
var ida_vuelta_link = $('#ida_vuelta_link');
var fecha_regreso = $('#fecha_regreso');

solo_ida_link.click(function(){
    fecha_regreso.hide();
});

ida_vuelta_link.click(function(){
    fecha_regreso.show();
});

