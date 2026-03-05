import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse
from contextlib import contextmanager
from datetime import datetime
import base64

# ==========================================
# CONFIGURATION & DESIGN
# ==========================================
st.set_page_config(page_title="Teranga Gourmet", page_icon="🍽️", layout="wide")

NUMERO_WHATSAPP = "221778615900"

# Fonction pour l'alerte sonore
def play_notification():
    audio_file = "https://www.soundjay.com"
    st.markdown(f'<audio src="{audio_file}" autoplay></audio>', unsafe_allow_html=True)

st.markdown("""
<style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    .hero-container {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url('https://images.unsplash.com');
        background-size: cover; padding: 80px 20px; text-align: center; border-radius: 20px; border: 1px solid #d4af37;
    }
    .product-card {
        background: #121212; border-radius: 15px; border: 1px solid #222; margin-bottom: 15px;
    }
    .price-tag { color: #d4af37; font-weight: bold; font-size: 22px; }
    div.stButton > button { background: #d4af37 !important; color: black !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATABASE
# ==========================================
@contextmanager
def db_conn():
    conn = sqlite3.connect("teranga_final.db", check_same_thread=False)
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
    elif action == "remove":
        if item_id in st.session_state.cart:
            st.session_state.cart[item_id]["qty"] -= 1
            if st.session_state.cart[item_id]["qty"] <= 0: del st.session_state.cart[item_id]

# ==========================================
# NAVIGATION
# ==========================================
nb_items = sum(v["qty"] for v in st.session_state.cart.values())
page = st.sidebar.selectbox("Explorer", ["🏠 Accueil", "📋 La Carte", f"🛒 Panier ({nb_items})", "🔍 Suivre ma commande", "⚙️ Admin"])

# ==========================================
# ACCUEIL
# ==========================================
if page == "🏠 Accueil":
    st.markdown("""<div class="hero-container">
        <h1 style='color:#d4af37; font-size:60px;'>TERANGA GOURMET</h1>
        <p style='font-size:20px;'>L'art culinaire de Mboro livré chez vous.</p>
    </div>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("🕒 **Horaires** : 11h00 - 23h30")
    with col2:
        st.success("📍 **Zone** : Mboro et environs")

# ==========================================
# LA CARTE
# ==========================================
elif "Carte" in page:
    st.title("👨‍🍳 Notre Menu")
    with db_conn() as conn:
        df = pd.read_sql("SELECT * FROM menu", conn)

    if df.empty:
        st.warning("Le chef prépare le menu. Revenez bientôt !")
    else:
        for i in range(0, len(df), 3):
            cols = st.columns(3)
            for j, row in df.iloc[i:i+3].iterrows():
                with cols[j % 3]:
                    st.markdown(f"""<div class="product-card">
                        <img src="{row['img']}" style="width:100%; border-radius:15px 15px 0 0; height:180px; object-fit:cover;">
                        <div style="padding:15px">
                            <h4>{row['nom']}</h4>
                            <p class="price-tag">{int(row['prix'])} FCFA</p>
                            <p style="font-size:12px; color:#888;">Stock : {row['stock']}</p>
                        </div>
                    </div>""", unsafe_allow_html=True)
                    if row['stock'] > 0:
                        st.button("Ajouter", key=f"btn_{row['id']}", on_click=update_cart, args=(row["id"], row["nom"], row["prix"], row["stock"]))
                    else:
                        st.button("Épuisé", disabled=True, key=f"off_{row['id']}")

# ==========================================
# ADMIN : GESTION TOTALE
# ==========================================
elif "Admin" in page:
    st.title("⚙️ Espace Administration")
    pwd = st.sidebar.text_input("Mot de passe", type="password")
    
    if pwd == "admin123":
        tab_cmd, tab_menu = st.tabs(["📋 Commandes & Alertes", "🍱 Gestion du Menu"])
        
        with tab_cmd:
            with db_conn() as conn:
                # Alerte si nouvelle commande "En attente"
                new_cmds = conn.execute("SELECT COUNT(*) FROM commandes WHERE statut='En attente'").fetchone()[0]
                if new_cmds > 0:
                    st.warning(f"🔔 {new_cmds} nouvelle(s) commande(s) !")
                    play_notification()
                
                df_c = pd.read_sql("SELECT * FROM commandes ORDER BY id DESC", conn)
                for _, row in df_c.iterrows():
                    with st.expander(f"📦 Commande #{row['id']} - {row['statut']} ({row['total']}F)"):
                        st.write(f"**Détail :** {row['articles']}")
                        st.write(f"**Infos Client :** {row['detail']}")
                        new_st = st.selectbox("Statut", ["En attente", "En préparation", "Prête", "Livrée"], index=["En attente", "En préparation", "Prête", "Livrée"].index(row['statut']), key=f"st_{row['id']}")
                        if st.button("Actualiser Statut", key=f"up_{row['id']}"):
                            conn.execute("UPDATE commandes SET statut=? WHERE id=?", (new_st, row['id']))
                            conn.commit()
                            st.rerun()

        with tab_menu:
            st.subheader("Ajouter un nouveau plat")
            with st.form("new_dish"):
                n = st.text_input("Nom")
                p = st.number_input("Prix (FCFA)", min_value=0)
                i = st.text_input("URL Image")
                s = st.number_input("Stock Initial", min_value=0, value=10)
                if st.form_submit_button("➕ Ajouter au menu"):
                    with db_conn() as conn:
                        conn.execute("INSERT INTO menu (nom, prix, img, stock) VALUES (?,?,?,?)", (n,p,i,s))
                        conn.commit()
                    st.success("Plat ajouté !")
                    st.rerun()

            st.divider()
            st.subheader("Modifier / Supprimer des plats")
            with db_conn() as conn:
                df_m = pd.read_sql("SELECT * FROM menu", conn)
                for _, row in df_m.iterrows():
                    col1, col2, col3, col4 = st.columns([2,1,1,1])
                    col1.write(f"**{row['nom']}**")
                    col2.write(f"{int(row['prix'])}F")
                    if col3.button("🗑️ Supprimer", key=f"del_m_{row['id']}"):
                        with db_conn() as conn:
                            conn.execute("DELETE FROM menu WHERE id=?", (row['id'],))
                            conn.commit()
                        st.rerun()
                    # Possibilité d'ajuster le stock rapidement
                    new_stock = col4.number_input("Stock", value=row['stock'], key=f"stock_{row['id']}")
                    if new_stock != row['stock']:
                        with db_conn() as conn:
                            conn.execute("UPDATE menu SET stock=? WHERE id=?", (new_stock, row['id']))
                            conn.commit()
    else:
        st.error("Mot de passe incorrect")

# (Le reste du code pour Panier et Suivi reste identique à la version précédente)
elif "Panier" in page:
    st.title("🛒 Votre Panier")
    if not st.session_state.cart: st.info("Vide")
    else:
        total = 0
        summary = ""
        for k, v in list(st.session_state.cart.items()):
            total += v["prix"] * v["qty"]
            summary += f"{v['nom']} (x{v['qty']}) "
            st.write(f"**{v['nom']}** x{v['qty']} - {int(v['prix']*v['qty'])} F")
        
        st.subheader(f"Total : {int(total)} FCFA")
        infos = st.text_area("Adresse ou Table")
        if st.button("🚀 Commander"):
            with db_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO commandes (articles, total, paiement, detail, date) VALUES (?,?,'Espèces',?,?)", (summary, total, infos, datetime.now()))
                oid = cursor.lastrowid
                for k, v in st.session_state.cart.items():
                    conn.execute("UPDATE menu SET stock = stock - ? WHERE id = ?", (v['qty'], k))
                conn.commit()
            st.success(f"Commande N°{oid} reçue !")
            st.session_state.cart = {}
            st.markdown(f'<a href="https://wa.me{NUMERO_WHATSAPP}?text=Commande {oid}: {summary}" target="_blank">WhatsApp</a>', unsafe_allow_html=True)

elif "Suivre" in page:
    st.title("🔍 Suivi")
    cid = st.number_input("N° Commande", min_value=1)
    if st.button("Chercher"):
        with db_conn() as conn:
            r = conn.execute("SELECT statut FROM commandes WHERE id=?", (cid,)).fetchone()
            if r: st.info(f"Statut actuel : **{r[0]}**")
            else: st.error("Inconnu")
