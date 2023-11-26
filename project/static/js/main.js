
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


//Filter styling
let periodFilter;
function periodFilterSelected(event) {
    // Remove active class from all buttons
    document.querySelectorAll('.periodFilters').forEach((btn) => {
      btn.classList.remove('bg-blue-500', 'text-white');
      btn.classList.add('bg-gray-200', 'text-gray-700');
    });

    // Add active class to the clicked button
    event.currentTarget.classList.remove('bg-gray-200', 'text-gray-700');
    event.currentTarget.classList.add('bg-blue-500', 'text-white');
    //Get the selected period
    periodFilter = event.currentTarget.textContent;
  }

function chartTypeSelected(event) {
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
    // console.log(chartType);
}

   // let sensor_locations = JSON.parse(document.getElementById('sensor_locations').textContent);
if (document.getElementById('map')) {
   var mapObject=createMap([51.505, -0.09], 13);
var markerFeatureGroup = L.featureGroup()
mapObject.addLayer(markerFeatureGroup);
}
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

function sensorChanged() {
    // Get selected sensor from input
    if (document.getElementById('weeklyBoxplots')) {
    weekChanged();
    }else if(document.getElementById('dailyChart')){
        dateChanged();
    }
}
const weekRangeHeading = document.getElementById("weekRangeHeading");
function weekChanged() {
    // Get selected sensor from input
    let weekInput = weekFilter.value;
    let sensorInput1 = document.getElementById("sensor1").value;
    let sensorInput2 = document.getElementById("sensor2").value;
    // Get selected week from input
    if ((sensorInput1 == '' && sensorInput2 == '') || weekInput == '') {
        return;
    }
    let [year, week] = weekInput.split("-W");
    let {startDate, endDate} = getWeekDates(year, week); ///get the start and end date of the week
    weekRangeHeading.textContent = `${startDate} - ${endDate}`
    fetchWeeklyData([sensorInput1,sensorInput2],[startDate, endDate]);
}
function getWeekDates(year, week) {
    let startDate = new Date(year, 0, 2 + ((week - 1) * 7)); 
    let endDate = new Date(year, 0, 2 + ((week - 1) * 7) + 6);
    startDate=startDate.toLocaleDateString();
    endDate=endDate.toLocaleDateString();
    return {startDate, endDate};
    }


function fetchWeeklyData(sensors,dateRange){

    sensorsQuery=`sensor_one=${sensors[0]}&sensor_two=${sensors[1]}`
    fetch(`/weekly-sensors-data/?${sensorsQuery}&start_date=${encodeURIComponent(dateRange[0])}&end_date=${encodeURIComponent(dateRange[1])}`)
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
if (document.getElementById('weeklyBoxplots')) {
// const colors = ['rgba(255, 99, 132, 0.6)', 'rgba(255, 159, 64, 0.6)', 'rgba(255, 206, 86, 0.6)', 'rgba(75, 192, 192, 0.6)', 'rgba(54, 162, 235, 0.6)'];
for (let param of parameters){
    createBoxPlotChart(`${param.toLowerCase()}Boxplot`, param);
}
}


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
if (weekFilter){
    let curWeek=getCurrentWeek();
    weekFilter.value = curWeek;
    weekFilter.max = curWeek;
    //Call the weekChanged function to update the chart
    weekChanged();
}