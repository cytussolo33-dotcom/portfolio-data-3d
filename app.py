import streamlit as st
import mercadopago
import json
import os
import hashlib
import pandas as pd

# ==============================
# CONFIG
# ==============================
def get_secret(key, default=None):
    try:
        return st.secrets[key]
    except:
        return default

ACCESS_TOKEN = get_secret("MP_ACCESS_TOKEN")
WEBHOOK_URL = get_secret("WEBHOOK_URL")

sdk = mercadopago.SDK(ACCESS_TOKEN)

# ==============================
# BANCO
# ==============================
def carregar_usuarios():
    if not os.path.exists("users.json"):
        return {}
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def salvar_usuarios(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2)

# ==============================
# SEGURANÇA
# ==============================
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# ==============================
# SESSION
# ==============================
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if "email" not in st.session_state:
    st.session_state["email"] = None

if "pro" not in st.session_state:
    st.session_state["pro"] = False

# ==============================
# LOGIN
# ==============================
st.title("💰 Controle de Entregas PRO")

email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if st.button("Entrar / Criar conta"):
    users = carregar_usuarios()

    if email in users:
        if users[email]["senha"] == hash_senha(senha):
            st.session_state["logado"] = True
            st.session_state["email"] = email
            st.success("Login feito!")
        else:
            st.error("Senha incorreta")
    else:
        users[email] = {
            "senha": hash_senha(senha),
            "pro": False,
            "historico": []
        }
        salvar_usuarios(users)
        st.success("Conta criada!")

# ==============================
# AREA LOGADA
# ==============================
if st.session_state["logado"]:

    users = carregar_usuarios()
    email = st.session_state["email"]

    st.write(f"👤 {email}")

    # Atualiza PRO
    if email in users:
        st.session_state["pro"] = users[email].get("pro", False)

    historico = users[email].get("historico", [])

    st.markdown("## 📊 Controle diário")

    ganho = st.number_input("💰 Quanto ganhou hoje?", min_value=0.0)
    gasto = st.number_input("💸 Quanto gastou?", min_value=0.0)

    lucro = ganho - gasto

    if lucro >= 0:
        st.success(f"🟢 Lucro: R$ {lucro:.2f}")
    else:
        st.error(f"🔴 Prejuízo: R$ {lucro:.2f}")

    # ==============================
    # LIMITAÇÃO FREE
    # ==============================
    if not st.session_state["pro"] and len(historico) >= 3:
        st.warning("🔒 Limite grátis atingido (3 dias)")
        st.info("👉 Libere o PRO para continuar usando")

    else:
        if st.button("💾 Salvar dia"):
            historico.append({
                "ganho": ganho,
                "gasto": gasto,
                "lucro": lucro
            })
            users[email]["historico"] = historico
            salvar_usuarios(users)
            st.success("Dia salvo!")

    # ==============================
    # PRO FEATURES
    # ==============================
    if st.session_state["pro"]:

        st.markdown("## 📈 Seu desempenho")

        df = pd.DataFrame(historico)

        if not df.empty:
            total = df["lucro"].sum()

            st.write(f"💰 Lucro total: R$ {total:.2f}")
            st.write(f"📅 Dias registrados: {len(df)}")

            st.line_chart(df["lucro"])

            st.dataframe(df[::-1])

    else:
        st.markdown("## 🚀 Liberar PRO")

        st.write("✔ Histórico completo")
        st.write("✔ Gráficos de lucro")
        st.write("✔ Uso ilimitado")

        if st.button("💳 Assinar por R$9,90"):

            pagamento = {
                "transaction_amount": 9.90,
                "description": "Plano PRO",
                "payment_method_id": "pix",
                "payer": {"email": email},
                "external_reference": email,
                "notification_url": WEBHOOK_URL
            }

            try:
                res = sdk.payment().create(pagamento)

                if res["status"] == 201:
                    data = res["response"]
                    td = data["point_of_interaction"]["transaction_data"]

                    st.image(f"data:image/png;base64,{td['qr_code_base64']}")
                    st.code(td["qr_code"])
                    st.info("💡 Pague o PIX e atualize a página")
                else:
                    st.error("Erro ao gerar pagamento")

            except Exception as e:
                st.error(str(e))
