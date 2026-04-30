import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import numpy as np

# IA
try:
    from sklearn.cluster import KMeans
    from sklearn.ensemble import IsolationForest
    IA = True
except:
    IA = False

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

# TÍTULO
st.title("🌍 GeoData Platform PRO AI")
st.markdown("Sistema avançado de análise geoespacial com Inteligência Artificial")

# SIDEBAR
st.sidebar.title("⚙️ Configurações")

modo = st.sidebar.selectbox(
    "Modo de visualização",
    ["Mapa 3D", "Heatmap", "IA Insights"]
)

# UPLOAD (CORRIGIDO)
file = st.file_uploader(
    "📂 Envie um arquivo CSV (lat, lon, elevation)",
    type=["csv"]
)

if file:
    df = pd.read_csv(file)

    # VALIDAÇÃO
    if not all(col in df.columns for col in ["lat", "lon", "elevation"]):
        st.error("❌ O CSV precisa ter colunas: lat, lon, elevation")
        st.stop()

    # LIMPEZA
    df = df.dropna()

    # FILTRO
    min_alt, max_alt = st.slider(
        "Faixa de altitude",
        int(df["elevation"].min()),
        int(df["elevation"].max()),
        (int(df["elevation"].min()), int(df["elevation"].max()))
    )

    df = df[(df["elevation"] >= min_alt) & (df["elevation"] <= max_alt)]

    # MÉTRICAS
    col1, col2, col3 = st.columns(3)
    col1.metric("Pontos", len(df))
    col2.metric("Média", f"{df.elevation.mean():.0f} m")
    col3.metric("Máxima", f"{df.elevation.max():.0f} m")

    # =========================
    # MAPA 3D
    # =========================
    if modo == "Mapa 3D":

        st.subheader("🗺️ Mapa 3D Interativo")

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
                    radius=200,
                    get_fill_color='[elevation * 5, 100, 200]',
                    pickable=True,
                )
            ],
        ))

    # =========================
    # HEATMAP
    # =========================
    elif modo == "Heatmap":

        st.subheader("🔥 Heatmap de Densidade")

        st.pydeck_chart(pdk.Deck(
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

    # =========================
    # IA INSIGHTS
    # =========================
    elif modo == "IA Insights":

        st.subheader("🤖 Análise com Inteligência Artificial")

        if IA:

            # CLUSTER
            kmeans = KMeans(n_clusters=3, n_init=10)
            df["cluster"] = kmeans.fit_predict(df[["lat", "lon", "elevation"]])

            # ANOMALIA
            iso = IsolationForest(contamination=0.1, random_state=42)
            df["anomalia"] = iso.fit_predict(df[["lat", "lon", "elevation"]])

            # MAPA
            st.pydeck_chart(pdk.Deck(
                initial_view_state=pdk.ViewState(
                    latitude=df['lat'].mean(),
                    longitude=df['lon'].mean(),
                    zoom=10,
                    pitch=50,
                ),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=df,
                        get_position='[lon, lat]',
                        get_color='[cluster * 80, 150, 200]',
                        get_radius=120,
                    )
                ],
            ))

            # INSIGHTS
            st.markdown("### 📊 Resultados")

            st.write(f"🔹 Clusters encontrados: {df.cluster.nunique()}")
            st.write(f"🚨 Anomalias detectadas: {(df.anomalia == -1).sum()}")

            st.write("📈 Média de altitude por cluster:")
            st.dataframe(df.groupby("cluster")["elevation"].mean())

        else:
            st.error("❌ Biblioteca scikit-learn não instalada")

else:
    st.info("📂 Envie um CSV para começar 🚀")
