import streamlit as st
import pandas as pd
import numpy as np
import openai

from dotenv import load_dotenv
import os

#Load enviaronment variables
load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_KEY')
#print("OPENAI_KEY", OPENAI_KEY)

# Configurar la API key de OpenAI
openai.api_key = OPENAI_KEY

st.title('¿ORGANIZAMOS UN VIAJE?')

DATA_URL = './data/paises_mundo_ciudades_coordenadas.csv'

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    return data

data_load_state = st.text('Loading data...')
data = load_data(10000)
data_load_state.text("Done! (using st.cache_data)")

if st.checkbox('Busca el país al que podrías viajar'):
    st.subheader('Países del Mundo')
    st.write(data)

# Lista de países
paises = data['país'].unique()

# Selector de país
pais_seleccionado = st.selectbox('Selecciona un país', paises)

# Mostrar datos del país seleccionado y permitir la selección de ciudades
if pais_seleccionado:
    st.subheader(f'Datos del país seleccionado: {pais_seleccionado}')
    data_pais = data[data['país'] == pais_seleccionado]
    st.write(data_pais)

    # Extraer las ciudades del país seleccionado
    ciudades = []
    for i in range(1, 11):
        ciudad_col = f'ciudad{i}'
        if data_pais[ciudad_col].values[0] is not np.nan:
            ciudades.append(data_pais[ciudad_col].values[0])

    # Selector de ciudades
    ciudades_seleccionadas = st.multiselect('Selecciona las ciudades', ciudades)

    # Mostrar las ciudades seleccionadas
    if ciudades_seleccionadas:
        st.subheader(f'Ciudades seleccionadas en {pais_seleccionado}:')
        for ciudad in ciudades_seleccionadas:
            st.write(ciudad)

        # Crear el prompt para OpenAI
        prompt = "Dame una lista de los 5 monumentos más destacados y sus coordenadas (latitud y longitud) en las siguientes ciudades:\n"
        for ciudad in ciudades_seleccionadas:
            prompt += f"- {ciudad}\n"
            print("prompt:", prompt)

        # Realizar la solicitud a la API de OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        # Mostrar la respuesta generada por la API
        st.subheader('Monumentos destacados y sus coordenadas:')
        st.write(response.choices[0].message['content'].strip())