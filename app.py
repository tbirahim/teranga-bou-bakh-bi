import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse

# ==========================================
# CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Teranga Gourmet Mboro",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

NUMERO_WHATSAPP = "221778615900"
NUMERO_MARCHAND_WAVE = "221778615900" # Ton numéro pour le lien Wave

try:
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except:
    ADMIN_PASSWORD = "admin" # Mot de passe de secours si secrets.toml n'est pas configuré

# ==========================================
# DATABASE
# ==========================================
def get_connection():
    # check_same_thread=False évite les plantages sur Streamlit Cloud
    return sqlite3.connect("restaurant_v5.db", check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            prix REAL,
            img TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS commandes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            articles TEXT,
            total REAL,
            paiement TEXT,
            detail TEXT,
            type_commande TEXT,
            statut TEXT DEFAULT 'En préparation',
            date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ==========================================
# SESSION
# ==========================================
if "cart" not in st.session_state:
    st.session_state.cart = {}

def add_to_cart(item_id, nom, prix):
    item_id = str(item_id)
    if item_id in st.session_state.cart:
        st.session_state.cart[item_id]["qty"] += 1
    else:
        st.session_state.cart[item_id] = {"nom": nom, "prix": prix, "qty": 1}
    st.toast(f"✅ {nom} ajouté au panier")

# ==========================================
# STYLE
# ==========================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f0f0f,#1c1c1c);
    color: white;
}
.hero {
    text-align:center;
    padding:60px 20px;
}
.hero h1 {
    font-size:48px;
    color:#d4af37;
}
.primary-btn {
    display: block;
    background:#d4af37;
    color:black!important;
    text-align:center;
    padding:15px 30px;
    border-radius:10px;
    font-weight:bold;
    text-decoration:none;
    margin-top: 10px;
}
.pay-btn-wave { display: block; width: 100%; background-color: #0096ff; color: white !important; text-align: center; padding: 12px; border-radius: 10px; font-weight: bold; text-decoration: none; margin: 10px 0; }
.pay-btn-om { display: block; width: 100%; background-color: #ff6600; color: white !important; text-align: center; padding: 12px; border-radius: 10px; font-weight: bold; text-decoration: none; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# NAVIGATION
# ==========================================
nb_articles = sum(item['qty'] for item in st.session_state.cart.values())
with st.sidebar:
    page = st.radio(
        "Navigation",
        ["Accueil", "La Carte", f"Panier ({nb_articles})", "Admin"],
        key="navigation"
    )

# ==========================================
# ACCUEIL
# ==========================================
if page == "Accueil":

    st.image(
        "https://images.unsplash.com/photo-1555992336-03a23c9f8a5c",
        use_container_width=True
    )

    st.markdown("""
    <div class="hero">
        <h1>Teranga Gourmet Mboro</h1>
        <p>Saveurs authentiques • Service rapide • Livraison fiable</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🍽️ Commander Maintenant", use_container_width=True):
        st.session_state.navigation = "La Carte"
        st.rerun()

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🍲 Cuisine de qualité")
        st.write("Des plats préparés avec passion et ingrédients frais.")

    with col2:
        st.subheader("🚚 Livraison rapide")
        st.write("Commandez en ligne et recevez chez vous rapidement.")

    with col3:
        st.subheader("🏪 Service sur place")
        st.write("Installez-vous et profitez d’un service professionnel.")

    st.divider()
    st.subheader("📍 Informations")
    st.write("📌 Mboro, Sénégal")
    st.write("🕒 Ouvert tous les jours : 10h - 23h")
    st.write(f"📞 WhatsApp : {NUMERO_WHATSAPP}")

# ==========================================
# LA CARTE
# ==========================================
elif page == "La Carte":

    st.header("📋 Notre Menu")

    conn = get_connection()
    df = pd.read_sql("SELECT * FROM menu", conn)
    conn.close()

    if df.empty:
        st.info("Le menu est en cours de préparation.")
    else:
        for _, row in df.iterrows():
            col1, col2 = st.columns([1,2])
            with col1:
                st.image(
                    row["img"] if row["img"] else "https://via.placeholder.com/150",
                    use_container_width=True
                )
            with col2:
                st.subheader(row["nom"])
                st.markdown(f"<h3 style='color:#d4af37;'>{int(row['prix'])} FCFA</h3>", unsafe_allow_html=True)
                st.button(
                    "Ajouter au panier",
                    key=f"btn_{row['id']}",
                    on_click=add_to_cart,
                    args=(row["id"], row["nom"], row["prix"])
                )
            st.divider()

# ==========================================
# PANIER
# ==========================================
elif "Panier" in page:

    st.header("🛒 Votre Panier")

    if not st.session_state.cart:
        st.info("Votre panier est vide.")
    else:
        total = 0
        txt_commande = ""

        for k, v in list(st.session_state.cart.items()):
            sub = v["prix"] * v["qty"]
            total += sub
            txt_commande += f"- {v['nom']} x{v['qty']}\n"

            col1, col2, col3 = st.columns([3,1,1])
            col1.write(f"**{v['nom']}** ({int(v['prix'])}F)")
            col2.write(f"x{v['qty']}")
            if col3.button("🗑️", key=f"del{k}"):
                del st.session_state.cart[k]
                st.rerun()

        st.markdown(f"<h2 style='text-align: right; color:#d4af37;'>Total : {int(total)} FCFA</h2>", unsafe_allow_html=True)
        st.divider()

        type_commande = st.radio(
            "📍 Comment souhaitez-vous manger ?",
            ["🏪 Sur place", "🚚 Livraison"],
            horizontal=True
        )

        detail_lieu = ""

        if type_commande == "🏪 Sur place":
            table = st.text_input("🔢 Numéro de table")
            if table:
                detail_lieu = f"Table N° {table}"
        else:
            adresse = st.text_input("📍 Adresse complète de livraison")
            telephone = st.text_input("📞 Numéro de téléphone")
            if adresse and telephone:
                detail_lieu = f"{adresse} | Tel: {telephone}"

        st.divider()
        st.subheader("💳 Paiement")
        methode = st.radio("Choisissez votre méthode :", ["Wave", "Orange Money", "Espèces"])

        if methode == "Wave":
            st.markdown(f'<a href="https://wave.com/pay/{NUMERO_MARCHAND_WAVE}" target="_blank" class="pay-btn-wave">📱 PAYER {int(total)} F DIRECTEMENT PAR WAVE</a>', unsafe_allow_html=True)
        elif methode == "Orange Money":
            st.markdown(f'<a href="tel:#144#39#" class="pay-btn-om">📱 COMPOSER LE CODE ORANGE MONEY</a>', unsafe_allow_html=True)

        if st.button("🚀 Valider et envoyer la commande", use_container_width=True):
            if not detail_lieu:
                st.error("⚠️ Veuillez compléter les informations de lieu (Table ou Adresse/Téléphone).")
            else:
                conn = get_connection()
                c = conn.cursor()
                c.execute(
                    "INSERT INTO commandes (articles,total,paiement,detail,type_commande) VALUES (?,?,?,?,?)",
                    (txt_commande,total,methode,detail_lieu,type_commande)
                )
                conn.commit()
                conn.close()

                st.session_state.cart = {} # On vide le panier
                st.success("Commande enregistrée ! Cliquez sur le bouton ci-dessous pour nous prévenir.")

                msg = f"🥘 *NOUVELLE COMMANDE*\n\n*Articles :*\n{txt_commande}\n💰 *TOTAL:* {int(total)} FCFA\n📍 *TYPE:* {type_commande}\n📌 *LIEU:* {detail_lieu}\n💳 *PAIEMENT:* {methode}"
                link = f"https://wa.me/{NUMERO_WHATSAPP}?text={urllib.parse.quote(msg)}"

                st.markdown(
                    f'<a href="{link}" target="_blank" class="primary-btn">📲 CONFIRMER SUR WHATSAPP</a>',
                    unsafe_allow_html=True
                )

# ==========================================
# ADMIN
# ==========================================
elif page == "Admin":

    st.header("🔐 Administration")
    code = st.text_input("Mot de passe gérant", type="password")

    if code == ADMIN_PASSWORD:
        st.success("Connecté avec succès.")
        
        tab_ajout, tab_menu, tab_stats = st.tabs(["➕ Ajouter Plat", "📋 Gérer la Carte", "📈 Commandes & Stats"])
        
        # --- ONGLET 1 : AJOUTER ---
        with tab_ajout:
            with st.form("form_ajout", clear_on_submit=True):
                nom_plat = st.text_input("Nom du plat")
                prix_plat = st.number_input("Prix en FCFA", min_value=0, step=100)
                img_plat = st.text_input("Lien de l'image (URL)")
                
                if st.form_submit_button("Ajouter à la carte"):
                    if nom_plat and prix_plat > 0:
                        conn = get_connection()
                        conn.cursor().execute('INSERT INTO menu (nom, prix, img) VALUES (?,?,?)', (nom_plat, prix_plat, img_plat))
                        conn.commit()
                        st.success(f"Plat '{nom_plat}' ajouté !")
                        st.rerun()
                    else:
                        st.error("Veuillez mettre un nom et un prix.")

        # --- ONGLET 2 : GÉRER LE MENU ---
        with tab_menu:
            conn = get_connection()
            df_m = pd.read_sql("SELECT * FROM menu", conn)
            
            if df_m.empty:
                st.write("Aucun plat sur la carte.")
            else:
                for _, r in df_m.iterrows():
                    col_info, col_btn = st.columns([4, 1])
                    col_info.write(f"**{r['nom']}** - {int(r['prix'])} F")
                    if col_btn.button("Supprimer", key=f"del_plat_{r['id']}"):
                        conn.cursor().execute('DELETE FROM menu WHERE id=?', (r['id'],))
                        conn.commit()
                        st.rerun()

        # --- ONGLET 3 : COMMANDES ---
        with tab_stats:
            conn = get_connection()
            df_c = pd.read_sql("SELECT * FROM commandes ORDER BY id DESC", conn)
            
            if not df_c.empty:
                col1, col2 = st.columns(2)
                col1.metric("💰 Chiffre d'affaires total", f"{int(df_c['total'].sum())} FCFA")
                col2.metric("📦 Nombre de commandes", len(df_c))
                st.dataframe(df_c, use_container_width=True)
                
                if st.button("Vider l'historique"):
                    conn.cursor().execute('DELETE FROM commandes')
                    conn.commit()
                    st.rerun()
            else:
                st.write("Aucune commande enregistrée.")
