import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

# CONFIG
st.set_page_config(page_title="GeoData Platform 3D", layout="wide")

# ESTILO
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("🌍 GeoData Platform 3D")
st.markdown("Análise inteligente de dados geoespaciais com visualização 3D interativa")

# UPLOAD
uploaded_file = st.file_uploader("📂 Envie um CSV com colunas: lat, lon, elevation", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # VALIDAÇÃO
    if not all(col in df.columns for col in ["lat", "lon", "elevation"]):
        st.error("O CSV precisa ter colunas: lat, lon, elevation")
        st.stop()

    # FILTRO DE ALTITUDE
    min_alt, max_alt = st.slider(
        "Faixa de altitude",
        int(df["elevation"].min()),
        int(df["elevation"].max()),
        (int(df["elevation"].min()), int(df["elevation"].max()))
    )

    # TAMANHO DAS COLUNAS
    radius = st.slider("Tamanho das colunas 3D", 50, 500, 200)

    df = df[(df["elevation"] >= min_alt) & (df["elevation"] <= max_alt)]

    # MÉTRICAS
    col1, col2, col3 = st.columns(3)

    col1.metric("Pontos", len(df))
    col2.metric("Média", f"{df.elevation.mean():.0f} m")
    col3.metric("Máxima", f"{df.elevation.max():.0f} m")

    # MAPA 3D
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

    # GRÁFICO
    st.subheader("📊 Distribuição de Altitude")
    fig = px.histogram(df, x="elevation", nbins=30)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Envie um arquivo CSV para começar 🚀")
