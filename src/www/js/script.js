/* 
Fetch data from json_name parameter and convert to GeoJSON format 

Args: json_name (str): The name of the JSON file to fetch data from

Returns: list: A list of GeoJSON features
*/

async function doFetch(json_name) {
  const features = [];
  const response = await fetch("./" + json_name);
  const data = await response.json();
  for (let i = 0; i < data.length; i++) {
    features.push({
      type: "Feature",
      properties: { name: data[i].name },
      geometry: {
        coordinates: [data[i].longitude, data[i].latitude],
        type: "Point",
      },
    });
  }
  return features;
}

/* 
Create GeoJSON FeatureCollection from fetched data

Returns: dict: A GeoJSON FeatureCollection
*/

async function createGeojson() {
  const features = await doFetch("sample.JSON");
  const geojson = {
    type: "FeatureCollection",
    features: features,
  };
  return geojson;
}

document.addEventListener("DOMContentLoaded", async function () {
  // Initialize map with a default view and set minimum zoom.
  const map = L.map("map", { minZoom: 2 }).setView([0, 0], 2);

  L.tileLayer(
    "https://api.maptiler.com/maps/streets-v2/{z}/{x}/{y}.png?key=BqtwcjnWGsiCTa30jj5M",
    {
      //I used the 'Streets' Map from MapTiler. Other formats can be found at https://cloud.maptiler.com/maps/
      attribution:
        '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap contributors</a>',
    },
  ).addTo(map);

  const geojson = await createGeojson(); // Fetch and create GeoJSON data
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
});
