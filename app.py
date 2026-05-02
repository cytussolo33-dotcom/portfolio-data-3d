# ==============================
# 📊 CONTROLE REAL
# ==============================
st.subheader("📊 Controle de entregas")

# Inputs
ganho = st.number_input("💰 Quanto você ganhou hoje?", min_value=0.0)
gasto = st.number_input("💸 Quanto gastou hoje?", min_value=0.0)

lucro = ganho - gasto

st.write(f"🟢 Lucro do dia: R$ {lucro:.2f}")

# ==============================
# 💾 SALVAR DADOS
# ==============================
if st.button("Salvar dia"):

    users = carregar_usuarios()
    email = st.session_state["email"]

    if "historico" not in users[email]:
        users[email]["historico"] = []

    users[email]["historico"].append({
        "ganho": ganho,
        "gasto": gasto,
        "lucro": lucro
    })

    salvar_usuarios(users)
    st.success("Dia salvo!")

# ==============================
# 📈 HISTÓRICO (PRO)
# ==============================
users = carregar_usuarios()
email = st.session_state["email"]

historico = users[email].get("historico", [])

if st.session_state["pro"]:

    st.subheader("📈 Seu histórico")

    total_lucro = sum(d["lucro"] for d in historico)

    st.write(f"💰 Lucro total: R$ {total_lucro:.2f}")
    st.write(f"📅 Dias registrados: {len(historico)}")

    for dia in historico[::-1]:
        st.write(f"💰 {dia['ganho']} | 💸 {dia['gasto']} | 🟢 {dia['lucro']}")

else:
    st.warning("🔒 Libere o PRO para ver histórico completo")
