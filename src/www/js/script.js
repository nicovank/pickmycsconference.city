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
  return marker;
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
        name:
          submissions[i].author_name +
          " (" +
          submissions[i].affiliation_name.split(",")[0] +
          ")",
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

async function populateMap(map, json = "data/FSE.json") {
  const markers = L.markerClusterGroup();
  const { geojson, data } = await createGeojson(json);
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

  const suggested_city_marker = await addSuggestedCityMarker(map, data);
  return { markers, suggested_city_marker };
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
  const legend = L.control({ position: "bottomright" });

  legend.onAdd = function (map) {
    const div = L.DomUtil.create("div", "info legend card p-2");
    const grades = [
      {
        label: "Suggested City",
        type: "icon",
        iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
      },
      {
        label: "Author Affiliation",
        type: "icon",
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
      },
      {
        label: "Large Cluster",
        type: "swatch",
        color: "#3a5ccf", 
      },
      {
        label: "Medium Cluster",
        type: "swatch",
        color: "#73aeed", 
      },
      {
        label: "Small Cluster",
        type: "swatch",
        color: "#a6dbf7", 
      },
    ];

    let innerHTML = "<h6>Legend</h6>";
    
    // Loop through our legend items and generate a label with a colored swatch or icon for each
    for (let i = 0; i < grades.length; i++) {
        let item = grades[i];
        let symbol;

        if (item.type === "icon") {
            symbol = `<img src="${item.iconUrl}" class="legend-icon" alt="${item.label}">`;
        } else if (item.type === "swatch") {
            symbol = `<i class="legend-swatch" style="background:${item.color}"></i>`;
        }

        innerHTML += `<div class="legend-item">${symbol} <span>${item.label}</span></div>`;
    }
    div.innerHTML = innerHTML;

    // Prevents map events (like zoom) from firing when clicking on the legend
    L.DomEvent.disableClickPropagation(div);

    return div;
  };

  legend.addTo(map);

  let currentMarkers, currentSuggestedCityMarker;

  ({
    markers: currentMarkers,
    suggested_city_marker: currentSuggestedCityMarker,
  } = await populateMap(map));

  // Disable map interactions when dropdown is shown and enable them when hidden
  function disableMapInteractions() {
    map.dragging.disable();
    map.scrollWheelZoom.disable();
    map.doubleClickZoom.disable();
    map.touchZoom.disable();
    map.boxZoom.disable();
    map.keyboard.disable();
  }

  // Enable map interactions
  function enableMapInteractions() {
    map.dragging.enable();
    map.scrollWheelZoom.enable();
    map.doubleClickZoom.enable();
    map.touchZoom.enable();
    map.boxZoom.enable();
    map.keyboard.enable();
  }

  document.addEventListener(
    "show.bs.dropdown",
    function (e) {
      if (e.target.closest("#map .dropdown")) {
        disableMapInteractions();
      }
    },
    true,
  );

  document.addEventListener(
    "hide.bs.dropdown",
    function (e) {
      if (e.target.closest("#map .dropdown")) {
        enableMapInteractions();
      }
    },
    true,
  );

  document.addEventListener(
    "hidden.bs.dropdown",
    function (e) {
      if (e.target.closest("#map .dropdown")) {
        enableMapInteractions();
      }
    },
    true,
  );

  // Change map data based on dropdown selection
  const items = document.querySelectorAll("#map .dropdown-item");
  items.forEach((item) => {
    item.addEventListener("click", async function (e) {
      e.preventDefault(); // prevent page jump if it's an <a href="#">
      const fileName = this.dataset.file;
      console.log(fileName);

      if (currentMarkers) map.removeLayer(currentMarkers);
      console.log("removing current markers");
      if (currentSuggestedCityMarker)
        map.removeLayer(currentSuggestedCityMarker);
      console.log("removed current suggested city marker");

      ({
        markers: currentMarkers,
        suggested_city_marker: currentSuggestedCityMarker,
      } = await populateMap(map, fileName));
    });
  });
});
