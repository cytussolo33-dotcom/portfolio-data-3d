import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pydeck as pdk
from sklearn.cluster import KMeans

# CONFIG
st.set_page_config(page_title="GeoData ULTRA++", layout="wide")

# LOGIN SIMPLES
if "logado" not in st.session_state:
    st.session_state.logado = False

def login():
    st.title("🔐 Login")

    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user == "admin" and senha == "123":
            st.session_state.logado = True
        else:
            st.error("Usuário ou senha inválidos")

def app():
    st.title("🌍 GeoData ULTRA++")
    st.caption("Sistema profissional com IA, mapa e dashboard")

    # Upload
    file = st.file_uploader("Envie CSV (lat, lon, valor)", type=["csv"])

    # Dados fake se não tiver arquivo
    def gerar():
        lat = -3.1 + np.random.randn(200) * 0.02
        lon = -60 + np.random.randn(200) * 0.02
        valor = np.random.randint(1, 100, 200)
        return pd.DataFrame({"lat": lat, "lon": lon, "valor": valor})

    if file:
        df = pd.read_csv(file)
    else:
        st.info("Usando dados de exemplo")
        df = gerar()

    # IA (cluster)
    kmeans = KMeans(n_clusters=3, n_init=10)
    df["cluster"] = kmeans.fit_predict(df[["lat", "lon"]])

    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Pontos", len(df))
    c2.metric("Clusters", df["cluster"].nunique())
    c3.metric("Média", int(df["valor"].mean()))

    # MAPA 3D (SEM BUG)
    st.subheader("🌍 Mapa 3D")

    layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position='[lon, lat]',
        get_elevation='valor',
        elevation_scale=50,
        radius=50,
        get_fill_color='[cluster * 80, 100, 200]',
        pickable=True,
        auto_highlight=True
    )

    view = pdk.ViewState(
        latitude=df["lat"].mean(),
        longitude=df["lon"].mean(),
        zoom=11,
        pitch=50
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        map_style="mapbox://styles/mapbox/dark-v10"
    ))

    # GRÁFICO
    st.subheader("📊 Análise")

    fig = px.scatter(
        df,
        x="lon",
        y="lat",
        color="cluster",
        size="valor"
    )
    st.plotly_chart(fig, use_container_width=True)

# FLOW
if not st.session_state.logado:
    login()
else:
    app()
