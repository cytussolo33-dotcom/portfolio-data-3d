import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import numpy as np
from sklearn.cluster import KMeans

# ================= CONFIG =================
st.set_page_config(page_title="GeoData Platform PRO AI", layout="wide")

# ================= ESTILO =================
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ================= CACHE =================
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

# ================= HEADER =================
st.title("🌍 GeoData Platform PRO AI")
st.markdown("Plataforma avançada com IA para análise geoespacial 3D")

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Configurações")

modo = st.sidebar.selectbox(
    "Modo de visualização",
    ["3D Column", "Heatmap", "Scatter + IA"]
)

usar_exemplo = st.sidebar.checkbox("Usar dados de exemplo")

# ================= DADOS =================
if usar_exemplo:
    data = {
        "lat": [-3.119, -3.130, -3.140, -3.150, -3.160, -3.170],
        "lon": [-60.021, -60.015, -60.010, -60.005, -60.000, -60.030],
        "elevation": [120, 200, 80, 300, 250, 400]
    }
    df = pd.DataFrame(data)
else:
    uploaded_file = st.file_uploader("📂 Envie CSV", type=["csv"])
    if uploaded_file:
        df = load_data(uploaded_file)
    else:
        st.info("Envie um CSV ou use dados de exemplo")
        st.stop()

# ================= VALIDAÇÃO =================
required_cols = ["lat", "lon", "elevation"]
if not all(col in df.columns for col in required_cols):
    st.error("CSV precisa ter: lat, lon, elevation")
    st.stop()

df = df.dropna()

# ================= FILTROS =================
st.sidebar.subheader("🎛️ Filtros")

min_alt, max_alt = st.sidebar.slider(
    "Altitude",
    int(df.elevation.min()),
    int(df.elevation.max()),
    (int(df.elevation.min()), int(df.elevation.max()))
)

radius = st.sidebar.slider("Tamanho", 50, 500, 200)

df = df[(df.elevation >= min_alt) & (df.elevation <= max_alt)]

# ================= IA =================
st.sidebar.subheader("🧠 IA")

n_clusters = st.sidebar.slider("Clusters", 2, 6, 3)

coords = df[["lat", "lon"]]
kmeans = KMeans(n_clusters=n_clusters, n_init=10)
df["cluster"] = kmeans.fit_predict(coords)

# Anomalias
mean = df["elevation"].mean()
std = df["elevation"].std()
df["anomaly"] = abs(df["elevation"] - mean) > 2 * std

# ================= MÉTRICAS =================
col1, col2, col3 = st.columns(3)
col1.metric("📍 Pontos", len(df))
col2.metric("📊 Média", f"{df.elevation.mean():.0f} m")
col3.metric("🏔️ Máxima", f"{df.elevation.max():.0f} m")

# ================= MAPA =================
st.subheader("🗺️ Visualização Inteligente")

view_state = pdk.ViewState(
    latitude=df["lat"].mean(),
    longitude=df["lon"].mean(),
    zoom=4,
    pitch=60,
    bearing=30,
)

# CAMADAS
layers = []

if modo == "3D Column":
    layers.append(
        pdk.Layer(
            "ColumnLayer",
            data=df,
            get_position='[lon, lat]',
            get_elevation="elevation",
            elevation_scale=100,
            radius=radius,
            get_fill_color='[elevation*3, 50, 200, 180]',
            extruded=True,
            pickable=True,
        )
    )

elif modo == "Heatmap":
    layers.append(
        pdk.Layer(
            "HeatmapLayer",
            data=df,
            get_position='[lon, lat]',
            get_weight="elevation",
        )
    )

else:  # Scatter + IA
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position='[lon, lat]',
            get_color='[cluster * 80, 100, 200]',
            get_radius=radius,
            pickable=True,
        )
    )

    # Anomalias destacadas
    anomalias = df[df["anomaly"]]
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=anomalias,
            get_position='[lon, lat]',
            get_color='[255, 0, 0]',
            get_radius=radius * 1.5,
        )
    )

deck = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    map_style="carto-darkmatter",
    tooltip={"text": "Alt: {elevation} | Cluster: {cluster}"},
)

st.pydeck_chart(deck)

# ================= INSIGHTS =================
st.subheader("🧠 Insights automáticos")

max_cluster = df.groupby("cluster")["elevation"].mean().idxmax()
min_cluster = df.groupby("cluster")["elevation"].mean().idxmin()

st.write(f"🔺 Cluster {max_cluster} tem maior altitude média")
st.write(f"🔻 Cluster {min_cluster} tem menor altitude média")
st.write(f"🚨 Anomalias detectadas: {df['anomaly'].sum()}")

# ================= GRÁFICOS =================
st.subheader("📊 Análises")

col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(df, x="elevation", nbins=30, title="Distribuição")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = px.scatter(df, x="lat", y="elevation", color="cluster", title="Latitude vs Altitude")
    st.plotly_chart(fig2, use_container_width=True)

# ================= EXPORT =================
st.subheader("⬇️ Exportar dados")

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Baixar CSV filtrado", csv, "dados_filtrados.csv")

# ================= TABELA =================
with st.expander("🔍 Ver dados"):
    st.dataframe(df)
