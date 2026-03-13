import streamlit as st
from PIL import Image

# Configuration de la page
st.set_page_config(
    page_title="Baobab High Tech | Transformation Digitale",
    page_icon="🌳",
    layout="wide"
)

# --- STYLE PERSONNALISÉ (Couleurs de votre logo) ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        background-color: #2E7D32; /* Vert Baobab */
        color: white;
        border-radius: 10px;
        padding: 10px 24px;
    }
    h1 {
        color: #1565C0; /* Bleu Tech */
    }
    .card {
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER / LOGO ---
col1, col2 = st.columns([1, 4])
with col1:
    # Assurez-vous d'avoir votre logo dans le même dossier
    st.image("logo.png", width=150) 

with col2:
    st.title("Baobab High Tech")
    st.subheader("Convertir la complexité en simplicité pour les entreprises sénégalaises.")

st.divider()

# --- SECTION HÉRO ---
st.markdown("### 🚀 Propulsez votre entreprise dans l'ère du digital")
st.write("""
Nous remplaçons les processus manuels lents par des systèmes intelligents, fluides et intuitifs. 
Gagnez en efficacité et sécurisez votre croissance avec nos solutions sur mesure.
""")

# --- NOS SERVICES (Colonnes) ---
st.write("## Ce que nous faisons pour vous")
col_a, col_b = st.columns(2)

with col_a:
    st.info("### 🤖 Automatisation Intelligente")
    st.write("Gestion automatisée des factures, des stocks et des flux de travail.")
    
    st.info("### 📊 Développement sur mesure")
    st.write("Création de dashboards pour une prise de décision en temps réel.")

with col_b:
    st.success("### 📂 Digitalisation des données")
    st.write("Dématérialisation sécurisée de vos archives et dossiers clients.")
    
    st.success("### 🔌 Intégration Technologique")
    st.write("Mise en place d'outils modernes adaptés au marché sénégalais.")

# --- DÉMO INTERACTIVE (Le "Plus" de Streamlit) ---
st.divider()
st.write("### 🧮 Simulateur de Gain d'Efficacité")
taches = st.slider("Nombre de tâches manuelles par jour / employé", 1, 50, 20)
temps_gagne = taches * 0.15 # 15 min gagnées par tâche automatisée

st.metric(label="Temps libéré par mois (par employé)", value=f"{int(temps_gagne * 22)} Heures")

# --- CONTACT ---
st.divider()
st.write("## 📧 Contactez un expert")
with st.form("contact_form"):
    nom = st.text_input("Nom de l'entreprise")
    email = st.text_input("Email professionnel")
    message = st.text_area("Votre besoin (Automatisation, Digitalisation...)")
    submitted = st.form_submit_button("Envoyer la demande")
    if submitted:
        st.success(f"Merci {nom}, nous vous recontacterons sous 24h sur {email} !")

# --- FOOTER ---
st.markdown("---")
st.caption("© 2026 Baobab High Tech - Sénégal | Expertise .sn")
