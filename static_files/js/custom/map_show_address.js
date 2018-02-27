function initMap() {

    // En la clase del div se encuentra el id del Alojamiento
    var alojamiento_id = $('#map_show_address').attr("class");

    // Llamamos a una vista con Ajax para obtener la longitud y latitud del Alojamiento
    $.ajax({
        url : "/servicios/get_lat_lng/"+alojamiento_id,
        type : "GET",

        success : function(json) {
            var latitud = parseFloat(json.latitud);
            var longitud = parseFloat(json.longitud);
            var myLatLng = {lat: latitud, lng: longitud};
            var map = new google.maps.Map(document.getElementById('map_show_address'), {
                zoom: 13,
                center: myLatLng,
                gestureHandling: 'cooperative'
            });

            var marker = new google.maps.Marker({
                position: myLatLng,
                map: map,
                title: 'Hello World!'
            });

        }
    });
}