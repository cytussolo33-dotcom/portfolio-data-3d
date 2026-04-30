import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="GeoData PRO", layout="wide")

# =========================
# HEADER
# =========================
st.title("🌍 GeoData Platform PRO AI")
st.caption("Sistema avançado de análise geoespacial com IA + Dashboard profissional")

# =========================
# SIDEBAR (FILTROS)
# =========================
st.sidebar.header("⚙️ Filtros")

file = st.sidebar.file_uploader("📂 Envie CSV", type=["csv"])

if file:
    df = pd.read_csv(file)

    st.sidebar.success("Dados carregados!")

    # =========================
    # IA - CLUSTER + ANOMALIA
    # =========================
    kmeans = KMeans(n_clusters=3, n_init=10)
    df["cluster"] = kmeans.fit_predict(df[["lat", "lon", "elevation"]])

    iso = IsolationForest(contamination=0.05)
    df["anomalia"] = iso.fit_predict(df[["lat", "lon", "elevation"]])

    # =========================
    # FILTROS
    # =========================
    cluster_filter = st.sidebar.multiselect(
        "Clusters",
        options=df["cluster"].unique(),
        default=df["cluster"].unique()
    )

    df = df[df["cluster"].isin(cluster_filter)]

    # =========================
    # KPIs (CARDS)
    # =========================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📊 Total", len(df))
    col2.metric("📈 Altitude média", int(df["elevation"].mean()))
    col3.metric("🧩 Clusters", df["cluster"].nunique())
    col4.metric("🚨 Anomalias", len(df[df["anomalia"] == -1]))

    st.divider()

    # =========================
    # MAPA 3D (PYDECK)
    # =========================
    st.subheader("🌆 Mapa 3D Inteligente")

    layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position='[lon, lat]',
        get_elevation="elevation",
        elevation_scale=10,
        radius=30,
        get_fill_color="[255, 0, 0, 160] if anomalia == -1 else [0, 255, 0, 160]",
        pickable=True,
        auto_highlight=True,
    )

    view = pdk.ViewState(
        latitude=df["lat"].mean(),
        longitude=df["lon"].mean(),
        zoom=11,
        pitch=50,
    )

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view))

    # =========================
    # MAPA GOOGLE STYLE (FOLIUM)
    # =========================
    st.subheader("🗺️ Mapa Interativo (Estilo Google Maps)")

    m = folium.Map(
        location=[df["lat"].mean(), df["lon"].mean()],
        zoom_start=12,
        tiles="cartodbpositron"
    )

    for _, row in df.iterrows():
        cor = "red" if row["anomalia"] == -1 else "blue"
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=5,
            color=cor,
            fill=True
        ).add_to(m)

    st_folium(m, width=1200, height=500)

    # =========================
    # GRÁFICOS
    # =========================
    st.subheader("📊 Análises")

    colA, colB = st.columns(2)

    fig1 = px.histogram(df, x="elevation", title="Distribuição de Altitude")
    colA.plotly_chart(fig1, use_container_width=True)

    fig2 = px.scatter_3d(
        df,
        x="lon",
        y="lat",
        z="elevation",
        color="cluster",
        title="Clusters 3D"
    )
    colB.plotly_chart(fig2, use_container_width=True)

    # =========================
    # IA INSIGHTS
    # =========================
    st.subheader("🧠 Insights automáticos")

    st.write(f"""
    - O sistema detectou **{df['cluster'].nunique()} clusters**
    - Foram encontradas **{len(df[df['anomalia']==-1])} anomalias**
    - Altitude média: **{int(df['elevation'].mean())}**
    """)

    # =========================
    # TABELA
    # =========================
    st.subheader("📄 Dados processados")
    st.dataframe(df, use_container_width=True)

else:
    st.info("📂 Envie um CSV com: lat, lon, elevation")
