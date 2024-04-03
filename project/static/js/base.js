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


function navigateToPage(page) {
  //Get sensor type1, sensor id1, and date selected on the page if found
  let sensorType1 = document.getElementById("sensorTypeSelect1");
  let sensorId1 = document.getElementById("sensorIdSelect1");
  let date = document.getElementById("dateInput");

  if (sensorType1 && sensorId1 && date) {
    let sensorType1Value = sensorType1.value;
    let sensorId1Value = sensorId1.value;
    let dateValue = date.value;
    window.location.href=`/${page}?sensorType1=${sensorType1Value}&sensorId1=${sensorId1Value}&date=${dateValue}`;
  } else {
      window.location.href=`/${page}`;
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
  
const parameters = ["NO2", "PM10", "PM2_5"];

//Set the date filter to default date
document.getElementById("dateInput").value = new Date().toISOString().slice(0, 10);

