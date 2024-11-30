import streamlit as st
import streamlit.components.v1 as components
import requests
import subprocess
import plotly.graph_objects as go
import numpy as np
import random
import time
from chatbot import RAGPipeline

# Set Streamlit page config
st.set_page_config(page_title="Aabar Dashboard", layout="wide")
def get_language():
    """Return the selected language (Arabic or English)."""
    return st.selectbox("Select Language", ["en", "ar"])

# Add the language toggle at the top of your app
language = get_language()
# FastAPI Backend URL
API_BASE_URL = "http://127.0.0.1:8000"
translations = {
    "en": {
        "step_1_title": "Step 1: Select a location on the map",
        "step_1_instructions": "Click on the map where you want to dig a well, then click Confirm.",
        "step_2_title": "Step 2: Run prediction for the selected well location",
        "step_2_instructions": "Select a location and run the prediction.",
        "login": "Login",
        "signup": "Sign Up",
        "well_monitor": "Monitor Wells",
        "well_metrics": "Well Metrics",
        "water_depth": "Water Depth Over Time",
        "confirm": "Confirm",
        "select_well": "Select a Well",
        "logout": "Logout",
        "home": "Home",
        "monitor": "Monitor Wells",
        "anzarchat": "AnzarChat",
        "dig_new_well": "Dig a new well",
        "edit_info": "Edit personal info",
        "authenticated": "Authenticated",
        "username": "Username",
        "password": "Password",
        "login_failed": "Login failed",
        "signup_failed": "Sign-up failed",
        "please_enter_both": "Please enter both username and password.",
        "account_created": "Account created successfully. Please log in.",
        "select_location": "Select a location on the map to dig a well.",
        "error_retrieving_coordinates": "Error retrieving coordinates: ",
        "error_clearing_coordinates": "Error clearing coordinates: ",
        "please_select_location": "Please select a valid location first.",
        "running_prediction": "Running prediction...",
        "prediction_result": "Predicted Depth to Water: ",
        "water_depth_evolution": "Water Depth Evolution for ",
        "water_depth_over_time": "Water Depth Over Time",
        "depth_info": "Depth to Water: ",
        "coords_error": "Error retrieving coordinates: ",
        "coords_cleared": "Coordinates cleared successfully.",
        "error_clearing_coordinates": "Error clearing coordinates: ",
        "error_running_predictor": "An error occurred: ",
        "conductivity": "Conductivity",
        "temperature": "Temperature",
        "authentication page": "Aabar Authentication",
        "Aabar Dashboard": "Aabar Dashboard",
    },
    "ar": {
        "step_1_title": "الخطوة 1: اختر موقعًا على الخريطة",
        "step_1_instructions": "انقر على الخريطة حيث ترغب في حفر بئر، ثم انقر فوق تأكيد.",
        "step_2_title": "الخطوة 2: تشغيل التنبؤ للموقع المحدد للبئر",
        "step_2_instructions": "حدد موقعًا وقم بتشغيل التنبؤ.",
        "login": "تسجيل الدخول",
        "signup": "إنشاء حساب",
        "well_monitor": "مراقبة الآبار",
        "well_metrics": "مقاييس البئر",
        "water_depth": "عمق المياه على مر الزمن",
        "confirm": "تأكيد",
        "select_well": "اختيار بئر",
        "logout": "تسجيل الخروج",
        "home": "الصفحة الرئيسية",
        "monitor": "مراقبة الآبار",
        "anzarchat": "أنزار شات",
        "dig_new_well": "حفر بئر جديد",
        "edit_info": "تعديل المعلومات الشخصية",
        "authenticated": "تم التوثيق",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "login_failed": "فشل تسجيل الدخول",
        "signup_failed": "فشل التسجيل",
        "please_enter_both": "يرجى إدخال اسم المستخدم وكلمة المرور.",
        "account_created": "تم إنشاء الحساب بنجاح. يرجى تسجيل الدخول.",
        "select_location": "حدد موقعًا على الخريطة لحفر بئر.",
        "error_retrieving_coordinates": "خطأ في استرجاع الإحداثيات: ",
        "error_clearing_coordinates": "خطأ في مسح الإحداثيات: ",
        "please_select_location": "يرجى اختيار موقع صالح أولاً.",
        "running_prediction": "جاري تشغيل التنبؤ...",
        "prediction_result": "عمق المياه المتوقع:",
        "water_depth_evolution": "تطور عمق المياه لـ",
        "water_depth_over_time": "عمق المياه عبر الزمن",
        "depth_info": "عمق المياه: ",
        "coords_error": "خطأ في استرجاع الإحداثيات: ",
        "coords_cleared": "تم مسح الإحداثيات بنجاح.",
        "error_clearing_coordinates": "خطأ في مسح الإحداثيات: ",
        "error_running_predictor": "حدث خطأ: ",
        "conductivity": "الموصلية الكهربائية",
        "temperature": "درجة الحرارة",
        "authentication page": "ولوج أبار",
        "Aabar Dashboard": "لوحة تحكم أبار",
    },
}


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
                center: ol.proj.fromLonLat([-7.0926, 29]),  // Centered on Morocco
                zoom: 5  // Adjust the zoom level to suit your preference (between 0-22)
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

rag_pipeline = RAGPipeline()

def get_coordinates():
    """Fetch the coordinates from the server."""
    try:
        response = requests.get('http://127.0.0.1:8000/get_coordinates')
        data = response.json()
        return data.get('lat'), data.get('lon')
    except Exception as e:
        st.error(translations[language]["coords_error"].format(e))
        return None, None

def clear_coordinates():
    """Clear coordinates on the server."""
    try:
        response = requests.post('http://127.0.0.1:8000/clear_coordinates')
        if response.status_code == 200:
            st.success(translations[language]["coords_cleared"])
    except Exception as e:
        st.error(translations[language]["error_clearing_coordinates"].format(e))

def step_one():
    """Step 1: Map Selection."""
    st.markdown(f"<h2 style='text-align: center;'>{translations[language]['step_1_title']}</h2>", unsafe_allow_html=True)
    components.html(map_html, height=550, scrolling=False)
    st.markdown(f"<p style='text-align: center;'>{translations[language]['step_1_instructions']}</p>", unsafe_allow_html=True)

    if st.button("Confirm", key="s1"):
        lat, lon = get_coordinates()
        if lat is not None and lon is not None:
            st.session_state["digwell_step"] = 2
        else:
            st.error("You must confirm the location by clicking on the map.")
        st.rerun()

def step_two():
    """Step 2: Prediction Using predictor.py."""
    st.markdown(f"<h2 style='text-align: center;'>{translations[language]['step_2_title']}</h2>", unsafe_allow_html=True)

    # Get the coordinates (lat, lon) from the previous step
    lat, lon = get_coordinates()

    if lat and lon:
        # Start spinner animation while the predictor is running
        with st.spinner(translations[language]["running_prediction"]):
            # Call predictor.py and pass the coordinates (lat, lon)
            result = run_predictor(lat, lon)
            st.markdown(f"<p style='text-align: center;'>{translations[language]['prediction_result']} {str(result)} meters</p>", unsafe_allow_html=True)
    else:
        st.error(translations[language]["please_select_location"])

def run_predictor(lat, lon):
    """Run the predictor script (predictor.py) with the given coordinates."""
    try:
        # Create a subprocess to run the Python script (predictor.py) with coordinates
        command = ["python3", "predictor.py", "--lon", str(float(lon)), "--lat", str(float(lat))]
        # # for hambam env
        # command = ["conda", "run", "-n", "base", "python", "predictor.py", "--lon", str(float(lon)), "--lat", str(float(lat))]
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            # If the script ran successfully, parse the output and return the prediction
            return result.stdout.strip()
        else:
            st.error(translations[language]["error_running_predictor"] + result.stderr)
            return None
    except Exception as e:
        st.error(translations[language]["error_running_predictor"] + str(e))
        return None
    
def monitor_page():
    st.markdown(f"<h1 style='text-align: center;'>{translations[language]['well_monitor']}</h1>", unsafe_allow_html=True)

    # Dropdown to select a well
    if language == "ar":
        well_names = ["بئر-1", "بئر-2", "بئر-3"]
    else:
        well_names = ["well-1", "well-2", "well-3"]
    selected_well = st.selectbox(translations[language]["select_well"], well_names)

    # Generate dummy data for each well
    if language == "ar":
        well_data = {
            "بئر-1":  {
                "pH": random.uniform(6.5, 8.5),
                "conductivity": random.uniform(100, 500),
                "temperature": random.uniform(15, 30),
                "water_depth": np.cumsum(np.random.normal(loc=-0.1, scale=0.5, size=30)).tolist()
            },
            "بئر-2":  {
                "pH": random.uniform(6.5, 8.5),
                "conductivity": random.uniform(100, 500),
                "temperature": random.uniform(15, 30),
                "water_depth": np.cumsum(np.random.normal(loc=-0.1, scale=0.5, size=30)).tolist()
            },
            "بئر-3":  {
                "pH": random.uniform(6.5, 8.5),
                "conductivity": random.uniform(100, 500),
                "temperature": random.uniform(15, 30),
                "water_depth": np.cumsum(np.random.normal(loc=-0.1, scale=0.5, size=30)).tolist()
            }          
        }
    else:
        well_data = {
            "well-1": {
                "pH": random.uniform(6.5, 8.5),
                "conductivity": random.uniform(100, 500),
                "temperature": random.uniform(15, 30),
                "water_depth": np.cumsum(np.random.normal(loc=-0.1, scale=0.5, size=30)).tolist()
            },
            "well-2": {
                "pH": random.uniform(6.5, 8.5),
                "conductivity": random.uniform(100, 500),
                "temperature": random.uniform(15, 30),
                "water_depth": np.cumsum(np.random.normal(loc=-0.1, scale=0.5, size=30)).tolist()
            },
            "well-3": {
                "pH": random.uniform(6.5, 8.5),
                "conductivity": random.uniform(100, 500),
                "temperature": random.uniform(15, 30),
                "water_depth": np.cumsum(np.random.normal(loc=-0.1, scale=0.5, size=30)).tolist()
            }
        }

    # Fetch data for the selected well
    data = well_data[selected_well]

    # Create a responsive layout
    with st.expander(translations[language]["well_metrics"], expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"<h2 style='text-align: center;'>pH Level</h2>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=data["pH"],
                title={"text": "pH Level"},
                gauge={
                    'axis': {'range': [0, 14]},
                    'bar': {'color': "green"},
                    'steps': [
                        # Lighter shades for each pH range to avoid overlap with green
                        {'range': [0, 3], 'color': "lightcoral"},  # Acidic (pH 0-3) - Light Red
                        {'range': [3, 7], 'color': "lightyellow"},  # Slightly acidic (pH 3-7) - Light Yellow
                        {'range': [7, 10], 'color': "lightgreen"},  # Neutral to slightly basic (pH 7-10) - Light Green
                        {'range': [10, 14], 'color': "lightblue"}  # Basic (pH 10-14) - Light Blue
                    ]
                }
            ))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown(f"<h2 style='text-align: center;'>{translations[language]['conductivity']}</h2>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=data["conductivity"],
                title={"text": "Conductivity (µS/cm)"},
                gauge={
                    "axis": {"range": [0, 1500]},  # Adjust the axis range if needed
                    "bar": {"color": "green"},
                    "steps": [
                        {"range": [0, 500], "color": "lightgreen"},  # Safe drinking water
                        {"range": [500, 1000], "color": "lightyellow"},  # Warning
                        {"range": [1000, 1500], "color": "lightcoral"}  # Unsafe
                    ]
                }
            ))
            st.plotly_chart(fig, use_container_width=True)

        with col3:
            st.markdown(f"<h2 style='text-align: center;'>{translations[language]['temperature']}</h2>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=data["temperature"],
                title={"text": "Temperature (°C)"},
                gauge={
                    "axis": {"range": [0, 50], "tickwidth": 1, "tickcolor": "darkblue"},
                    "bar": {"color": "red"},
                    "steps": [
                        {"range": [0, 20], "color": "lightblue"},
                        {"range": [20, 30], "color": "lightgreen"},
                        {"range": [30, 50], "color": "lightcoral"}
                    ],
                }
            ))
            st.plotly_chart(fig, use_container_width=True)

    # Evolution of water depth over time
    with st.expander(translations[language]["water_depth_over_time"], expanded=True):
        st.markdown(f"<h2 style='text-align: center;'>{translations[language]['water_depth_evolution']} {selected_well}</h2>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(len(data["water_depth"]))),
            y=data["water_depth"],
            mode='lines+markers',
            name="Water Depth"
        ))
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Water Depth (m)",
            title=translations[language]["water_depth_evolution"] + " " + selected_well,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

# Utility functions for API calls
def login_user(username, password):
    """Authenticate the user."""
    response = requests.post(f"{API_BASE_URL}/login", json={"username": username, "password": password})
    return response.json()

def create_account(username, password):
    """Create a new user account."""
    response = requests.post(f"{API_BASE_URL}/signup", json={"username": username, "password": password})
    return response.json()

# Authentication page
def auth_page():
    st.markdown(f"<h1 style='text-align: center;'>{translations[language]['authentication page']}</h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs([translations[language]["login"], translations[language]["signup"]])
    st.markdown(
        """
        <style>
        .stTabs [role="tablist"] button {
            flex: 1;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with tab1:
        st.markdown(f"<h2 style='text-align: center;'>{translations[language]['login']}</h2>", unsafe_allow_html=True)
        username = st.text_input(translations[language]["username"], key="login_username")
        password = st.text_input(translations[language]["password"], type="password", key="login_password")
        if st.button(translations[language]["login"]):
            if username and password:
                result = login_user(username, password)
                if result.get("success"):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.rerun()
                else:
                    st.error(result.get("message", "Login failed"))
            else:
                st.warning(translations[language]["please_enter_both"])

    with tab2:
        st.markdown(f"<h2 style='text-align: center;'>{translations[language]['signup']}</h2>", unsafe_allow_html=True)
        new_username = st.text_input(translations[language]["username"], key="signup_username")
        new_password = st.text_input(translations[language]["password"], type="password", key="signup_password")
        if st.button(translations[language]["signup"]):
            if new_username and new_password:
                result = create_account(new_username, new_password)
                if result.get("success"):
                    st.success(translations[language]["account_created"])
                else:
                    st.error(result.get("message", "Sign-up failed"))
            else:
                st.warning(translations[language]["please_enter_both"])

# Main dashboard page
def main_page():
    st.sidebar.markdown(f"<h1 style='text-align: center;'>{translations[language]['Aabar Dashboard']}</h1>", unsafe_allow_html=True)
    if language == "ar":
        tabs = ["الصفحة الرئيسية", "مراقبة الآبار", "أنزار شات", "حفر بئر جديد", "تعديل المعلومات الشخصية"]
    else:
        tabs = ["Home", "Monitor", "AnzarChat", "Dig a new well", "Edit personal info"]
    for tab in tabs:
        if st.sidebar.button(tab, use_container_width=True):
            st.session_state["selected_tab"] = tab

    if st.sidebar.button(translations[language]["logout"], use_container_width=True, key="logout_button", help="Logout", on_click=lambda: st.session_state.clear(), args=(), kwargs={}):
        st.session_state["authenticated"] = False
        st.rerun()

    st.sidebar.markdown(
        """
        <style>
        div.stButton > button#logout_button {
            background-color: red;
            color: white;
            width: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    selected_tab = st.session_state.get("selected_tab", tabs[0])

    if selected_tab == tabs[0]:
        st.markdown(f"<h1 style='text-align: center;'>{translations[language]['home']}</h1>", unsafe_allow_html=True)

    elif selected_tab == tabs[1]:
        monitor_page()

    elif selected_tab == tabs[2]:        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display previous messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Handle the user's input
        if prompt := st.chat_input("What is up?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate response from RAGPipeline
            with st.chat_message("assistant"):
                # Use the RAGPipeline to process the query and get the response
                response = rag_pipeline.process_query(prompt)
                st.markdown(response)
            
            # Append the assistant's response to the session state messages
            st.session_state.messages.append({"role": "assistant", "content": response})

    elif selected_tab == tabs[3]:
        if "digwell_step" not in st.session_state:
            st.session_state["digwell_step"] = 1
        if st.session_state["digwell_step"] == 1:
            step_one()
        elif st.session_state["digwell_step"] == 2:
            step_two()

    elif selected_tab == tabs[4]:
        st.write(translations[language]["edit_info"])

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    auth_page()
else:
    main_page()
