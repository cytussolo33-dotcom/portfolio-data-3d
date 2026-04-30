import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np

st.set_page_config(page_title="Mapa 3D Profissional", layout="wide")

st.title("🌍 Mapa 3D Profissional de Dados Espaciais")

# Dados simulados (pode trocar depois por dados reais)
data = pd.DataFrame({
    'lat': np.random.uniform(-3.2, -2.9, 200),
    'lon': np.random.uniform(-60.1, -59.8, 200),
    'elevation': np.random.uniform(100, 500, 200)
})

# Camada 3D
layer = pdk.Layer(
    "ColumnLayer",
    data=data,
    get_position='[lon, lat]',
    get_elevation='elevation',
    elevation_scale=50,
    radius=100,
    get_fill_color='[255, 100, 100, 200]',
    pickable=True,
    extruded=True,
)

# Visualização
view_state = pdk.ViewState(
    latitude=-3.1,
    longitude=-60.0,
    zoom=10,
    pitch=50,
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
))
