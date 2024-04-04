
function getAQIColor(aqi) {
  if (aqi == 1) return "#a0fc9c"; //Low
  if (aqi == 2) return "#38fc04"; //Low
  if (aqi == 3) return "#38cc04"; //Low
  if (aqi == 4) return "#fffc04"; //Moderate
  if (aqi == 5) return "#fccc04"; //Moderate
  if (aqi == 6) return "#ff9c04"; //Moderate
  if (aqi == 7) return "#ff6464"; //High
  if (aqi == 8) return "#ff0404"; //High
  if (aqi == 9) return "#a00404"; //High
  if (aqi == 10) return "#d034fc"; //Very High
  return "#626262"; //Unknown or no data
}

function getAQIDescription(aqi) {
  if (aqi >= 1 && aqi <= 3) return "Low"; 
  if (aqi >= 4 && aqi <= 6) return "Moderate";
  if (aqi >= 7 && aqi <= 9) return "High";
  if (aqi >= 10) return "Very High";
  return "";
}

function updateAQICards(aqi_data) {
  let no2Div = document.getElementById("no2card");
  let pm2_5Div = document.getElementById("pm2_5card");
  let pm10Div = document.getElementById("pm10card");
  let no2aqi = getAQIColor(aqi_data.no2);
  let pm2_5aqi = getAQIColor(aqi_data.pm2_5);
  let pm10aqi = getAQIColor(aqi_data.pm10);
  no2Div.style.backgroundColor = no2aqi;
  pm2_5Div.style.backgroundColor = pm2_5aqi;
  pm10Div.style.backgroundColor = pm10aqi;
}

function switchPeriodTab(event, tabName) {
  //Restyle the tabs
  let tabs = document.querySelectorAll(".periodTabs");
  tabs.forEach((tab) => {
    tab.className = tab.className.replace("font-bold bg-white", "");
  });

  // Highlight the current tab
  event.currentTarget.className += " font-bold bg-white";

  if (tabName == "HourlyData") {
    document.getElementById("hourlydata").style.display = "block";
    document.getElementById("rawdata").style.display = "none";
  } else if (tabName == "RawData") {
    document.getElementById("hourlydata").style.display = "none";
    document.getElementById("rawdata").style.display = "block";
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

  let sensortype = document.getElementById("sensorTypeSelect1").value;
  let sensorid = document.getElementById("sensorIdSelect1").value;
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
  fetch(`/compare-days/${sensortype}/${sensorid}/${dates}`)
    .then((response) => response.json())
    .then((data) => { 
      if (data.data) {
        updateComparisonMultiCharts(data.data);
      }
      // console.log(data);
      // updateComparisonMultiCharts(data);
    })   
}

function createBarChartObj(chartId) {
  let canvas = document.getElementById(chartId);
  let ctx = canvas.getContext("2d");
  canvas.chartInstance = new Chart(ctx, {
    type: "bar", //bar, horizontalBar, pie, line, doughnut, radar, polarArea//bar, horizontalBar, pie, line, doughnut, radar, polarArea
    data: {
      labels: [],
      datasets: [
        {
          label: "",
          data: [],
          backgroundColor: [],
        },
      ],
    },
    options: {
      scales: {
        x: {
          type: "time",
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "µg/m³",
          },
        },
      },
      plugins: {
        legend: {
          display: false,
        },
      },
      maintainAspectRatio: false,
      aspectRatio: 1,
    },
  });
  canvas.chartInstance.update();
}


function createComparisonMultiChart(chartId) {
  let canvas = document.getElementById(chartId);
  let ctx = canvas.getContext("2d");
  canvas.chartInstance = new Chart(ctx, {
    type: "line", //bar, horizontalBar, pie, line, doughnut, radar, polarArea//bar, horizontalBar, pie, line, doughnut, radar, polarArea
    data: {
      datasets: [
        {
          label: "",
          //disabling the label for now
          // type: 'line',
          data: [],
          backgroundColor: "rgba(168,220,84, 0.3)",
          borderColor: "rgba(168,220,84, 1)",
          borderWidth: 3,
          pointRadius: 3,
          pointBackgroundColor: "rgba(168,220,84, 1)",
          // yAxisID: 'y',
          lineTension: 0.3,
          radius: 0,
        //   fill: true,
        },
        {
          label: "",
          // type: 'line',
          data: [],
          backgroundColor: "rgba(256,140,100, 0.1)",
          borderColor: "rgba(256,140,100, 1)",
          borderWidth: 1.5,
          pointRadius: 3,
          pointBackgroundColor: "rgba(256,140,100, 1)",
          // yAxisID: 'y2',
          lineTension: 0.3,
          radius: 0,
        },
        {
          label: "",
          // type: 'line',
          data: [],
          backgroundColor: "rgba(144,164,204, 0.1)",
          borderColor: "rgba(144,164,204, 1)",
          borderWidth: 1.5,
          pointRadius: 3,
          pointBackgroundColor: "rgba(144,164,204, 1)",
          // yAxisID: 'y2',
          lineTension: 0.3,
          radius: 0,
        },
        {
          label: "",
          data: [],
          backgroundColor: "rgba(232,140,196, 0.1)",
          borderColor: "rgba(232,140,196, 1)",
          borderWidth: 1.5,
          pointRadius: 3,
          pointBackgroundColor: "rgba(232,140,196, 1)",
          lineTension: 0.3,
          radius: 0,
        },
        {
          label: "",
          data: [],
          backgroundColor: "rgba(192,236,244, 0.1)",
          borderColor: "rgba(192,236,244, 1)",
          borderWidth: 1.5,
          pointRadius: 3,
          pointBackgroundColor: "rgba(192,236,244, 1)",
          lineTension: 0.3,
          radius: 0,
        },
        {
          label: "",
          data: [],
          backgroundColor: "rgba(256,220,44, 0.1)",
          borderColor: "rgba(256,220,44, 1)",
          borderWidth: 1.5,
          pointRadius: 3,
          pointBackgroundColor: "rgba(256,220,44, 1)",
          lineTension: 0.3,
          radius: 0,
        },
        {
          label: "",
          data: [],
          backgroundColor: "rgba(232,196,148, 0.1)",
          borderColor: "rgba(232,196,148, 1)",
          borderWidth: 1.5,
          pointRadius: 3,
          pointBackgroundColor: "rgba(232,196,148, 1)",
          lineTension: 0.3,
          radius: 0,
        },
      ],
    },
    options: {
      scales: {
        x: {
          type: "time",
        },

        y: {
          type: "linear",
          display: true,
          position: "left",
          title: {
            display: true,
            text: "µg/m³",
          },
        },
      },
      plugins: {
        legend: {
          display: true,
        },
      },
      responsive: true,
      maintainAspectRatio: false,
      aspectRatio: 1,
    },
  });
  canvas.chartInstance.update();
}

function updateLineCharts(data) {
  // //Set the labels hours 00:00 to 23:00
  if (data) {
    let time = data.time;
    for (let param of parameters) {
      let chartObj = document.getElementById(
        `${param.toLowerCase()}LineChart`
      ).chartInstance;
      if (chartObj){
        //Map the time as JS Date objects
        chartObj.data.labels = time.map((x) => new Date(x)); //x-axis labels
        chartObj.data.datasets[0].data = data[param.toLowerCase()]; //y-axis data
        chartObj.update();
      }
    }
  }
}

function updateHourlyAvgCharts(avgData, aqiData) {
  if (avgData) {
    let time = avgData.time;
    if (time) {
      time = time.map((x) => new Date(x));
      for (let param of parameters) {
        let chartObj = document.getElementById(
          `${param.toLowerCase()}HourlyAvgChart`
        ).chartInstance;
        if (chartObj) {
          chartObj.data.labels = time;
          chartObj.data.datasets[0].data = avgData[param.toLowerCase()];
          chartObj.data.datasets[0].backgroundColor = aqiData[
            param.toLowerCase()
          ].map((x) => getAQIColor(x));
          chartObj.update();
        }
      }
    }
  }
}

function updateComparisonMultiCharts(data) {
  if (data) {
    let time = Object.values(data)[0].time.map((x) => new Date(x).getTime());
    for (let param of parameters) {
      let chartObj = document.getElementById(
        `${param.toLowerCase()}ComparisonMultiChart`
      ).chartInstance;
      if (chartObj) {
        chartObj.data.labels = time;
        let day = 0;
        for (let date in data) {
          chartObj.data.datasets[day].label = `${date}`; //label
          chartObj.data.datasets[day].data = data[date][param.toLowerCase()]; //y-axis data
          day++;
        }
        chartObj.update();
      }
    }
  }
}


function fetchData() {
  let sensortype = document.getElementById("sensorTypeSelect1").value;
  let sensorid = document.getElementById("sensorIdSelect1").value;

  if (!sensortype || !sensorid)  return;

  let date=document.getElementById("dateInput").value;
  fetch(`/sensor-data/${sensortype}/${sensorid}/${date}`)
    .then((response) => response.json())
    .then((data) => {
      if (data) {
        if (data.last_updated) {
          let lastUpdated = new Date(
            `${data.last_updated["obs_date"]} ${data.last_updated["obs_time_utc"]}`
          );
          document.getElementById("lastUpdated").textContent =
            relativeTime(lastUpdated);
        } else {
          document.getElementById("lastUpdated").textContent = "No data";
        }
        updateLineCharts(data.rawdata);
        updateHourlyAvgCharts(data.hourly_avgs, data.hourly_aqis);
        let aqiData = data.aqi_data;
        updateAQICards(aqiData);
        avgData = data.avg_data;
        if (avgData) {
          //Update the average values in the table
          document.getElementById("no2Value").textContent = avgData.no2;
          document.getElementById("pm2_5Value").textContent = avgData.pm2_5;
          document.getElementById("pm10Value").textContent = avgData.pm10;
          document.getElementById("no2AQIDesc").textContent = getAQIDescription(aqiData.no2);
          document.getElementById("pm2_5AQIDesc").textContent = getAQIDescription(aqiData.pm2_5);
          document.getElementById("pm10AQIDesc").textContent = getAQIDescription(aqiData.pm10);
        }
        //Update the sensor type and id in the table
        document.getElementById("sensorType").textContent = sensortype;
        document.getElementById("sensorId").textContent = sensorid;

      }
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
}


//Create the chart objects for each parameter
for (let param of parameters) {
  createLineChartObj(`${param.toLowerCase()}LineChart`);
  createBarChartObj(`${param.toLowerCase()}HourlyAvgChart`);
  createComparisonMultiChart(`${param.toLowerCase()}ComparisonMultiChart`);
}



//Hide the sensor Type 2 and sensor ID 2 dropdowns by defaults
document.getElementById("sensorDiv2").style.display = "none";


//Fetch the sensor IDs and update the charts on page load
// sensorTypeChanged(1);

//Select the hourly data tab by default
document.getElementById("hourlyTab").click();



// let sensor_locations = JSON.parse(document.getElementById('sensor_locations').textContent);
if (document.getElementById("map")) {
  var mapObject = createMap([51.505, -0.09], 13);
  var markerFeatureGroup = L.featureGroup();
  mapObject.addLayer(markerFeatureGroup);
}
//Create a map object and set the center and zoom level
function createMap(center, zoom) {
  let map = L.map("map").setView(center, zoom);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19, //Max zoom level
    attribution:
      '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>', //Attribution (bottom bar)
  }).addTo(map);
  return map;
}
