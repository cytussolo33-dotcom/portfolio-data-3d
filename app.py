import streamlit as st
import json
import os
import hashlib

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Controle PRO", layout="centered")

# =========================
# DATABASE
# =========================
def carregar():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def salvar(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2)

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# =========================
# SESSION
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

# =========================
# LOGIN
# =========================
if not st.session_state.user:

    st.title("🔐 Login")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar / Criar conta"):
        users = carregar()

        senha_hash = hash_senha(senha)

        if email in users:
            if users[email]["senha"] == senha_hash:
                st.session_state.user = email
                st.rerun()
            else:
                st.error("Senha errada")
        else:
            users[email] = {
                "senha": senha_hash,
                "pro": False,
                "dados": []
            }
            salvar(users)
            st.success("Conta criada!")
            st.session_state.user = email
            st.rerun()

# =========================
# APP
# =========================
else:

    email = st.session_state.user
    users = carregar()

    # 🔒 segurança real
    user_data = users.get(email, {"pro": False, "dados": []})
    is_pro = user_data.get("pro", False)

    st.title("💼 Controle Financeiro PRO")
    st.write(f"👤 {email}")

    ganho = st.number_input("💰 Ganho", min_value=0.0)
    gasto = st.number_input("💸 Gasto", min_value=0.0)

    lucro = ganho - gasto
    st.success(f"Lucro: R$ {lucro:.2f}")

    if st.button("Salvar dia"):
        user_data["dados"].append(lucro)
        users[email] = user_data
        salvar(users)
        st.success("Salvo!")

    # =========================
    # PRO
    # =========================
    if is_pro:
        st.subheader("🚀 Área PRO")

        dados = user_data.get("dados", [])
        if dados:
            st.line_chart(dados)
        else:
            st.info("Sem dados ainda")

    else:
        st.warning("Plano grátis")

        st.subheader("🚀 Liberar PRO")

        st.write("✔ Histórico completo")
        st.write("✔ Gráficos")
        st.write("✔ Uso ilimitado")

        st.link_button(
            "💳 Pagar com PIX",
            "COLOCA_SEU_LINK_DO_MERCADOPAGO_AQUI"
        )

    if st.button("Sair"):
        st.session_state.user = None
        st.rerun()
