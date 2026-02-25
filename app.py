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
    layout="wide"
)

NUMERO_WHATSAPP = "221778615900"

try:
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("Mot de passe admin non configuré dans secrets.toml")
    st.stop()

# ==========================================
# DATABASE
# ==========================================
def get_connection():
    return sqlite3.connect("restaurant_v4.db")

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

if "page" not in st.session_state:
    st.session_state.page = "Accueil"

def add_to_cart(item_id, nom, prix):
    item_id = str(item_id)
    if item_id in st.session_state.cart:
        st.session_state.cart[item_id]["qty"] += 1
    else:
        st.session_state.cart[item_id] = {"nom": nom, "prix": prix, "qty": 1}
    st.toast(f"{nom} ajouté au panier")

# ==========================================
# STYLE GLOBAL
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
.hero p {
    font-size:20px;
}
.primary-btn {
    background:#d4af37;
    color:black!important;
    padding:15px 30px;
    border-radius:10px;
    font-weight:bold;
    text-decoration:none;
}
.section {
    padding:40px 0;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    page = st.radio(
        "Navigation",
        ["Accueil", "La Carte", "Panier", "Admin"],
        index=["Accueil", "La Carte", "Panier", "Admin"].index(st.session_state.page)
    )
    st.session_state.page = page

# ==========================================
# ACCUEIL PREMIUM
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
        st.session_state.page = "La Carte"
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
        st.info("Menu vide.")
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
                st.markdown(f"### {int(row['prix'])} FCFA")
                st.button(
                    "Ajouter au panier",
                    key=row["id"],
                    on_click=add_to_cart,
                    args=(row["id"], row["nom"], row["prix"])
                )
            st.divider()

# ==========================================
# PANIER
# ==========================================
elif page == "Panier":

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
            col1.write(f"{v['nom']} ({int(v['prix'])}F)")
            col2.write(f"x{v['qty']}")
            if col3.button("🗑️", key=f"del{k}"):
                del st.session_state.cart[k]
                st.rerun()

        st.markdown(f"## Total : {int(total)} FCFA")
        st.divider()

        type_commande = st.radio(
            "📍 Type de commande",
            ["🏪 Sur place", "🚚 Livraison"]
        )

        detail_lieu = ""

        if type_commande == "🏪 Sur place":
            table = st.text_input("Numéro de table")
            if table:
                detail_lieu = f"Table {table}"
        else:
            adresse = st.text_input("Adresse complète")
            telephone = st.text_input("Téléphone")
            if adresse and telephone:
                detail_lieu = f"{adresse} | Tel: {telephone}"

        methode = st.radio("💳 Paiement", ["Wave", "Orange Money", "Espèces"])

        if st.button("🚀 Valider la commande"):
            if not detail_lieu:
                st.error("Complétez les informations.")
            else:
                conn = get_connection()
                c = conn.cursor()
                c.execute(
                    "INSERT INTO commandes (articles,total,paiement,detail,type_commande) VALUES (?,?,?,?,?)",
                    (txt_commande,total,methode,detail_lieu,type_commande)
                )
                conn.commit()
                conn.close()

                st.session_state.cart = {}
                st.success("Commande enregistrée !")

                msg = f"""🥘 NOUVELLE COMMANDE

{txt_commande}
💰 TOTAL: {int(total)} FCFA
📍 TYPE: {type_commande}
📌 LIEU: {detail_lieu}
💳 PAIEMENT: {methode}
"""

                link = f"https://wa.me/{NUMERO_WHATSAPP}?text={urllib.parse.quote(msg)}"

                st.markdown(
                    f'<a href="{link}" target="_blank" class="primary-btn">📲 Envoyer sur WhatsApp</a>',
                    unsafe_allow_html=True
                )

# ==========================================
# ADMIN
# ==========================================
elif page == "Admin":

    st.header("🔐 Administration")
    code = st.text_input("Mot de passe", type="password")

    if code == ADMIN_PASSWORD:

        conn = get_connection()
        df = pd.read_sql("SELECT * FROM commandes ORDER BY id DESC", conn)
        conn.close()

        if not df.empty:
            st.metric("💰 Total ventes", f"{int(df['total'].sum())} FCFA")
            st.metric("📦 Nombre commandes", len(df))
            st.dataframe(df, use_container_width=True)
