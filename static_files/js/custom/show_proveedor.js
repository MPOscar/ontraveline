function show_proveedor(){
    pais = $('#select_pais option:selected').text();
    if (pais == 'CUBA') {
        $('#proveedor').show()
    }
    else {
        $('#proveedor').hide()
    }
}

$(document).ready(function(){
    show_proveedor();
    $('#select_pais').change(show_proveedor);
});


