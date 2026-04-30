import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest

# ===== CONFIG =====
st.set_page_config(
    page_title="GeoData Platform PRO AI",
    page_icon="🌍",
    layout="wide"
)

# ===== ESTILO =====
st.markdown("""
<style>
.main {background-color: #0e1117;}
h1, h2, h3, h4 {color: white;}
</style>
""", unsafe_allow_html=True)

# ===== HEADER =====
st.markdown("""
# 🌍 GeoData Platform PRO AI
### Plataforma inteligente de análise geoespacial com IA em tempo real
""")

st.divider()

# ===== SIDEBAR =====
st.sidebar.title("⚙️ Configurações")

num_clusters = st.sidebar.slider("Clusters (IA)", 2, 6, 3)
contaminacao = st.sidebar.slider("Sensibilidade de anomalia", 0.01, 0.2, 0.05)
altura_min, altura_max = st.sidebar.slider("Filtro de altitude", 0, 1000, (0, 500))

# ===== UPLOAD =====
uploaded_file = st.file_uploader("📂 Envie CSV (lat, lon, elevation)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # ===== VALIDAÇÃO =====
    if not {"lat", "lon", "elevation"}.issubset(df.columns):
        st.error("CSV precisa ter colunas: lat, lon, elevation")
        st.stop()

    # ===== FILTRO =====
    df = df[(df["elevation"] >= altura_min) & (df["elevation"] <= altura_max)]

    # ===== IA: CLUSTER =====
    kmeans = KMeans(n_clusters=num_clusters, n_init=10)
    df["cluster"] = kmeans.fit_predict(df[["lat", "lon"]])

    # ===== IA: ANOMALIA REAL =====
    model = IsolationForest(contamination=contaminacao, random_state=42)
    df["anomaly"] = model.fit_predict(df[["lat", "lon", "elevation"]])

    # ===== CORES =====
    def get_color(row):
        if row["anomaly"] == -1:
            return [255, 0, 0]  # vermelho
        return [0, 255, 0]  # verde

    df["color"] = df.apply(get_color, axis=1)

    # ===== MÉTRICAS =====
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total de pontos", len(df))
    col2.metric("Altitude média", int(df["elevation"].mean()))
    col3.metric("Clusters", num_clusters)
    col4.metric("Anomalias", (df["anomaly"] == -1).sum())

    st.divider()

    # ===== MAPA 3D =====
    st.subheader("🗺️ Mapa 3D Inteligente")

    layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position='[lon, lat]',
        get_elevation="elevation",
        elevation_scale=20,
        radius=80,
        get_fill_color="color",
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=df["lat"].mean(),
        longitude=df["lon"].mean(),
        zoom=10,
        pitch=50,
    )

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

    st.divider()

    # ===== GRÁFICO =====
    st.subheader("📊 Distribuição de Altitude")

    fig = px.histogram(
        df,
        x="elevation",
        nbins=25,
        title="Distribuição de Altitude"
    )

    fig.update_layout(
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font=dict(color="white")
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ===== INSIGHTS =====
    st.subheader("🤖 Insights da IA")

    anomalias = df[df["anomaly"] == -1].shape[0]

    st.info(f"Foram detectadas **{anomalias} anomalias** nos dados.")

    # ===== DOWNLOAD =====
    st.download_button(
        label="⬇️ Baixar dados processados",
        data=df.to_csv(index=False),
        file_name="dados_processados.csv",
        mime="text/csv"
    )

    st.divider()

    # ===== TABELA =====
    st.subheader("📋 Dados Processados")
    st.dataframe(df)

else:
    st.info("👆 Envie um arquivo CSV para começar")
