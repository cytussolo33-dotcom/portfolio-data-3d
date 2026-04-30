import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pydeck as pdk
from sklearn.cluster import KMeans

# MAPA GOOGLE STYLE
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster

# CONFIG
st.set_page_config(page_title="GeoData PRO", layout="wide")

st.title("🌍 GeoData Platform PRO AI")
st.caption("Sistema avançado de análise geoespacial com IA + Dashboard profissional")

# =========================
# UPLOAD (CORRIGIDO)
# =========================
st.subheader("📂 Envie seu CSV")

file = st.file_uploader(
    "Upload CSV (colunas: lat, lon, valor)",
    type=["csv"]
)

# =========================
# DADOS DEMO AUTOMÁTICO
# =========================
def gerar_dados():
    lat = -3.1 + np.random.randn(200) * 0.02
    lon = -60 + np.random.randn(200) * 0.02
    valor = np.random.randint(1, 100, 200)
    return pd.DataFrame({"lat": lat, "lon": lon, "valor": valor})

if file:
    df = pd.read_csv(file)
else:
    st.info("Usando dados de exemplo")
    df = gerar_dados()

# =========================
# VALIDAÇÃO
# =========================
if not {"lat", "lon"}.issubset(df.columns):
    st.error("CSV precisa ter colunas: lat, lon")
    st.stop()

# =========================
# CLUSTER (IA)
# =========================
kmeans = KMeans(n_clusters=3, n_init=10)
df["cluster"] = kmeans.fit_predict(df[["lat", "lon"]])

# =========================
# KPIs
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("📍 Pontos", len(df))
col2.metric("📊 Média valor", int(df["valor"].mean()) if "valor" in df else 0)
col3.metric("🧠 Clusters", df["cluster"].nunique())

# =========================
# MAPA 3D (PYDECK)
# =========================
st.subheader("🗺️ Mapa 3D Inteligente")

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[lon, lat]',
    get_color='[cluster * 80, 100, 200]',
    get_radius=120,
    pickable=True
)

view_state = pdk.ViewState(
    latitude=df["lat"].mean(),
    longitude=df["lon"].mean(),
    zoom=12,
    pitch=40
)

st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

# =========================
# MAPA GOOGLE STYLE (FOLIUM)
# =========================
st.subheader("🌍 Mapa Interativo (Google Style)")

m = folium.Map(
    location=[df["lat"].mean(), df["lon"].mean()],
    zoom_start=12,
    tiles="cartodbpositron"
)

cluster = MarkerCluster().add_to(m)

for _, row in df.iterrows():
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=f"Cluster: {row['cluster']}",
    ).add_to(cluster)

st_folium(m, width=900, height=500)

# =========================
# GRÁFICO
# =========================
st.subheader("📊 Distribuição")

fig = px.histogram(df, x="cluster")
st.plotly_chart(fig, use_container_width=True)

# =========================
# TABELA
# =========================
st.subheader("📋 Dados")

st.dataframe(df)
