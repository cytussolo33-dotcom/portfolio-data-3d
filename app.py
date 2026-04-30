import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ========================
# FUNÇÕES
# ========================

def carregar_usuarios():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def salvar_usuarios(usuarios):
    with open("users.json", "w") as f:
        json.dump(usuarios, f, indent=2)

def carregar_dados(user):
    arquivo = f"dados_{user}.json"
    if not os.path.exists(arquivo):
        return []
    with open(arquivo, "r") as f:
        return json.load(f)

def salvar_dados(user, dados):
    with open(f"dados_{user}.json", "w") as f:
        json.dump(dados, f, indent=2)

# ========================
# CONFIG
# ========================

st.set_page_config(page_title="Lucro Delivery PRO")

# ========================
# LOGIN
# ========================

if "logado" not in st.session_state:
    st.session_state.logado = False

usuarios = carregar_usuarios()

if not st.session_state.logado:
    st.title("🔐 Login")

    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user in usuarios and usuarios[user]["senha"] == senha:
            st.session_state.logado = True
            st.session_state.usuario = user
            st.session_state.is_admin = usuarios[user].get("role") == "admin"
            st.success(f"Bem-vindo, {user}")
            st.rerun()
        else:
            st.error("Login inválido")

    st.stop()

# ========================
# SISTEMA
# ========================

user = st.session_state.usuario
usuario_info = usuarios[user]
dados = carregar_dados(user)

st.title("🚀 Lucro Delivery")
st.success(f"Bem-vindo, {user}")

if st.button("Sair"):
    st.session_state.logado = False
    st.session_state.is_admin = False
    st.rerun()

# ========================
# CONTROLE DE ENTREGAS
# ========================

st.header("📦 Controle de Entregas")

valor = st.number_input("Valor (R$)", min_value=0.0)
custo = st.number_input("Custo (R$)", min_value=0.0)

if st.button("Adicionar"):
    lucro = valor - custo
    dados.append({
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "valor": valor,
        "custo": custo,
        "lucro": lucro
    })
    salvar_dados(user, dados)
    st.success("Adicionado!")
    st.rerun()

# ========================
# RESUMO
# ========================

st.header("📊 Resumo")

if dados:
    df = pd.DataFrame(dados)

    st.metric("Entregas", len(df))
    st.metric("Faturamento", f"R$ {df['valor'].sum():.2f}")
    st.metric("Lucro", f"R$ {df['lucro'].sum():.2f}")

    st.dataframe(df)
    st.line_chart(df["lucro"])
else:
    st.info("Sem dados ainda")

# ========================
# PRO
# ========================

st.header("💎 Versão PRO")

if usuario_info.get("pro"):
    st.success("Você é PRO 🎉")
else:
    if st.button("Pagar R$ 9,90 (simulado)"):
        usuarios[user]["pro"] = True
        salvar_usuarios(usuarios)
        st.success("Pagamento aprovado!")
        st.rerun()

# ========================
# 🔐 ACESSO AO PAINEL ADMIN
# ========================

st.header("🔒 Painel Admin")

if usuario_info.get("role") == "admin":

    senha_admin = st.text_input("Digite sua senha para acessar o painel", type="password")

    if senha_admin == usuario_info["senha"]:

        st.success("Acesso liberado ao painel ADMIN")

        st.subheader("🛠 Gerar login")

        novo_user = st.text_input("Novo usuário")
        nova_senha = st.text_input("Senha do usuário", type="password")

        if st.button("Criar usuário"):
            if novo_user in usuarios:
                st.error("Usuário já existe")
            else:
                usuarios[novo_user] = {
                    "senha": nova_senha,
                    "pro": False,
                    "role": "user"
                }
                salvar_usuarios(usuarios)
                st.success("Usuário criado!")

    elif senha_admin:
        st.error("Senha incorreta")

else:
    st.info("Área restrita ao administrador")
