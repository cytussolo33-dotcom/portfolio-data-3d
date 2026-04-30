import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np

# Configuração da página
st.set_page_config(page_title="Plataforma 3D Geoespacial", layout="wide")

# Título
st.title("🌍 Plataforma 3D de Análise Geoespacial")
st.markdown("Visualização interativa de dados espaciais em 3D com Python, Streamlit e PyDeck.")

# -------------------------
# DADOS (simulação melhorada)
# -------------------------
@st.cache_data
def carregar_dados():
    data = pd.DataFrame({
        'lat': np.random.uniform(-3.2, -2.9, 300),
        'lon': np.random.uniform(-60.1, -59.8, 300),
        'elevation': np.random.uniform(50, 500, 300)
    })
    return data

data = carregar_dados()

# -------------------------
# FILTROS
# -------------------------
st.sidebar.header("Filtros")

min_altura = st.sidebar.slider("Altura mínima", 0, 500, 100)
max_altura = st.sidebar.slider("Altura máxima", 100, 500, 500)

data_filtrada = data[
    (data["elevation"] >= min_altura) &
    (data["elevation"] <= max_altura)
]

# -------------------------
# MÉTRICAS
# -------------------------
col1, col2 = st.columns(2)

col1.metric("Total de pontos", len(data_filtrada))
col2.metric("Altitude média", int(data_filtrada["elevation"].mean()))

# -------------------------
# MAPA 3D
# -------------------------
layer = pdk.Layer(
    "ColumnLayer",
    data=data_filtrada,
    get_position='[lon, lat]',
    get_elevation='elevation',
    elevation_scale=50,
    radius=100,
    get_fill_color='[elevation/2, 100, 200, 180]',
    pickable=True,
    extruded=True,
)

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

# -------------------------
# RODAPÉ
# -------------------------
st.markdown("---")
st.markdown("Desenvolvido com Python, Streamlit e PyDeck")
