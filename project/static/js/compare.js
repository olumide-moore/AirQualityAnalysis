function fetchSensorIDs() {
  let sensorType = document.getElementById("sensortype");
  let selectedOption = sensorType.options[sensorType.selectedIndex];
  let typeid = selectedOption.getAttribute("data-id");
  fetch(`/sensors-ids/${typeid}`)
      .then((response) => response.json())
      .then((data) => {
      let sensorIdSelect1 = document.getElementById("sensorid1");
      let sensorIdSelect2 = document.getElementById("sensorid2");
      if (sensorIdSelect1) sensorIdSelect1.innerHTML = "";
      if (sensorIdSelect2) sensorIdSelect2.innerHTML = "";
      data.sensors.forEach((sensor) => {
          let option = document.createElement("option");
          option.value = sensor.id;
          option.text = sensor.id;
          if (sensorIdSelect1) sensorIdSelect1.add(option);
          if (sensorIdSelect2) sensorIdSelect2.add(option.cloneNode(true));
      });
      fetchComparisonData();
      })
      .catch((error) => {
      console.error("Error fetching sensor IDs:", error);
      });
  }

function fetchComparisonData() {
    let sensortype = document.getElementById("sensortype").value;
    let sensorid = document.getElementById("sensorid1").value;

    let sensortype2 = document.getElementById("sensortype").value;
    let sensorid2 = document.getElementById("sensorid2").value;


    if (!sensortype || !sensorid || !sensortype2 || !sensorid2) return; //if no sensor is selected, return
    
    let date=document.getElementById("dateFilter").value;
    fetch(`/compare-sensors-data/${sensortype}/${sensorid}/${sensortype2}/${sensorid2}/${date}`)
      .then((response) => response.json())
      .then((data) => {
        if (data) {
            // if (data.last_updated) {
            //     let lastUpdated = new Date(
            //       `${data.last_updated["obs_date"]} ${data.last_updated["obs_time_utc"]}`
            //     );
            //     document.getElementById("lastUpdated").textContent =
            //       relativeTime(lastUpdated);
            //   } else {
            //     document.getElementById("lastUpdated").textContent = "No data";
            //   }
              let sensor1info= data.sensors_info['sensor1'];
              let sensor2info= data.sensors_info['sensor2'];
              document.getElementById("sensorType1").textContent = sensor1info.type;
              document.getElementById("sensorId1").textContent = sensor1info.id;
              if (sensor1info.last_updated){
                let last_updated = new Date(`${sensor1info.last_updated["obs_date"]} ${sensor1info.last_updated["obs_time_utc"]}`);
                document.getElementById("lastUpdated1").textContent = relativeTime(last_updated);
              }else{
                document.getElementById("lastUpdated1").textContent = "No data";
              }
              document.getElementById("sensorType2").textContent = sensor2info.type;
              document.getElementById("sensorId2").textContent = sensor2info.id;
              if (sensor2info.last_updated){
                last_updated = new Date(`${sensor2info.last_updated["obs_date"]} ${sensor2info.last_updated["obs_time_utc"]}`);
                document.getElementById("lastUpdated2").textContent = relativeTime(last_updated);
              }else{
                document.getElementById("lastUpdated2").textContent = "No data";
              }
              updateCompareLineCharts(data.minutely_avgs);
              updateScatterPlot(data.minutely_avgs);
              // updateHourlyAvgCharts(data.hourly_avgs, data.hourly_aqis);
              // updateAQICards(data.aqi_data);
              // avgData = data.avg_data;
              // if (avgData) {
              //   //Update the average values in the aqi card and the table
              //   Array.from(document.getElementsByClassName("no2Value")).forEach(
              //     (element) => {
              //       element.textContent = avgData.no2;
              //     }
              //   );
      
              //   Array.from(document.getElementsByClassName("pm2_5Value")).forEach(
              //     (element) => {
              //       element.textContent = avgData.pm2_5;
              //     }
              //   );
      
              //   Array.from(document.getElementsByClassName("pm10Value")).forEach(
              //     (element) => {
              //       element.textContent = avgData.pm10;
              //     }
              //   );
              // }
              // //Update the sensor type and id in the table
              // document.getElementById("sensorType").textContent = sensortype;
              // document.getElementById("sensorId").textContent = sensorid;
      
            }
            })
      .catch((error) => {
        console.error("Error fetching data:", error);
      });
  }

function updateCompareLineCharts(data) {

  if (data) {
      if (!data.sensor1 || !data.sensor2) return;
      let sensor1data = data.sensor1;
      let sensor2data = data.sensor2;
      let time = sensor1data.time;
      for (let param of parameters) {
          let chartObj = document.getElementById(
              `${param.toLowerCase()}LineChart`
          ).chartInstance;
          chartObj.data.labels = time.map((x) => new Date(x)); //x-axis labels
          let curData= sensor1data[param.toLowerCase()];
          let curData2= sensor2data[param.toLowerCase()];
          chartObj.data.datasets[0].data = curData.map((x) => x==null? Number.NaN: x); //y-axis data
          chartObj.data.datasets[1].data = curData2.map((x) => x==null? Number.NaN: x); //y-axis data
          chartObj.data.datasets[0].label = `ID: ${sensor1data.id}`; //label
          chartObj.data.datasets[1].label = `ID: ${sensor2data.id}`; //label
          chartObj.options.plugins.legend.display = true;
          // chartObj.options.spanGaps = true;
          chartObj.update();
  }  

      // let time = data.time;
      // // console.log(time);
      // // let curData = time.map(label => sensorData[label]);
      // // console.log(sensorData);
      // for (let param of parameters) {
      //   let chartObj = document.getElementById(
      //     `${param.toLowerCase()}LineChart`
      //   ).chartInstance;
      // //   chartObj.data.datasets[0].label = `Minutely ${param.toUpperCase()}`; //label
      //   // chartObj.data.labels = time.map(label => label.slice(5,16)); //x-axis labels
      //   //Map the time as JS Date objects
      //   chartObj.data.labels = time.map((x) => new Date(x)); //x-axis labels
      //   chartObj.data.datasets[0].data = data[param.toLowerCase()]; //y-axis data
      //   chartObj.update();
      // }
  }
}


function createScatterPlotObj(chartId) {
  let canvas = document.getElementById(chartId);
  let ctx = canvas.getContext("2d");
  canvas.chartInstance = new Chart(ctx, {
    type: "scatter", //bar, horizontalBar, pie, line, doughnut, radar, polarArea//bar, horizontalBar, pie, line, doughnut, radar, polarArea
    data: {
      datasets: [
        {
          label: "Scatter Plot",
          data: [],
          backgroundColor: "rgba(0, 0, 0, 0.1)",
        },
      ],
    },
    options: {
      scales: {
        x: {
          // type: 'linear',
          // position: 'bottom'
        },
      },
    },
  });
  canvas.chartInstance.update();
}

function updateScatterPlot(data) {
  if (data) {
    let sensor1data = data.sensor1;
    let sensor2data = data.sensor2;
    for (let param of parameters) {
        let chartObj = document.getElementById(
            `${param.toLowerCase()}ScatterPlot`
        ).chartInstance;
        let scatterData = [];
        let param_lower = param.toLowerCase();
        for (let i = 0; i < sensor1data[param_lower].length; i++) {
            scatterData.push({
                x: sensor1data[param_lower][i],
                y: sensor2data[param_lower][i],
            });
        }
        chartObj.data.datasets[0].data = scatterData;
        chartObj.update();
      
    }
  }
}
    



for (let param of parameters) {
  createLineChartObj(`${param.toLowerCase()}LineChart`);
  createScatterPlotObj(`${param.toLowerCase()}ScatterPlot`);
}

fetchSensorIDs();

// //Hamburger menu
// const hamburger = document.querySelector('.hamburger');
// const navMenu = document.querySelector('.nav-menu');

// hamburger.addEventListener('click', () => {
//     hamburger.classList.toggle('active');
//     navMenu.classList.toggle('active');
// });
// //Ensure that the hamburger menu is hidden when a menu item is clicked
// const menuLinks = document.querySelectorAll('.nav-link');
// menuLinks.forEach((menuLink) => {
//     menuLink.addEventListener('click', () => {
//         hamburger.classList.remove('active');
//         navMenu.classList.remove('active');
//     });
// });

// var chartType='Line';
// var sensor1=document.getElementById("sensor1").value;
// var sensor2;
// var comparingSensors=false;
// var comparingAverageTrend=false;

// let currentDate = new Date();


// fetchData();
// // Function to handle the sensor comparison toggle
// function toggleSensorComparison(checkbox) {
//     let sensor2Div = document.getElementById('sensor2div');
//     if (checkbox.checked) {
//         // Show the second sensor dropdown
//         sensor2Div.classList.remove('hidden');
//         let sensor2dropdown = document.getElementById('sensor2');
//         sensor2 = sensor2dropdown.value;
//         if (sensor1 == sensor2){ //if the second sensor is the same as the first one, select the next sensor
//             if (sensor2dropdown.options.length>1){ //if there is more than one sensor
//                 for (let i=0; i<sensor2dropdown.options.length; i++){
//                     if (sensor2dropdown.options[i].value != sensor1){
//                         sensor2dropdown.selectedIndex = i;
//                         sensor2 = sensor2dropdown.value;
//                         break;
//                     }
//                 }
//             }
//         }
//         //Uncheck the compare average trend checkbox
//         document.getElementById('compareAverageTrend').checked = false;
//         comparingAverageTrend=false;
//         comparingSensors=true;
//     } else {
//         // Hide the second sensor dropdown
//         sensor2Div.classList.add('hidden');
//         comparingSensors=false;
//         sensor2= undefined;
//     }
//     fetchData();
// }
// function toggleCompareAverageTrend(checkbox) {
//     if (checkbox.checked) {
//         //Uncheck the sensor comparison checkbox
//         document.getElementById('compareTwoSensors').checked = false;
//         let sensor2Div = document.getElementById('sensor2div');
//         sensor2Div.classList.add('hidden'); //hide the second sensor dropdown
//         comparingSensors=false;
//         comparingAverageTrend=true;

//     }else{
//         comparingAverageTrend=false;
//     }
//     fetchData();
// }
    
// function sensorIdChanged() {
//     sensor1 = document.getElementById("sensor1").value;
//     sensor2 = document.getElementById("sensor2").value;
//     fetchData();
// }

// function dateRange() {
//     let date = document.getElementById("dateFilter").value;
//     let start_datetime = `${date} 00:00:00`;
//     let end_datetime = `${date} 23:59:59`;
//     return [start_datetime, end_datetime];
// }

// function getAQIColor(aqi){
// if (aqi==1) return '#a0fc9c'; //Low
// if (aqi==2) return '#38fc04'; //Low
// if (aqi==3) return '#38cc04'; //Low
// if (aqi==4) return '#fffc04'; //Moderate
// if (aqi==5) return '#fccc04'; //Moderate
// if (aqi==6) return '#ff9c04'; //Moderate
// if (aqi==7) return '#ff6464'; //High
// if (aqi==8) return '#ff0404'; //High
// if (aqi==9) return '#a00404'; //High
// if (aqi==10) return '#d034fc'; //Very High
// return '#626262'; //Unknown or no data
// }

// // function getAQIDescription(aqi){
// //     if (aqi==1) return 'Good'; //Low
// //     if (aqi==2) return 'Good'; //Low


// function updateAQICards(aqi_data){
//     let no2Div = document.getElementById('no2card');
//     let pm2_5Div = document.getElementById('pm2_5card');
//     let pm10Div = document.getElementById('pm10card');
//     no2aqi= getAQIColor(aqi_data.no2);
//     pm2_5aqi= getAQIColor(aqi_data.pm2_5);
//     pm10aqi= getAQIColor(aqi_data.pm10);
//     no2Div.style.backgroundColor = no2aqi;
//     pm2_5Div.style.backgroundColor = pm2_5aqi;
//     pm10Div.style.backgroundColor = pm10aqi;
// }
// function chartTypeChanged(event) {
//     // Remove active class from all buttons
//     document.querySelectorAll('.chartTypes').forEach((btn) => {
//         btn.classList.remove('bg-blue-500', 'text-white');
//         btn.classList.add('bg-gray-200', 'text-gray-700');
//     });
//     // Add active class to the clicked button
//     event.currentTarget.classList.remove('bg-gray-200', 'text-gray-700');
//     event.currentTarget.classList.add('bg-blue-500', 'text-white');
//     //Get the chart type
//     chartType = event.currentTarget.textContent;
//     fetchData();
// }


// // dateChanged(); 
// function fetchData(){
//     let sensorQuery;
//     let periodQuery;
//     let chartQuery;
//     if (!sensor1) { //if no sensor is selected, return
//         return;
//     }
//     if (comparingSensors) { //if comparing two sensors
//         if (!sensor2 || sensor2 == sensor1){ //if no second sensor is selected or the second sensor is the same as the first one, return
//             return;
//         }
//         sensorQuery = `sensor_one=${sensor1}&sensor_two=${sensor2}`; 
//     } else if (comparingAverageTrend){ //if comparing the average trend
//         sensorQuery = `sensor_one=${sensor1}&compare_average_trend=True`; 
//     }
//     else { //if only one sensor is selected
//         sensorQuery = `sensor_one=${sensor1}`;
//     }
//     let period = dateRange();
//     if (period.length !=2){ //if period range is not 2, return
//             return;
//         }
//     periodQuery = `&start_date=${period[0]}&end_date=${period[1]}`; //get the start and end date of the period
//     chartQuery = `&chart_type=${chartType}`; //get the chart type

//     fetch(`/sensors-data/?${sensorQuery}${periodQuery}${chartQuery}`)
//     .then(response => response.json()).then(data => 
//         {   if (data){
//                 updateAQICards(data.aqi_data);
//                 updateLineCharts(data.minutely_avgs);
//                 updateHourlyAvgCharts(data.hourly_avgs, data.hourly_aqis);
//             }
//     }).catch(error => {
//         console.error('Error fetching data:', error)});
// }



// let lineChartsObjsArray = {};

// // var data= [{
// //     x: 10,
// //     y: 20
// // }, {
// //     x: 15,
// //     y: 10
// // }]


// function newChartObj(chartId,label, color){
//     let ctx= document.getElementById(chartId).getContext('2d');
//     lineChartsObjsArray[label] = new Chart(ctx, {
//         type: 'scatter', //bar, horizontalBar, pie, line, doughnut, radar, polarArea//bar, horizontalBar, pie, line, doughnut, radar, polarArea
//         data: {
//             datasets: [
//                 {
//                 label: "",
//                 //disabling the label for now
//                 // type: 'line',
//                 data: [],
//                 // borderColor: 'green',
//                 // borderWidth: 1.5,
//                 backgroundColor: 'rgba(0, 255, 0, 0.1)',
//                 // yAxisID: 'y',
//                 // lineTension: 0.3,
//                 // radius: 0,
//                 // fill: true,
//             },
//             {
//                 label: "",
//                 // type: 'line',
//                 data: [],
//                 // backgroundColor: 'rgba(240, 75, 75, 0.8)',
//                 // borderColor: 'orange',
//                 // // borderWidth: 1.5,
//                 backgroundColor: 'rgba(255, 165, 0, 0.1)',
//                 // // yAxisID: 'y2',
//                 // lineTension: 0.3,
//                 // radius: 0,
//                 // fill: true,
//             }        
//         ]
//         },
//         options: {

//             // scales: {
//             //     x: {
//             //         type: 'time'
//             //         // ticks: {
//             //         //     maxRotation: 90,
//             //         //     minRotation: 90
//             //         // }
//             //     },
                
//             //     y: {
//             //         type: 'linear',
//             //         display: true,
//             //         position: 'left',
//             //         title: {
//             //             display: true,
//             //             text: 'µg/m³'
//             //         }
//             //     },
//             // }, 
//             plugins: {
//                 legend: {
//                     display: true,
//                     },                
//                 zoom: {
//                     zoom: {
//                         drag: {
//                             enabled: true,
//                             backgroundColor: 'rgba(159, 179, 255, 0.5)',
//                             borderColor: 'rgba(99, 119, 255, 1)',
//                             borderWidth: 1,
//                         }
//                     }
//                 }
//             },
//             responsive: true,
//             maintainAspectRatio: false,
//             aspectRatio: 1
//             }
//    });
//     lineChartsObjsArray[label].update();
// }


// // function newChartObj(chartId,label, color){
// //     let ctx= document.getElementById(chartId).getContext('2d');
// //     lineChartsObjsArray[label] = new Chart(ctx, {
// //             type: 'scatter',
// //             data: {
// //                 datasets: [{
// //                     data: data,
// //                     options: {
// //                         scales: {
// //                             x: {
// //                                 // type: 'linear',
// //                                 // position: 'bottom'
// //                             }
// //                         }
// //                     }
// //                 }]
// //             }
// //           });
// //     lineChartsObjsArray[label].update();
// // }

// const parameters = ['NO2','PM10', 'PM2_5'];

// if (document.getElementById('lineCharts')) {
//     // const colors = ['rgba(255, 99, 132, 0.6)', 'rgba(255, 159, 64, 0.6)', 'rgba(255, 206, 86, 0.6)', 'rgba(75, 192, 192, 0.6)', 'rgba(54, 162, 235, 0.6)'];
//     for (let param of parameters){
//         newChartObj(`${param.toLowerCase()}lineChart`, param);
//     }
// }

// function updateLineCharts(data){
//     // let correlations=receivedData.correlations;
//     // // for (let param of parameters){
//     // //     let correlationDiv = document.getElementById(`${param.toLowerCase()}Correlation`);
//     // //     correlationDiv.textContent = '';
//     // //     let chartObj = lineChartsObjsArray[param];
//     // //     chartObj.data.datasets[0].data = [];
//     // //     chartObj.data.datasets[1].data = [];
//     // //     chartObj.update();
//     // // }

//     // if (correlations){
//     //     for (let param of parameters){
//     //         let correlation = correlations[param.toLowerCase()];
//     //         if (correlation){
//     //             let correlationDiv = document.getElementById(`${param.toLowerCase()}Correlation`);
//     //             correlationDiv.textContent = `Correlation: ${correlation}`;
//     //         }
//     //         else{
//     //             let correlationDiv = document.getElementById(`${param.toLowerCase()}Correlation`);
//     //             correlationDiv.textContent = '';
//     //         }
//     //     }
//     // }
//     // else{
//     // }
//     if (!comparingSensors){
//         for (let param of parameters){
//             let chartObj = lineChartsObjsArray[param];
//             if (chartObj.data.datasets[1]){
//                 chartObj.data.datasets[1].data = [];
//                 chartObj.update();
//             }
//         }
//     }
//         // //Set the labels hours 00:00 to 23:00
//         if (data){
//             // console.log(data);
//             if (chartType=='Scatter' && data.length==2){
//                 let id1 =Object.values(data[0])[0]
//                 let id2 =Object.values(data[1])[0]
//                 for (let param of parameters){
//                     let chartObj = lineChartsObjsArray[param];
//                     let scatterData = [];   
//                     let param_lower = param.toLowerCase();
//                     for (let i=0; i<id1[param_lower].length; i++){
//                         scatterData.push({x: id1[param_lower][i], y: id2[param_lower][i]});
//                     // }
//                     }
//                     chartObj.data.datasets= [{
//                         'type': 'scatter',
//                         'label': 'Scatter Plot'
//                     }]
//                     chartObj.options.scales= {}

//                     chartObj.data.datasets[0].data = scatterData;
//                     chartObj.data.datasets[0].backgroundColor = 'rgba(0, 0, 0, 0.1)';

//                     chartObj.update();
//                 }
//             }
//             else if (chartType=='Bar' && comparingSensors){
//                 console.log(data);
//                 // let labels=Object.keys(data);
//                 for (let param of parameters){

//                     let chartObj = lineChartsObjsArray[param];
//                     // chartObj.type= 'bar';
//                     chartObj.data.labels = Object.keys(data[param.toLowerCase()]).map( x => parseFloat(x));
//                     chartObj.data.datasets= [{
//                         label: `Difference in ${param}`,
//                         type: 'bar',
//                         data: Object.values(data[param.toLowerCase()]),
//                         backgroundColor: 'rgba(0, 255, 0, 0.4)',
//                         // borderColor: 'green',
//                         // borderWidth: 1.5,
//                         // lineTension: 0.3,
//                         // radius: 0,
//                         // fill: true,
//                     }]
//                     chartObj.options.scales= {
//                         xAxes: [{
//                             display: false,
//                             barPercentage: 1.3,
//                             ticks: {
//                               max: 3,
//                             }
//                           }, {
//                             display: true,
//                             ticks: {
//                               autoSkip: false,
//                               max: 4,
//                             }
//                           }],
//                           yAxes: [{
//                             ticks: {
//                               beginAtZero: true
//                             }
//                           }]
//                     }
//                     chartObj.update();
//                 }
//                 // chartObj.data.datasets[i].type=chartType.toLowerCase(); //set the chart type

//             }
//             else if (chartType=='Line'){
//                 // console.log('here');
//                 let time= data.time;
//                 // console.log(time);
//                 for (let param of parameters){
//                     let chartObj = lineChartsObjsArray[param];
//                     chartObj.data.datasets= [{
//                         label: "",
//                         //disabling the label for now
//                         // type: 'line',
//                         data: [],
//                         borderColor: 'green',
//                         borderWidth: 1.5,
//                         backgroundColor: 'rgba(0, 255, 0, 0.1)',
//                         yAxisID: 'y',
//                         lineTension: 0.3,
//                         radius: 0,
//                         fill: true,
//                         },
//                     {
//                         label: "",
//                         // type: 'line',
//                         data: [],
//                         backgroundColor: 'rgba(240, 75, 75, 0.8)',
//                         borderColor: 'orange',
//                         borderWidth: 1.5,
//                         backgroundColor: 'rgba(255, 165, 0, 0.1)',
//                         // yAxisID: 'y2',
//                         lineTension: 0.3,
//                         radius: 0,
//                         fill: true,
//                         }        
//                 ]
//                     chartObj.options.scales= {
//                         x: {
//                             type: 'time'
//                         },
                        
//                         y: {
//                             type: 'linear',
//                             display: true,
//                             position: 'left',
//                             title: {
//                                 display: true,
//                                 text: 'µg/m³'
//                             }
//                         },
//                     }
//                 }
//                     // let curData = time.map(label => sensorData[label]);
//                     // console.log(sensorData);
//                     for (let param of parameters){
//                         let chartObj = lineChartsObjsArray[param];
//                         chartObj.data.datasets[0].label = `${sensor1}`
//                         // chartObj.data.labels = time.map(label => label.slice(5,16)); //x-axis labels
//                         //Map the time as JS Date objects
//                         chartObj.data.labels = time.map(x => new Date(x));
//                         chartObj.data.datasets[0].data = data[param.toLowerCase()]; //x-axis data
//                         // chartObj.data.datasets[i].type='bar'; //set the chart type
//                         chartObj.data.datasets[0].type=chartType.toLowerCase(); //set the chart type

//                     }
//                 parameters.forEach(param => { lineChartsObjsArray[param].update();});
//             }
//         }

// }


// const hourlyavgChartsObjsArray = {};
// for (let param of parameters){
//     let ctx= document.getElementById(`${param.toLowerCase()}HourlyAvgChart`).getContext('2d');
//     let chart = new Chart(ctx, {
//         type: 'bar',
//         data: {
//             labels: [],
//             datasets: [ {
//                 label: `Average ${param.toUpperCase()}` ,
//                 data: []
//             }]
//         },
//         options : {
//             scales: {
//                 x: {
//                     type: 'time'
//                 },
//                 y: {
//                     beginAtZero: true
//                 }
//             },
//             plugins: {
//                 tooltip: {
//                     enabled: true
//                 },
//                 legend: {
//                     display: true
//                 }
//             }
//         }
//     });
//     hourlyavgChartsObjsArray[param] = chart;
// }



// function updateHourlyAvgCharts(avgData,aqiData){

//     if (avgData){
//         let time= avgData.time;
//         if (time){
//             time = time.map(x => new Date(x));
//             for (let param of parameters){
//                 let chartObj = hourlyavgChartsObjsArray[param];
//                 // console.log(avgData[param.toLowerCase()]);
//                 if (chartObj){
//                     chartObj.data.labels = time;
//                     if (avgData[param.toLowerCase()]){
//                         chartObj.data.datasets[0].data = avgData[param.toLowerCase()];
//                         chartObj.data.datasets[0].backgroundColor = aqiData[param.toLowerCase()].map(x => getAQIColor(x));
//                         chartObj.update();
//                     }
//                 }
//             }
//         }
//     }
// }


// //Set the date filter to default date
// document.getElementById("dateFilter").value = new Date().toISOString().slice(0,10);
// fetchData();




//    // let sensor_locations = JSON.parse(document.getElementById('sensor_locations').textContent);
// if (document.getElementById('map')) {
//     var mapObject=createMap([51.505, -0.09], 13);
//  var markerFeatureGroup = L.featureGroup()
//  mapObject.addLayer(markerFeatureGroup);
//  }
// //Create a map object and set the center and zoom level
// function createMap(center, zoom){
//     let map=L.map('map').setView(center, zoom);
//     L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { 
//         maxZoom: 19, //Max zoom level
//         attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>' //Attribution (bottom bar)
//     }).addTo(map);
//     return map;
// }

