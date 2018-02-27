function initMap() {
    var myLatLng = {lat: 23.1354, lng: -82.3592};

    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 10,
        center: myLatLng,
        gestureHandling: 'cooperative'
    });

    var marker = new google.maps.Marker({
        position: myLatLng,
        map: map,
        title: 'Ubicación del Alojamiento',
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