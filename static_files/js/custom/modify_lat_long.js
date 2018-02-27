function initMap() {

    // En la clase del div se encuentra el id del Alojamiento
    var alojamiento_id = $('#map').attr("class");

    // Llamamos a una vista con Ajax para obtener la longitud y latitud del Alojamiento
    $.ajax({
        url : "/servicios/get_lat_lng/"+alojamiento_id,
        type : "GET",

        success : function(json) {
            var latitud = parseFloat(json.latitud);
            var longitud = parseFloat(json.longitud);
            var myLatLng = {lat: latitud, lng: longitud};

            // Se cargan los input hidden con las coordenadas del Alojamiento
            $('#latitud').val(latitud);
            $('#longitud').val(longitud);

            var map = new google.maps.Map(document.getElementById('map'), {
                zoom: 13,
                center: myLatLng,
                gestureHandling: 'cooperative'
            });

            var marker = new google.maps.Marker({
                position: myLatLng,
                map: map,
                title: 'Arrastra Para cambiar la ubicación',
                draggable: true
            });

            marker.addListener('dragend', show_position);
            function show_position(){
                var latitud = marker.getPosition().lat();
                var longitud = marker.getPosition().lng();

                $('#latitud').val(latitud);
                $('#longitud').val(longitud);
            }

        }
    });
}