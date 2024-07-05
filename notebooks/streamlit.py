import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from geopy.geocoders import GoogleV3

# Load environment variables from .env file
load_dotenv()

DATA_URL = './data/paises_mundo_ciudades_coordenadas.csv'

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    #data.rename(lowercase, axis='columns', inplace=True)
    return data

data_load_state = st.text('Loading data...')
df = load_data(10000)
data_load_state.text("Done! (using st.cache_data)")

# Set up OpenAI API
client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))

# Function to generate city description using OpenAI
def generate_city_description(city, country):
    messages = [
        {"role": "system", "content": "You are a travel guide. Provide information in JSON format."},
        {"role": "user", "content": f"""Provide a brief description of {city}, {country}, in the following JSON format:
        {{
            "city": "{city}",
            "country": "{country}",
            "description": "Brief overview of the city",
            "landmarks": ["Famous landmark 1", "Famous landmark 2", "Famous landmark 3", "Famous landmark 4", "Famous landmark 5"],
            "activities": ["Popular activity 1", "Popular activity 2", "Popular activity 3", "Popular activity 4", "Popular activity 5"]
        }}
        """}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=500,
        temperature=0.7
    )

    return json.loads(response.choices[0].message.content)

# Streamlit app
st.title("City Explorer")

# Country selection (multi-select)
countries = df['País'].unique()
selected_countries = st.multiselect("Select countries", countries)

# Create map
m = folium.Map(location=[0, 0], zoom_start=2)

# Dictionary to store selected cities for each country
selected_cities = {}

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
        folium.Marker([lat, lon], popup=city).add_to(m)

# Display map
folium_static(m)

# Button to generate descriptions
if st.button("Generate City Descriptions"):
    # Create tabs for each selected city
    all_selected_cities = [city for country_cities in selected_cities.values() for city in country_cities]
    if all_selected_cities:
        tabs = st.tabs(all_selected_cities)
        for tab, city in zip(tabs, all_selected_cities):
            with tab:
                country = next(country for country, cities in selected_cities.items() if city in cities)
                city_info = generate_city_description(city, country)
                
                st.header(f"{city}, {country}")
                st.write(city_info["description"])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Famous Landmarks")
                    for landmark in city_info["landmarks"]:
                        st.write(f"- {landmark}")
                
                with col2:
                    st.subheader("Popular Activities")
                    for activity in city_info["activities"]:
                        st.write(f"- {activity}")
    else:
        st.warning("Please select at least one city to generate descriptions.")

# Set up GoogleMaps API
google_maps_api_key = os.environ.get("GOOGLEMAP_KEY")

# Define el código HTML para incrustar el mapa
map_html = f'''
<!DOCTYPE html>
<html>
  <head>
    <title>Google Maps API Example</title>
    <style>
      #map {{
        height: 100%;
      }}-
      html, body {{
        height: 100%;
        margin: 0;
        padding: 0;
      }}
    </style>
    <script src="https://maps.googleapis.com/maps/api/js?key={google_maps_api_key}"></script>
    <script>
      function initMap() {{
        var location = {{lat: -34.397, lng: 150.644}};
        var map = new google.maps.Map(document.getElementById('map'), {{
          center: location,
          zoom: 8
        }});
        var marker = new google.maps.Marker({{
          position: location,
          map: map
        }});
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


def get_latlong(landmark):

    geolocator = GoogleV3(api_key='GOOGLEMAP_KEY')
    
    location = geolocator.geocode(landmark)
    
    if location:
        latitude = location.latitude
        longitude = location.longitude
        return latitude, longitude
    else:
        return None

#landmark = json
coordinates = get_latlong(landmark)

if coordinates:
    print(f"Latitud: {coordinates[0]}, Longitud: {coordinates[1]}")
else:
    print("No se pudo obtener la geocodificación para la dirección proporcionada.")