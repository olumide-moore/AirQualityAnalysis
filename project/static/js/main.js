
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

var chartType='Line';
var sensor1=document.getElementById("sensor1").value;
var sensor2;
var comparingSensors=false;
var comparingAverageTrend=false;

let currentDate = new Date();


fetchData();
// Function to handle the sensor comparison toggle
function toggleSensorComparison(checkbox) {
    let sensor2Div = document.getElementById('sensor2div');
    if (checkbox.checked) {
        // Show the second sensor dropdown
        sensor2Div.classList.remove('hidden');
        let sensor2dropdown = document.getElementById('sensor2');
        sensor2 = sensor2dropdown.value;
        if (sensor1 == sensor2){ //if the second sensor is the same as the first one, select the next sensor
            if (sensor2dropdown.options.length>1){ //if there is more than one sensor
                for (let i=0; i<sensor2dropdown.options.length; i++){
                    if (sensor2dropdown.options[i].value != sensor1){
                        sensor2dropdown.selectedIndex = i;
                        sensor2 = sensor2dropdown.value;
                        break;
                    }
                }
            }
        }
        //Uncheck the compare average trend checkbox
        document.getElementById('compareAverageTrend').checked = false;
        comparingAverageTrend=false;
        comparingSensors=true;
    } else {
        // Hide the second sensor dropdown
        sensor2Div.classList.add('hidden');
        comparingSensors=false;
        sensor2= undefined;
    }
    fetchData();
}
function toggleCompareAverageTrend(checkbox) {
    if (checkbox.checked) {
        //Uncheck the sensor comparison checkbox
        document.getElementById('compareTwoSensors').checked = false;
        let sensor2Div = document.getElementById('sensor2div');
        sensor2Div.classList.add('hidden'); //hide the second sensor dropdown
        comparingSensors=false;
        comparingAverageTrend=true;

    }else{
        comparingAverageTrend=false;
    }
    fetchData();
}
    
function sensorIdChanged() {
    sensor1 = document.getElementById("sensor1").value;
    sensor2 = document.getElementById("sensor2").value;
    fetchData();
}

function dateRange() {
    let date = document.getElementById("dateFilter").value;
    let start_datetime = `${date} 00:00:00`;
    let end_datetime = `${date} 23:59:59`;
    return [start_datetime, end_datetime];
}




function chartTypeChanged(event) {
    // Remove active class from all buttons
    document.querySelectorAll('.chartTypes').forEach((btn) => {
        btn.classList.remove('bg-blue-500', 'text-white');
        btn.classList.add('bg-gray-200', 'text-gray-700');
    });
    // Add active class to the clicked button
    event.currentTarget.classList.remove('bg-gray-200', 'text-gray-700');
    event.currentTarget.classList.add('bg-blue-500', 'text-white');
    //Get the chart type
    chartType = event.currentTarget.textContent;
    fetchData();
}


// dateChanged(); 
function fetchData(){
    let sensorQuery;
    let periodQuery;
    let chartQuery;
    if (!sensor1) { //if no sensor is selected, return
        return;
    }
    if (comparingSensors) { //if comparing two sensors
        if (!sensor2 || sensor2 == sensor1){ //if no second sensor is selected or the second sensor is the same as the first one, return
            return;
        }
        sensorQuery = `sensor_one=${sensor1}&sensor_two=${sensor2}`; 
    } else if (comparingAverageTrend){ //if comparing the average trend
        sensorQuery = `sensor_one=${sensor1}&compare_average_trend=True`; 
    }
    else { //if only one sensor is selected
        sensorQuery = `sensor_one=${sensor1}`;
    }
    let period = dateRange();
    if (period.length !=2){ //if period range is not 2, return
            return;
        }
    periodQuery = `&start_date=${period[0]}&end_date=${period[1]}`; //get the start and end date of the period
    chartQuery = `&chart_type=${chartType}`; //get the chart type

    fetch(`/sensors-data/?${sensorQuery}${periodQuery}${chartQuery}`)
    .then(response => response.json()).then(data => 
        {   if (data && data.minutely_data){
                updateCharts(data.minutely_data);
            }
    }).catch(error => {
        console.error('Error fetching data:', error)});
}



let chartsArray = {};

// var data= [{
//     x: 10,
//     y: 20
// }, {
//     x: 15,
//     y: 10
// }]


function newChartObj(chartId,label, color){
    let ctx= document.getElementById(chartId).getContext('2d');
    chartsArray[label] = new Chart(ctx, {
        type: 'scatter', //bar, horizontalBar, pie, line, doughnut, radar, polarArea//bar, horizontalBar, pie, line, doughnut, radar, polarArea
        data: {
            datasets: [
                {
                label: "",
                //disabling the label for now
                // type: 'line',
                data: [],
                // borderColor: 'green',
                // borderWidth: 1.5,
                backgroundColor: 'rgba(0, 255, 0, 0.1)',
                // yAxisID: 'y',
                // lineTension: 0.3,
                // radius: 0,
                // fill: true,
            },
            {
                label: "",
                // type: 'line',
                data: [],
                // backgroundColor: 'rgba(240, 75, 75, 0.8)',
                // borderColor: 'orange',
                // // borderWidth: 1.5,
                backgroundColor: 'rgba(255, 165, 0, 0.1)',
                // // yAxisID: 'y2',
                // lineTension: 0.3,
                // radius: 0,
                // fill: true,
            }        
        ]
        },
        options: {

            // scales: {
            //     x: {
            //         type: 'time'
            //         // ticks: {
            //         //     maxRotation: 90,
            //         //     minRotation: 90
            //         // }
            //     },
                
            //     y: {
            //         type: 'linear',
            //         display: true,
            //         position: 'left',
            //         title: {
            //             display: true,
            //             text: 'µg/m³'
            //         }
            //     },
            // }, 
            plugins: {
                legend: {
                    display: true,
                    },                
                zoom: {
                    zoom: {
                        drag: {
                            enabled: true,
                            backgroundColor: 'rgba(159, 179, 255, 0.5)',
                            borderColor: 'rgba(99, 119, 255, 1)',
                            borderWidth: 1,
                        }
                    }
                }
            },
            responsive: true,
            maintainAspectRatio: false,
            aspectRatio: 1
            }
   });
    chartsArray[label].update();
}


// function newChartObj(chartId,label, color){
//     let ctx= document.getElementById(chartId).getContext('2d');
//     chartsArray[label] = new Chart(ctx, {
//             type: 'scatter',
//             data: {
//                 datasets: [{
//                     data: data,
//                     options: {
//                         scales: {
//                             x: {
//                                 // type: 'linear',
//                                 // position: 'bottom'
//                             }
//                         }
//                     }
//                 }]
//             }
//           });
//     chartsArray[label].update();
// }

const parameters = ['NO2','ParticulatePM10', 'ParticulatePM2_5'];

if (document.getElementById('allCharts')) {
    // const colors = ['rgba(255, 99, 132, 0.6)', 'rgba(255, 159, 64, 0.6)', 'rgba(255, 206, 86, 0.6)', 'rgba(75, 192, 192, 0.6)', 'rgba(54, 162, 235, 0.6)'];
    for (let param of parameters){
        newChartObj(`${param.toLowerCase()}Chart`, param);
    }
}


function updateCharts(data){
    // let correlations=receivedData.correlations;
    // // for (let param of parameters){
    // //     let correlationDiv = document.getElementById(`${param.toLowerCase()}Correlation`);
    // //     correlationDiv.textContent = '';
    // //     let chartObj = chartsArray[param];
    // //     chartObj.data.datasets[0].data = [];
    // //     chartObj.data.datasets[1].data = [];
    // //     chartObj.update();
    // // }

    // if (correlations){
    //     for (let param of parameters){
    //         let correlation = correlations[param.toLowerCase()];
    //         if (correlation){
    //             let correlationDiv = document.getElementById(`${param.toLowerCase()}Correlation`);
    //             correlationDiv.textContent = `Correlation: ${correlation}`;
    //         }
    //         else{
    //             let correlationDiv = document.getElementById(`${param.toLowerCase()}Correlation`);
    //             correlationDiv.textContent = '';
    //         }
    //     }
    // }
    // else{
    // }
    if (!comparingSensors){
        for (let param of parameters){
            let chartObj = chartsArray[param];
            if (chartObj.data.datasets[1]){
                chartObj.data.datasets[1].data = [];
                chartObj.update();
            }
        }
    }
        // //Set the labels hours 00:00 to 23:00
        if (data){
            // console.log(data);
            if (chartType=='Scatter' && data.length==2){
                let id1 =Object.values(data[0])[0]
                let id2 =Object.values(data[1])[0]
                for (let param of parameters){
                    let chartObj = chartsArray[param];
                    let scatterData = [];   
                    let param_lower = param.toLowerCase();
                    for (let i=0; i<id1[param_lower].length; i++){
                        scatterData.push({x: id1[param_lower][i], y: id2[param_lower][i]});
                    // }
                    }
                    chartObj.data.datasets= [{
                        'type': 'scatter',
                        'label': 'Scatter Plot'
                    }]
                    chartObj.options.scales= {}

                    chartObj.data.datasets[0].data = scatterData;
                    chartObj.data.datasets[0].backgroundColor = 'rgba(0, 0, 0, 0.1)';

                    chartObj.update();
                }
            }
            else if (chartType=='Bar' && comparingSensors){
                console.log(data);
                // let labels=Object.keys(data);
                for (let param of parameters){

                    let chartObj = chartsArray[param];
                    // chartObj.type= 'bar';
                    chartObj.data.labels = Object.keys(data[param.toLowerCase()]).map( x => parseFloat(x));
                    chartObj.data.datasets= [{
                        label: `Difference in ${param}`,
                        type: 'bar',
                        data: Object.values(data[param.toLowerCase()]),
                        backgroundColor: 'rgba(0, 255, 0, 0.4)',
                        // borderColor: 'green',
                        // borderWidth: 1.5,
                        // lineTension: 0.3,
                        // radius: 0,
                        // fill: true,
                    }]
                    chartObj.options.scales= {
                        xAxes: [{
                            display: false,
                            barPercentage: 1.3,
                            ticks: {
                              max: 3,
                            }
                          }, {
                            display: true,
                            ticks: {
                              autoSkip: false,
                              max: 4,
                            }
                          }],
                          yAxes: [{
                            ticks: {
                              beginAtZero: true
                            }
                          }]
                    }
                    chartObj.update();
                }
                // chartObj.data.datasets[i].type=chartType.toLowerCase(); //set the chart type

            }
            else if (chartType=='Line'){
                // console.log('here');
                let time= Object.values(data)[0];
                // console.log(time);
                for (let param of parameters){
                    let chartObj = chartsArray[param];
                    chartObj.data.datasets= [{
                        label: "",
                        //disabling the label for now
                        // type: 'line',
                        data: [],
                        borderColor: 'green',
                        borderWidth: 1.5,
                        backgroundColor: 'rgba(0, 255, 0, 0.1)',
                        yAxisID: 'y',
                        lineTension: 0.3,
                        radius: 0,
                        fill: true,
                        },
                    {
                        label: "",
                        // type: 'line',
                        data: [],
                        backgroundColor: 'rgba(240, 75, 75, 0.8)',
                        borderColor: 'orange',
                        borderWidth: 1.5,
                        backgroundColor: 'rgba(255, 165, 0, 0.1)',
                        // yAxisID: 'y2',
                        lineTension: 0.3,
                        radius: 0,
                        fill: true,
                        }        
                ]
                    chartObj.options.scales= {
                        x: {
                            type: 'time'
                        },
                        
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: 'µg/m³'
                            }
                        },
                    }
                }
                    // let curData = time.map(label => sensorData[label]);
                    // console.log(sensorData);
                    for (let param of parameters){
                        let chartObj = chartsArray[param];
                        chartObj.data.datasets[0].label = `${sensor1}`
                        // chartObj.data.labels = time.map(label => label.slice(5,16)); //x-axis labels
                        //Map the time as JS Date objects
                        chartObj.data.labels = time.map(x => new Date(x));
                        chartObj.data.datasets[0].data = data[param.toLowerCase()]; //x-axis data
                        // chartObj.data.datasets[i].type='bar'; //set the chart type
                        chartObj.data.datasets[0].type=chartType.toLowerCase(); //set the chart type

                    }
                parameters.forEach(param => { chartsArray[param].update();});
            }
        }

}


//Set the date filter to default date
document.getElementById("dateFilter").value = new Date().toISOString().slice(0,10);
fetchData();




   // let sensor_locations = JSON.parse(document.getElementById('sensor_locations').textContent);
if (document.getElementById('map')) {
    var mapObject=createMap([51.505, -0.09], 13);
 var markerFeatureGroup = L.featureGroup()
 mapObject.addLayer(markerFeatureGroup);
 }
//Create a map object and set the center and zoom level
function createMap(center, zoom){
    let map=L.map('map').setView(center, zoom);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { 
        maxZoom: 19, //Max zoom level
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>' //Attribution (bottom bar)
    }).addTo(map);
    return map;
}



// const ctx = document.getElementById('no2Chart').getContext('2d');

// // Example labels for each hour of the day
// const labels = [
//     '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', 
//     '00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', 
//     '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00'
//   ];
  
//   // Example data for PM2.5
//   const pm25Data = [
//     5, 4, 6, 3, 5, 4, 6, 3, 5, 4, 6, 3, 7, 8, 9, 7, 
//     8, 9, 10, 9, 8, 10, 11, 9
//   ];
  
//   // Example data for PM10
//   const pm10Data = [
//     20, 22, 19, 18, 21, 20, 22, 19, 21, 20, 19, 18, 23, 24, 25, 23, 
//     24, 25, 26, 25, 24, 26, 27, 25
//   ];
  
//   // Chart.js configuration
//   const airQualityChart = new Chart(ctx, {
//       type: 'line',
//       data: {
//           labels: labels,
//           datasets: [{
//                 label: 'PM2.5',
//                 data: pm25Data,
//                 borderColor: 'green',
//                 borderWidth: 1.5,
//                 backgroundColor: 'rgba(0, 255, 0, 0.1)',
//                 yAxisID: 'y',
//                 lineTension: 0.4,
//                 radius: 0,
//                 fill: true,
//           }, {
//                 label: 'PM10',
//                 data: pm10Data,
//                 borderColor: 'orange',
//                 borderWidth: 1.5,
//                 backgroundColor: 'rgba(255, 165, 0, 0.1)',
//                 yAxisID: 'y1',
//                 lineTension: 0.4,
//                 radius: 0,
//                 fill: true, 
//           }]
//       },
//       options: {
//           scales: {
//               y: {
//                   type: 'linear',
//                   display: true,
//                   position: 'left',
//                   title: {
//                     display: true,
//                     text: 'Concentration (µg/m³)'
//                   }
//               },
//               y1: {
//                   type: 'linear',
//                   display: true,
//                   position: 'right',
//                   grid: {
//                     drawOnChartArea: false, // only want the grid lines for one axis to show up
//                   },
//                   title: {
//                     display: true,
//                     text: 'Concentration (µg/m³)'
//                   }
//               }
//           }
//       }
//   });
  