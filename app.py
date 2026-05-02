import streamlit as st
import json
import os
import hashlib

# =========================
# BANCO
# =========================
def carregar():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def salvar(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2)

def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

# =========================
# SESSION (FIX FORÇADO)
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.email = ""

# =========================
# LOGIN BLOQUEADO
# =========================
if not st.session_state.logado:

    st.title("🔐 Login")

    email = st.text_input("Email", key="login_email")
    senha = st.text_input("Senha", type="password", key="login_senha")

    if st.button("Entrar"):
        users = carregar()

        if email in users and users[email]["senha"] == hash_senha(senha):
            st.session_state.logado = True
            st.session_state.email = email
            st.rerun()
        else:
            st.error("Login inválido")

    if st.button("Criar conta"):
        users = carregar()
        users[email] = {
            "senha": hash_senha(senha),
            "pro": False,
            "dados": []
        }
        salvar(users)

        st.session_state.logado = True
        st.session_state.email = email
        st.rerun()

    st.stop()  # 🔥 TRAVA TOTAL

# =========================
# APP
# =========================
users = carregar()
email = st.session_state.email

# 🔥 proteção extra
if email not in users:
    st.session_state.logado = False
    st.rerun()

user = users[email]

st.write(f"👤 {email}")

# =========================
# CONTROLE
# =========================
st.markdown("## 📊 Controle diário")

ganho = st.number_input("💰 Ganho", 0.0)
gasto = st.number_input("💸 Gasto", 0.0)

lucro = ganho - gasto
st.success(f"Lucro: R$ {lucro:.2f}")

if st.button("💾 Salvar dia"):
    user["dados"].append(lucro)
    users[email] = user
    salvar(users)
    st.success("Salvo!")

# =========================
# PRO
# =========================
if user.get("pro"):
    st.success("🚀 PRO ativo")

    if user["dados"]:
        st.line_chart(user["dados"])
else:
    st.warning("Plano grátis")

    st.markdown("## 🚀 Liberar PRO")

    st.link_button(
        "💳 Assinar PRO",
        "https://mpago.la/SEU_LINK_AQUI"
    )
