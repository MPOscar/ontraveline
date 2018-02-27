var habitaciones = $("input#habitaciones");
var alojamientos = $("input#alojamientos");
var lugar = $("#lugar");

var options = {
	//Origen de los Datos
	url: function() {
		return "../get_destinos_provincias_municipios_alojamientos";
	},

	// Mostramos el elemento del diccionario con key = 'name'
	getValue: "name",

	// Alguna configuración de la lista
	list: {
		match: {enabled: true}, // Con esto, se activa la opción de solo mostrar las opciones en las que coincida la búsqueda con las posibles opciones
		maxNumberOfElements: 6 // Se define el largo de la lista con el máximo de elementos a mostrar
	},

	// Con esto hacemos que el tiempo mínimo de consulta sea de medio segundo, lo que proteje de excesivas consultas en caso de que un usuario escriba muy rápido
	requestDelay: 400
};


habitaciones.easyAutocomplete(options);
alojamientos.easyAutocomplete(options);
lugar.easyAutocomplete(options);

// Con la siguiente línea evitamos que se altere el estilo que hayamos definido para nuestro input
$('div.easy-autocomplete').removeAttr('style');