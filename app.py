import streamlit as st

# 1. Configuration de la page
st.set_page_config(
    page_title="Baobab High Tech | Transformation Digitale",
    page_icon="🌳",
    layout="wide"
)

# 2. Style CSS Premium (Design Moderne)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #e1e4e8;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #1565C0 !important;
        color: white !important;
        border-radius: 25px !important;
        padding: 10px 30px !important;
        font-weight: bold !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Bannière Hero
st.markdown("""
    <div style="background-color: #0d47a1; color: white; padding: 60px 20px; border-radius: 20px; text-align: center; margin-bottom: 30px;">
        <h1 style="color: white; font-size: 3rem;">Baobab High Tech</h1>
        <p style="font-size: 1.5rem;">L'intelligence numérique au service de votre croissance au Sénégal.</p>
    </div>
""", unsafe_allow_html=True)

# 4. Logo et Présentation
col1, col2 = st.columns([1, 3])
with col1:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.write("🌳 Logo Baobab")
with col2:
    st.write("## À propos")
    st.write("Nous aidons les PME sénégalaises à digitaliser leurs processus métier pour gagner en efficacité et en compétitivité.")

st.divider()

# 5. Section Services avec Cartes Stylisées
st.write("## 💡 Nos Expertises")
cols = st.columns(3)

def service_card(col, icon, title, text):
    col.markdown(f"""
    <div class="card" style="text-align: center; height: 300px;">
        <div style="font-size: 3rem; margin-bottom: 10px;">{icon}</div>
        <h3>{title}</h3>
        <p>{text}</p>
    </div>
    """, unsafe_allow_html=True)

service_card(cols[0], "🤖", "Automatisation", "Supprimez les tâches manuelles répétitives de vos équipes.")
service_card(cols[1], "📊", "Business Intelligence", "Pilotez avec des tableaux de bord en temps réel.")
service_card(cols[2], "☁️", "Transformation Cloud", "Sécurisez vos données et archives en ligne.")

# 6. Simulateur de ROI
st.divider()
st.subheader("🧮 Calculez vos gains de productivité")
taches = st.slider("Nombre de tâches manuelles par jour / employé", 1, 50, 20)
gain_mensuel = taches * 0.25 * 22 
st.metric(label="Heures libérées par mois (par employé)", value=f"{int(gain_mensuel)} H")

# 7. Formulaire de Contact
st.divider()
st.write("## 📩 Prêt à franchir le pas ?")
with st.form("contact_form", clear_on_submit=True):
    col_a, col_b = st.columns(2)
    nom = col_a.text_input("Entreprise")
    email = col_b.text_input("Email professionnel")
    besoin = st.text_area("Expliquez-nous votre besoin")
    submit = st.form_submit_button("Demander un audit gratuit")
    
    if submit:
        if nom and email:
            st.success(f"Merci {nom}, notre équipe vous contacte sous 24h.")
        else:
            st.error("Veuillez remplir au moins le nom et l'email.")

# 8. Footer
st.markdown("---")
st.caption("Baobab High Tech © 2026 | Dakar, Sénégal | Digitalisons l'avenir, ensemble.")
