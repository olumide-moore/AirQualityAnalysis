
function sensorTypeChanged(dropdownNumber) {
  let sensorTypeSelect = document.getElementById(`sensorType${dropdownNumber}`);
  let sensorId = document.getElementById(`sensorId${dropdownNumber}`);
   // Getting the selected sensor type id 
   let selectedType = sensorTypeSelect.options[sensorTypeSelect.selectedIndex];
   let typeid = selectedType.getAttribute("data-id");
    fetchSensorIDs(typeid).then((sensorIds) => {
      populateSensorOptions(sensorId, sensorIds); //populate sensor ids of first sensor list
      fetchData();
    });
  }
  
  
  function fetchSensorIDs(typeid) {
    return fetch(`/sensors-ids/${typeid}`)
        .then((response) => response.json())
        .then((data) => {
          return data.sensors;
        })
        .catch((error) => {
        console.error("Error fetching sensor IDs:", error);
        });
  }
  
  function populateSensorOptions(sensorSelect, sensorIds) {
    if (sensorSelect) {
      sensorSelect.innerHTML = ""; // Clear any existing options
      sensorIds.forEach((id) => {
        let option = document.createElement("option");
        option.value = id;
        option.text = id;
        sensorSelect.add(option);
      });
    }
  }
  
  
function initializeInputs(sensorTypeChangeIndex) {
  document.addEventListener('DOMContentLoaded', function() {
    let sensorTypeSelect = document.getElementById("sensorType1"); //get select of sensor type list
    if (init_sensorType1 !="None")  sensorTypeSelect.value = init_sensorType1; //set sensor type 1
    //get the type id of selected sensor type
    let selectedType = sensorTypeSelect.options[sensorTypeSelect.selectedIndex];
    let typeid1 = selectedType.getAttribute("data-id"); //get sensor type id 1
    let sensorIdSelect1 = document.getElementById("sensorId1"); //get select of sensor id list
    if (init_date !="None")  document.getElementById('dateInput').value = init_date;
    fetchSensorIDs(typeid1).then((sensorData1) => {
      populateSensorOptions(sensorIdSelect1, sensorData1); //populate sensor ids of first sensor list
      if (init_sensorId1 !="None")   sensorIdSelect1.value = `${init_sensorId1}`; //set sensor id 1
      sensorTypeChanged(sensorTypeChangeIndex); //fetch for the first or second sensor
    });
    });
}