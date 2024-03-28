function fetchSensorIDs() {
  let object = document.getElementById("sensortype");
  let selectedOption = object.options[object.selectedIndex];
  let typeid = selectedOption.getAttribute("data-id");
  fetch(`/sensors_ids/${typeid}`)
    .then((response) => response.json())
    .then((data) => {
      let sensorSelect = document.getElementById("sensorid");
      sensorSelect.innerHTML = "";
      data.sensors.forEach((sensor) => {
        let option = document.createElement("option");
        option.value = sensor.id;
        option.text = sensor.id;
        sensorSelect.add(option);
      });
      fetchData();
    })
    .catch((error) => {
      console.error("Error fetching sensor IDs:", error);
    });
}

function dateRange() {
  let date = document.getElementById("dateFilter").value;
  let start_datetime = `${date} 00:00:00`;
  let end_datetime = `${date} 23:59:59`;
  return [start_datetime, end_datetime];
}

// dateChanged();
function fetchData() {
  let sensortype = document.getElementById("sensortype").value;
  let sensorid = document.getElementById("sensorid").value;

  if (!sensorid) return; //if no sensor is selected, return
  let period = dateRange();
  if (period.length != 2) return; //if period range is not 2
  fetch(`/sensors-data/${sensortype}/${sensorid}/${period[0]}/${period[1]}`)
    .then((response) => response.json())
    .then((data) => {
      if (data) {
        updateAQICards(data.aqi_data);
        updateLineCharts(data.minutely_avgs);
        updateHourlyAvgCharts(data.hourly_avgs, data.hourly_aqis);
        document.getElementById("sensorType").textContent = sensortype;
        document.getElementById("sensorId").textContent = sensorid;
        avgData = data.avg_data;
        if (avgData) {
          Array.from(document.getElementsByClassName("no2Value")).forEach(
            (element) => {
              element.textContent = avgData.no2;
            }
          );

          Array.from(document.getElementsByClassName("pm2_5Value")).forEach(
            (element) => {
              element.textContent = avgData.pm2_5;
            }
          );

          Array.from(document.getElementsByClassName("pm10Value")).forEach(
            (element) => {
              element.textContent = avgData.pm10;
            }
          );
        }
        // console.log(data);
        if (data.last_updated) {
          let lastUpdated = new Date(
            `${data.last_updated["obs_date"]} ${data.last_updated["obs_time_utc"]}`
          );
          document.getElementById("lastUpdated").textContent =
            relativeTime(lastUpdated);
        } else {
          document.getElementById("lastUpdated").textContent = "No data";
        }
        if (data.hourly_avgs_7lastdays) {
          updateComparisonMultiCharts(data.hourly_avgs_7lastdays);
        //   hourly_avgs_samedaylast7weeks
        }

        // document.getElementById('no2Value').textContent = data.a
      }
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
}

function relativeTime(date) {
  var seconds = Math.floor((new Date() - date) / 1000);
  var interval = seconds / 31536000;

  if (interval > 1) {
    return (
      Math.floor(interval) + " years ago (" + date.toLocaleDateString() + ")"
    );
  }
  interval = seconds / 2592000;
  if (interval > 1) {
    return (
      Math.floor(interval) + " months ago (" + date.toLocaleDateString() + ")"
    );
  }
  interval = seconds / 86400;
  if (interval > 1) {
    return Math.floor(interval) + " days ago";
  }
  interval = seconds / 3600;
  if (interval > 1) {
    return Math.floor(interval) + " hours ago";
  }
  interval = seconds / 60;
  if (interval > 1) {
    return Math.floor(interval) + " minutes ago";
  }
  return Math.floor(seconds) + " seconds ago";
}

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

// function getAQIDescription(aqi){
//     if (aqi==1) return 'Good'; //Low
//     if (aqi==2) return 'Good'; //Low

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

// var data= [{
//     x: 10,
//     y: 20
// }, {
//     x: 15,
//     y: 10
// }]

function switchDaysComparisonTab(event, tabName) {
    //Restyle the tabs
    var tabs = document.querySelectorAll(".multiChartCompoarisonTabs");
    tabs.forEach((tab) => {
      tab.className = tab.className.replace("text-blue-500 border-blue-500", "");
    });
    // Highlight the current tab
    event.currentTarget.className += " text-blue-500 border-blue-500";
}


function createMinutelyChartObj(chartId) {
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
          borderColor: "rgba(168,220,84, 1)",
          borderWidth: 1.5,
          backgroundColor: "rgba(168,220,84, 0.3)",
          yAxisID: "y",
          lineTension: 0.3,
          radius: 0,
          fill: true,
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
          display: false,
        },
      },
      responsive: true,
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

const parameters = ["NO2", "PM10", "PM2_5"];

for (let param of parameters) {
  createMinutelyChartObj(`${param.toLowerCase()}LineChart`);
  createComparisonMultiChart(`${param.toLowerCase()}ComparisonMultiChart`);
}

function updateLineCharts(data) {
  // //Set the labels hours 00:00 to 23:00
  if (data) {
    // console.log('here');
    let time = data.time;
    // console.log(time);
    // let curData = time.map(label => sensorData[label]);
    // console.log(sensorData);
    for (let param of parameters) {
      let chartObj = document.getElementById(
        `${param.toLowerCase()}LineChart`
      ).chartInstance;
    //   chartObj.data.datasets[0].label = `Minutely ${param.toUpperCase()}`; //label
      // chartObj.data.labels = time.map(label => label.slice(5,16)); //x-axis labels
      //Map the time as JS Date objects
      chartObj.data.labels = time.map((x) => new Date(x)); //x-axis labels
      chartObj.data.datasets[0].data = data[param.toLowerCase()]; //y-axis data
      chartObj.update();
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
      chartObj.data.labels = time;
      let days = 0;
      for (let date in data) {
        chartObj.data.datasets[days].label = `${date}`; //label
        chartObj.data.datasets[days].data = data[date][param.toLowerCase()]; //y-axis data
        days++;
      }
      chartObj.update();
    }
  }
}

const hourlyavgChartsObjsArray = {};
for (let param of parameters) {
  let ctx = document
    .getElementById(`${param.toLowerCase()}HourlyAvgChart`)
    .getContext("2d");
  let chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: [],
      datasets: [
        {
        //   label: `Average ${param.toUpperCase()}`,
          label: "",
          data: [],
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
  hourlyavgChartsObjsArray[param] = chart;
}

function updateHourlyAvgCharts(avgData, aqiData) {
  if (avgData) {
    let time = avgData.time;
    if (time) {
      time = time.map((x) => new Date(x));
      for (let param of parameters) {
        let chartObj = hourlyavgChartsObjsArray[param];
        // console.log(avgData[param.toLowerCase()]);
        if (chartObj) {
          chartObj.data.labels = time;
          if (avgData[param.toLowerCase()]) {
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
}


//Set the date filter to default date
document.getElementById("dateFilter").value = new Date()
  .toISOString()
  .slice(0, 10);

fetchSensorIDs();

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
