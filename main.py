import streamlit as st
import streamlit.components.v1 as components
import requests
import time
import subprocess
import os

st.set_page_config(page_title="Aabar Dashboard", layout="wide")

if "selected_tab" not in st.session_state:
    st.session_state["selected_tab"] = "Home"

st.sidebar.title("Aabar Dashboard")

if st.sidebar.button("Home"):
    st.session_state["selected_tab"] = "Home"
if st.sidebar.button("Monitor"):
    st.session_state["selected_tab"] = "Monitor"
if st.sidebar.button("AnzarChat"):
    st.session_state["selected_tab"] = "AnzarChat"
if st.sidebar.button("Dig a new well"):
    st.session_state["selected_tab"] = "DigWell"
if st.sidebar.button("Edit personal info"):
    st.session_state["selected_tab"] = "EditInfo"
if st.sidebar.button("Logout"):
    st.session_state["selected_tab"] = "Logout"
selected_tab = st.session_state["selected_tab"]

map_html = """
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ol@v10.2.1/ol.css" />
    <script src="https://cdn.jsdelivr.net/npm/ol@v10.2.1/dist/ol.js"></script>
    <style>
        #map { height: 500px; }
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = new ol.Map({
            target: 'map',
            layers: [
                new ol.layer.Tile({
                    source: new ol.source.OSM()
                })
            ],
            view: new ol.View({
                center: ol.proj.fromLonLat([0, 0]),
                zoom: 2
            })
        });

        var marker = null;

        map.on('click', function(e) {
            var coords = ol.proj.toLonLat(e.coordinate);
            var lat = coords[1];
            var lon = coords[0];

            if (marker) {
                map.removeLayer(marker);
            }

            marker = new ol.layer.Vector({
                source: new ol.source.Vector({
                    features: [new ol.Feature(new ol.geom.Point(e.coordinate))]
                }),
                style: new ol.style.Style({
                    image: new ol.style.Icon({
                        src: 'https://cdn-icons-png.flaticon.com/512/684/684908.png',
                        scale: 0.05
                    })
                })
            });
            map.addLayer(marker);

            fetch('http://127.0.0.1:8000/set_coordinates', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({lat: lat, lon: lon})
            });
        });
    </script>
</body>
</html>
"""

def get_coordinates():
    """Fetch the coordinates from the server."""
    try:
        response = requests.get('http://127.0.0.1:8000/get_coordinates')
        data = response.json()
        return data.get('lat'), data.get('lon')
    except Exception as e:
        st.error(f"Error retrieving coordinates: {e}")
        return None, None

def clear_coordinates():
    """Clear coordinates on the server."""
    try:
        response = requests.post('http://127.0.0.1:8000/clear_coordinates')
        if response.status_code == 200:
            st.success("Coordinates cleared successfully.")
    except Exception as e:
        st.error(f"Error clearing coordinates: {e}")

def step_one():
    """Step 1: Map Selection."""
    st.subheader("Step 1: Select a location on the map")
    components.html(map_html, height=550, scrolling=False)
    st.write("Click on the map where you want to dig a well, then click Confirm.")

    if st.button("Confirm", key="s1"):
        lat, lon = get_coordinates()
        if lat is not None and lon is not None:
            st.session_state["digwell_step"] = 2
        else:
            st.error("You must confirm the location by clicking on the map.")

def step_two():
    """Step 2: Prediction Using predictor.py."""
    st.subheader("Step 2: Run prediction for the selected well location")

    # Get the coordinates (lat, lon) from the previous step
    lat, lon = get_coordinates()

    if lat and lon:
        # Start spinner animation while the predictor is running
        with st.spinner("Running prediction..."):
            # Call predictor.py and pass the coordinates (lat, lon)
            result = run_predictor(lat, lon)
            st.success(f"Predicted Depth to Water: {result} meters")
    else:
        st.error("Please select a valid location first.")

def run_predictor(lat, lon):
    """Run the predictor script (predictor.py) with the given coordinates."""
    try:
        # Create a subprocess to run the Python script (predictor.py) with coordinates
        command = ["python3", "predictor.py", "--lon", str(float(lon)), "--lat", str(float(lat))]
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            # If the script ran successfully, parse the output and return the prediction
            return result.stdout.strip()
        else:
            st.error(f"Error running predictor: {result.stderr}")
            return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def run():
    """Run the appropriate step based on selected tab."""
    if selected_tab == "Home":
        st.title("Welcome to the Aabar Dashboard")
    elif selected_tab == "DigWell":
        if "digwell_step" not in st.session_state:
            st.session_state["digwell_step"] = 1
        if st.session_state["digwell_step"] == 1:
            step_one()
        elif st.session_state["digwell_step"] == 2:
            step_two()
    elif selected_tab == "AnzarChat":
        st.title("AnzarChat")
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("What is up?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                response = "Hello! How can I help you today?"  # Replace with your response logic
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
    elif selected_tab == "Logout":
        st.session_state.clear()
        st.write("You have logged out.")
    else:
        st.write(f"Selected tab: {selected_tab}")

if __name__ == "__main__":
    run()
