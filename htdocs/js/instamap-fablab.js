function addInfoWindow(marker, message) {
  var infoWindow = new google.maps.InfoWindow({
      content: message,
      marker: marker
  });

  google.maps.event.addListener(marker, 'mouseover', function() {
    marker.setIcon(marker.LargeIcon);
  });

  google.maps.event.addListener(marker, 'mouseout', function() {
    marker.setIcon(marker.SmallIcon);
  });

  google.maps.event.addListener(marker, 'click', function () {
    if (currentInfoWindow !== null && currentInfoWindow != infoWindow) {
      currentInfoWindow.close();
      currentInfoWindow.marker.setIcon(currentInfoWindow.marker.SmallIcon);
    }
    currentInfoWindow = infoWindow;

    google.maps.event.clearListeners(marker, 'mouseout');

    infoWindow.open(map, marker);
    marker.setIcon(marker.LargeIcon);

    google.maps.event.addListener(infoWindow, 'closeclick', function() {
      marker.setIcon(marker.SmallIcon);

      google.maps.event.addListener(marker, 'mouseout', function() {
        marker.setIcon(marker.SmallIcon);
      });
    });

    google.maps.event.addListener(map, 'click', function() {
      infoWindow.setMap(null);
      marker.setIcon(marker.SmallIcon);

      google.maps.event.addListener(marker, 'mouseout', function() {
        marker.setIcon(marker.SmallIcon);
      });
    });
  });
}

function drawInstaMarkers() {
  $.getJSON(INSTA_JSON, function(data) {
    for (var i = 0; i < data.length; i++) {
      insta_marker = new google.maps.Marker({
        icon: 'img/marker_IG.png',
        SmallIcon: 'img/marker_IG.png',
        LargeIcon: 'img/marker_IG@2x.png',
        draggable: false,
        position: new google.maps.LatLng(data[i].lat, data[i].lon),
        map: map,
        title: data[i].text,
        //visible: false
      });
      markers_foto.push(insta_marker);

      var msg = '<div class="infobox-content scrollFix">\n' +
        '<div class="infow_title">' + data[i].fullname + '</div>\n' +
        '<div class="username_instagram"><a title="' + data[i].username + '" href="http://instagram.com/' + data[i].username + '">' + data[i].username + '</a></div>\n' +
        '<div class="insta_photo"><a href="' + data[i].data.standard + '" onclick="$.colorbox({href:\'' + data[i].data.standard + '\', opacity:\'0.5\',  scalePhotos:\'true\', maxWidth:\'95%\', maxHeight:\'95%\', title:\'' + data[i].text + ' - by ' + data[i].fullname + '\'});return false;"><img src="' + data[i].data.low + '" /></a></div><br>\n' +
        '<div class="time_instagram">' + new Date(parseInt(data[i].time, 10)) + '</div>\n' +
        '<div class="text_instagram">' + data[i].text + '</div>\n' +
        '</div>';
      addInfoWindow(insta_marker, msg);
    }
  });
}

function initialize() {
  var mapOptions = {
    center: { lat: 45.7438461, lng: 7.3156776},
    zoom: 14
  };

  var map = new google.maps.Map(
    document.getElementById('map-canvas'),
    mapOptions
  );

  tileListener = google.maps.event.addListener(map, 'tilesloaded', drawInstaMarkers);
}

google.maps.event.addDomListener(window, 'load', initialize);
