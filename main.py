import streamlit as st
import streamlit.components.v1 as components
import requests
import random
import time

st.set_page_config(page_title="Aabar Dashboard", layout="wide")

if "selected_tab" not in st.session_state:
    st.session_state["selected_tab"] = "Home"

st.sidebar.title("Aabar Dashboard")

if st.sidebar.button("Home"):
    st.session_state["selected_tab"] = "Home"
if st.sidebar.button("AnzarChat"):
    st.session_state["selected_tab"] = "AnzarChat"
if st.sidebar.button("Predictor"):
    st.session_state["selected_tab"] = "Predictor"
if st.sidebar.button("License"):
    st.session_state["selected_tab"] = "License"

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
    try:
        response = requests.get('http://127.0.0.1:8000/get_coordinates')
        data = response.json()
        return data.get('lat'), data.get('lon')
    except Exception as e:
        st.error(f"Error retrieving coordinates: {e}")
        return None, None

def response_generator():
    response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

if selected_tab == "Home":
    st.title("Home")
elif selected_tab == "AnzarChat":
    st.title("AnzarChat")
    # Streamed response emulator
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = st.write_stream(response_generator())
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
elif selected_tab == "Predictor":
    st.title("Predictor")
    components.html(map_html, height=550, scrolling=False)
    st.write("Click on the map to get the coordinates here.")

    if st.button("Get Coordinates from Server"):
        lat, lon = get_coordinates()
        if lat is not None and lon is not None:
            st.write(f"**Latitude:** {lat}, **Longitude:** {lon}")
        else:
            st.write("No coordinates available. Please click on the map first.")
elif selected_tab == "License":
    st.title("License")
