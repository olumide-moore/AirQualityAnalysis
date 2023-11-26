

function dateChanged() {
    let date = dateFilter.value;
    // window.location.href = "/daily/" + date;

    let sensorInput1 = document.getElementById("sensor1").value;
    fetchDailyData(sensorInput1,date);
}

function fetchDailyData(sensor,date){
    fetch(`/daily/sensors-data/?sensor=${sensor}&date=${encodeURIComponent(date)}`)
    .then(response => response.json()).then(data => {
        console.log(data);
        updateDailyChart(data);
       
    }).catch(error => {
        console.error('Error fetching data:', error)});
    }


//Set the date filter to default date
const dateFilter = document.getElementById("dateFilter");
if (dateFilter){
dateFilter.value = new Date().toISOString().slice(0,10);
//Call the weekChanged function to update the chart
dateChanged();
}



function updateDailyChart(data){
    if (data && data.data){
        let time = data.data.map(d => d.hour_beginning.slice(11,16));
        //slice the time to get the hour only
        let no2 = data.data.map(d => d.no2_avg);

    dailyChart.data.labels = time;
    dailyChart.data.datasets[0].data = no2;
    // dailyChart.data.datasets[1].data = data.voc;
    dailyChart.update();
    }
}

if (document.getElementById('dailyChart')) {

// Sample data - replace this with your hourly aggregated data
var data = {
    // labels: ['00:00', '01:00', '02:00', '03:00'], // Hour labels
    labels: [], // Hour labels
    datasets: [{
        label: 'NO2 Levels',
        data: [], // NO2 data for each hour
        // data: [11.73, 13.33, 18.02, 12.77], // NO2 data for each hour
        borderColor: 'rgba(255, 206, 86, 0.6)',
        fill: false
    }
    // , {
    //     label: 'VOC Levels',
    //     data: [3.01, 4.28, 5.77, 10.63], // VOC data for each hour
    //     borderColor: 'blue',
    //     fill: false
    // }
]
};

var ctx = document.getElementById('dailyChart').getContext('2d');
var dailyChart = new Chart(ctx, {
    type: 'line',
    data: data,
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
}