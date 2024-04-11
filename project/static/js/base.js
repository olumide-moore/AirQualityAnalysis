
Chart.register({
  id: 'NoData',
  afterDraw: function(chart) {

  if (chart.data.datasets.length === 0 || chart.data.datasets.every((dataset) => dataset.data.length === 0 || dataset.data.every((x) => x === null))) {

      const ctx = chart.ctx;
      const width = chart.width;
      const height = chart.height;
      chart.clear();

      ctx.save();
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.font = `1.5rem ${window.getComputedStyle(document.body).fontFamily}`;

      ctx.fillText('No data', width / 2, height / 2);
      ctx.restore();
    }
  }
});

function isInteger(variable) {
    return Number.isInteger(Number(variable));
}

function isString(variable) {
    return typeof variable === "string" || variable instanceof String;
}

function isValidDate(dateStr) {
    var date = new Date(dateStr);
    if (!(date instanceof Date && !isNaN(date)) ) return false;
    if (date.getFullYear() < 1970 || date.getFullYear() > 2262) return false; //year range permissble by pandas Timestamp
    if (date.getMonth() < 0 || date.getMonth() > 11) return false;
    if (date.getDate() < 1 || date.getDate() > 31) return false;

    return true;
}


function navigateToPage(page) {
  let sensortype1 = document.getElementById("sensorType1").value;
  let sensorid1 = document.getElementById("sensorId1").value;
  let date = document.getElementById("dateInput").value;

 
  if(!(isString(sensortype1) && isInteger(sensorid1) && isValidDate(date))) {
      return;
  }
  
  if (page === "compare") {
    let form = document.getElementById("inputsForm");
    form.action = `/${page}/`;
    form.submit();
    initializeInputs().then(() => {
      //Select the raw data tab by default
      document.getElementById("rawdataTab").click();
      //Select the last 7 days tab by default
      document.getElementById("last7daysTab").click();
      
    });
  }
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

function createLineChartObj(chartId) {
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
            // fill: true,
          }, 
          {
            label: "",
            //disabling the label for now
            // type: 'line',
            data: [],
            borderColor: "rgba(256,220,44, 1)",
            borderWidth: 1.5,
            backgroundColor: "rgba(256,220,44, 0.3)",
            yAxisID: "y",
            lineTension: 0.3,
            radius: 0,
            // fill: true,
          }
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


  const parameters = ["NO2", "PM10", "PM2_5"];

//Set the date filter to default date
document.getElementById("dateInput").value = new Date().toISOString().slice(0, 10);

