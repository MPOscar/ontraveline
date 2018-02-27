// Obtiene una lista de listas con la forma: [[empresa_1.id, empresa_1], [empresa_2.id, empresa_2] ...]

var select_pais = $("#select_pais");
var select_provincia = $("#select_provincia");

function load_provincias(){

    // Caso en que el selector de pais no tenga ninguno seleccionado
    if (select_pais.val() == ''){
        // Se vacían todas las opciones del select de provincia
        select_provincia.empty();
        // Se le añade una opcion por defecto, vacía y que muestra la palabra "Provincia"
        select_provincia.append(
            $("<option>")
            .val('')
            .html('Provincia')
        );
        // Se deshabilita el select
        select_provincia.prop('disabled', 'disabled');
    }
    // Caso que el select de país tenga algún país seleccionado
    else {
        // Se habilita el selector de Provincia
        select_provincia.prop('disabled', false);
        // Se captura el valor que tenga cargado el selector de provincia
        var loaded = select_provincia.val();
        // Se eliminan todas las opciones del selector de provincia
        select_provincia.empty();

        $.ajax({
            // Esta vista devuelve todas las provincias relacionados con el país que se establece en el selector de país
            url: '/usuarios/get_provincias_pais/' + select_pais.val(),
            type: 'GET',

            success: function (json) {
                // Se obtiene la lista de Provincias relacionadas con el país
                var provincias = json.provincias;
                // Esta variable bandera se utiliza posteriormente para identificar si alguna de las provincias  a cargar al select
                // coincide con la que tenía seleccionada antes de eliminar todas las opciones
                var current = false;
                // Con este ciclo se cargan todas las opciones de provincias relacionados con el país en cuestión
                for (i = 0; i < provincias.length; i++) {
                    var value = provincias[i][0];
                    // Si una provincia de la lista a cargar coincide con la provincia que tenía seleccionada antes de este proceso
                    // la variable current pasa a ser true, lo que permitirá identificar que debemos volver a cargar el select con el valor original
                    if (loaded == value) {
                        current = true;
                    }
                    var option = provincias[i][1];
                    // Se añaden todas las opciones de las provincias devueltas por el ajax al select de provincia
                    select_provincia.append($("<option>")
                        .val(value)
                        .html(option)
                    );
                    // Una vez se han cargado los valores de provincias, si es el caso, se deja seleccionada la que estaba antes de eliminar las opciones
                    if (current == true) {
                        select_provincia.val(loaded)
                    }
                }
            }
        });



    }
}

$(document).ready(function() {
    // Si el select de Provincia no tiene seleccionada ninguna provincia, el select de Municipio debe estar sin seleccionar y deshabilitado
    // Esta validación se realiza al cargar la página y cada vez que hay un cambio en el select de provincia
    load_provincias();
    select_pais.change(load_provincias);

});