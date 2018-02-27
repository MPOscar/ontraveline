function initMap() {
    // Llamamos a una vista con Ajax para obtener las coordenadas de todos los Alojamientos
    $.ajax({
        url : "/servicios/get_data_alojamientos",
        type : "GET",

        success : function(json) {
            var map = new google.maps.Map(document.getElementById('alojamientos_map'), {
                center: {lat: 21.5, lng: -79.399237},
                zoom: 7,
                disableDefaultUI: true,
                gestureHandling: 'cooperative',
                styles: [
                    {
                      featureType: 'administrative.locality',
                      elementType: 'labels.text.fill',
                      stylers: [{color: '#da4371'}]
                    },
                    {
                      featureType: 'road',
                      elementType: 'geometry',
                      // stylers: [{color: '#38414e'}]
                      stylers: [{visibility: 'off'}]
                    },
                    {
                      featureType: 'road',
                      elementType: 'geometry.stroke',
                      stylers: [{color: '#212a37'}]
                    },
                    {
                      featureType: 'road',
                      elementType: 'labels.text.fill',
                      stylers: [{visibility: 'off'}]
                    },
                    {
                      featureType: 'road.highway',
                      elementType: 'geometry',
                      stylers: [{visibility: 'off'}]
                    },
                    {
                      featureType: 'road.highway',
                      elementType: 'geometry.stroke',
                      stylers: [{visibility: 'off'}]
                    },
                    {
                      featureType: 'road.highway',
                      elementType: 'labels.text.fill',
                      stylers: [{visibility: 'off'}]
                    },
                    {
                      featureType: 'transit',
                      elementType: 'geometry',
                      stylers: [{visibility: 'off'}]
                    },
                    {
                      featureType: 'transit.station',
                      elementType: 'labels.text.fill',
                      stylers: [{visibility: 'off'}]
                    },
                    {
                      featureType: 'water',
                      elementType: 'geometry',
                      stylers: [{color: '#ffffff'}]
                    },
                    {
                      featureType: 'water',
                      elementType: 'labels.text.fill',
                      stylers: [{color: '#da4371'}]
                    }
                  ]
            });
            var markers = [];
            var infoWindowContent = [];
            for (var i = 0; i < json.data_alojamientos.length; i++) {

                var id_alojamiento        = json.data_alojamientos[i][0];
                var nombre                = json.data_alojamientos[i][1];
                var descripcion           = json.data_alojamientos[i][2];
                var foto_url              = json.data_alojamientos[i][3];
                var lat                   = parseFloat(json.data_alojamientos[i][4]);
                var lng                   = parseFloat(json.data_alojamientos[i][5]);

                var cantidad_habitaciones = json.data_alojamientos[i][6];
                var modo_alquiler = json.data_alojamientos[i][7];
                var precio_minimo         = parseFloat(json.data_alojamientos[i][8]);
                var rate         = parseFloat(json.data_alojamientos[i][9]);
                var moneda         = json.data_alojamientos[i][10];

                // Calculando el valor a mostrar en la ventana de información del Alojamiento en el Mapa según la moneda establecida por el Usuario
                var precio_actual = (Math.round(precio_minimo * rate * 100)/100).toFixed(2);

                // Info Window Content
                infoWindowContent.push(
                    [
                        '<div>' +
                            '<a href = "/servicios/detalles_alojamiento/' + id_alojamiento + '">' +
                                '<div class = "row">' +
                                    '<div class = "col-md-3">' +
                                        '<img style = "float: left;" class = "box-icon-gray box-icon-center round box-icon-border box-icon-big" src = ' + foto_url + '/>' +
                                    '</div>' +
                                    '<div class = "col-md-9 offset1">' +
                                        '<p style="color: #0082BC">' + nombre + '</p>' +
                                        '<p>' + cantidad_habitaciones + ' habitaciones</p>' +
                                        '<p>Se alquila ' + modo_alquiler +' desde ' + precio_actual + ' ' + moneda + ' la noche</p>' +
                                    '</div>' +
                                '</div>' +
                                '<div class = "row">' +
                                    '<div class = "col-md-12">' +
                                        '<p style="text-align: justify">' + descripcion.substring(0, 100) + '...more -></p>' +
                                    '</div>' +
                                '</div>' +
                            '</a>' +
                        '</div>'
                    ]
                );

                // Display multiple markers on a map
                var infoWindow = new google.maps.InfoWindow({maxWidth: 280}), marker, i;

                // Define Position
                var position = new google.maps.LatLng(lat, lng);

                // Create Marker
                marker = new google.maps.Marker({
                    position: position,
                    map: map,
                    title: nombre,
                    icon: '/static/img/map_marker.png'
                });

                // Allow each marker to have an info window
                google.maps.event.addListener(marker, 'click', (function(marker, i) {
                    return function() {
                        infoWindow.setContent(infoWindowContent[i][0]);
                        infoWindow.open(map, marker);
                    }
                })(marker, i));

                // event to close the infoWindow with a click on the map
                google.maps.event.addListener(map, 'click', function() {
                    infoWindow.close();
                });

                markers.push(marker);

            }

            // Create an array of alphabetical characters used to label the markers.
            // var labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

            // Add some markers to the map.
            // Note: The code uses the JavaScript Array.prototype.map() method to
            // create an array of markers based on a given "locations" array.
            // The map() method here has nothing to do with the Google Maps API.
            // var markers = locations.map(function(location, i) {
            //     return new google.maps.Marker({
            //         position: location,
            //         label: labels[i % labels.length]
            //     });
            // });

            // Add a marker clusterer to manage the markers.
            var markerCluster = new MarkerClusterer(
                map,
                markers,
                {imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'}
            );

            var iconBase = 'https://maps.google.com/mapfiles/kml/shapes/';

            var icons = {
                parking: {
                    icon: iconBase + 'parking_lot_maps.png'
                },
                library: {
                    icon: iconBase + 'library_maps.png'
                },
                info: {
                    icon: iconBase + 'info-i_maps.png'
                }
            };
        }
    });
}