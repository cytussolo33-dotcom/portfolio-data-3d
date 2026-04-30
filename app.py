import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# CONFIG
st.set_page_config(page_title="Dashboard Geoespacial 3D", layout="wide")

st.title("🌍 Plataforma Geoespacial 3D Profissional")

st.markdown("Análise interativa de dados espaciais com filtros e visualização avançada.")

# ===== DADOS REALISTAS (simulados com lógica melhor) =====
np.random.seed(42)

data = pd.DataFrame({
    'lat': np.random.uniform(-3.2, -2.9, 500),
    'lon': np.random.uniform(-60.1, -59.8, 500),
    'elevation': np.random.uniform(50, 500, 500),
    'categoria': np.random.choice(['Baixa', 'Média', 'Alta'], 500)
})

# ===== SIDEBAR (FILTROS) =====
st.sidebar.header("Filtros")

min_alt = st.sidebar.slider("Altitude mínima", 0, 500, 50)
categoria = st.sidebar.multiselect(
    "Categoria",
    options=data['categoria'].unique(),
    default=data['categoria'].unique()
)

# ===== FILTRAGEM =====
filtered = data[
    (data['elevation'] >= min_alt) &
    (data['categoria'].isin(categoria))
]

# ===== MÉTRICAS =====
col1, col2, col3 = st.columns(3)

col1.metric("Total de pontos", len(filtered))
col2.metric("Altitude média", int(filtered['elevation'].mean()) if len(filtered) > 0 else 0)
col3.metric("Altitude máxima", int(filtered['elevation'].max()) if len(filtered) > 0 else 0)

# ===== COR POR ALTURA =====
def get_color(elevation):
    if elevation < 150:
        return [0, 255, 0]
    elif elevation < 300:
        return [255, 165, 0]
    else:
        return [255, 0, 0]

filtered['color'] = filtered['elevation'].apply(get_color)

# ===== MAPA 3D =====
layer = pdk.Layer(
    "ColumnLayer",
    data=filtered,
    get_position='[lon, lat]',
    get_elevation='elevation',
    get_fill_color='color',
    elevation_scale=40,
    radius=80,
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
    map_style='mapbox://styles/mapbox/dark-v10'
))

# ===== TABELA =====
st.subheader("Dados filtrados")
st.dataframe(filtered.head(50))

# ===== RODAPÉ =====
st.markdown("---")
st.markdown("🚀 Projeto desenvolvido para portfólio profissional de Dados Espaciais 3D")
