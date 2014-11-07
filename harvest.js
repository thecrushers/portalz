// Set IITC map window to extent of the area you want to parse. Resize your browser window if needed.
// When you are ready, type "startCollecting()"

var scan_complete = false;
//var url = "http://localhost:8080";
var url = "http://portalz-a.appspot.com";

var startCollecting = function() {
  bounds = map.getBounds();
  window.addHook('mapDataRefreshEnd', function(data){collectAndMove(bounds)});
  window.addHook('portalAdded', function(data){addPortal(data)});
  window.addHook('portalDetailsUpdated', function(data){addDetails(data)});
  scan_complete = false;
  window.mapDataRequest.REFRESH_CLOSE = 3;
  window.mapDataRequest.MOVE_REFRESH = 3;
  map.setView(bounds.getNorthWest(), 15);
};

var stopCollecting = function() {
  scan_complete = true;
  delete window._hooks['mapDataRefreshEnd'];
  delete window._hooks['portalAdded'];
  delete window._hooks['portalDetailsUpdated'];
}

var move = function(bounds) {
  if (scan_complete === false) {
    if (bounds.intersects(map.getBounds())) {
      // Just move to the right
      map.panBy([map.getSize().x, 0]);
    } else {
      // Move down and back to the West most point
      geo = map.containerPointToLatLng([map.getSize().x/2, map.getSize().y*1]);
      new_center = L.latLng(geo.lat, bounds.getWest())
      map.setView(new_center, 15);
    }
  }
};

var collectAndMove = function(bounds) {
  if (scan_complete === false) {
    if (bounds.getSouth() > map.getBounds().getNorth()) {
      console.log("Scan complete!!!!!!!");
      stopCollecting();
      // Reset values so IITC stops requesting so often
      window.mapDataRequest.REFRESH_CLOSE = 300
      window.mapDataRequest.MOVE_REFRESH = 3;
    } else {
      move(bounds);
    }
  }
};

var addPortal = function(data) {
  //guid = data.portal.options.guid;
  //portal_data = data.options.data;
  //portal_data["guid"] = guid;
  //console.log(portal_data);
  window.renderPortalDetails(data.portal.options.guid);
}

var addDetails = function(data) {
  guid = data.guid;
  portal_details = data.portalDetails;
  portal_details["guid"] = guid;
  sendDetailData(portal_details);
}

var sendDetailData = function(data) {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", url + '/submit_details', true);
  xhr.setRequestHeader('Content-Type', 'text/plain');
  xhr.send(JSON.stringify(data));
  xhr.onloadend = function () {
    console.log("Portal details submitted!");
  };
}
