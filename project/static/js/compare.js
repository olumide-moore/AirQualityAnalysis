
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

function switchDaysComparisonTab(event, tabName) {
  //Restyle the tabs
  let tabs = document.querySelectorAll(".multiChartComparisonTabs");
  tabs.forEach((tab) => {
    tab.className = tab.className.replace("font-bold bg-white", "");
  });
  // Highlight the current tab
  event.currentTarget.className += " font-bold bg-white";

  let sensortype1 = document.getElementById("sensorType1").value;
  let sensorid1 = document.getElementById("sensorId1").value;
  let sensortype2 = document.getElementById("sensorType2").value;
  let sensorid2 = document.getElementById("sensorId2").value;
  let date = document.getElementById("dateInput").value;
 
  let dates = [date];
  let dateObj = new Date(date);
  if (tabName == "Last7Days") {
    //Get the last 7 days
    for (let i = 1; i < 7; i++) {
      let newDate = new Date(dateObj);
      newDate.setDate(dateObj.getDate() - i);
      dates.push(newDate.toISOString().slice(0, 10));
    }
  }else if(tabName == "SameDayLast7Weeks"){
    //Get the same day of the week for the last 7 weeks
    for (let i = 1; i < 7; i++) {
      let newDate = new Date(dateObj);
      newDate.setDate(dateObj.getDate() - i*7);
      dates.push(newDate.toISOString().slice(0, 10));
    }
  }
  dates=dates.join(',');
  fetch(`/compare-sensors-days/${sensortype1}/${sensorid1}/${sensortype2}/${sensorid2}/${dates}`)
    .then((response) => response.json())
    .then((data) => { 
      if (data) {
        updateDaysBoxPlot(data);
      }
      // console.log(data);
      // updateComparisonMultiCharts(data);
    })   
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
      responsive: true,
      maintainAspectRatio: false,
      aspectRatio: 1,
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
              // label: label,
              //disabling the label for now
              data: [],
              backgroundColor: "rgba(168,220,84, 1)",
          //     // borderColor: 'rgb(255, 99, 132)',
          //     // borderWidth: 1,
          //     // barThickness: 10,
          //     // maxBarThickness: 8,
          //     // hoverBorderColor: "rgba(234, 236, 244, 1)",
          //     // hoverBorderWidth: 3
          },
          {
              // label: label,
              //disabling the label for now
              data: [],
              backgroundColor: "rgba(256,220,44, 1)",
          }]
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
        // let firsthour1 = sensor1param[0];
        // let firsthour2 = sensor2param[0];
        // chartObj.data.datasets[0].data = [firsthour1];
        // chartObj.data.datasets[1].data = [firsthour2];
        chartObj.data.datasets[0].data = curData1;
        chartObj.data.datasets[1].data = curData2;

        chartObj.data.datasets[0].label = `ID: ${sensor1data.id}`; //label
        chartObj.data.datasets[1].label = `ID: ${sensor2data.id}`; //label
        chartObj.options.plugins.legend.display = true;
        chartObj.update();
        }
  }
}

function updateDaysBoxPlot(data) {
  if (data) {
    let sensor1data = data.sensor1;
    let sensor2data = data.sensor2;
    for (let param of parameters) {
        let chartObj = document.getElementById(
            `${param.toLowerCase()}DaysBoxPlot`
        ).chartInstance;
        chartObj.data.labels = sensor1data.dates;
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
    if (correlations.no2) no2 = correlations.no2;
    if (correlations.pm2_5) pm2_5 = correlations.pm2_5;
    if (correlations.pm10) pm10 = correlations.pm10;
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


  if(!(isString(sensortype1) && isInteger(sensorid1)  && isString(sensortype2) && isInteger(sensorid2) && isValidDate(date))) {
    return;
  }
  fetch(`/compare-sensors-data/${sensortype1}/${sensorid1}/${sensortype2}/${sensorid2}/${date}`)
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
            updateCompareLineCharts(data.rawdata);
            updateScatterPlot(data.rawdata);
            updateBoxPlot(data.hourly_rawdata);
            updateCorrelationCards(data.correlations);

          }
          })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
}

    

//Create the chart objects
for (let param of parameters) {
  createLineChartObj(`${param.toLowerCase()}LineChart`);
  createScatterPlotObj(`${param.toLowerCase()}ScatterPlot`);
  createBoxPlotChartObj(`${param.toLowerCase()}BoxPlot`);
  createBoxPlotChartObj(`${param.toLowerCase()}DaysBoxPlot`);
}

//Select the raw data tab by default
document.getElementById("rawDataTab").click();