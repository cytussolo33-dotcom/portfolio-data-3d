import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import hashlib
import pydeck as pdk
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

st.set_page_config(page_title="GeoData ULTRA++", layout="wide")

# =========================
# BANCO DE DADOS
# =========================
conn = sqlite3.connect("app.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users(
    username TEXT, password TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS datasets(
    name TEXT, data TEXT
)""")

conn.commit()

# =========================
# FUNÇÕES
# =========================
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def login(user, pwd):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, hash_pass(pwd)))
    return c.fetchone()

def create_user(user, pwd):
    c.execute("INSERT INTO users VALUES (?,?)", (user, hash_pass(pwd)))
    conn.commit()

def save_dataset(name, df):
    c.execute("INSERT INTO datasets VALUES (?,?)", (name, df.to_json()))
    conn.commit()

def load_datasets():
    c.execute("SELECT * FROM datasets")
    return c.fetchall()

# =========================
# LOGIN
# =========================
if "logged" not in st.session_state:
    st.session_state.logged = False

if not st.session_state.logged:

    st.title("🔐 Login")

    tab1, tab2 = st.tabs(["Login", "Cadastrar"])

    with tab1:
        user = st.text_input("Usuário")
        pwd = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if login(user, pwd):
                st.session_state.logged = True
                st.success("Login feito!")
                st.rerun()
            else:
                st.error("Usuário inválido")

    with tab2:
        new_user = st.text_input("Novo usuário")
        new_pwd = st.text_input("Nova senha", type="password")

        if st.button("Criar conta"):
            create_user(new_user, new_pwd)
            st.success("Conta criada!")

    st.stop()

# =========================
# APP PRINCIPAL
# =========================
st.title("🌍 GeoData ULTRA++")
st.caption("Sistema profissional com IA, mapa, banco de dados e login")

# SIDEBAR
st.sidebar.header("⚙️ Controle")

uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
clusters = st.sidebar.slider("Clusters", 2, 10, 3)
contamination = st.sidebar.slider("Anomalias", 0.01, 0.2, 0.05)

# DEMO
def gerar():
    lat = -3.1 + np.random.randn(200) * 0.02
    lon = -60 + np.random.randn(200) * 0.02
    elevation = np.random.randint(0, 300, 200)
    return pd.DataFrame({"lat": lat, "lon": lon, "elevation": elevation})

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = gerar()

# IA
kmeans = KMeans(n_clusters=clusters, n_init=10)
df["cluster"] = kmeans.fit_predict(df[["lat", "lon"]])

iso = IsolationForest(contamination=contamination)
df["anomalia"] = iso.fit_predict(df[["elevation"]])

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Pontos", len(df))
col2.metric("Clusters", df["cluster"].nunique())
col3.metric("Anomalias", (df["anomalia"] == -1).sum())

# MAPA
st.subheader("🗺️ Mapa")

m = folium.Map(
    location=[df["lat"].mean(), df["lon"].mean()],
    zoom_start=12,
    tiles="cartodbpositron"
)

HeatMap(df[["lat", "lon"]].values).add_to(m)

for _, row in df.iterrows():
    cor = "red" if row["anomalia"] == -1 else "blue"
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=5,
        color=cor,
        fill=True
    ).add_to(m)

st_folium(m, width=1000, height=500)

# 3D
st.subheader("🌐 3D")

layer = pdk.Layer(
    "ColumnLayer",
    data=df,
    get_position='[lon, lat]',
    get_elevation="elevation",
    elevation_scale=10,
    radius=40,
    get_fill_color='[0,200,255,160]'
)

view = pdk.ViewState(
    latitude=df["lat"].mean(),
    longitude=df["lon"].mean(),
    zoom=12,
    pitch=50
)

st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view))

# GRÁFICOS
colA, colB = st.columns(2)
colA.plotly_chart(px.histogram(df, x="elevation"), use_container_width=True)
colB.plotly_chart(px.scatter(df, x="lat", y="lon", color="cluster"), use_container_width=True)

# SALVAR
st.subheader("💾 Banco de dados")

name = st.text_input("Nome do dataset")
if st.button("Salvar dataset"):
    save_dataset(name, df)
    st.success("Salvo!")

datasets = load_datasets()
for d in datasets:
    if st.button(f"Carregar {d[0]}"):
        df = pd.read_json(d[1])
        st.success("Dataset carregado!")

# TABELA
st.dataframe(df)
