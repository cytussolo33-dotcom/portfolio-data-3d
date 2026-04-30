import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np

# CONFIG
st.set_page_config(page_title="Plataforma Geoespacial 3D", layout="wide")

# TÍTULO
st.title("🌍 Plataforma de Análise Geoespacial 3D")

st.markdown("""
Visualização interativa de dados espaciais em 3D com análise por altitude.

Tecnologias:
- Python
- Streamlit
- PyDeck
""")

# DADOS (simulados)
np.random.seed(42)
data = pd.DataFrame({
    'lat': np.random.uniform(-3.2, -2.9, 500),
    'lon': np.random.uniform(-60.1, -59.8, 500),
    'elevation': np.random.uniform(50, 500, 500)
})

# FILTRO
min_alt = st.slider("Filtrar altitude mínima", 0, 500, 100)
data_filtrada = data[data["elevation"] >= min_alt]

# MÉTRICAS
col1, col2, col3 = st.columns(3)
col1.metric("Total de pontos", len(data_filtrada))
col2.metric("Altitude média", int(data_filtrada["elevation"].mean()))
col3.metric("Altitude máxima", int(data_filtrada["elevation"].max()))

# CORES
def get_color(elev):
    if elev < 200:
        return [0, 255, 0]
    elif elev < 350:
        return [255, 165, 0]
    else:
        return [255, 0, 0]

data_filtrada["color"] = data_filtrada["elevation"].apply(get_color)

# CAMADA 3D
layer = pdk.Layer(
    "ColumnLayer",
    data=data_filtrada.sample(200),
    get_position='[lon, lat]',
    get_elevation='elevation',
    elevation_scale=50,
    radius=80,
    get_fill_color='color',
    pickable=True,
    extruded=True,
)

# VISÃO
view_state = pdk.ViewState(
    latitude=-3.1,
    longitude=-60.0,
    zoom=10,
    pitch=50,
)

# MAPA
st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/dark-v10"
))

# TABELA
st.subheader("📊 Dados filtrados")
st.dataframe(data_filtrada)

# RODAPÉ
st.markdown("---")
st.markdown("Desenvolvido com Python, Streamlit e PyDeck 🚀")
