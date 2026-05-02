import streamlit as st
import mercadopago
import json
import os
import hashlib

# ==============================
# CONFIG
# ==============================
def get_secret(key, default=None):
    try:
        return st.secrets[key]
    except Exception:
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
st.title("SaaS Entregas PRO")

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

    st.write(f"Usuario: {st.session_state['email']}")

    users = carregar_usuarios()
    email = st.session_state["email"]

    # Atualiza PRO
    if email in users:
        st.session_state["pro"] = users[email].get("pro", False)

    # ==============================
    # CONTROLE
    # ==============================
    st.subheader("Controle de entregas")

    ganho = st.number_input("Quanto ganhou hoje?", min_value=0.0)
    gasto = st.number_input("Quanto gastou?", min_value=0.0)

    lucro = ganho - gasto

    st.write(f"Lucro do dia: R$ {lucro:.2f}")

    # Salvar
    if st.button("Salvar dia"):

        if "historico" not in users[email]:
            users[email]["historico"] = []

        users[email]["historico"].append({
            "ganho": ganho,
            "gasto": gasto,
            "lucro": lucro
        })

        salvar_usuarios(users)
        st.success("Salvo com sucesso!")

    # ==============================
    # PRO
    # ==============================
    if st.session_state["pro"]:

        st.subheader("Historico")

        historico = users[email].get("historico", [])

        total = sum(d["lucro"] for d in historico)

        st.write(f"Lucro total: R$ {total:.2f}")
        st.write(f"Dias registrados: {len(historico)}")

        for d in historico[::-1]:
            st.write(f"Ganhou: {d['ganho']} | Gastou: {d['gasto']} | Lucro: {d['lucro']}")

    else:
        st.warning("Plano gratis limitado")

        if st.button("Virar PRO"):

            pagamento = {
                "transaction_amount": 9.90,
                "description": "Plano PRO",
                "payment_method_id": "pix",
                "payer": {
                    "email": email
                },
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
                    st.info("Pague o PIX e depois atualize a pagina.")
                else:
                    st.error("Erro ao gerar pagamento")
                    st.write(res)

            except Exception as e:
                st.error("Erro no pagamento")
                st.write(str(e))
