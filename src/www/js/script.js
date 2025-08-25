const redIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

/* 
Fetches suggested location from json and adds a red marker to the map

*/
async function addSuggestedCityMarker(map, data) {
  const location = data.suggested_location;

  const lat = Number(location.latitude);
  const lon = Number(location.longitude);

  var marker = L.marker([lat, lon], { icon: redIcon });
  if (location.city) {
    marker.bindPopup(location.city);
  }
  marker.addTo(map);
}

/* 
Fetch data from json_name parameter and convert to GeoJSON format 

Args: json_name (str): The name of the JSON file to fetch data from

Returns: list: A list of GeoJSON features
*/

async function doFetch(json_name) {
  const features = [];
  const response = await fetch("./" + json_name);
  const data = await response.json();

  const submissions = data.happenings[0].submissions;

  for (let i = 0; i < submissions.length; i++) {
    features.push({
      type: "Feature",
      properties: {
        name: submissions[i].affiliation_name,
      },
      geometry: {
        coordinates: [
          submissions[i].location.longitude,
          submissions[i].location.latitude,
        ],
        type: "Point",
      },
    });
  }
  return { features, data }; //return data so that we don't need to fetch it again
}

/* 
Create GeoJSON FeatureCollection from fetched data

Returns: dict: A GeoJSON FeatureCollection
*/

async function createGeojson(json_name) {
  const { features, data } = await doFetch(json_name);
  const geojson = {
    type: "FeatureCollection",
    features: features,
  };
  return { geojson, data };
}

document.addEventListener("DOMContentLoaded", async function () {
  // Initialize map with a default view and set minimum zoom.

  const map = L.map("map", {
    minZoom: 2,
    maxBounds: [
      [-90, -180],
      [90, 180],
    ],
  }).setView([0, 0], 2);

  L.tileLayer(
    "https://api.maptiler.com/maps/streets-v2/{z}/{x}/{y}.png?key=BqtwcjnWGsiCTa30jj5M",
    {
      // I used the 'Streets' Map from MapTiler. Other formats can be found at https://cloud.maptiler.com/maps/
      attribution:
        '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap contributors</a>',
    },
  ).addTo(map);

  // Fetch and create GeoJSON data.
  const { geojson, data } = await createGeojson("data/FSE.json");
  const markers = L.markerClusterGroup(); // Create a marker cluster group

  L.geoJSON(geojson, {
    pointToLayer: function (feature, latlng) {
      const marker = L.marker(latlng);
      if (feature.properties && feature.properties.name) {
        marker.bindPopup(feature.properties.name);
      }
      return marker;
    },
  }).eachLayer((layer) => markers.addLayer(layer));

  map.addLayer(markers);

  addSuggestedCityMarker(map, data);

  function disableMapInteractions() {
    map.dragging.disable();
    map.scrollWheelZoom.disable();
    map.doubleClickZoom.disable();
    map.touchZoom.disable();
    map.boxZoom.disable();
    map.keyboard.disable();
  }

  function enableMapInteractions() {
    map.dragging.enable();
    map.scrollWheelZoom.enable();
    map.doubleClickZoom.enable();
    map.touchZoom.enable();
    map.boxZoom.enable();
    map.keyboard.enable();
  }

  document.addEventListener('show.bs.dropdown', function (e) {
    if (e.target.closest('#map .dropdown')) {
      disableMapInteractions();
    }
  }, true);

  document.addEventListener('hide.bs.dropdown', function (e) {
    if (e.target.closest('#map .dropdown')) {
      enableMapInteractions();
    }
  }, true);

  document.addEventListener('hidden.bs.dropdown', function (e) {
    if (e.target.closest('#map .dropdown')) {
      enableMapInteractions();
    }
  }, true);
});
