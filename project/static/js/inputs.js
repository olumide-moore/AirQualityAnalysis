
async function sensorTypeChanged(dropdownNumber, fetchdata=true) {
  let sensorTypeSelect = document.getElementById(`sensorType${dropdownNumber}`);
  let sensorId = document.getElementById(`sensorId${dropdownNumber}`);
  // Getting the selected sensor type id 
  let selectedType = sensorTypeSelect.options[sensorTypeSelect.selectedIndex];
  let typeid = selectedType.getAttribute("data-id");
  try {
    let sensorIds = await fetchSensorIDs(typeid);
    populateSensorIDs(sensorId, sensorIds); //populate sensor ids of first sensor list
    if (fetchdata) await fetchData();
  } catch (error) {
    console.error("Error in sensorTypeChanged:", error);
  }
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
  
function populateSensorIDs(sensorSelect, sensorIds) {
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
  
  
