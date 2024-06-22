import streamlit as st
import pandas as pd
import numpy as np

#import folium
#from streamlit_folium import st_folium

st.title('¿ORGANIZAMOS UN VIAJE?')

DATE_COLUMN = ['pais', 'Ciudad1', 'Ciudad2']
DATA_URL = ('./data/paises_mundo_ciudades_coordenadas.csv')

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
   # data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

data_load_state = st.text('Loading data...')
data = load_data(10000)
data_load_state.text("Done! (using st.cache_data)")

if st.checkbox('Busca el país al que podrias viajar'):
    st.subheader('Países del Mundo')
    st.write(data)

# Lista de países
paises = data['país'].unique()

# Selector de país
pais_seleccionado = st.selectbox('Selecciona un país', paises)

# Mostrar datos del país seleccionado
if pais_seleccionado:
    st.subheader(f'Datos del país seleccionado: {pais_seleccionado}')
    #st.write(data[data['país'] == pais_seleccionado])
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









