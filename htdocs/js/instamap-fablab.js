function initialize() {
  var mapOptions = {
    center: { lat: 45.7438461, lng: 7.3156776},
    zoom: 14
  };
  var map = new google.maps.Map(
    document.getElementById('map-canvas'),
    mapOptions
  );
}
google.maps.event.addDomListener(window, 'load', initialize);
