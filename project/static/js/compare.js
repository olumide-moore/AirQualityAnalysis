
function switchChartTypeTab(event, tabName) {
  //Restyle the tabs
  let tabs = document.querySelectorAll(".chartTypeTabs");
  tabs.forEach((tab) => {
    tab.className = tab.className.replace("font-bold bg-white", "");
  });

  // Highlight the current tab
  event.currentTarget.className += " font-bold bg-white";
  if (tabName == "RawDtaMultiLineCharts") {
    document.getElementById("rawdataMultiLineCharts").style.display = "block";
    document.getElementById("scatterPlots").style.display = "none";
    document.getElementById("hourlyBoxPlots").style.display = "none";
  } else if (tabName == "ScatterPlots") {
    document.getElementById("rawdataMultiLineCharts").style.display = "none";
    document.getElementById("scatterPlots").style.display = "block";
    document.getElementById("hourlyBoxPlots").style.display = "none";
  } else if (tabName == "HourlyBoxPlots") {
    document.getElementById("rawdataMultiLineCharts").style.display = "none";
    document.getElementById("scatterPlots").style.display = "none";
    document.getElementById("hourlyBoxPlots").style.display = "block";
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
          // label: "Scatter Plot",
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
      responsive: true,
      maintainAspectRatio: false,
      aspectRatio: 1,
      plugins: {
        legend: {
          display: false,
        },
      }
    },
  });
  canvas.chartInstance.update();
}

function createBoxPlotChartObj(chartId){
  let canvas = document.getElementById(chartId);
  let ctx = canvas.getContext("2d");
  canvas.chartInstance = new Chart(ctx, {
      type: 'boxplot', //bar, horizontalBar, pie, line, doughnut, radar, polarArea//bar, horizontalBar, pie, line, doughnut, radar, polarArea
      data: {

          datasets: [{
                data: [],
                backgroundColor: "rgba(0,0,0, 0.4)",
                  },
                  {
                data: [],
                backgroundColor: "rgba(0, 120, 200, 0.4)",
            }],
      },
      options: {
          plugins: {
              legend: {
                  display: false,
                  }
              },
              responsive: true,
              maintainAspectRatio: false,
              aspectRatio: 1

          }
 });
  canvas.chartInstance.update();
}

function updateCompareLineCharts(data) {
  if (data) {
      // if (!data.sensor1 || !data.sensor2) return;
      let sensor1data = data.sensor1;
      let sensor2data = data.sensor2;
      let time1 = sensor1data.time.map((x) => new Date(x));
      let time2 = sensor2data.time.map((x) => new Date(x));
      for (let param of parameters) {
        let chartObj = document.getElementById(
            `${param.toLowerCase()}LineChart`
        ).chartInstance;
        let lineData = [];
        let lineData2 = [];
        for (let i = 0; i < time1.length; i++) {
            lineData.push({
                x: time1[i],
                y: sensor1data[param.toLowerCase()][i],
            });
        }
        for (let i = 0; i < time2.length; i++) {
            lineData2.push({
                x: time2[i],
                y: sensor2data[param.toLowerCase()][i],
            });
        }
        chartObj.data.datasets[0].data = lineData; //data
        chartObj.data.datasets[1].data = lineData2; //data
        chartObj.data.datasets[0].label = `ID: ${sensor1data.id}`; //label
        chartObj.data.datasets[1].label = `ID: ${sensor2data.id}`; //label
        chartObj.options.plugins.legend.display = true;
        // chartObj.options.spanGaps = true;
        chartObj.update();
    }  
  }
}

function updateAvgData(data) {
  if (data) {
    let sensor1info = data.sensor1;
    let sensor2info = data.sensor2;
    if (sensor1info.no2) document.getElementById("table-no2Value1 ").textContent = sensor1info.no2;
    if (sensor1info.pm2_5) document.getElementById("table-pm2_5Value1").textContent = sensor1info.pm2_5;
    if (sensor1info.pm10) document.getElementById("table-pm10Value1").textContent = sensor1info.pm10;
    if (sensor2info.no2) document.getElementById("table-no2Value2").textContent = sensor2info.no2;
    if (sensor2info.pm2_5) document.getElementById("table-pm2_5Value2").textContent = sensor2info.pm2_5;
    if (sensor2info.pm10) document.getElementById("table-pm10Value2").textContent = sensor2info.pm10;
  }
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

function updateBoxPlot(data) {
  if (data) {
    let sensor1data = data.sensor1;
    let sensor2data = data.sensor2;
    for (let param of parameters) {
        let chartObj = document.getElementById(
            `${param.toLowerCase()}BoxPlot`
        ).chartInstance;
        chartObj.data.labels = sensor1data.time;
        let param_lower = param.toLowerCase();
        let curData1 = sensor1data[param_lower];
        let curData2 = sensor2data[param_lower];
        chartObj.data.datasets[0].data = curData1;
        chartObj.data.datasets[1].data = curData2;

        chartObj.data.datasets[0].label = `ID: ${sensor1data.id}`; //label
        chartObj.data.datasets[1].label = `ID: ${sensor2data.id}`; //label
        chartObj.options.plugins.legend.display = true;
        chartObj.update();
        }
  }
}

function updateCorrelationCards(correlations) {
  let no2=""; let pm2_5=""; let pm10="";
  if (correlations) {
    if (correlations.no2 != null) no2 = correlations.no2;
    if (correlations.pm2_5 != null) pm2_5 = correlations.pm2_5;
    if (correlations.pm10 != null) pm10 = correlations.pm10;
  }
  document.getElementById("no2correlation").textContent = no2;
  document.getElementById("pm2_5correlation").textContent = pm2_5;
  document.getElementById("pm10correlation").textContent = pm10;
}

function fetchData() {
  let sensortype1 = document.getElementById("sensorType1").value;
  let sensorid1 = document.getElementById("sensorId1").value;

  let sensortype2 = document.getElementById("sensorType2").value;
  let sensorid2 = document.getElementById("sensorId2").value;
  let date=document.getElementById("dateInput").value;
  let corravginterval = document.getElementById("corravginterval").value;
  corravginterval = parseInt(corravginterval);


  if(!(isString(sensortype1) && isInteger(sensorid1)  && isString(sensortype2) && isInteger(sensorid2) && isValidDate(date) && isInteger(corravginterval))) {
    return;
  }
  fetch(`/sensors/compare/${sensortype1}/${sensorid1}/and/${sensortype2}/${sensorid2}/date/${date}/corravginterval/${corravginterval}`)
    .then((response) => response.json())
    .then((data) => {
      if (data) {
            let sensor1info= data.sensors_info['sensor1'];
            let sensor2info= data.sensors_info['sensor2'];
            document.getElementById("table-sensorType1").textContent = sensor1info.type;
            document.getElementById("table-sensorId1").textContent = sensor1info.id;
            if (sensor1info.last_updated){
              let last_updated = new Date(sensor1info.last_updated);
              document.getElementById("table-lastUpdated1").textContent = relativeTime(last_updated);
            }else{
              document.getElementById("table-lastUpdated1").textContent = "No data";
            }
            document.getElementById("table-sensorType2").textContent = sensor2info.type;
            document.getElementById("table-sensorId2").textContent = sensor2info.id;
            if (sensor2info.last_updated){
              last_updated = new Date(sensor2info.last_updated);
              document.getElementById("table-lastUpdated2").textContent = relativeTime(last_updated);
            }else{
              document.getElementById("table-lastUpdated2").textContent = "No data";
            }
            updateAvgData(data.avg_data);
            updateCompareLineCharts(data.rawdata);
            updateScatterPlot(data.rawdata);
            updateBoxPlot(data.hourly_rawdata);
            updateCorrelationCards(data.correlations);

            //Whichever tab is active between last 7 days and same day last 7 weeks, update the data
            let activeTab = document.querySelector(".multiChartComparisonTabs.font-bold.bg-white");
            if (activeTab && activeTab.id) {
              document.getElementById(activeTab.id).click();
            }
            }
          })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
}

function updateCorrelation() {
  let sensortype1 = document.getElementById("sensorType1").value;
  let sensorid1 = document.getElementById("sensorId1").value;
  let sensortype2 = document.getElementById("sensorType2").value;
  let sensorid2 = document.getElementById("sensorId2").value;
  let date=document.getElementById("dateInput").value;
  let corravginterval = document.getElementById("corravginterval").value;
  corravginterval = parseInt(corravginterval);
  if(!(isString(sensortype1) && isInteger(sensorid1)  && isString(sensortype2) && isInteger(sensorid2) && isValidDate(date))) {
    return;
  }
  fetch(`/sensors/compare-correlation/${sensortype1}/${sensorid1}/and/${sensortype2}/${sensorid2}/date/${date}/corravginterval/${corravginterval}`)
    .then((response) => response.json())
    .then((data) => {
      if (data) {
        updateCorrelationCards(data.correlations);
      }
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
}

async function initializeInputs() {
  await sensorTypeChanged(2, fetchdata=false); // Ensure this completes before proceeding
  
  let sensorTypeDropDown = document.getElementById("sensorType1"); 
  if (init_sensorType1 != "None") sensorTypeDropDown.value = init_sensorType1; //set the sensor type dropdown to the initial value
  
  let newtypeid = sensorTypeDropDown.options[sensorTypeDropDown.selectedIndex].getAttribute("data-id");
  let sensorIdDropdown = document.getElementById("sensorId1");
  if (init_date != "None") document.getElementById('dateInput').value = init_date;
  updateSensorIdsDropDown(sensorIdDropdown, newtypeid); //populate sensor ids of first sensor list
  
  if (init_sensorId1 != "None") sensorIdDropdown.value = `${init_sensorId1}`;
  fetchData();

}


//Unhide the sensor Type 2 and sensor ID 2 dropdowns by defaults
document.getElementById("sensorTypeDiv2").style.display = "block";
document.getElementById("sensorIdDiv2").style.display = "block";

    

//Create the chart objects
for (let param of parameters) {
  createLineChartObj(`${param.toLowerCase()}LineChart`);
  createScatterPlotObj(`${param.toLowerCase()}ScatterPlot`);
  createBoxPlotChartObj(`${param.toLowerCase()}BoxPlot`);
}


window.onload = function() {
  initializeInputs().then(() => {
    //Select the hourly data tab by default
    document.getElementById("rawdataTab").click();
  });
  
}