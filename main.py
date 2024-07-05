import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from geopy.geocoders import GoogleV3
import time
import webbrowser

# Load environment variables from .env file
load_dotenv()

DATA_URL = './data/paises_mundo_ciudades_coordenadas.csv'

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    return data

data_load_state = st.text('')
df = load_data(10000)

# Set up OpenAI API
client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))

# Function to generate city description using OpenAI
def generate_city_description(city, country):
    try:
        messages = [
            {"role": "system", "content": "You are a travel guide. Provide information in JSON format."},
            {"role": "user", "content": f"""Provide a brief description of {city}, {country}, in the following JSON format:
            {{
                "city": "{city}",
                "country": "{country}",
                "description": "Brief overview of the city",
                "landmarks": ["Famous landmark 1", "Famous landmark 2", "Famous landmark 3", "Famous landmark 4", "Famous landmark 5", "Famous landmark 6", "Famous landmark 7", "Famous landmark 8", "Famous landmark 9", "Famous landmark 10"],
                "activities": ["Popular activity 1", "Popular activity 2", "Popular activity 3", "Popular activity 4", "Popular activity 5"]
            }}
            """}
        ]

        for t in range(4):
            print(f"Try: {t}")
            if t < 4:
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        max_tokens=4000,
                        temperature=0.7
                    )
                    print("Finish...¿?")
                    return json.loads(response.choices[0].message.content)

                except Exception as e:
                    print("The openAI got error...:")

    except Exception as e:
        print(f"Error: {e}")
        print("----------EMERGENCY REQUEST----------------")
        print(messages)
        print(type(response))

        messages = [
            {"role": "system", "content": "You are a travel guide. Provide information in JSON format."},
            {"role": "user", "content": f"""Provide a brief description of {city}, {country}, in the following JSON format:
            {{
                "city": "{city}",
                "country": "{country}",
                "description": "Brief overview of the city",
                "landmarks": ["Famous landmark 1"],
                "activities": ["Popular activity 1"],
                "wikipedia_lin":[]
            }}
            """}
        ]
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=4000,
            temperature=0.7
        )

        return json.loads(response.choices[0].message.content)

# Function to get latitude and longitude from an address
def get_latlong(address):
    geolocator = GoogleV3(api_key=os.environ.get("GOOGLEMAP_KEY"))
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None

# Function to suggest a country based on dream vacation description
def suggest_country(dream_description):
    messages = [
        {"role": "system", "content": "You are a travel guide. Suggest a country based on the user's dream vacation description."},
        {"role": "user", "content": f"My dream vacation: {dream_description}"}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=100,
        temperature=0.7
    )
    suggestion = response.choices[0].message.content.strip()
    return suggestion

# Function to open URLs in a new tab
def open_url(url):
    webbrowser.open_new_tab(url)

# Streamlit app
st.title("City Explorer")

# Tabs
tab1, tab2 = st.tabs(["Dream Vacation", "City Explorer"])

# Dream Vacation tab
with tab1:
    st.header("Describe Your Dream Vacation")
    dream_description = st.text_area("Describe what you want in your dream vacation (e.g., beaches, mountains, culture).")
    if st.button("Suggest a Country"):
        if dream_description:
            country_suggestion = suggest_country(dream_description)
            st.write(f"Based on your description, you might enjoy visiting: {country_suggestion}")
        else:
            st.warning("Please enter a description of your dream vacation.")

# City Explorer tab
with tab2:
    # Country selection (multi-select)
    countries = df['País'].unique()
    selected_countries = st.multiselect("Select countries", countries)

    # Dictionary to store selected cities for each country
    selected_cities = {}

    # List to store all coordinates for centering the map
    all_coordinates = []

    # Process each selected country
    for selected_country in selected_countries:
        country_data = df[df['País'] == selected_country].iloc[0]
        cities = [col for col in country_data.index if col.startswith('Ciudad') and pd.notna(country_data[col])]
        city_names = [country_data[city] for city in cities]

        # City selection for each country
        selected_cities[selected_country] = st.multiselect(f"Select cities in {selected_country}", city_names)

        # Add markers for selected cities
        for city in selected_cities[selected_country]:
            city_index = city_names.index(city)
            lat = country_data[f'Lat{city_index+1}']
            lon = country_data[f'Long{city_index+1}']
            all_coordinates.append((lat, lon))

    # Calculate center of the map
    if all_coordinates:
        avg_lat = sum(coord[0] for coord in all_coordinates) / len(all_coordinates)
        avg_lon = sum(coord[1] for coord in all_coordinates) / len(all_coordinates)
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=2)
    else:
        m = folium.Map(location=[0, 0], zoom_start=2)

    # Add markers to the map
    for coord in all_coordinates:
        folium.Marker(coord).add_to(m)

    # Display map
    folium_static(m)

    # Button to generate descriptions
    if st.button("Generate City Descriptions", type="primary"):
        # Create tabs for each selected city
        all_selected_cities = [city for country_cities in selected_cities.values() for city in country_cities]
        city_infos = {}  # To store city information

        if all_selected_cities:
            tabs = st.tabs(all_selected_cities)
            for tab, city in zip(tabs, all_selected_cities):
                with tab:
                    country = next(country for country, cities in selected_cities.items() if city in cities)
                    city_info = generate_city_description(city, country)
                    city_infos[city] = city_info  # Store city information

                    st.header(f"{city}, {country}")
                    st.write(city_info["description"])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Famous Landmarks")
                        for landmark in city_info["landmarks"]:
                            search_url = f"https://en.wikipedia.org/wiki/{landmark.replace(' ', '_')}"
                            st.markdown(f"- [{landmark}]({search_url})")
                    
                    with col2:
                        st.subheader("Popular Activities")
                        for activity in city_info["activities"]:
                            st.write(f"- {activity}")

            # Generate Google Maps with landmarks
            if city_infos:
                google_maps_api_key = os.environ.get("GOOGLEMAP_KEY")
                
                # JavaScript to add markers for landmarks
                markers_js = ""
                for city, info in city_infos.items():
                    for landmark in info["landmarks"]:
                        # Get coordinates for each landmark
                        coordinates = get_latlong(f"{landmark}, {city}, {info['country']}")
                        if coordinates:
                            markers_js += f'''
                            new google.maps.Marker({{
                                position: {{lat: {coordinates[0]}, lng: {coordinates[1]}}},
                                map: map,
                                title: "{landmark}"
                            }});\n
                            '''

                # Define el código HTML para incrustar el mapa
                map_html = f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Google Maps API Example</title>
                    <style>
                    #map {{
                        height: 100%;
                    }}
                    html, body {{
                        height: 100%;
                        margin: 0;
                        padding: 0;
                    }}
                    </style>
                    <script src="https://maps.googleapis.com/maps/api/js?key={google_maps_api_key}"></script>
                    <script>
                    function initMap() {{
                        var map = new google.maps.Map(document.getElementById('map'), {{
                        center: {{lat: {avg_lat}, lng: {avg_lon}}},
                        zoom: 2
                        }});
                        {markers_js}
                    }}
                    </script>
                </head>
                <body onload="initMap()">
                    <div id="map" style="height: 500px; width: 100%;"></div>
                </body>
                </html>
                '''

                # Usa Streamlit para mostrar el HTML
                st.components.v1.html(map_html, height=500)
        else:
            st.warning("Please select at least one city to generate descriptions.")


# Add buttons for external links at the end of the page
st.markdown("---")
st.markdown("### Consult External Resources")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Go to ElTiempo"):
        open_url("https://www.eltiempo.es/el-mundo")
with col2:
    if st.button("Go to Skyscanner"):
        open_url("https://www.skyscanner.com")
with col3:
    if st.button("Go to currency converter"):
        open_url("https://www.xe.com/es/currencyconverter/")