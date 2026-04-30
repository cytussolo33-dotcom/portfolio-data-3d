import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pydeck as pdk
from sklearn.cluster import KMeans

st.set_page_config(layout="wide")

st.title("🚚 Painel Inteligente de Entregas")
st.caption("Descubra onde estão suas entregas e otimize sua operação")

# Upload
file = st.file_uploader("Envie seu CSV (lat, lon, entregas)", type=["csv"])

# Dados demo
def gerar():
    lat = -3.1 + np.random.randn(200) * 0.02
    lon = -60 + np.random.randn(200) * 0.02
    entregas = np.random.randint(1, 50, 200)
    return pd.DataFrame({"lat": lat, "lon": lon, "entregas": entregas})

if file:
    df = pd.read_csv(file)
else:
    st.info("Usando dados de exemplo")
    df = gerar()

# Cluster
kmeans = KMeans(n_clusters=3, n_init=10)
df["cluster"] = kmeans.fit_predict(df[["lat", "lon"]])

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total de pontos", len(df))
col2.metric("Entregas médias", int(df["entregas"].mean()))
col3.metric("Clusters", df["cluster"].nunique())

# Mapa
st.subheader("📍 Mapa de Entregas")

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[lon, lat]',
    get_radius=100,
    get_fill_color='[0, 200, 255, 160]',
)

view = pdk.ViewState(
    latitude=df["lat"].mean(),
    longitude=df["lon"].mean(),
    zoom=11,
)

st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view))

# Gráfico
st.subheader("📊 Análise")

fig = px.histogram(df, x="entregas", nbins=30)
st.plotly_chart(fig, use_container_width=True)

# Insight automático
st.subheader("🧠 Insights")

maior_cluster = df.groupby("cluster")["entregas"].mean().idxmax()

st.success(f"""
Cluster mais forte: {maior_cluster}

👉 Essa região tem mais entregas  
👉 Pode focar marketing ou logística ali
""")
