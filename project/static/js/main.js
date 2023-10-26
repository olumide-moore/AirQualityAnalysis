    // let sensor_locations = JSON.parse(document.getElementById('sensor_locations').textContent);
var mapObject=createMap([51.505, -0.09], 13);
var markerFeatureGroup = L.featureGroup()
mapObject.addLayer(markerFeatureGroup);
dateChanged(); 
    
//Create a map object and set the center and zoom level
function createMap(center, zoom){
    let map=L.map('map').setView(center, zoom);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { 
        maxZoom: 19, //Max zoom level
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>' //Attribution (bottom bar)
    }).addTo(map);
    return map;
}

// Filter table by date range
function dateChanged() {
    // Get date range from input
    var dateRange = document.getElementById("dateRangeFilter");
    var dateRange = dateRange.value.split(" to ");
    
    var startDate = dateRange[0];
    var endDate = dateRange[1] || startDate; // If no end date, use start date

    // startDate = new Date(startDate);
    // endDate = new Date(endDate);
    // var table = document.getElementById("dataTable");
    // var rows = table.getElementsByTagName("tr");
    // var filteredData = [];
    // for (var i = 1; i < rows.length; i++) { // Start from 1 to skip the header row
    //     var observationDate = rows[i].getElementsByTagName("td")[1].textContent; // Assuming date is in the second column
    //     observationDate= new Date(observationDate);
    //     if (observationDate >= startDate && observationDate <= endDate) {
    //         rows[i].style.display = "";
    //         filteredData.push(rows[i]);
    //     } else {
    //         rows[i].style.display = "none";
    //     }
    // }
    // Update map markers
    fetchSensorsData([startDate, endDate]);

    // // Other logic for updating statistical values, if needed
    // updateStatistics(filteredData);
}


function fetchSensorsData(dateRange){
        //Send request to the server and get the updated data for the date
    // const crsftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    // fetch(`/sensors-data/`, {
    //     method: 'POST', 
    //     body: JSON.stringify(date), 
    //     headers: {'Content-Type': 'application/json'
    //     // 'X-CSRFToken': crsftoken
    // }
    // })
    // .then(response => response.json()).then(data => {
    fetch(`/sensors-data/?start_date=${encodeURIComponent(dateRange[0])}&end_date=${encodeURIComponent(dateRange[1])}`)
    .then(response => response.json()).then(data => {
        console.log(data);
        updateMapMarkers(data);
       
    });
}


function updateMapMarkers(data){
        markerFeatureGroup.clearLayers();//Clear existing markers
        //Add new markers based on filtered data
        for (let sensor of data.sensors) {
            let marker = L.marker([sensor.latitude, sensor.longitude]).addTo(markerFeatureGroup);
            marker.bindPopup(`Sensor ID: ${sensor.sensor_id}<br>NO2: ${sensor.no2}<br>VOC: ${sensor.voc}<br>PM10: ${sensor.particulatepm10}<br>PM2.5: ${sensor.particulatepm2_5}<br>PM1: ${sensor.particulatepm1}`);
        }
        //Center map on the markers
        bounds=markerFeatureGroup.getBounds();
        if (bounds.isValid()) {
            mapObject.fitBounds(bounds);
        }else{
            mapObject.setView([51.505, -0.09], 13);
        }


        //Update table
        let tableBody = document.getElementById("tableBody");
        tableBody.innerHTML = "";
        for (let sensor of data.sensors) {
            let row = tableBody.insertRow();
            row.insertCell().innerHTML = sensor.sensor_id;
            row.insertCell().innerHTML = sensor.obs_date;
            row.insertCell().innerHTML = sensor.obs_time_utc;
            row.insertCell().innerHTML = sensor.latitude;
            row.insertCell().innerHTML = sensor.longitude;
            row.insertCell().innerHTML = sensor.no2;
            row.insertCell().innerHTML = sensor.voc;
            row.insertCell().innerHTML = sensor.particulatepm10;
            row.insertCell().innerHTML = sensor.particulatepm2_5;
            row.insertCell().innerHTML = sensor.particulatepm1;
            row.insertCell().innerHTML = sensor.geom;
        }

}







// function updateStatistics(filteredData) {

//     // Clear existing statistics
//     var statistics = document.getElementById("statistics");
//     statistics.innerHTML = "";
//     n_sensors = filteredData.length;
// }
// // // Function to calculate mean
// // function calculateMean(values) {
// //     const sum = values.reduce((acc, val) => acc + val, 0);
// //     return sum / values.length;
// // }

// // // Function to update statistics on the UI
// // function updateStatistics(filteredData) {
// //     const no2Values = filteredData.map((data) => data.no2);

// //     // Calculate mean
// //     const mean = calculateMean(no2Values);

// //     // Update UI elements with statistical values
// //     document.getElementById('meanValue').innerText = `Mean NO2: ${mean.toFixed(2)}`;
// // }



// // //Custom marker icon;
// // const locationIcon = L.icon({
// //     iconUrl: 'download.png',
// //     iconSize: [38, 38]
// //     // iconAnchor: [22, 38],
// //     // popupAnchor: [-3, -76],
// // });
// //Add a marker to the map