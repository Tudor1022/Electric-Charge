var map = L.map('map').setView([20, 0], 2); // Start with a zoomed-out global view

// Load and display OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Function to load EV charging stations in the current map view
async function loadChargingStations() {
    const bounds = map.getBounds();
    const southWest = bounds.getSouthWest();
    const northEast = bounds.getNorthEast();

    // Query for charging stations in the current bounding box
    const query = `
        [out:json];
        node["amenity"="charging_station"](${southWest.lat},${southWest.lng},${northEast.lat},${northEast.lng});
        out;
    `;
    const response = await fetch(`https://overpass-api.de/api/interpreter?data=${encodeURIComponent(query)}`);
    const data = await response.json();

    // Add markers for each charging station
    data.elements.forEach(station => {
        const marker = L.marker([station.lat, station.lon]).addTo(map)
            .bindPopup(`<strong>Charging Station</strong><br>Latitude: ${station.lat}, Longitude: ${station.lon}`);
    });
}

// Load EV charging stations initially
loadChargingStations();

// Load EV charging stations whenever the map is moved or zoomed
map.on('moveend', loadChargingStations);

// Geolocation to center the map on the user's location
function onLocationFound(e) {
    map.setView(e.latlng, 13); // Zoom in to the user's location
    L.marker(e.latlng).addTo(map).bindPopup("You are here").openPopup();
}

function onLocationError(e) {
    alert(e.message);
}

map.on('locationfound', onLocationFound);
map.on('locationerror', onLocationError);

// Request the user's location
map.locate({ setView: true, maxZoom: 16 });
