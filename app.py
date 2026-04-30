import streamlit as st
import pandas as pd
import json
import os

# -----------------------
# BANCO DE USUÁRIOS
# -----------------------
DB_FILE = "usuarios.json"

def carregar_usuarios():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def salvar_usuarios(usuarios):
    with open(DB_FILE, "w") as f:
        json.dump(usuarios, f)

usuarios = carregar_usuarios()

# -----------------------
# LOGIN
# -----------------------
st.set_page_config(page_title="Lucro Delivery PRO", layout="centered")

if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario = None
    st.session_state.pro = False

st.title("🚀 Lucro Delivery")

if not st.session_state.logado:

    menu = st.radio("Escolha", ["Login", "Criar conta"])

    if menu == "Login":
        user = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if user in usuarios and usuarios[user]["senha"] == senha:
                st.session_state.logado = True
                st.session_state.usuario = user
                st.session_state.pro = usuarios[user]["pro"]
                st.success("Login realizado!")
                st.rerun()
            else:
                st.error("Login inválido")

    if menu == "Criar conta":
        new_user = st.text_input("Novo usuário")
        new_pass = st.text_input("Nova senha", type="password")

        if st.button("Cadastrar"):
            if new_user in usuarios:
                st.warning("Usuário já existe")
            else:
                usuarios[new_user] = {"senha": new_pass, "pro": False}
                salvar_usuarios(usuarios)
                st.success("Conta criada!")

# -----------------------
# PAINEL LOGADO
# -----------------------
else:
    st.success(f"Bem-vindo, {st.session_state.usuario}")

    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    # -----------------------
    # CONTROLE DE ENTREGAS
    # -----------------------
    st.header("📦 Controle de Entregas")

    valor = st.number_input("Valor da entrega (R$)", min_value=0.0)
    custo = st.number_input("Custo (R$)", min_value=0.0)

    if "dados" not in st.session_state:
        st.session_state.dados = []

    if st.button("Adicionar entrega"):
        lucro = valor - custo
        st.session_state.dados.append({
            "valor": valor,
            "custo": custo,
            "lucro": lucro
        })

    if st.session_state.dados:
        df = pd.DataFrame(st.session_state.dados)

        st.subheader("📊 Resumo")
        st.write("Total entregas:", len(df))
        st.write("Faturamento:", df["valor"].sum())
        st.write("Lucro:", df["lucro"].sum())

        # PRO libera gráfico
        if st.session_state.pro:
            st.line_chart(df["lucro"])
        else:
            st.warning("🔒 Gráficos apenas na versão PRO")

    # -----------------------
    # PAGAMENTO (SIMULADO)
    # -----------------------
    st.header("💎 Versão PRO")

    if st.session_state.pro:
        st.success("Você já é PRO 🚀")
    else:
        if st.button("Pagar R$ 9,90 (simulado)"):
            usuarios[st.session_state.usuario]["pro"] = True
            salvar_usuarios(usuarios)
            st.session_state.pro = True
            st.success("Pagamento aprovado!")
            st.rerun()

    # -----------------------
    # ADMIN (GERAR LOGINS)
    # -----------------------
    if st.session_state.usuario == "admin":
        st.header("⚙️ Painel Admin")

        novo_user = st.text_input("Criar usuário")
        nova_senha = st.text_input("Senha do usuário")

        if st.button("Gerar login"):
            usuarios[novo_user] = {"senha": nova_senha, "pro": False}
            salvar_usuarios(usuarios)
            st.success(f"Usuário {novo_user} criado!")
