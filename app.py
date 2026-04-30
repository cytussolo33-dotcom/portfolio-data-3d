import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest

# CONFIG
st.set_page_config(page_title="GeoData Platform PRO AI", layout="wide")

# HEADER
st.title("🌍 GeoData Platform PRO AI")
st.caption("Sistema avançado de análise geoespacial com IA + Visualização 3D")

# SIDEBAR
st.sidebar.title("⚙️ Configurações")

cluster_n = st.sidebar.slider("Número de Clusters", 2, 10, 3)
contamination = st.sidebar.slider("Sensibilidade de Anomalia", 0.01, 0.2, 0.05)

st.sidebar.markdown("---")
st.sidebar.info("Envie um CSV com: lat, lon, elevation")

# UPLOAD
uploaded_file = st.file_uploader("📂 Envie um CSV", type=["csv"])

# DEMO DATA
def gerar_dados():
    np.random.seed(42)
    lat = -3.1 + np.random.randn(100) * 0.02
    lon = -60.0 + np.random.randn(100) * 0.02
    elevation = np.random.randint(50, 400, 100)
    return pd.DataFrame({"lat": lat, "lon": lon, "elevation": elevation})

if uploaded_file is None:
    st.warning("Nenhum arquivo enviado — usando dados de demonstração 🚀")
    df = gerar_dados()
else:
    df = pd.read_csv(uploaded_file)

# VALIDAÇÃO
required_cols = {"lat", "lon", "elevation"}
if not required_cols.issubset(df.columns):
    st.error("CSV precisa ter colunas: lat, lon, elevation")
    st.stop()

# IA - CLUSTER
kmeans = KMeans(n_clusters=cluster_n, n_init=10)
df["cluster"] = kmeans.fit_predict(df[["lat", "lon", "elevation"]])

# IA - ANOMALIA
iso = IsolationForest(contamination=contamination)
df["anomalia"] = iso.fit_predict(df[["lat", "lon", "elevation"]])

# CORES
df["color"] = df["anomalia"].apply(lambda x: [255,0,0] if x == -1 else [0,255,0])

# MÉTRICAS
col1, col2, col3 = st.columns(3)
col1.metric("📊 Registros", len(df))
col2.metric("📍 Altitude Média", int(df["elevation"].mean()))
col3.metric("🚨 Anomalias", int((df["anomalia"] == -1).sum()))

# MAPA 3D
st.subheader("🗺️ Mapa 3D Inteligente")

layer = pdk.Layer(
    "ColumnLayer",
    data=df,
    get_position="[lon, lat]",
    get_elevation="elevation",
    elevation_scale=5,
    radius=50,
    get_fill_color="color",
    pickable=True,
)

view_state = pdk.ViewState(
    latitude=df["lat"].mean(),
    longitude=df["lon"].mean(),
    zoom=12,
    pitch=45,
)

st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

# MAPA ESTILO GOOGLE MAPS (2D)
st.subheader("🌎 Mapa Interativo (Estilo Google Maps)")

mapa = px.scatter_mapbox(
    df,
    lat="lat",
    lon="lon",
    color="cluster",
    size="elevation",
    zoom=12,
    height=500,
)

mapa.update_layout(mapbox_style="open-street-map")
st.plotly_chart(mapa, use_container_width=True)

# GRÁFICOS
col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(df, x="elevation", nbins=30, title="Distribuição de Altitude")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = px.scatter_3d(
        df,
        x="lat",
        y="lon",
        z="elevation",
        color="cluster",
        title="Clusters 3D",
    )
    st.plotly_chart(fig2, use_container_width=True)

# TABELA
st.subheader("📋 Dados Processados")
st.dataframe(df, use_container_width=True)

# DOWNLOAD
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Baixar dados processados", csv, "dados_processados.csv")

# FOOTER
st.markdown("---")
st.caption("🚀 Desenvolvido com Streamlit + IA + Visualização 3D")
