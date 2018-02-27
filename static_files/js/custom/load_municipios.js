// Obtiene una lista de listas con la forma: [[empresa_1.id, empresa_1], [empresa_2.id, empresa_2] ...]

var select_provincia = $("#select_provincia");
var select_municipio = $("#select_municipio");

function load_municipios(){

    // Caso en que el selector de provincia no tenga ninguna provincia seleccionada
    if (select_provincia.val() == ''){
        // Se vacían todas las opciones del select de municipio
        select_municipio.empty();
        // Se le añade una opcion por defecto, vacía y que muestra la palabra "Municipio"
        select_municipio.append(
            $("<option>")
            .val('')
            .html('Municipio')
        );
        // Se deshabilita el select
        select_municipio.prop('disabled', 'disabled');
    }
    // Caso que el select de provincia tenga alguna provincia seleccionada
    else {
        // Se habilita el selector de Municipio
        select_municipio.prop('disabled', false);
        // Se captura el valor que tenga cargado el selector de municipio
        var loaded = select_municipio.val();
        // Se eliminan todas las opciones del selector de municipio
        select_municipio.empty();

        $.ajax({
            // Esta vista devuelve todos los municipios relacionados con la Provincia que se establece en el selector de provincia
            url: '/servicios/get_municipios_provincia/' + select_provincia.val(),
            type: 'GET',

            success: function (json) {
                // Se obtiene la lista de Municipios relacionados con la provincia
                var municipios = json.municipios;
                // Esta variable bandera se utiliza posteriormente para identificar si alguno de los municipios  a cargar al select de municipio
                // coincide con el que tenía seleccionado antes de eliminar todas las opciones
                var current = false;
                // Con este ciclo se cargan todas las opciones de municipio relacionados con la provincia en cuestión
                for (i = 0; i < municipios.length; i++) {
                    var value = municipios[i][0];
                    // Si un municipio de la lista a cargar coincide con el municipio que tenía seleccionado antes de este proceso
                    // la variable current pasa a ser true, lo que permitirá identificar que debemos volver a cargar el select con el valor original
                    // Esto es útil si se ejecuta este código desde la vista de Modificar Alojamiento, porque así una vez se carga el select con los
                    // valores apropiados, podemos dejar seleccionado el valor que le viene indicado de la vista
                    if (loaded == value) {
                        current = true;
                    }
                    var option = municipios[i][1];
                    // Se añaden todas las copnes de los municipios devueltos por el ajax al select de municipio
                    select_municipio.append($("<option>")
                        .val(value)
                        .html(option)
                    );
                    // Una vez se han cargado los valores de municipios, si es el caso, se deja seleccionado el que estaba antes de eliminar las opciones
                    if (current == true) {
                        select_municipio.val(loaded)
                    }
                }
            }
        });



    }
}

$(document).ready(function() {
    // Si el select de Provincia no tiene seleccionada ninguna provincia, el select de Municipio debe estar sin seleccionar y deshabilitado
    // Esta validación se realiza al cargar la página y cada vez que hay un cambio en el select de provincia
    load_municipios();
    select_provincia.change(load_municipios);

});