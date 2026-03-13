import streamlit as st
from PIL import Image

# 1. Configuration de la page
st.set_page_config(
    page_title="Baobab High Tech | Transformation Digitale",
    page_icon="🌳",
    layout="wide"
)

# 2. Style CSS Personnalisé
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        background-color: #2E7D32; 
        color: white; 
        border-radius: 8px; 
        width: 100%;
        font-weight: bold;
    }
    .css-1544g2n { padding: 1rem 0; }
    .hero-text { font-size: 1.2rem; color: #333; }
    </style>
    """, unsafe_allow_html=True)

# 3. Header : Logo et Titre
col1, col2 = st.columns([1, 4])
with col1:
    try:
        # Assurez-vous que logo.png est dans le même dossier
        st.image("logo.png", width=120)
    except:
        st.write("🌳")

with col2:
    st.title("Baobab High Tech")
    st.subheader("Digitalisons l'avenir du Sénégal")

st.divider()

# 4. Section Présentation
st.markdown("<p class='hero-text'>Nous automatisons vos processus métier pour transformer votre productivité.</p>", unsafe_allow_html=True)

# 5. Services (Grid)
st.write("## 🚀 Nos Expertises")
cols = st.columns(2)
services = [
    ("🤖 Automatisation", "Gestion intelligente de factures et stocks."),
    ("📊 Data & Reporting", "Dashboards pour piloter votre activité."),
    ("📂 Digitalisation", "Dématérialisation sécurisée de vos archives."),
    ("🔌 Intégration", "Solutions tech adaptées au marché local.")
]

for i, (titre, desc) in enumerate(services):
    with cols[i % 2]:
        st.markdown(f"**{titre}**")
        st.write(desc)

# 6. Simulateur de ROI
st.divider()
st.subheader("🧮 Calculez vos gains de productivité")
taches = st.slider("Tâches manuelles quotidiennes par employé", 1, 50, 20)
gain_mensuel = taches * 0.25 * 22 # 15 min par tâche sur 22 jours
st.metric(label="Heures économisées par mois (par employé)", value=f"{int(gain_mensuel)} H")

# 7. Formulaire de Contact
st.divider()
st.write("## 📩 Prêt à franchir le pas ?")
with st.form("contact_form", clear_on_submit=True):
    col_a, col_b = st.columns(2)
    nom = col_a.text_input("Entreprise")
    email = col_b.text_input("Email")
    besoin = st.text_area("Expliquez-nous votre besoin")
    submit = st.form_submit_button("Demander un audit gratuit")
    
    if submit:
        if nom and email:
            st.success(f"C'est noté, {nom} ! Notre équipe vous contacte sous 24h.")
        else:
            st.error("Veuillez remplir au moins le nom et l'email.")

# 8. Footer
st.markdown("---")
st.caption("Baobab High Tech | 2026 | Dakar, Sénégal")
