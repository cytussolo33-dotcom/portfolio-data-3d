import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(page_title="Plataforma Geoespacial 3D", layout="wide")

st.title("🌍 Plataforma Profissional de Análise Geoespacial 3D")
st.markdown("Sistema interativo para análise de dados espaciais com visualização 3D")

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📊 Controles")

# Upload de arquivo
file = st.sidebar.file_uploader("📂 Enviar arquivo CSV", type=["csv"])

# =========================
# DADOS
# =========================
if file:
    data = pd.read_csv(file)
else:
    # dados simulados caso não tenha arquivo
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

filtered = data[data['elevation'] >= min_alt]

# =========================
# MÉTRICAS
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("Total de pontos", len(filtered))
col2.metric("Altitude média", int(filtered['elevation'].mean()))
col3.metric("Altitude máxima", int(filtered['elevation'].max()))

# =========================
# CORES MAIS PROFISSIONAIS
# =========================
def get_color(value):
    if value < 200:
        return [0, 200, 0]  # verde
    elif value < 350:
        return [255, 140, 0]  # laranja
    else:
        return [220, 20, 60]  # vermelho suave

filtered["color"] = filtered["elevation"].apply(get_color)

# =========================
# MAPA 3D
# =========================
layer = pdk.Layer(
    "ColumnLayer",
    data=filtered,
    get_position='[lon, lat]',
    get_elevation='elevation',
    elevation_scale=40,
    radius=80,
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
# TABELA
# =========================
st.markdown("### 📋 Dados analisados")
st.dataframe(filtered)

# =========================
# RODAPÉ
# =========================
st.markdown("---")
st.markdown("🚀 Desenvolvido com Python, Streamlit e PyDeck")
