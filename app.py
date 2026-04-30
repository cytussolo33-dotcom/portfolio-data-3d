import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import plotly.express as px

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="GeoData Platform", layout="wide")

st.title("🌍 GeoData Platform 3D")
st.markdown("Análise inteligente de dados geoespaciais com visualização avançada")

st.info("📂 Envie um CSV com colunas: lat, lon, elevation")

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ Controles")

file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

# =========================
# DADOS
# =========================
if file:
    data = pd.read_csv(file)
else:
    np.random.seed(42)
    data = pd.DataFrame({
        'lat': np.random.uniform(-3.2, -2.9, 500),
        'lon': np.random.uniform(-60.1, -59.8, 500),
        'elevation': np.random.uniform(50, 500, 500),
    })

# =========================
# FILTROS
# =========================
min_alt = st.sidebar.slider("Altitude mínima", 0, int(data['elevation'].max()), 50)

filtered = data[data['elevation'] >= min_alt].copy()

# =========================
# MÉTRICAS
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("📍 Pontos", len(filtered))
col2.metric("📊 Média", f"{int(filtered['elevation'].mean())} m")
col3.metric("🚀 Máxima", f"{int(filtered['elevation'].max())} m")

# =========================
# GRÁFICO (NOVO)
# =========================
st.markdown("### 📊 Distribuição de Altitude")

fig = px.histogram(filtered, x="elevation", nbins=30)
st.plotly_chart(fig, use_container_width=True)

# =========================
# CORES
# =========================
def get_color(value):
    if value < 200:
        return [0, 180, 0]
    elif value < 350:
        return [255, 170, 0]
    else:
        return [200, 50, 50]

filtered["color"] = filtered["elevation"].apply(get_color)

# =========================
# MAPA 3D
# =========================
layer = pdk.Layer(
    "ColumnLayer",
    data=filtered,
    get_position='[lon, lat]',
    get_elevation='elevation',
    elevation_scale=25,
    radius=60,
    get_fill_color='color',
    pickable=True,
    extruded=True,
)

view_state = pdk.ViewState(
    latitude=filtered['lat'].mean(),
    longitude=filtered['lon'].mean(),
    zoom=11,
    pitch=50,
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style='mapbox://styles/mapbox/dark-v11'
))

# =========================
# INSIGHTS AUTOMÁTICOS
# =========================
st.markdown("### 🧠 Insights")

st.success(f"A maioria dos pontos está acima de {min_alt}m")
st.info(f"Distribuição média de altitude: {int(filtered['elevation'].mean())}m")

# =========================
# TABELA
# =========================
st.markdown("### 📋 Dados")
st.dataframe(filtered)

# =========================
# RODAPÉ
# =========================
st.markdown("---")
st.markdown("🚀 Plataforma desenvolvida com Python, Streamlit, PyDeck e Plotly")
