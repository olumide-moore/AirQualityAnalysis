function switchDaysComparisonTab(event, tabName) {
  //Restyle the tabs
  let tabs = document.querySelectorAll(".multiChartComparisonTabs");
  tabs.forEach((tab) => {
    tab.className = tab.className.replace("font-bold bg-white", "");
  });
  // Highlight the current tab
  event.currentTarget.className += " font-bold bg-white";

  let sensortype1 = document.getElementById("sensorTypeSelect1").value;
  let sensorid1 = document.getElementById("sensorIdSelect1").value;
  let sensortype2 = document.getElementById("sensorTypeSelect2").value;
  let sensorid2 = document.getElementById("sensorIdSelect2").value;
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
        console.log(data);
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
              backgroundColor: "rgba(168,220,84, 0.3)",
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
              backgroundColor: "rgba(256,220,44, 0.3)",
          }]
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
  canvas.chartInstance.update();
}


function updateCompareLineCharts(data) {
  if (data) {
      // if (!data.sensor1 || !data.sensor2) return;
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
          chartObj.data.datasets[0].data = curData;//.map((x) => x==null? Number.NaN: x); //y-axis data
          chartObj.data.datasets[1].data = curData2;//.map((x) => x==null? Number.NaN: x); //y-axis data
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
        chartObj.update();
        }
  }
}



function fetchData() {
  let sensortype1 = document.getElementById("sensorTypeSelect1").value;
  let sensorid1 = document.getElementById("sensorIdSelect1").value;

  let sensortype2 = document.getElementById("sensorTypeSelect2").value;
  let sensorid2 = document.getElementById("sensorIdSelect2").value;


  if (!sensortype1 || !sensorid1 || !sensortype2 || !sensorid2) return; //if no sensor is selected, return
  
  let date=document.getElementById("dateInput").value;
  fetch(`/compare-sensors-data/${sensortype1}/${sensorid1}/${sensortype2}/${sensorid2}/${date}`)
    .then((response) => response.json())
    .then((data) => {
      if (data) {
            let sensor1info= data.sensors_info['sensor1'];
            let sensor2info= data.sensors_info['sensor2'];
            document.getElementById("table-sensorType1").textContent = sensor1info.type;
            document.getElementById("table-sensorId1").textContent = sensor1info.id;
            if (sensor1info.last_updated){
              let last_updated = new Date(`${sensor1info.last_updated["obs_date"]} ${sensor1info.last_updated["obs_time_utc"]}`);
              document.getElementById("table-lastUpdated1").textContent = relativeTime(last_updated);
            }else{
              document.getElementById("table-lastUpdated1").textContent = "No data";
            }
            document.getElementById("table-sensorType2").textContent = sensor2info.type;
            document.getElementById("table-sensorId2").textContent = sensor2info.id;
            if (sensor2info.last_updated){
              last_updated = new Date(`${sensor2info.last_updated["obs_date"]} ${sensor2info.last_updated["obs_time_utc"]}`);
              document.getElementById("table-lastUpdated2").textContent = relativeTime(last_updated);
            }else{
              document.getElementById("table-lastUpdated2").textContent = "No data";
            }
            updateCompareLineCharts(data.rawdata);
            updateScatterPlot(data.rawdata);
            updateBoxPlot(data.hourly_rawdata);
          }
          })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
}

    

for (let param of parameters) {
  createLineChartObj(`${param.toLowerCase()}LineChart`);
  createScatterPlotObj(`${param.toLowerCase()}ScatterPlot`);
  createBoxPlotChartObj(`${param.toLowerCase()}BoxPlot`);
  createBoxPlotChartObj(`${param.toLowerCase()}DaysBoxPlot`);
}

