import streamlit as st
import json
import os
import hashlib

# =========================
# Funções de usuário
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
# Sessão
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.email = None

# =========================
# Login
# =========================
st.title("🚚 SaaS Entregas PRO")

email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if st.button("Entrar / Criar conta"):
    users = carregar()
    senha_hash = hash_senha(senha)

    if email in users:
        if users[email]["senha"] == senha_hash:
            st.session_state.logado = True
            st.session_state.email = email
            st.success("Login feito!")
        else:
            st.error("Senha errada")
    else:
        users[email] = {"senha": senha_hash, "pro": False}
        salvar(users)
        st.success("Conta criada!")

# =========================
# Área logada
# =========================
if st.session_state.logado:

    st.write("Usuário:", st.session_state.email)

    st.header("📊 Controle diário")

    ganho = st.number_input("Quanto ganhou hoje?", value=0.0)
    gasto = st.number_input("Quanto gastou?", value=0.0)

    lucro = ganho - gasto
    st.success(f"Lucro: R$ {lucro:.2f}")

    if st.button("Salvar dia"):
        st.success("Dia salvo!")

    # =========================
    # PRO
    # =========================
    users = carregar()
    user = users.get(st.session_state.email, {})

    if user.get("pro"):
        st.success("🚀 Você é PRO!")
        st.write("✔ Histórico completo")
        st.write("✔ Gráficos liberados")
    else:
        st.warning("Plano grátis")

        st.subheader("🚀 Liberar PRO")
        st.write("✔ Histórico completo")
        st.write("✔ Gráficos de lucro")
        st.write("✔ Uso ilimitado")

        st.link_button(
            "💳 Assinar por R$9,90",
            "https://www.mercadopago.com.br"  # depois colocamos o seu link real
        )
