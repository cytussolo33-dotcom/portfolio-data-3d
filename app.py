import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

# CONFIGURAÇÃO
st.set_page_config(
    page_title="GeoData Platform 3D",
    layout="wide"
)

st.title("🌍 GeoData Platform 3D")
st.markdown("Análise inteligente de dados geoespaciais com visualização avançada")

# UPLOAD
uploaded_file = st.file_uploader(
    "📂 Envie um CSV com colunas: lat, lon, elevation",
    type=["csv"]
)

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # 🔥 LIMPEZA (resolve seu erro)
    df.columns = df.columns.str.strip().str.lower()

    # Verifica colunas obrigatórias
    required = {"lat", "lon", "elevation"}
    if not required.issubset(df.columns):
        st.error("O CSV precisa ter colunas: lat, lon, elevation")
        st.stop()

    # Converter para número
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df["elevation"] = pd.to_numeric(df["elevation"], errors="coerce")

    # Remove valores inválidos
    df = df.dropna()

    if df.empty:
        st.error("Os dados ficaram vazios após limpeza 😢")
        st.stop()

    # FILTRO
    min_alt = st.slider(
        "Altitude mínima",
        int(df["elevation"].min()),
        int(df["elevation"].max()),
        int(df["elevation"].min())
    )

    df = df[df["elevation"] >= min_alt]

    # MÉTRICAS
    col1, col2, col3 = st.columns(3)

    col1.metric("Pontos", len(df))
    col2.metric("Média", f"{df['elevation'].mean():.0f} m")
    col3.metric("Máxima", f"{df['elevation'].max():.0f} m")

    # MAPA 3D
    st.subheader("🗺️ Mapa 3D")

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10",
        initial_view_state=pdk.ViewState(
            latitude=df["lat"].mean(),
            longitude=df["lon"].mean(),
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
                get_fill_color='[200, 30, 0, 160]',
                pickable=True,
            ),
        ],
    ))

    # GRÁFICO
    st.subheader("📊 Distribuição de Altitude")

    fig = px.histogram(df, x="elevation", nbins=30)
    st.plotly_chart(fig)
