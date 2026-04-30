import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pydeck as pdk
from sklearn.cluster import KMeans

# CONFIG
st.set_page_config(page_title="GeoData SaaS", layout="wide")

# =========================
# 🔐 LOGIN SIMPLES
# =========================
USUARIO = "admin"
SENHA = "1234"

if "logado" not in st.session_state:
    st.session_state.logado = False

def tela_login():
    st.title("🔐 GeoData Login")
    st.caption("Acesso ao sistema profissional")

    user = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user == USUARIO and password == SENHA:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Login inválido")

# =========================
# 📊 APP PRINCIPAL
# =========================
def app():

    st.title("🌍 GeoData ULTRA++")
    st.caption("Plataforma inteligente de análise geoespacial com IA")

    # BOTÃO SAIR
    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    # =========================
    # 📂 UPLOAD
    # =========================
    file = st.file_uploader("Envie CSV (lat, lon, valor)", type=["csv"])

    def gerar_dados():
        lat = -3.1 + np.random.randn(200) * 0.02
        lon = -60 + np.random.randn(200) * 0.02
        valor = np.random.randint(10, 100, 200)
        return pd.DataFrame({"lat": lat, "lon": lon, "valor": valor})

    if file:
        df = pd.read_csv(file)
    else:
        st.info("Usando dados de exemplo")
        df = gerar_dados()

    # =========================
    # 🤖 IA (CLUSTER)
    # =========================
    kmeans = KMeans(n_clusters=3, n_init=10)
    df["cluster"] = kmeans.fit_predict(df[["lat", "lon"]])

    # =========================
    # 📊 KPIs
    # =========================
    c1, c2, c3 = st.columns(3)
    c1.metric("Pontos", len(df))
    c2.metric("Clusters", df["cluster"].nunique())
    c3.metric("Média Valor", int(df["valor"].mean()))

    # =========================
    # 🌍 MAPA 3D (PRO)
    # =========================
    st.subheader("🌍 Mapa 3D Inteligente")

    layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position='[lon, lat]',
        get_elevation='valor',
        elevation_scale=40,
        radius=60,
        get_fill_color='[cluster * 80, 200, 150]',
        pickable=True,
        auto_highlight=True,
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

    # =========================
    # 📈 GRÁFICOS
    # =========================
    st.subheader("📊 Análise Avançada")

    col1, col2 = st.columns(2)

    fig1 = px.scatter(df, x="lon", y="lat", color="cluster", size="valor")
    col1.plotly_chart(fig1, use_container_width=True)

    fig2 = px.histogram(df, x="valor", nbins=20)
    col2.plotly_chart(fig2, use_container_width=True)

    # =========================
    # 🧠 INSIGHT AUTOMÁTICO
    # =========================
    st.subheader("🧠 Insights Inteligentes")

    maior_cluster = df["cluster"].value_counts().idxmax()

    st.success(f"""
    🔎 Cluster dominante: {maior_cluster}

    📍 Recomendação:
    Foque nessa região para aumentar resultados.
    """)

# =========================
# 🚀 EXECUÇÃO
# =========================
if not st.session_state.logado:
    tela_login()
else:
    app()
