import streamlit as st
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ─────────────────────────────────────────
# 1. Configuration de la page
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Baobab High Tech | Transformation Digitale",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────
# 2. CSS Premium
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Variables globales ── */
:root {
    --primary:     #0A2540;
    --accent:      #00C6A2;
    --accent2:     #F5A623;
    --surface:     #F4F7FC;
    --card-bg:     #FFFFFF;
    --border:      #E2E8F4;
    --text-main:   #0A2540;
    --text-muted:  #6B7A99;
    --radius-lg:   1.5rem;
    --radius-sm:   0.75rem;
    --shadow-sm:   0 2px 8px rgba(10,37,64,.06);
    --shadow-md:   0 8px 28px rgba(10,37,64,.10);
    --shadow-lg:   0 20px 60px rgba(10,37,64,.14);
    --transition:  0.25s cubic-bezier(.4,0,.2,1);
}

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--text-main);
    background: var(--surface) !important;
}

/* ── Scrollbar élégante ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ══════════════════════════════════════
   HERO SECTION
══════════════════════════════════════ */
.hero-wrapper {
    position: relative;
    background: var(--primary);
    overflow: hidden;
    padding: 5rem 4rem 4rem;
    margin-bottom: 0;
}

/* Cercles décoratifs en arrière-plan */
.hero-wrapper::before {
    content: '';
    position: absolute;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(0,198,162,.18) 0%, transparent 70%);
    top: -200px; right: -100px;
    border-radius: 50%;
    pointer-events: none;
}
.hero-wrapper::after {
    content: '';
    position: absolute;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(245,166,35,.12) 0%, transparent 70%);
    bottom: -150px; left: 60px;
    border-radius: 50%;
    pointer-events: none;
}

.hero-badge {
    display: inline-block;
    background: rgba(0,198,162,.15);
    color: var(--accent);
    border: 1px solid rgba(0,198,162,.30);
    border-radius: 99px;
    padding: .35rem 1.1rem;
    font-family: 'Sora', sans-serif;
    font-size: .78rem;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

.hero-title {
    font-family: 'Sora', sans-serif;
    font-size: clamp(2.4rem, 5vw, 4rem);
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1.12;
    margin: 0 0 1.2rem;
}

.hero-title span {
    color: var(--accent);
}

.hero-sub {
    font-size: 1.15rem;
    font-weight: 300;
    color: rgba(255,255,255,.72);
    max-width: 520px;
    line-height: 1.7;
    margin-bottom: 2.4rem;
}

.hero-stats {
    display: flex;
    gap: 2.5rem;
    flex-wrap: wrap;
}

.hero-stat-num {
    font-family: 'Sora', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1;
}

.hero-stat-label {
    font-size: .82rem;
    color: rgba(255,255,255,.55);
    margin-top: .25rem;
    letter-spacing: .04em;
}

/* ── Barre accent sous le hero ── */
.hero-accent-bar {
    height: 4px;
    background: linear-gradient(90deg, var(--accent) 0%, var(--accent2) 100%);
    margin-bottom: 3.5rem;
}

/* ══════════════════════════════════════
   SECTION WRAPPER
══════════════════════════════════════ */
.section {
    padding: 0 4rem;
    margin-bottom: 3rem;
}

.section-label {
    font-family: 'Sora', sans-serif;
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: .6rem;
}

.section-title {
    font-family: 'Sora', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: var(--primary);
    margin: 0 0 .5rem;
}

.section-sub {
    font-size: 1rem;
    color: var(--text-muted);
    font-weight: 300;
    max-width: 560px;
    line-height: 1.7;
    margin-bottom: 2.2rem;
}

/* ══════════════════════════════════════
   ABOUT CARD
══════════════════════════════════════ */
.about-card {
    background: var(--card-bg);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
    padding: 2.5rem;
    box-shadow: var(--shadow-sm);
    display: flex;
    align-items: center;
    gap: 2rem;
}

.about-logo-wrap {
    width: 80px; height: 80px;
    background: var(--primary);
    border-radius: 1.2rem;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.2rem;
    flex-shrink: 0;
    box-shadow: var(--shadow-md);
}

.about-text h3 {
    font-family: 'Sora', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    margin: 0 0 .5rem;
    color: var(--primary);
}

.about-text p {
    font-size: .97rem;
    color: var(--text-muted);
    margin: 0;
    line-height: 1.7;
}

/* ══════════════════════════════════════
   SERVICE CARDS
══════════════════════════════════════ */
.service-card {
    background: var(--card-bg);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
    padding: 2.2rem 1.8rem;
    box-shadow: var(--shadow-sm);
    transition: transform var(--transition), box-shadow var(--transition), border-color var(--transition);
    height: 100%;
    position: relative;
    overflow: hidden;
}

.service-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    opacity: 0;
    transition: opacity var(--transition);
}

.service-card:hover {
    transform: translateY(-6px);
    box-shadow: var(--shadow-lg);
    border-color: transparent;
}

.service-card:hover::before { opacity: 1; }

.service-icon {
    width: 56px; height: 56px;
    border-radius: 1rem;
    background: linear-gradient(135deg, rgba(0,198,162,.12), rgba(0,198,162,.05));
    display: flex; align-items: center; justify-content: center;
    font-size: 1.6rem;
    margin-bottom: 1.4rem;
}

.service-card h3 {
    font-family: 'Sora', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--primary);
    margin: 0 0 .7rem;
}

.service-card p {
    font-size: .93rem;
    color: var(--text-muted);
    margin: 0;
    line-height: 1.7;
}

.service-tag {
    display: inline-block;
    margin-top: 1.2rem;
    background: rgba(0,198,162,.1);
    color: var(--accent);
    border-radius: 99px;
    padding: .25rem .9rem;
    font-size: .76rem;
    font-weight: 600;
    letter-spacing: .04em;
}

/* ══════════════════════════════════════
   ROI CARD
══════════════════════════════════════ */
.roi-card {
    background: var(--primary);
    border-radius: var(--radius-lg);
    padding: 2.8rem;
    color: white;
    box-shadow: var(--shadow-lg);
    position: relative;
    overflow: hidden;
}

.roi-card::after {
    content: '◈';
    position: absolute;
    right: 2rem; top: 1.5rem;
    font-size: 8rem;
    color: rgba(255,255,255,.04);
    font-family: sans-serif;
    pointer-events: none;
}

.roi-result {
    background: rgba(0,198,162,.12);
    border: 1px solid rgba(0,198,162,.25);
    border-radius: var(--radius-sm);
    padding: 1.5rem 2rem;
    margin-top: 1.5rem;
}

.roi-result-num {
    font-family: 'Sora', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    color: var(--accent);
    line-height: 1;
}

.roi-result-sub {
    font-size: .9rem;
    color: rgba(255,255,255,.6);
    margin-top: .3rem;
}

/* ── Streamlit slider override ── */
[data-baseweb="slider"] .rc-slider-track { background: var(--accent) !important; }
[data-baseweb="slider"] .rc-slider-handle { border-color: var(--accent) !important; }

/* ══════════════════════════════════════
   FORM / CONTACT
══════════════════════════════════════ */
.contact-wrapper {
    background: var(--card-bg);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
    padding: 2.8rem;
    box-shadow: var(--shadow-sm);
}

.contact-highlight {
    background: linear-gradient(135deg, rgba(0,198,162,.08), rgba(245,166,35,.06));
    border-radius: var(--radius-sm);
    padding: 1.1rem 1.4rem;
    border-left: 3px solid var(--accent);
    margin-bottom: 2rem;
    font-size: .93rem;
    color: var(--text-main);
}

/* ── Inputs Streamlit ── */
.stTextInput input, .stTextArea textarea {
    border-radius: var(--radius-sm) !important;
    border: 1.5px solid var(--border) !important;
    background: var(--surface) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: .95rem !important;
    color: var(--text-main) !important;
    transition: border-color var(--transition) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,198,162,.12) !important;
}

/* ── Submit button ── */
.stFormSubmitButton > button, .stButton > button {
    background: var(--primary) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 99px !important;
    padding: .7rem 2.2rem !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    font-size: .95rem !important;
    letter-spacing: .02em !important;
    transition: all var(--transition) !important;
    box-shadow: 0 4px 16px rgba(10,37,64,.22) !important;
}
.stFormSubmitButton > button:hover, .stButton > button:hover {
    background: #0d3460 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(10,37,64,.28) !important;
}

/* ── Checkbox ── */
.stCheckbox label { font-size: .92rem; color: var(--text-muted); }

/* ══════════════════════════════════════
   FOOTER
══════════════════════════════════════ */
.footer-wrap {
    background: var(--primary);
    padding: 3rem 4rem 2rem;
    margin-top: 3rem;
}

.footer-logo-text {
    font-family: 'Sora', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: .4rem;
}

.footer-tagline {
    font-size: .87rem;
    color: rgba(255,255,255,.45);
    font-style: italic;
}

.footer-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,.1);
    margin: 1.8rem 0 1.2rem;
}

.footer-bottom {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: .8rem;
}

.footer-contact-item {
    font-size: .87rem;
    color: rgba(255,255,255,.55);
}

.footer-copyright {
    font-size: .82rem;
    color: rgba(255,255,255,.35);
}

/* ── Dividers custom ── */
hr { border-color: var(--border) !important; }

/* ── Metric override ── */
[data-testid="stMetricValue"] {
    font-family: 'Sora', sans-serif !important;
    color: var(--accent) !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# 3. HERO
# ─────────────────────────────────────────
st.markdown("""
<div class="hero-wrapper">
    <div class="hero-badge">🌳 Fondée au Sénégal · Active en Afrique de l'Ouest</div>
    <h1 class="hero-title">
        L'intelligence numérique<br>
        au service de <span>votre croissance</span>
    </h1>
    <p class="hero-sub">
        Baobab High Tech accompagne les PME sénégalaises dans leur transformation digitale —
        de l'automatisation au cloud, en passant par la Business Intelligence.
    </p>
    <div class="hero-stats">
        <div>
            <div class="hero-stat-num">+120</div>
            <div class="hero-stat-label">Entreprises accompagnées</div>
        </div>
        <div>
            <div class="hero-stat-num">98 %</div>
            <div class="hero-stat-label">Satisfaction client</div>
        </div>
        <div>
            <div class="hero-stat-num">5 ans</div>
            <div class="hero-stat-label">D'expertise digitale</div>
        </div>
    </div>
</div>
<div class="hero-accent-bar"></div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# 4. À PROPOS
# ─────────────────────────────────────────
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("""
<div class="section-label">À propos</div>
<h2 class="section-title">Qui sommes-nous ?</h2>
""", unsafe_allow_html=True)

# Logo + description
col_logo, col_desc = st.columns([1, 3], gap="large")
with col_logo:
    try:
        st.image("logo.png", width=140)
    except Exception:
        st.markdown("""
        <div class="about-logo-wrap" style="width:100%;height:130px;border-radius:1.2rem;
            background:var(--primary);display:flex;align-items:center;justify-content:center;
            font-size:3rem;">
            🌳
        </div>""", unsafe_allow_html=True)

with col_desc:
    st.markdown("""
    <div style="padding-top:.5rem;">
        <p style="font-size:1.05rem;color:var(--text-main);line-height:1.8;margin-bottom:1rem;">
            Chez <strong>Baobab High Tech</strong>, nous croyons que la technologie doit être
            un levier de croissance accessible à toutes les entreprises africaines.
        </p>
        <p style="font-size:.97rem;color:var(--text-muted);line-height:1.8;margin:0;">
            Nous accompagnons les <strong>PME sénégalaises</strong> dans leur transformation digitale :
            automatisation intelligente, pilotage par la donnée et migration sécurisée vers le cloud.
            Notre approche est pragmatique, sur mesure et ancrée dans les réalités locales.
        </p>
    </div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Séparateur
st.markdown('<hr style="margin:0 4rem 3rem;">', unsafe_allow_html=True)


# ─────────────────────────────────────────
# 5. NOS EXPERTISES
# ─────────────────────────────────────────
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("""
<div class="section-label">Expertises</div>
<h2 class="section-title">Ce que nous faisons</h2>
<p class="section-sub">Des solutions concrètes, adaptées à votre secteur et à votre taille.</p>
""", unsafe_allow_html=True)

services = [
    {
        "icon": "🤖",
        "title": "Automatisation",
        "desc": "Supprimez les tâches manuelles répétitives. Libérez vos équipes pour des missions à forte valeur ajoutée.",
        "tag": "RPA · No-Code · Intégrations"
    },
    {
        "icon": "📊",
        "title": "Business Intelligence",
        "desc": "Pilotez votre activité avec des tableaux de bord temps réel. Décidez vite, décidez juste.",
        "tag": "Dashboards · KPIs · Data Viz"
    },
    {
        "icon": "☁️",
        "title": "Cloud & Infrastructure",
        "desc": "Sécurisez vos données, réduisez vos coûts et accédez à vos systèmes de n'importe où.",
        "tag": "Migration · Sécurité · SaaS"
    },
    {
        "icon": "🧩",
        "title": "Développement Sur Mesure",
        "desc": "Applications web et mobiles conçues spécifiquement pour vos processus métier.",
        "tag": "Web · Mobile · API"
    },
    {
        "icon": "🎓",
        "title": "Formation & Conduite du Changement",
        "desc": "Formez vos équipes aux outils et accompagnez la transformation culturelle de l'entreprise.",
        "tag": "Ateliers · E-learning · Coaching"
    },
    {
        "icon": "🔒",
        "title": "Cybersécurité",
        "desc": "Protégez vos actifs numériques avec des audits, politiques et solutions adaptées à votre contexte.",
        "tag": "Audit · RGPD · Conformité"
    },
]

cols = st.columns(3, gap="medium")
for i, s in enumerate(services):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="service-card">
            <div class="service-icon">{s['icon']}</div>
            <h3>{s['title']}</h3>
            <p>{s['desc']}</p>
            <div class="service-tag">{s['tag']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<hr style="margin:2rem 4rem 3rem;">', unsafe_allow_html=True)


# ─────────────────────────────────────────
# 6. SIMULATEUR DE ROI
# ─────────────────────────────────────────
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("""
<div class="section-label">Simulateur</div>
<h2 class="section-title">Calculez vos gains de productivité</h2>
<p class="section-sub">Estimez le temps libéré chaque mois grâce à l'automatisation.</p>
""", unsafe_allow_html=True)

roi_col, result_col = st.columns([3, 2], gap="large")

with roi_col:
    st.markdown('<div class="roi-card">', unsafe_allow_html=True)
    st.markdown('<p style="color:rgba(255,255,255,.6);font-size:.88rem;margin-bottom:1.5rem;letter-spacing:.04em;text-transform:uppercase;font-weight:600;">Paramètres</p>', unsafe_allow_html=True)

    if "nb_taches" not in st.session_state:
        st.session_state.nb_taches = 20
    if "nb_employes" not in st.session_state:
        st.session_state.nb_employes = 5

    taches = st.slider("Tâches manuelles / jour / employé", 1, 50,
                        st.session_state.nb_taches, key="slider_taches")
    st.session_state.nb_taches = taches

    employes = st.slider("Nombre d'employés concernés", 1, 50,
                          st.session_state.nb_employes, key="slider_employes")
    st.session_state.nb_employes = employes

    gain_par_tache = 0.25  # 15 min
    heures_par_employe = taches * gain_par_tache * 22
    heures_total = heures_par_employe * employes

    st.markdown(f"""
    <div class="roi-result">
        <div class="roi-result-num">{int(heures_total)} h</div>
        <div class="roi-result-sub">libérées / mois pour {employes} employé(s)</div>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with result_col:
    equivalents = [
        ("🗓️", f"{int(heures_total / 8)}", "jours de travail récupérés"),
        ("💰", f"{int(heures_total * 3500):,}".replace(",", " "), "FCFA économisés/mois*"),
        ("📈", f"{min(int(heures_total / heures_par_employe * 20), 80)} %", "gain de productivité estimé"),
    ]
    for icon, val, label in equivalents:
        st.markdown(f"""
        <div style="background:var(--card-bg);border:1px solid var(--border);border-radius:var(--radius-sm);
            padding:1.4rem 1.6rem;margin-bottom:1rem;box-shadow:var(--shadow-sm);">
            <div style="font-size:1.6rem;margin-bottom:.4rem;">{icon}</div>
            <div style="font-family:'Sora',sans-serif;font-size:1.9rem;font-weight:700;color:var(--primary);">{val}</div>
            <div style="font-size:.85rem;color:var(--text-muted);margin-top:.25rem;">{label}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown('<p style="font-size:.75rem;color:var(--text-muted);font-style:italic;padding:.5rem;">* Estimation basée sur un coût horaire moyen de 3 500 FCFA.</p>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<hr style="margin:2rem 4rem 3rem;">', unsafe_allow_html=True)


# ─────────────────────────────────────────
# 7. FORMULAIRE DE CONTACT
# ─────────────────────────────────────────
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("""
<div class="section-label">Contact</div>
<h2 class="section-title">Demandez votre audit gratuit</h2>
<p class="section-sub">Un expert Baobab High Tech vous recontacte sous 24h pour analyser votre situation.</p>
""", unsafe_allow_html=True)

form_col, info_col = st.columns([3, 2], gap="large")

with form_col:
    st.markdown("""
    <div class="contact-highlight">
        🎁 <strong>Audit offert</strong> — Sans engagement. Nos experts analysent vos processus et vous proposent
        un plan d'action chiffré adapté à votre entreprise.
    </div>""", unsafe_allow_html=True)

    with st.form("contact_form", clear_on_submit=True):
        col_nom, col_email = st.columns(2)
        with col_nom:
            entreprise = st.text_input("Nom de l'entreprise *", placeholder="Ex: Dakar Commerce SARL")
        with col_email:
            email = st.text_input("Email professionnel *", placeholder="contact@entreprise.sn")

        secteur = st.selectbox("Secteur d'activité", [
            "Choisir…", "Commerce & Distribution", "Finance & Banque",
            "Santé", "Éducation", "Agriculture", "Transport & Logistique",
            "BTP & Immobilier", "Services", "Autre"
        ])

        besoin = st.text_area("Décrivez votre besoin", height=130,
                              placeholder="Ex: Nous cherchons à automatiser notre facturation et créer un tableau de bord des ventes...")

        consentement = st.checkbox("J'accepte d'être recontacté(e) par l'équipe Baobab High Tech.")

        submitted = st.form_submit_button("🚀 Demander mon audit gratuit")

        if submitted:
            erreurs = []
            if not entreprise:
                erreurs.append("⚠️ Le nom de l'entreprise est requis.")
            if not email:
                erreurs.append("⚠️ L'email professionnel est requis.")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                erreurs.append("⚠️ Format d'email invalide.")
            if secteur == "Choisir…":
                erreurs.append("⚠️ Veuillez sélectionner votre secteur d'activité.")
            if not consentement:
                erreurs.append("⚠️ Vous devez accepter d'être recontacté(e).")

            if erreurs:
                for err in erreurs:
                    st.error(err)
            else:
                try:
                    sender    = st.secrets["email"]["sender"]
                    password  = st.secrets["email"]["password"]
                    recipient = st.secrets["email"]["recipient"]
                    smtp_server = st.secrets["email"]["smtp_server"]
                    smtp_port   = st.secrets["email"]["smtp_port"]

                    msg = MIMEMultipart()
                    msg["From"]    = sender
                    msg["To"]      = recipient
                    msg["Subject"] = f"[BHT] Audit gratuit · {entreprise} · {secteur}"

                    body = f"""
╔══════════════════════════════════════════╗
   NOUVELLE DEMANDE D'AUDIT — Baobab High Tech
╚══════════════════════════════════════════╝

Entreprise  : {entreprise}
Secteur     : {secteur}
Email       : {email}

Besoin exprimé :
{besoin or '(non renseigné)'}

Le contact a donné son consentement pour être recontacté.
──────────────────────────────────────────
Envoyé depuis le site Baobab High Tech
                    """
                    msg.attach(MIMEText(body, "plain"))

                    with smtplib.SMTP(smtp_server, smtp_port) as server:
                        server.starttls()
                        server.login(sender, password)
                        server.send_message(msg)

                    st.success(f"✅ Merci **{entreprise}** ! Notre équipe vous contactera sous 24h à **{email}**.")

                except Exception as e:
                    st.error(f"Erreur technique : {e}. Contactez-nous directement à contact@baobabht.sn")

with info_col:
    infos = [
        ("📍", "Localisation", "Dakar, Sénégal<br>Plateau · Almadies"),
        ("📞", "Téléphone", "+221 77 861 59 00"),
        ("✉️", "Email", "    thiernogaye2005@gmail.com"),
        ("🕐", "Disponibilité", "Lun–Ven · 8h–18h GMT"),
    ]
    for icon, label, value in infos:
        st.markdown(f"""
        <div style="display:flex;gap:1rem;align-items:flex-start;
            background:var(--card-bg);border:1px solid var(--border);
            border-radius:var(--radius-sm);padding:1.2rem 1.4rem;
            margin-bottom:.9rem;box-shadow:var(--shadow-sm);">
            <div style="font-size:1.4rem;line-height:1;">{icon}</div>
            <div>
                <div style="font-size:.78rem;font-weight:600;color:var(--text-muted);
                    text-transform:uppercase;letter-spacing:.07em;margin-bottom:.3rem;">{label}</div>
                <div style="font-size:.97rem;color:var(--primary);font-weight:500;">{value}</div>
            </div>
        </div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────
# 8. FOOTER
# ─────────────────────────────────────────
st.markdown("""
<div class="footer-wrap">
    <div class="footer-logo-text">🌳 Baobab High Tech</div>
    <div class="footer-tagline">Digitalisons l'avenir, ensemble.</div>
    <hr class="footer-divider">
    <div class="footer-bottom">
        <div style="display:flex;gap:2rem;flex-wrap:wrap;">
            <span class="footer-contact-item">📞 +221 77 861 59 00</span>
            <span class="footer-contact-item">✉️ thiernogaye2005@gmail.com</span>
            <span class="footer-contact-item">📍 Dakar, Sénégal</span>
        </div>
        <span class="footer-copyright">© 2026 Baobab High Tech — Tous droits réservés</span>
    </div>
</div>
""", unsafe_allow_html=True)
