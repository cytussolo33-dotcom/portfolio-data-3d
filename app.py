import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
from sklearn.cluster import KMeans

st.set_page_config(page_title="GeoData Platform PRO", layout="wide")

# ------------------ HEADER ------------------
st.title("🌍 GeoData Platform PRO AI")
st.markdown("Sistema avançado de análise geoespacial com IA + Visualização 3D")

# ------------------ SIDEBAR ------------------
st.sidebar.title("⚙️ Configurações")

uploaded_file = st.sidebar.file_uploader("📂 Upload CSV", type=["csv"])

map_style_option = st.sidebar.selectbox(
    "🗺️ Estilo do mapa",
    ["Google (claro)", "Satélite", "Escuro"]
)

cluster_n = st.sidebar.slider("🤖 Número de clusters", 2, 6, 3)

# Map styles
map_styles = {
    "Google (claro)": "mapbox://styles/mapbox/light-v9",
    "Satélite": "mapbox://styles/mapbox/satellite-v9",
    "Escuro": "mapbox://styles/mapbox/dark-v10"
}

# ------------------ PROCESSAMENTO ------------------
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if not all(col in df.columns for col in ["lat", "lon", "elevation"]):
        st.error("CSV precisa ter colunas: lat, lon, elevation")
        st.stop()

    # Filtro
    min_alt, max_alt = st.slider(
        "Filtro de altitude",
        float(df["elevation"].min()),
        float(df["elevation"].max()),
        (float(df["elevation"].min()), float(df["elevation"].max()))
    )

    df = df[(df["elevation"] >= min_alt) & (df["elevation"] <= max_alt)]

    # IA - Clusters
    kmeans = KMeans(n_clusters=cluster_n, n_init=10)
    df["cluster"] = kmeans.fit_predict(df[["lat", "lon", "elevation"]])

    # Anomalias
    threshold = df["elevation"].mean() + 2 * df["elevation"].std()
    df["anomaly"] = np.where(df["elevation"] > threshold, -1, 1)

    # Cores inteligentes
    df["color"] = df["anomaly"].apply(
        lambda x: [255, 0, 0] if x == -1 else [0, 200, 0]
    )

    # ------------------ DASHBOARD ------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📊 Total", len(df))
    col2.metric("📏 Média Altitude", round(df["elevation"].mean(), 2))
    col3.metric("📍 Clusters", cluster_n)
    col4.metric("🚨 Anomalias", (df["anomaly"] == -1).sum())

    # ------------------ GRÁFICO ------------------
    st.subheader("📊 Distribuição de Altitude")
    fig = px.histogram(df, x="elevation", nbins=30)
    st.plotly_chart(fig, use_container_width=True)

    # ------------------ MAPA 3D ------------------
    st.subheader("🗺️ Mapa 3D Inteligente")

    layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position='[lon, lat]',
        get_elevation="elevation",
        elevation_scale=40,
        radius=60,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=float(df["lat"].mean()),
        longitude=float(df["lon"].mean()),
        zoom=13,
        pitch=50,
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style=map_styles[map_style_option]
    ))

    # ------------------ TABELA ------------------
    st.subheader("📋 Dados processados")
    st.dataframe(df)

    # ------------------ DOWNLOAD ------------------
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Baixar dados processados",
        csv,
        "dados_processados.csv",
        "text/csv"
    )

else:
    st.info("📂 Envie um CSV para começar")
