import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse

# ==============================
# CONFIGURATION
# ==============================
st.set_page_config(
    page_title="Teranga Gourmet Mboro",
    page_icon="🥘",
    layout="wide"
)

NUMERO_WHATSAPP = "221778615900"

try:
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("Mot de passe admin non configuré dans secrets.toml")
    st.stop()

# ==============================
# BASE DE DONNÉES
# ==============================
def get_connection():
    return sqlite3.connect("menu_express_v3.db")

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

# ==============================
# SESSION
# ==============================
if "cart" not in st.session_state:
    st.session_state.cart = {}

if "page" not in st.session_state:
    st.session_state.page = "Accueil"

def add_to_cart(item_id, nom, prix):
    item_id = str(item_id)
    if item_id in st.session_state.cart:
        st.session_state.cart[item_id]["qty"] += 1
    else:
        st.session_state.cart[item_id] = {
            "nom": nom,
            "prix": prix,
            "qty": 1
        }
    st.toast(f"{nom} ajouté au panier")

# ==============================
# STYLE
# ==============================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f0f0f,#1c1c1c);
    color: white;
}
.btn-whatsapp {
    display:block;
    width:100%;
    background:#25D366;
    color:white!important;
    text-align:center;
    padding:15px;
    border-radius:12px;
    font-weight:bold;
    text-decoration:none;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# NAVIGATION
# ==============================
nb_articles = sum(item["qty"] for item in st.session_state.cart.values())

with st.sidebar:
    page = st.radio(
        "Navigation",
        ["Accueil", "La Carte", "Panier", "Admin"],
        index=["Accueil", "La Carte", "Panier", "Admin"].index(st.session_state.page)
    )
    st.session_state.page = page

# ==============================
# ACCUEIL
# ==============================
if page == "Accueil":
    st.title("🍽️ Teranga Gourmet Mboro")
    st.write("Cuisine locale & internationale – Sur place & Livraison")

# ==============================
# LA CARTE
# ==============================
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
                st.image(row["img"] if row["img"] else "https://via.placeholder.com/150", use_container_width=True)
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

# ==============================
# PANIER
# ==============================
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
                st.error("Complétez les informations de réception.")
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
                    f'<a href="{link}" target="_blank" class="btn-whatsapp">📲 Envoyer sur WhatsApp</a>',
                    unsafe_allow_html=True
                )

# ==============================
# ADMIN
# ==============================
elif page == "Admin":
    st.header("🔐 Administration")
    code = st.text_input("Mot de passe", type="password")

    if code == ADMIN_PASSWORD:

        tab1, tab2 = st.tabs(["📋 Menu", "📦 Commandes"])

        # MENU
        with tab1:
            st.subheader("Ajouter un plat")
            nom = st.text_input("Nom du plat")
            prix = st.number_input("Prix", step=100)
            img = st.text_input("URL Image")

            if st.button("Ajouter"):
                conn = get_connection()
                c = conn.cursor()
                c.execute("INSERT INTO menu (nom,prix,img) VALUES (?,?,?)",(nom,prix,img))
                conn.commit()
                conn.close()
                st.success("Plat ajouté")
                st.rerun()

        # COMMANDES
        with tab2:
            conn = get_connection()
            df = pd.read_sql("SELECT * FROM commandes ORDER BY id DESC", conn)
            conn.close()

            if df.empty:
                st.info("Aucune commande.")
            else:
                st.metric("💰 Total ventes", f"{int(df['total'].sum())} FCFA")
                st.metric("📦 Nombre commandes", len(df))
                st.dataframe(df, use_container_width=True)

                st.subheader("Modifier statut")

                for _, row in df.iterrows():
                    col1, col2 = st.columns([3,2])
                    col1.write(f"Commande #{row['id']} - {row['statut']}")
                    new_status = col2.selectbox(
                        "Statut",
                        ["En préparation", "Prête", "Livrée"],
                        index=["En préparation", "Prête", "Livrée"].index(row["statut"]),
                        key=f"status{row['id']}"
                    )

                    if new_status != row["statut"]:
                        conn = get_connection()
                        c = conn.cursor()
                        c.execute(
                            "UPDATE commandes SET statut=? WHERE id=?",
                            (new_status,row["id"])
                        )
                        conn.commit()
                        conn.close()
                        st.rerun()
