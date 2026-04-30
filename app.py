import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

st.set_page_config(page_title="GeoData Platform 3D", layout="wide")

st.title("🌍 GeoData Platform 3D")
st.markdown("Plataforma interativa para análise geoespacial em 3D")

uploaded_file = st.file_uploader("📂 Envie um CSV (lat, lon, elevation)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Limpeza
    df.columns = df.columns.str.strip().str.lower()
    required = {"lat", "lon", "elevation"}

    if not required.issubset(df.columns):
        st.error("CSV precisa ter: lat, lon, elevation")
        st.stop()

    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df["elevation"] = pd.to_numeric(df["elevation"], errors="coerce")

    df = df.dropna()

    # 🎯 NOVO: Filtro por altitude (range)
    min_alt, max_alt = st.slider(
        "Faixa de Altitude",
        int(df["elevation"].min()),
        int(df["elevation"].max()),
        (int(df["elevation"].min()), int(df["elevation"].max()))
    )

    df = df[(df["elevation"] >= min_alt) & (df["elevation"] <= max_alt)]

    # 🎯 NOVO: tamanho dos pontos
    size = st.slider("Tamanho das colunas 3D", 50, 500, 200)

    # 🎯 NOVO: cor baseada na altitude
    df["color"] = df["elevation"].apply(lambda x: [255, 0, 0] if x > df["elevation"].mean() else [0, 0, 255])

    # MÉTRICAS
    col1, col2, col3 = st.columns(3)
    col1.metric("Pontos", len(df))
    col2.metric("Média", f"{df['elevation'].mean():.0f} m")
    col3.metric("Máxima", f"{df['elevation'].max():.0f} m")

    # MAPA
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
                radius=size,
                get_fill_color='color',
                pickable=True,
            ),
        ],
    ))

    # GRÁFICO
    st.subheader("📊 Distribuição de Altitude")
    fig = px.histogram(df, x="elevation", nbins=30)
    st.plotly_chart(fig)

    # 🎯 NOVO: tabela
    st.subheader("📋 Dados")
    st.dataframe(df)
