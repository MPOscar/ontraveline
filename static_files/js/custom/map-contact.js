function initMap() {
    var myLatLng = {lat: 40.393304, lng: -3.7344777};

    var map = new google.maps.Map(document.getElementById('map-contact'), {
        zoom: 14,
        center: myLatLng
    });

    var marker = new google.maps.Marker({
        position: myLatLng,
        map: map,
        title: 'Magestree Network | Ontraveline',
        gestureHandling: 'cooperative'
    });
}