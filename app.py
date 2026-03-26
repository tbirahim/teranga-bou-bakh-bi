import streamlit as st
from datetime import datetime
import re

# ------------------------------
# 1. Configuration de la page
# ------------------------------
st.set_page_config(
    page_title="Baobab High Tech | Transformation Digitale",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------
# 2. Styles CSS personnalisés (modernes)
# ------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .card {
        background: white;
        padding: 1.8rem;
        border-radius: 1.2rem;
        border: 1px solid #e9ecef;
        box-shadow: 0 8px 20px rgba(0,0,0,0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 1.5rem;
        text-align: center;
        height: 100%;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.08);
    }
    .stButton > button {
        background: linear-gradient(135deg, #1565C0 0%, #0d47a1 100%);
        color: white !important;
        border-radius: 40px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        background: linear-gradient(135deg, #0d47a1 0%, #0a3b7a 100%);
        box-shadow: 0 4px 12px rgba(21,101,192,0.3);
    }
    .hero {
        background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 2rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1.5rem;
        border-top: 1px solid #e9ecef;
        color: #6c757d;
        font-size: 0.85rem;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------
# 3. Gestion de l'image du logo (sécurisée)
# ------------------------------
def afficher_logo():
    try:
        # Assurez-vous que le fichier s'appelle exactement "logo.png" à la racine
        st.image("logo.png", width=120, use_container_width=False)
    except FileNotFoundError:
        st.markdown("""
            <div style="background:#f8f9fa; padding:1rem; border-radius:1rem; text-align:center; width:120px;">
                🌳 <strong>Baobab</strong>
            </div>
        """, unsafe_allow_html=True)
    except Exception:
        st.write("🌳 Baobab Tech")

# ------------------------------
# 4. En-tête Hero
# ------------------------------
st.markdown("""
    <div class="hero">
        <h1 style="color: white; font-size: 3rem; margin-bottom: 0.5rem;">Baobab High Tech</h1>
        <p style="font-size: 1.5rem; opacity: 0.95;">L'intelligence numérique au service de votre croissance au Sénégal.</p>
    </div>
""", unsafe_allow_html=True)

# ------------------------------
# 5. Présentation avec logo
# ------------------------------
col_logo, col_desc = st.columns([1, 3])
with col_logo:
    afficher_logo()
with col_desc:
    st.markdown("## À propos")
    st.markdown("Nous accompagnons les **PME sénégalaises** dans leur transformation digitale : automatisation, pilotage par la donnée, et migration vers le cloud.")

st.divider()

# ------------------------------
# 6. Services (cartes stylisées)
# ------------------------------
st.markdown("## 💡 Nos Expertises")
cols = st.columns(3)

def service_card(col, icon, title, description):
    col.markdown(f"""
        <div class="card">
            <div style="font-size: 3.5rem; margin-bottom: 0.8rem;">{icon}</div>
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
    """, unsafe_allow_html=True)

service_card(cols[0], "🤖", "Automatisation", "Supprimez les tâches manuelles répétitives et libérez vos équipes.")
service_card(cols[1], "📊", "Business Intelligence", "Pilotez votre activité avec des tableaux de bord temps réel.")
service_card(cols[2], "☁️", "Transformation Cloud", "Sécurisez vos données et accédez-y partout.")

# ------------------------------
# 7. Simulateur de ROI (avec état persistant)
# ------------------------------
st.divider()
st.subheader("🧮 Calculez vos gains de productivité")

if "nb_taches" not in st.session_state:
    st.session_state.nb_taches = 20

taches = st.slider(
    "Nombre de tâches manuelles par jour / employé",
    min_value=1,
    max_value=50,
    value=st.session_state.nb_taches,
    key="slider_taches"
)
st.session_state.nb_taches = taches

gain_heure_par_tache = 0.25  # 15 min par tâche
heures_gagnees = taches * gain_heure_par_tache * 22  # 22 jours ouvrés
st.metric(
    label="⏱️ Heures libérées par mois (par employé)",
    value=f"{int(heures_gagnees)} h",
    delta=f"{heures_gagnees/22:.1f} h/jour"
)

# ------------------------------
# 8. Formulaire de contact avec validation
# ------------------------------
st.divider()
st.markdown("## 📩 Prêt à franchir le pas ?")

with st.form("contact_form", clear_on_submit=True):
    col_nom, col_email = st.columns(2)
    with col_nom:
        entreprise = st.text_input("Nom de l'entreprise *")
    with col_email:
        email = st.text_input("Email professionnel *")
    
    besoin = st.text_area("Expliquez-nous votre besoin", placeholder="Ex: automatisation de la facturation, dashboard commercial...")
    consentement = st.checkbox("J'accepte d'être recontacté par Baobab High Tech.")
    
    submitted = st.form_submit_button("🚀 Demander un audit gratuit")
    
    if submitted:
        # Validation
        erreurs = []
        if not entreprise:
            erreurs.append("Le nom de l'entreprise est requis.")
        if not email:
            erreurs.append("L'email professionnel est requis.")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            erreurs.append("Format d'email invalide.")
        if not consentement:
            erreurs.append("Vous devez accepter d'être recontacté.")
        
        if erreurs:
            for err in erreurs:
                st.error(err)
        else:
            # Ici, vous pourriez envoyer les données par email, API, ou stockage
            st.success(f"✅ Merci {entreprise} ! Notre équipe vous recontactera sous 24h à {email}.")
            # Exemple : st.session_state['form_data'] = {...}
            # Pour un vrai envoi, intégrer une fonction avec SMTP ou webhook

# ------------------------------
# 9. Pied de page
# ------------------------------
st.markdown("---")
st.markdown("""
    <div class="footer">
        Baobab High Tech © 2026 | Dakar, Sénégal<br>
        📞 +221 78 123 45 67 | ✉️ contact@baobabht.sn<br>
        <small>Digitalisons l'avenir, ensemble.</small>
    </div>
""", unsafe_allow_html=True)
