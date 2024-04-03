
function sensorTypeChanged(dropdownNumber) {
  let sensorTypeSelect = document.getElementById(`sensorTypeSelect${dropdownNumber}`);
  let sensorIdSelect = document.getElementById(`sensorIdSelect${dropdownNumber}`);
   // Getting the selected sensor type id 
   let selectedType = sensorTypeSelect.options[sensorTypeSelect.selectedIndex];
   let typeid = selectedType.getAttribute("data-id");
    fetchSensorIDs(typeid).then((sensorIds) => {
      populateSensorOptions(sensorIdSelect, sensorIds); //populate sensor ids of first sensor list
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
  
  