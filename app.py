import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import numpy as np

# IA (opcional)
try:
    from sklearn.cluster import KMeans
    IA_DISPONIVEL = True
except:
    IA_DISPONIVEL = False

# CONFIG
st.set_page_config(page_title="GeoData Platform PRO AI", layout="wide")

# ESTILO
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# CACHE
@st.cache_data
def carregar_dados(file):
    return pd.read_csv(file)

# HEADER
st.title("🌍 GeoData Platform PRO AI")
st.markdown("Plataforma avançada com IA para análise geoespacial 3D")

# SIDEBAR
st.sidebar.header("⚙️ Configurações")

modo = st.sidebar.selectbox(
    "Modo de visualização",
    ["Mapa 3D", "Heatmap", "Dispersão + IA"]
)

# UPLOAD
uploaded_file = st.file_uploader("📂 Envie um CSV com colunas: lat, lon, elevation", type=["csv"])

if uploaded_file:
    df = carregar_dados(uploaded_file)

    # VALIDAR
    if not all(col in df.columns for col in ["lat", "lon", "elevation"]):
        st.error("CSV precisa ter: lat, lon, elevation")
        st.stop()

    # FILTRO
    min_alt, max_alt = st.slider(
        "Faixa de altitude",
        int(df["elevation"].min()),
        int(df["elevation"].max()),
        (int(df["elevation"].min()), int(df["elevation"].max()))
    )

    df = df[(df["elevation"] >= min_alt) & (df["elevation"] <= max_alt)]

    radius = st.slider("Tamanho das colunas", 50, 500, 200)

    # MÉTRICAS
    col1, col2, col3 = st.columns(3)
    col1.metric("Pontos", len(df))
    col2.metric("Média", f"{df.elevation.mean():.0f} m")
    col3.metric("Máxima", f"{df.elevation.max():.0f} m")

    # =========================
    # MODOS
    # =========================

    if modo == "Mapa 3D":
        st.subheader("🗺️ Mapa 3D")

        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/dark-v10',
            initial_view_state=pdk.ViewState(
                latitude=df['lat'].mean(),
                longitude=df['lon'].mean(),
                zoom=10,
                pitch=50,
            ),
            layers=[
                pdk.Layer(
                    "ColumnLayer",
                    data=df,
                    get_position='[lon, lat]',
                    get_elevation='elevation',
                    elevation_scale=50,
                    radius=radius,
                    get_fill_color='[elevation * 5, 100, 200, 160]',
                    pickable=True,
                )
            ],
        ))

    elif modo == "Heatmap":
        st.subheader("🔥 Heatmap")

        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/dark-v10',
            initial_view_state=pdk.ViewState(
                latitude=df['lat'].mean(),
                longitude=df['lon'].mean(),
                zoom=10,
                pitch=40,
            ),
            layers=[
                pdk.Layer(
                    "HeatmapLayer",
                    data=df,
                    get_position='[lon, lat]',
                    get_weight="elevation",
                )
            ],
        ))

    elif modo == "Dispersão + IA":
        st.subheader("🧠 Análise com IA")

        if IA_DISPONIVEL:
            k = st.slider("Número de clusters", 2, 10, 3)

            coords = df[["lat", "lon", "elevation"]]

            kmeans = KMeans(n_clusters=k, n_init=10)
            df["cluster"] = kmeans.fit_predict(coords)

            fig = px.scatter_3d(
                df,
                x="lon",
                y="lat",
                z="elevation",
                color="cluster"
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("Scikit-learn não instalado")

    # GRÁFICO
    st.subheader("📊 Distribuição")
    fig = px.histogram(df, x="elevation", nbins=30)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Envie um CSV para começar 🚀")
