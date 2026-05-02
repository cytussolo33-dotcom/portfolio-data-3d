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

# =========================
# SEGURANÇA
# =========================
def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

# =========================
# SESSION
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.email = None

# =========================
# LOGIN
# =========================
st.title("💰 Controle de Entregas PRO")

email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if st.button("Entrar / Criar conta"):
    users = carregar()

    if email in users:
        if users[email]["senha"] == hash_senha(senha):
            st.session_state.logado = True
            st.session_state.email = email
            st.success("Login feito!")
        else:
            st.error("Senha incorreta")
    else:
        users[email] = {
            "senha": hash_senha(senha),
            "pro": False,
            "dados": []
        }
        salvar(users)
        st.session_state.logado = True
        st.session_state.email = email
        st.success("Conta criada!")

# =========================
# AREA LOGADA
# =========================
if st.session_state.logado:

    users = carregar()
    email = st.session_state.email

    if email not in users:
        st.error("Usuário não encontrado")
        st.stop()

    user = users[email]

    st.write(f"👤 {email}")

    # 🔥 PRO vem SOMENTE do banco
    pro = user.get("pro", False)

    st.markdown("## 📊 Controle diário")

    ganho = st.number_input("💰 Quanto ganhou hoje?", min_value=0.0)
    gasto = st.number_input("💸 Quanto gastou?", min_value=0.0)

    lucro = ganho - gasto

    if lucro >= 0:
        st.success(f"🟢 Lucro: R$ {lucro:.2f}")
    else:
        st.error(f"🔴 Prejuízo: R$ {lucro:.2f}")

    # =========================
    # SALVAR DIA
    # =========================
    if st.button("💾 Salvar dia"):

        if "dados" not in user:
            user["dados"] = []

        user["dados"].append(lucro)
        users[email] = user
        salvar(users)

        st.success("Dia salvo!")

    # =========================
    # PRO
    # =========================
    if pro:
        st.success("🚀 Você é PRO!")

        st.subheader("📈 Histórico")

        if user.get("dados"):
            st.line_chart(user["dados"])
        else:
            st.info("Sem dados ainda")

    else:
        st.warning("Plano grátis limitado")

        st.markdown("## 🚀 Liberar PRO")

        st.write("✔ Histórico completo")
        st.write("✔ Gráficos de lucro")
        st.write("✔ Uso ilimitado")

        # 🔥 IMPORTANTE: NÃO ativa PRO aqui
        st.link_button(
            "💳 Assinar PRO",
            "COLOCA_SEU_LINK_DO_MERCADOPAGO_AQUI"
        )
