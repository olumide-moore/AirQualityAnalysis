
async function sensorTypeChanged(dropdownNumber, fetchdata=true) {
  let sensorTypeDropDown = document.getElementById(`sensorType${dropdownNumber}`);
  let sensorIdDropdown = document.getElementById(`sensorId${dropdownNumber}`);
  // Getting the selected sensor type id 
  let newtypeid = sensorTypeDropDown.options[sensorTypeDropDown.selectedIndex].getAttribute("data-id");

  try {
    updateSensorIdsDropDown(sensorIdDropdown, newtypeid); //populate sensor ids of first sensor list
    if (fetchdata) await fetchData();
  } catch (error) {
    console.error("Error in sensorTypeChanged:", error);
  }
}

function updateSensorIdsDropDown(sensorIdDropdown, typeId) {
  let sensorIds = all_sensor_types[typeId].ids;
    if (sensorIdDropdown) {
      sensorIdDropdown.innerHTML = ""; // Clear any existing options
      sensorIds.forEach((id) => { // Add new options
        let option = document.createElement("option");
        option.value = id;
        option.text = id;
        sensorIdDropdown.add(option);
      });
    }
  }
  
  
