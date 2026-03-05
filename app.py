import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse
from contextlib import contextmanager
from datetime import datetime

# ==========================================
# CONFIGURATION & DESIGN
# ==========================================
st.set_page_config(page_title="Teranga Gourmet", page_icon="🍽️", layout="wide")

NUMERO_WHATSAPP = "221778615900"

st.markdown("""
<style>
    /* Global Style */
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    /* Hero Section */
    .hero-container {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url('https://images.unsplash.com');
        background-size: cover;
        padding: 100px 20px;
        text-align: center;
        border-radius: 20px;
        margin-bottom: 40px;
        border: 1px solid #d4af3733;
    }
    .hero-title { font-size: 55px; color: #d4af37; font-weight: 800; margin-bottom: 10px; }
    .hero-subtitle { font-size: 20px; color: #ffffff; opacity: 0.9; }

    /* Product Cards */
    .product-card {
        background: #121212;
        padding: 0px;
        border-radius: 15px;
        border: 1px solid #222;
        transition: transform 0.3s;
        margin-bottom: 15px;
    }
    .product-card:hover { border-color: #d4af37; transform: translateY(-5px); }
    .price-tag { color: #d4af37; font-weight: bold; font-size: 22px; }
    .stock-tag { font-size: 12px; color: #888; }
    
    /* Buttons */
    div.stButton > button {
        background: #d4af37 !important; color: black !important;
        font-weight: bold; border: none; border-radius: 8px; height: 45px;
    }
    div.stButton > button:disabled { background: #333 !important; color: #777 !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATABASE & STOCKS
# ==========================================
@contextmanager
def db_conn():
    conn = sqlite3.connect("teranga_v6.db", check_same_thread=False)
    try: yield conn
    finally: conn.close()

def init_db():
    with db_conn() as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS menu 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, prix REAL, img TEXT, stock INTEGER DEFAULT 10)""")
        c.execute("""CREATE TABLE IF NOT EXISTS commandes 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, articles TEXT, total REAL, 
             paiement TEXT, detail TEXT, statut TEXT DEFAULT 'En attente', date DATETIME)""")
        conn.commit()

init_db()

# ==========================================
# LOGIQUE PANIER
# ==========================================
if "cart" not in st.session_state: st.session_state.cart = {}

def update_cart(item_id, nom, prix, stock_dispo, action="add"):
    item_id = str(item_id)
    current_qty = st.session_state.cart.get(item_id, {}).get("qty", 0)
    
    if action == "add":
        if current_qty < stock_dispo:
            if item_id in st.session_state.cart: st.session_state.cart[item_id]["qty"] += 1
            else: st.session_state.cart[item_id] = {"nom": nom, "prix": prix, "qty": 1}
            st.toast(f"✅ {nom} ajouté")
        else:
            st.error("Stock insuffisant !")
    elif action == "remove":
        if item_id in st.session_state.cart:
            st.session_state.cart[item_id]["qty"] -= 1
            if st.session_state.cart[item_id]["qty"] <= 0: del st.session_state.cart[item_id]

# ==========================================
# UI NAVIGATION
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com", width=100)
nb_items = sum(v["qty"] for v in st.session_state.cart.values())
page = st.sidebar.selectbox("Explorer", ["🏠 Accueil", "📋 La Carte", f"🛒 Panier ({nb_items})", "🔍 Suivre ma commande", "⚙️ Admin"])

# ==========================================
# PAGE : ACCUEIL (DESIGN PRO)
# ==========================================
if page == "🏠 Accueil":
    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-title">TERANGA GOURMET</div>
        <div class="hero-subtitle">L'excellence de la cuisine Sénégalaise à Mboro</div>
        <br>
        <p style="color: #d4af37">✨ Ouvert de 11h00 à 23h30</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🍱 Fraîcheur")
        st.write("Produits locaux sélectionnés chaque matin au marché de Mboro.")
    with col2:
        st.markdown("### ⚡ Rapidité")
        st.write("Livraison en moins de 30 minutes dans toute la zone.")
    with col3:
        st.markdown("### 💳 Paiement")
        st.write("Sécurisé via Wave, Orange Money ou à la livraison.")

# ==========================================
# PAGE : LA CARTE (AVEC STOCKS)
# ==========================================
elif "Carte" in page:
    st.title("👨‍🍳 La Carte du Chef")
    with db_conn() as conn:
        df = pd.read_sql("SELECT * FROM menu", conn)

    if df.empty:
        st.info("Le menu arrive bientôt...")
    else:
        for i in range(0, len(df), 3):
            cols = st.columns(3)
            for j, row in df.iloc[i:i+3].iterrows():
                with cols[j % 3]:
                    st.markdown(f"""<div class="product-card">
                        <img src="{row['img']}" style="width:100%; border-radius:15px 15px 0 0; height:180px; object-fit:cover;">
                        <div style="padding:15px">
                            <h4 style="margin:0">{row['nom']}</h4>
                            <p class="stock-tag">En stock: {row['stock']}</p>
                            <p class="price-tag">{int(row['prix'])} FCFA</p>
                        </div>
                    </div>""", unsafe_allow_html=True)
                    
                    if row['stock'] > 0:
                        st.button("Ajouter au panier", key=f"add_{row['id']}", 
                                  on_click=update_cart, args=(row["id"], row["nom"], row["prix"], row["stock"]))
                    else:
                        st.button("Épuisé", disabled=True, key=f"off_{row['id']}")

# ==========================================
# PAGE : SUIVI DE COMMANDE
# ==========================================
elif "Suivre" in page:
    st.title("🔍 Suivi de commande")
    cmd_id = st.number_input("Entrez votre N° de commande", min_value=1, step=1)
    if st.button("Vérifier"):
        with db_conn() as conn:
            res = conn.execute("SELECT statut, articles, total FROM commandes WHERE id=?", (cmd_id,)).fetchone()
            if res:
                st.subheader(f"Statut : {res[0]}")
                st.write(f"Contenu : {res[1]}")
                st.info(f"Total payé : {res[2]} FCFA")
            else:
                st.error("Commande introuvable.")

# ==========================================
# PAGE : PANIER & VALIDATION
# ==========================================
elif "Panier" in page:
    st.title("🛒 Votre Panier")
    if not st.session_state.cart:
        st.info("Votre panier est vide.")
    else:
        total = 0
        summary = ""
        for k, v in list(st.session_state.cart.items()):
            sub = v["prix"] * v["qty"]
            total += sub
            summary += f"{v['nom']} (x{v['qty']}), "
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{v['nom']}**")
            c2.write(f"{int(sub)} F")
            if c3.button("🗑️", key=f"rm_{k}"):
                update_cart(k, None, None, 0, "remove")
                st.rerun()
        
        st.divider()
        infos = st.text_input("Adresse de livraison ou N° de table")
        pay_mode = st.selectbox("Mode de paiement", ["Wave", "Espèces", "Orange Money"])
        
        if st.button("🚀 Valider la commande"):
            if not infos:
                st.error("Précisez le lieu de livraison.")
            else:
                with db_conn() as conn:
                    # 1. Créer la commande
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO commandes (articles, total, paiement, detail, date) VALUES (?,?,?,?,?)",
                                (summary, total, pay_mode, infos, datetime.now()))
                    order_id = cursor.lastrowid
                    # 2. Déduire les stocks
                    for k, v in st.session_state.cart.items():
                        conn.execute("UPDATE menu SET stock = stock - ? WHERE id = ?", (v['qty'], k))
                    conn.commit()
                
                st.success(f"Commande N°{order_id} validée !")
                st.session_state.cart = {}
                st.balloons()
                
                # WhatsApp
                msg = f"Nouvelle Commande N°{order_id}\nArticles: {summary}\nTotal: {total}F\nLieu: {infos}"
                st.markdown(f'<a href="https://wa.me{NUMERO_WHATSAPP}?text={urllib.parse.quote(msg)}" target="_blank" style="display:block; background:#25D366; color:white; padding:15px; text-align:center; border-radius:10px; text-decoration:none;">📱 Prévenir le restaurant sur WhatsApp</a>', unsafe_allow_html=True)

# ==========================================
# ADMIN : GESTION STATUT & STOCKS
# ==========================================
elif "Admin" in page:
    pwd = st.sidebar.text_input("Accès", type="password")
    if pwd == "admin":
        t1, t2 = st.tabs(["Stock & Menu", "Gestion Commandes"])
        with t1:
            # Interface ajout/edition simplifiée
            st.subheader("Mise à jour des stocks")
            with db_conn() as conn:
                df_m = pd.read_sql("SELECT * FROM menu", conn)
                st.data_editor(df_m, key="menu_editor", num_rows="dynamic")
                if st.button("Sauvegarder modifications"):
                    # Logique de mise à jour simplifiée pour l'exemple
                    pass 
        with t2:
            with db_conn() as conn:
                df_c = pd.read_sql("SELECT * FROM commandes ORDER BY id DESC", conn)
                for _, row in df_c.iterrows():
                    with st.expander(f"Commande #{row['id']} - {row['statut']}"):
                        new_statut = st.selectbox("Changer statut", ["En attente", "En préparation", "Prête", "Livrée"], key=f"st_{row['id']}")
                        if st.button("Mettre à jour", key=f"up_{row['id']}"):
                            conn.execute("UPDATE commandes SET statut=? WHERE id=?", (new_statut, row['id']))
                            conn.commit()
                            st.rerun()
