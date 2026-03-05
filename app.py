import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse
from contextlib import contextmanager

# ==========================================
# CONFIGURATION & STYLE
# ==========================================
st.set_page_config(page_title="Teranga Gourmet", page_icon="🍽️", layout="wide")

NUMERO_WHATSAPP = "221778615900"
NUMERO_WAVE = "221778615900"

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .product-card {
        background: #1e1e1e; padding: 15px; border-radius: 15px;
        border: 1px solid #333; margin-bottom: 20px; text-align: center;
    }
    .price-tag { color: #d4af37; font-weight: bold; font-size: 20px; }
    div.stButton > button { width: 100%; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# GESTION DB (OPTIMISÉE)
# ==========================================
@contextmanager
def db_conn():
    conn = sqlite3.connect("restaurant_v5.db", check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with db_conn() as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS menu 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, prix REAL, img TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS commandes 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, articles TEXT, total REAL, 
             paiement TEXT, detail TEXT, type_commande TEXT, statut TEXT DEFAULT 'En attente', date DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        conn.commit()

init_db()

# ==========================================
# LOGIQUE PANIER
# ==========================================
if "cart" not in st.session_state:
    st.session_state.cart = {}

def update_cart(item_id, nom, prix, action="add"):
    item_id = str(item_id)
    if action == "add":
        if item_id in st.session_state.cart:
            st.session_state.cart[item_id]["qty"] += 1
        else:
            st.session_state.cart[item_id] = {"nom": nom, "prix": prix, "qty": 1}
    elif action == "remove":
        if item_id in st.session_state.cart:
            st.session_state.cart[item_id]["qty"] -= 1
            if st.session_state.cart[item_id]["qty"] <= 0:
                del st.session_state.cart[item_id]

# ==========================================
# NAVIGATION
# ==========================================
nb_items = sum(v["qty"] for v in st.session_state.cart.values())
page = st.sidebar.radio("Navigation", ["🏠 Accueil", "📋 La Carte", f"🛒 Panier ({nb_items})", "⚙️ Admin"])

# ==========================================
# LA CARTE
# ==========================================
if "Carte" in page:
    st.title("🍴 Notre Menu Gourmet")
    
    with db_conn() as conn:
        df = pd.read_sql("SELECT * FROM menu", conn)

    if df.empty:
        st.warning("Le menu est vide. Ajoutez des plats en mode Admin.")
    else:
        # Affichage en grille (3 colonnes)
        cols = st.columns(3)
        for idx, row in df.iterrows():
            with cols[idx % 3]:
                st.markdown(f"""<div class="product-card">
                    <img src="{row['img']}" style="width:100%; border-radius:10px; height:150px; object-fit:cover;">
                    <h3>{row['nom']}</h3>
                    <p class="price-tag">{int(row['prix'])} FCFA</p>
                </div>""", unsafe_allow_html=True)
                st.button("➕ Ajouter", key=f"add_{row['id']}", on_click=update_cart, args=(row["id"], row["nom"], row["prix"], "add"))

# ==========================================
# PANIER & PAIEMENT
# ==========================================
elif "Panier" in page:
    st.title("🛒 Récapitulatif")
    
    if not st.session_state.cart:
        st.info("Votre panier est vide.")
    else:
        total = 0
        summary_text = "Ma commande Teranga :\n"
        
        for k, v in list(st.session_state.cart.items()):
            sub = v["prix"] * v["qty"]
            total += sub
            summary_text += f"- {v['nom']} (x{v['qty']}) : {int(sub)}F\n"
            
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            c1.write(f"**{v['nom']}**")
            c2.write(f"{int(v['prix'])}F")
            c3.write(f"Qté: {v['qty']}")
            if c4.button("❌", key=f"del_{k}"):
                update_cart(k, None, None, "remove")
                st.rerun()
        
        st.subheader(f"Total : {int(total)} FCFA")
        
        # Options de livraison
        type_cmd = st.radio("Mode :", ["Livraison", "Sur place"], horizontal=True)
        infos = st.text_area("Précisions (Adresse, N° de table, Tel...)", placeholder="Ex: Mboro Gare, Villa 12 ou Table N°5")
        mode_paye = st.selectbox("Paiement :", ["Wave", "Orange Money", "Espèces"])

        if st.button("✅ Confirmer la commande", use_container_width=True):
            if not infos:
                st.error("Veuillez saisir vos informations de livraison/table.")
            else:
                # 1. Enregistrement DB
                with db_conn() as conn:
                    conn.execute("INSERT INTO commandes (articles, total, paiement, detail, type_commande) VALUES (?,?,?,?,?)",
                                (summary_text, total, mode_paye, infos, type_cmd))
                    conn.commit()
                
                # 2. Préparation Message WhatsApp
                msg_final = f"{summary_text}\n💰 Total: {int(total)}F\n📍 Info: {infos}\n💳 Payé par: {mode_paye}"
                url_wa = f"https://wa.me{NUMERO_WHATSAPP}?text={urllib.parse.quote(msg_final)}"
                
                st.success("Commande enregistrée !")
                st.markdown(f'''<a href="{url_wa}" target="_blank" style="background-color:#25D366; color:white; padding:15px; text-decoration:none; border-radius:10px; display:block; text-align:center;">🚀 Envoyer via WhatsApp</a>''', unsafe_allow_html=True)
                
                if mode_paye == "Wave":
                    st.markdown(f'<a href="https://wave.com/pay/{NUMERO_WAVE}" class="pay-btn-wave">📱 Payer par Wave</a>', unsafe_allow_html=True)

# ==========================================
# ADMIN (SIMPLIFIÉ)
# ==========================================
elif "Admin" in page:
    pwd = st.text_input("Mot de passe", type="password")
    if pwd == "admin123":
        tab1, tab2 = st.tabs(["Ajouter Plat", "Commandes"])
        
        with tab1:
            with st.form("add_form"):
                n = st.text_input("Nom du plat")
                p = st.number_input("Prix", min_value=0)
                i = st.text_input("Lien image (URL)")
                if st.form_submit_button("Ajouter"):
                    with db_conn() as conn:
                        conn.execute("INSERT INTO menu (nom, prix, img) VALUES (?,?,?)", (n, p, i))
                        conn.commit()
                    st.success("Plat ajouté !")
        
        with tab2:
            with db_conn() as conn:
                st.dataframe(pd.read_sql("SELECT * FROM commandes ORDER BY date DESC", conn))
    else:
        st.error("Accès restreint")

else: # Accueil
    st.image("https://images.unsplash.com/photo-1555992336-03a23c9f8a5c", use_container_width=True)
    st.title("Bienvenue chez Teranga Gourmet")
    st.write("Le meilleur de Mboro à portée de clic.")
