
//Hamburger menu
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
});
//Ensure that the hamburger menu is hidden when a menu item is clicked
const menuLinks = document.querySelectorAll('.nav-link');
menuLinks.forEach((menuLink) => {
    menuLink.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    });
});

//Fill the dropdown with sensor ids

   
   // let sensor_locations = JSON.parse(document.getElementById('sensor_locations').textContent);
var mapObject=createMap([51.505, -0.09], 13);
var markerFeatureGroup = L.featureGroup()
mapObject.addLayer(markerFeatureGroup);
// dateChanged(); 
    
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
// function dateChanged() {
//     // Get date range from input
//     var dateRange = document.getElementById("dateRangeFilter");
//     var dateRange = dateRange.value.split(" to ");
    
//     var startDate = dateRange[0];
//     var endDate = dateRange[1] || startDate; // If no end date, use start date

//     // startDate = new Date(startDate);
//     // endDate = new Date(endDate);
//     // var table = document.getElementById("dataTable");
//     // var rows = table.getElementsByTagName("tr");
//     // var filteredData = [];
//     // for (var i = 1; i < rows.length; i++) { // Start from 1 to skip the header row
//     //     var observationDate = rows[i].getElementsByTagName("td")[1].textContent; // Assuming date is in the second column
//     //     observationDate= new Date(observationDate);
//     //     if (observationDate >= startDate && observationDate <= endDate) {
//     //         rows[i].style.display = "";
//     //         filteredData.push(rows[i]);
//     //     } else {
//     //         rows[i].style.display = "none";
//     //     }
//     // }
//     // Update map markers
//     fetchSensorsData([startDate, endDate]);

//     // // Other logic for updating statistical values, if needed
//     // updateStatistics(filteredData);
// }
function sensorChanged() {
    // Get selected sensor from input
    weekChanged();
}
const weekRangeHeading = document.getElementById("weekRangeHeading");
function weekChanged() {
    // Get selected sensor from input
    let weekInput = weekFilter.value;
    let sensorInput1 = document.getElementById("sensor-id-1").value;
    let sensorInput2 = document.getElementById("sensor-id-2").value;
    // Get selected week from input
    if ((sensorInput1 == '' && sensorInput2 == '') || weekInput == '') {
        return;
    }
    let [year, week] = weekInput.split("-W");
    let {startDate, endDate} = getWeekDates(year, week); ///get the start and end date of the week
    weekRangeHeading.textContent = `${startDate} - ${endDate}`
    fetchSensorsData([sensorInput1,sensorInput2],[startDate, endDate]);
}
function getWeekDates(year, week) {
    let startDate = new Date(year, 0, 2 + ((week - 1) * 7)); 
    let endDate = new Date(year, 0, 2 + ((week - 1) * 7) + 6);
    startDate=startDate.toLocaleDateString();
    endDate=endDate.toLocaleDateString();
    return {startDate, endDate};
    }


function fetchSensorsData(sensors,dateRange){
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
    // sensorsQuery=``
    // if (sensors[0]!=''){
    //     sensorsQuery+=`sensor1=${sensors[0]}&`
    // }
    // if (sensors[1]!='' && sensors[1]!=sensors[0]){
    //     sensorsQuery+=`sensor2=${sensors[1]}&`
    // }
    sensorsQuery=`sensor_one=${sensors[0]}&sensor_two=${sensors[1]}`
    fetch(`/sensors-data/?${sensorsQuery}&start_date=${encodeURIComponent(dateRange[0])}&end_date=${encodeURIComponent(dateRange[1])}`)
    .then(response => response.json()).then(data => {
        // console.log(data);
        updateChart(data);
       
    }).catch(error => {
        console.error('Error fetching data:', error)});
    }
    


let boxplotCharts = {};
function createBoxPlotChart(chartId,label, color){
    let ctx= document.getElementById(chartId).getContext('2d');
    boxplotCharts[label] = new Chart(ctx, {
        type: 'boxplot', //bar, horizontalBar, pie, line, doughnut, radar, polarArea//bar, horizontalBar, pie, line, doughnut, radar, polarArea
        data: {
            datasets: [{
                // label: label,
                //disabling the label for now
                data: [],
                backgroundColor: 'rgba(255, 206, 86, 0.6)'
            //     // borderColor: 'rgb(255, 99, 132)',
            //     // borderWidth: 1,
            //     // barThickness: 10,
            //     // maxBarThickness: 8,
            //     // hoverBorderColor: "rgba(234, 236, 244, 1)",
            //     // hoverBorderWidth: 3
            },
            {
                // label: label,
                type: 'boxplot',
                data: [],
                backgroundColor: 'rgba(75, 192, 192, 0.6)'
                // barThickness: 10,
                // maxBarThickness: 8,
                // hoverBorderColor: "rgba(234, 236, 244, 1)",
                // hoverBorderWidth: 3
            }        
        ]
        },
        options: {
            plugins: {
                legend: {
                    display: false,
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
   });
}
const parameters = ['NO2', 'VOC', 'ParticulatePM10', 'ParticulatePM2_5', 'ParticulatePM1'];
// const colors = ['rgba(255, 99, 132, 0.6)', 'rgba(255, 159, 64, 0.6)', 'rgba(255, 206, 86, 0.6)', 'rgba(75, 192, 192, 0.6)', 'rgba(54, 162, 235, 0.6)'];
for (let param of parameters){
    createBoxPlotChart(`${param.toLowerCase()}Boxplot`, param);
}
// let ctx = document.getElementById('no2Graph').getContext('2d');

// let myChart = new Chart(ctx, {
//     type: 'boxplot', //bar, horizontalBar, pie, line, doughnut, radar, polarArea
//     data: {
//         // labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
//         datasets: [{
//             label: 'No2',
//             backgroundColor: [
//                 'rgba(255, 99, 132, 0.2)',
//                 'rgba(255, 159, 64, 0.2)',
//                 'rgba(255, 206, 86, 0.2)',
//                 'rgba(75, 192, 192, 0.2)',
//                 'rgba(54, 162, 235, 0.2)'
//             ],
//             borderColor: [
//                 'rgba(255, 99, 132, 1)', 
//                 'rgba(255, 159, 64, 1)', 
//                 'rgba(255, 206, 86, 1)', 
//                 'rgba(75, 192, 192, 1)', 
//                 'rgba(54, 162, 235, 1)'
//             ],
//             borderWidth: 1,
//             // barThickness: 10,
//             // maxBarThickness: 8,
//             hoverBorderColor: "rgba(234, 236, 244, 1)",
//             hoverBorderWidth: 3,
//         }]
//     }
//     // options: {
//     //     title: {
//     //         display: true,
//     //         text: 'Mean of pollutants', 
//     //         fontSize: 210
//     //     },
//     //     legend: {
//     //         display: false,
//     //         postion: 'right'
//     //     },

//     //     // responsive: true,
//     //     // maintainAspectRatio: false,
//     //     // scales: {
//     //     //     y: {
//     //     //         beginAtZero: true
//     //     //     }
//     //     // layout: {
//     //     //     left:50,
//     //     //     right:0, 
//     //     //     bottom:0,
//     //     //     top:0
//     //     // },
//     //     tooltips: {
//     //         enabled: true,
//     //         fontSize: 8
            
//     //     }
//     // }

// });



function updateChart(data){
    raw_data1=data.raw_data1;
    raw_datas=[raw_data1];

    if (data.raw_data2){
        raw_datas.push(data.raw_data2);
    }
    for (let j=0; j<raw_datas.length; j++){// for each sensor 
        labels = Object.keys(raw_datas[j]);
        //Add shortened day to the labels
        for (let i=0; i<labels.length; i++){
            let dateStr=labels[i];
            let date= new Date(dateStr.slice(6,10), dateStr.slice(3,5)-1, dateStr.slice(0,2));
            labels[i]=`${getWeekDay(date)}(${dateStr.slice(0,5)})`;
            // labels[i]=date.toLocaleDateString()+` (${getWeekDay(date)})`;
        }
        for (let param of parameters){
            let boxplot = boxplotCharts[param];
            boxplot.data.labels = labels;
            let allData = [];
            for (let dat in raw_datas[j]){
                allData.push(raw_datas[j][dat][param.toLowerCase()]);
            }
            // boxplot.data.datasets[0].data = allData;
            boxplot.data.datasets[j].data = allData;
            boxplot.update();
        }
}

}

function getWeekDay(date){
    let days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    return days[date.getDay()];
}


function getCurrentWeek(){
    let today = new Date();
    // let today = new Date(2023,1,21);
    let year = today.getFullYear();
    let week = getWeekNumber(today);
    return `${year}-W`+`${week}`.padStart(2, '0');
}
function getWeekNumber(date) {
    let yearStart = new Date(date.getFullYear(), 0, 1);
    let weekNo = Math.ceil((((date - yearStart) / 86400000) + yearStart.getDay() + 1) / 7);
    return weekNo;
}
//Set the week filter default date and maximum date
const weekFilter = document.getElementById("weekFilter");
let curWeek=getCurrentWeek();
weekFilter.value = curWeek;
weekFilter.max = curWeek;
//Call the weekChanged function to update the chart
weekChanged();
// function updateMapMarkers(data){
        // markerFeatureGroup.clearLayers();//Clear existing markers
        // //Add new markers based on filtered data
        // for (let sensor of data.sensors) {
        //     let marker = L.marker([sensor.latitude, sensor.longitude]).addTo(markerFeatureGroup);
        //     marker.bindPopup(`Sensor ID: ${sensor.sensor_id}<br>NO2: ${sensor.no2}<br>VOC: ${sensor.voc}<br>PM10: ${sensor.particulatepm10}<br>PM2.5: ${sensor.particulatepm2_5}<br>PM1: ${sensor.particulatepm1}`);
        // }
        // //Center map on the markers
        // bounds=markerFeatureGroup.getBounds();
        // if (bounds.isValid()) {
        //     mapObject.fitBounds(bounds);
        // }else{
        //     mapObject.setView([51.505, -0.09], 13);
        // }

        // //Update statistics
        // let meanData = document.getElementById("meanData");
        // mean=data.mean;
        // meanData.innerHTML = "";
        // meanData.innerHTML ="<p>NO2: "+mean.no2+"</p><p>VOC: "+mean.voc+"</p><p>PM10: "+mean.particulatepm10+"</p><p>PM2.5: "+mean.particulatepm2_5+"</p><p>PM1: "+mean.particulatepm1+"</p>";
        

        // //Update table
        // let tableBody = document.getElementById("tableBody");
        // tableBody.innerHTML = "";
        // for (let sensor of data.sensors) {
        //     let row = tableBody.insertRow();
        //     row.insertCell().innerHTML = sensor.sensor_id;
        //     row.insertCell().innerHTML = sensor.obs_date;
        //     row.insertCell().innerHTML = sensor.obs_time_utc;
        //     row.insertCell().innerHTML = sensor.latitude;
        //     row.insertCell().innerHTML = sensor.longitude;
        //     row.insertCell().innerHTML = sensor.no2;
        //     row.insertCell().innerHTML = sensor.voc;
        //     row.insertCell().innerHTML = sensor.particulatepm10;
        //     row.insertCell().innerHTML = sensor.particulatepm2_5;
        //     row.insertCell().innerHTML = sensor.particulatepm1;
        //     row.insertCell().innerHTML = sensor.geom;
        // }

// }

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
