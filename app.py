import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

st.set_page_config(page_title="GeoData Platform ULTRA", layout="wide")

st.title("🌍 GeoData Platform ULTRA AI")
st.markdown("🔥 Sistema profissional de análise geoespacial com IA")

# UPLOAD
uploaded_file = st.file_uploader("📂 Envie um CSV (lat, lon, elevation)", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    # SIDEBAR CONTROLES
    st.sidebar.header("⚙️ Controles")

    n_clusters = st.sidebar.slider("Clusters (KMeans)", 2, 10, 3)
    contamination = st.sidebar.slider("Anomalias (%)", 0.01, 0.2, 0.05)

    map_style = st.sidebar.selectbox(
        "🗺️ Estilo do mapa",
        ["OpenStreetMap", "Stamen Terrain", "CartoDB dark_matter"]
    )

    show_heatmap = st.sidebar.checkbox("🔥 Mostrar Heatmap", True)

    # IA
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df["cluster"] = kmeans.fit_predict(df[["lat", "lon"]])

    iso = IsolationForest(contamination=contamination)
    df["anomaly"] = iso.fit_predict(df[["elevation"]])

    # MÉTRICAS
    col1, col2, col3 = st.columns(3)
    col1.metric("📍 Pontos", len(df))
    col2.metric("🧠 Clusters", df["cluster"].nunique())
    col3.metric("🚨 Anomalias", (df["anomaly"] == -1).sum())

    # MAPA INTERATIVO
    st.subheader("🗺️ Mapa Profissional")

    m = folium.Map(
        location=[df["lat"].mean(), df["lon"].mean()],
        zoom_start=12,
        tiles=map_style
    )

    # HEATMAP
    if show_heatmap:
        heat_data = df[["lat", "lon"]].values.tolist()
        HeatMap(heat_data).add_to(m)

    # PONTOS
    for _, row in df.iterrows():
        color = "red" if row["anomaly"] == -1 else "lime"

        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=6,
            color=color,
            fill=True,
            fill_opacity=0.7
        ).add_to(m)

    st_folium(m, width=1000, height=500)

    # MAPA 3D
    st.subheader("🌐 Visualização 3D")

    layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position='[lon, lat]',
        get_elevation='elevation',
        elevation_scale=10,
        radius=50,
        get_fill_color='[0, 255, 150, 160]',
        pickable=True,
        auto_highlight=True
    )

    view = pdk.ViewState(
        latitude=df["lat"].mean(),
        longitude=df["lon"].mean(),
        zoom=11,
        pitch=50
    )

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view))

    # GRÁFICOS
    st.subheader("📊 Dashboard")

    col1, col2 = st.columns(2)

    fig1 = px.histogram(df, x="elevation", color="cluster")
    col1.plotly_chart(fig1, use_container_width=True)

    fig2 = px.scatter(df, x="lon", y="lat", color="cluster")
    col2.plotly_chart(fig2, use_container_width=True)

    # DOWNLOAD
    st.subheader("📦 Exportar Dados")

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Baixar CSV processado", csv, "dados_processados.csv")

else:
    st.warning("👆 Envie um CSV para começar")
