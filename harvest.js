// Set IITC map window to extent of the area you want to parse. Resize your browser window if needed.
// When you are ready, type "startCollecting()"

var scan_complete = false;
var url = "http://localhost:8080";
//var url = "http://portalz-a.appspot.com";
var portals_seen = [];
var do_owner = true;
var waiting_for_render = false;
var waiting;

var startCollecting = function() {
  bounds = map.getBounds();
  // Reset seen portals
  portals_seen = [];
  window.addHook('mapDataRefreshEnd', function(data){collectAndMove(bounds)});
  if (do_owner === true) {
    window.addHook('portalDetailsUpdated', function(data){
      addDetails(data.guid, data.portalDetails);
    });
  }
  scan_complete = false;
  window.mapDataRequest.REFRESH_CLOSE = 3;
  window.mapDataRequest.MOVE_REFRESH = 3;
  map.setView(bounds.getNorthWest(), 15);
};

var stopCollecting = function() {
  scan_complete = true;
  delete window._hooks['mapDataRefreshEnd'];
};

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
      window.mapDataRequest.REFRESH_CLOSE = 300;
      window.mapDataRequest.MOVE_REFRESH = 3;
    } else {
      $.each(window.portals, function(guid, data) {
        if (portals_seen.indexOf(guid) == -1) {
          portals_seen.push(guid);
          console.log("Iterating over: " + guid);
          if (do_owner === false) {
            addDetails(guid, data.options.data);
          } else {
            // One at a time...
            waiting = setInterval(function() {
              if (waiting_for_render === false) {
                waiting_for_render = true;
                console.log("Rendering: " + guid);
                window.renderPortalDetails(guid);
                clearInterval(waiting);
              }
            }, 1000);
          }
        }
      });
      move(bounds);
    }
  }
};

var addDetails = function(guid, portal_details) {
  portal_details["guid"] = guid;
  sendDetailData(portal_details);
};

var sendDetailData = function(data) {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", url + '/submit_details', true);
  xhr.setRequestHeader('Content-Type', 'text/plain');
  xhr.send(JSON.stringify(data));
  xhr.onloadend = function () {
    waiting_for_render = false;
  };
};
