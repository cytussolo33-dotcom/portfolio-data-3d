import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import plotly.express as px

# IA
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest

# CONFIG
st.set_page_config(page_title="GeoData Platform PRO AI", layout="wide")

# ESTILO
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# CACHE
@st.cache_data
def carregar_dados(arquivo):
    return pd.read_csv(arquivo)

# TÍTULO
st.title("🌍 GeoData Platform PRO AI")
st.markdown("Sistema avançado de análise geoespacial com Inteligência Artificial")

# UPLOAD
arquivo = st.file_uploader("📂 Envie CSV (lat, lon, elevation)", type=["csv"])

if arquivo is not None:
    df = carregar_dados(arquivo)

    # VALIDAR COLUNAS
    if not all(col in df.columns for col in ["lat", "lon", "elevation"]):
        st.error("CSV precisa ter colunas: lat, lon, elevation")
        st.stop()

    # SIDEBAR
    st.sidebar.header("⚙️ Configurações")

    # FILTROS
    lat_min, lat_max = st.sidebar.slider(
        "Latitude",
        float(df.lat.min()),
        float(df.lat.max()),
        (float(df.lat.min()), float(df.lat.max()))
    )

    lon_min, lon_max = st.sidebar.slider(
        "Longitude",
        float(df.lon.min()),
        float(df.lon.max()),
        (float(df.lon.min()), float(df.lon.max()))
    )

    elev_min, elev_max = st.sidebar.slider(
        "Altitude",
        float(df.elevation.min()),
        float(df.elevation.max()),
        (float(df.elevation.min()), float(df.elevation.max()))
    )

    # FILTRAR
    df = df[
        (df.lat >= lat_min) & (df.lat <= lat_max) &
        (df.lon >= lon_min) & (df.lon <= lon_max) &
        (df.elevation >= elev_min) & (df.elevation <= elev_max)
    ]

    # IA - ANOMALIAS
    model = IsolationForest(contamination=0.1)
    df["anomalia"] = model.fit_predict(df[["elevation"]])

    # IA - CLUSTER
    kmeans = KMeans(n_clusters=3, n_init=10)
    df["cluster"] = kmeans.fit_predict(df[["elevation"]])

    # CORES
    df["color"] = df["anomalia"].apply(
        lambda x: [255, 0, 0] if x == -1 else [0, 255, 0]
    )

    # MÉTRICAS
    col1, col2, col3 = st.columns(3)
    col1.metric("Pontos", len(df))
    col2.metric("Média", f"{df.elevation.mean():.1f} m")
    col3.metric("Máxima", f"{df.elevation.max():.1f} m")

    # GRÁFICO
    st.subheader("📊 Distribuição de Altitude")
    fig = px.histogram(df, x="elevation", nbins=30)
    st.plotly_chart(fig, use_container_width=True)

    # MAPA 3D
    st.subheader("🗺️ Mapa 3D Inteligente")

    layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position="[lon, lat]",
        get_elevation="elevation",
        elevation_scale=10,
        radius=200,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=df.lat.mean(),
        longitude=df.lon.mean(),
        zoom=10,
        pitch=50,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10"
    )

    st.pydeck_chart(deck)

    # TABELA
    st.subheader("📄 Dados processados")
    st.dataframe(df)

else:
    st.info("Envie um CSV para começar 🚀")
