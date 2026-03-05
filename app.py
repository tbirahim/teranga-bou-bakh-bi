import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse
from datetime import datetime

# ==========================================
# 1. CONFIGURATION & DESIGN
# ==========================================
st.set_page_config(page_title="Teranga Gourmet", page_icon="🇸🇳", layout="wide")

# Style Premium Sénégalais
st.markdown("""
<style>
    .stApp { background-color: #050a05; color: #e0e0e0; }
    .hero {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url('https://images.unsplash.com');
        background-size: cover; padding: 60px; text-align: center;
        border-radius: 20px; border: 1px solid #d4af37;
    }
    .product-card {
        background: #111; border-radius: 15px; border: 1px solid #222;
        padding: 10px; margin-bottom: 20px; transition: 0.3s;
    }
    .product-card:hover { border-color: #d4af37; }
    div.stButton > button {
        background-color: #d4af37 !important; color: black !important;
        font-weight: bold; border-radius: 10px; border: none;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INITIALISATION ET ETAT (SESSION STATE)
# ==========================================
if "page" not in st.session_state:
    st.session_state.page = "🏠 Accueil"
if "cart" not in st.session_state:
    st.session_state.cart = {}

# Fonction de navigation pour éviter les retours auto à l'accueil
def change_page():
    st.session_state.page = st.session_state.nav_choice

# ==========================================
# 3. BASE DE DONNÉES
# ==========================================
def init_db():
    conn = sqlite3.connect("teranga_final.db", check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS menu (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, prix REAL, img TEXT, stock INTEGER)")
    conn.execute("CREATE TABLE IF NOT EXISTS commandes (id INTEGER PRIMARY KEY AUTOINCREMENT, items TEXT, total REAL, detail TEXT, date DATETIME)")
    conn.commit()
    return conn

db = init_db()

# ==========================================
# 4. BARRE DE NAVIGATION (FIXÉE)
# ==========================================
with st.sidebar:
    st.title("🇸🇳 Teranga Menu")
    nb_art = sum(v['qty'] for v in st.session_state.cart.values())
    
    # On utilise st.session_state.page comme index par défaut
    nav_options = ["🏠 Accueil", "📋 La Carte", "🛒 Panier", "⚙️ Admin"]
    
    st.radio(
        "Navigation", 
        nav_options, 
        index=nav_options.index(st.session_state.page) if st.session_state.page in nav_options else 0,
        key="nav_choice",
        on_change=change_page
    )
    st.divider()
    st.write(f"Articles au panier : **{nb_art}**")

# ==========================================
# 5. LOGIQUE DES PAGES
# ==========================================

# --- ACCUEIL ---
if st.session_state.page == "🏠 Accueil":
    st.markdown("""
    <div class="hero">
        <h1 style='color:#d4af37;'>TERANGA GOURMET</h1>
        <p>L'excellence culinaire de Mboro livré avec passion.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("🍽️ DÉCOUVRIR LE MENU", use_container_width=True):
        st.session_state.page = "📋 La Carte"
        st.rerun()

# --- LA CARTE ---
elif st.session_state.page == "📋 La Carte":
    st.header("🥘 Notre Carte")
    df = pd.read_sql("SELECT * FROM menu", db)
    
    if df.empty:
        st.info("Le menu est vide. Ajoutez des plats en mode Admin.")
    else:
        cols = st.columns(3)
        for i, row in df.iterrows():
            with cols[i % 3]:
                st.markdown(f"""<div class="product-card">
                    <img src="{row['img']}" style="width:100%; border-radius:10px; height:180px; object-fit:cover;">
                    <h3 style="color:#d4af37; margin-bottom:0;">{row['nom']}</h3>
                    <p style="font-weight:bold; font-size:20px;">{int(row['prix'])} FCFA</p>
                    <p style="font-size:12px; color:#888;">Stock : {row['stock']}</p>
                </div>""", unsafe_allow_html=True)
                
                if row['stock'] > 0:
                    if st.button(f"Ajouter {row['nom']}", key=f"add_{row['id']}", use_container_width=True):
                        pid = str(row['id'])
                        if pid in st.session_state.cart:
                            st.session_state.cart[pid]['qty'] += 1
                        else:
                            st.session_state.cart[pid] = {'nom': row['nom'], 'prix': row['prix'], 'qty': 1, 'id': row['id']}
                        st.toast(f"✅ {row['nom']} ajouté !")
                else:
                    st.button("Épuisé", disabled=True, key=f"sold_{row['id']}", use_container_width=True)

# --- PANIER & COMMANDE ---
elif st.session_state.page == "🛒 Panier":
    st.header("🛒 Votre Sélection")
    
    if not st.session_state.cart:
        st.warning("Panier vide.")
    else:
        total = 0
        summary = ""
        for k, v in list(st.session_state.cart.items()):
            sub = v['prix'] * v['qty']
            total += sub
            summary += f"- {v['nom']} (x{v['qty']})\n"
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{v['nom']}**")
            c2.write(f"{int(sub)} F")
            if c3.button("🗑️", key=f"del_{k}"):
                del st.session_state.cart[k]
                st.rerun()
        
        st.divider()
        st.subheader(f"Total : {int(total)} FCFA")

        mode = st.radio("Comment souhaitez-vous consommer ?", ["Sur place", "Livraison"], horizontal=True)
        
        valid = False
        details = ""
        
        if mode == "Sur place":
            table = st.text_input("🔢 Numéro de table")
            if table:
                details = f"SUR PLACE - Table N°{table}"
                valid = True
        else:
            c1, c2 = st.columns(2)
            tel = c1.text_input("📞 Téléphone")
            adr = c2.text_input("📍 Adresse")
            if tel and adr:
                details = f"LIVRAISON - Tel: {tel} | Adr: {adr}"
                valid = True

        if valid:
            if st.button("🚀 VALIDER & ENVOYER SUR WHATSAPP", use_container_width=True):
                # Enregistrement + Déstockage
                c = db.cursor()
                c.execute("INSERT INTO commandes (items, total, detail, date) VALUES (?,?,?,?)", (summary, total, details, datetime.now()))
                for k, v in st.session_state.cart.items():
                    c.execute("UPDATE menu SET stock = stock - ? WHERE id = ?", (v['qty'], v['id']))
                db.commit()
                
                # WhatsApp
                msg = f"COMMANDE TERANGA\n\n{summary}\nTOTAL: {int(total)}F\n\nINFO: {details}"
                url = f"https://wa.me{urllib.parse.quote(msg)}"
                st.session_state.cart = {}
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
                st.success("Redirection vers WhatsApp...")

# --- ADMIN ---
elif st.session_state.page == "⚙️ Admin":
    pwd = st.sidebar.text_input("Password", type="password")
    if pwd == "admin123":
        tab1, tab2 = st.tabs(["Commandes", "Menu"])
        with tab1:
            st.dataframe(pd.read_sql("SELECT * FROM commandes ORDER BY date DESC", db), use_container_width=True)
        with tab2:
            st.subheader("Ajouter un plat")
            with st.form("add_form"):
                n = st.text_input("Nom")
                p = st.number_input("Prix", min_value=0)
                i = st.text_input("Lien Image URL")
                s = st.number_input("Stock", min_value=0, value=20)
                if st.form_submit_button("Sauvegarder"):
                    db.execute("INSERT INTO menu (nom, prix, img, stock) VALUES (?,?,?,?)", (n,p,i,s))
                    db.commit()
                    st.rerun()
            
            st.divider()
            df_m = pd.read_sql("SELECT * FROM menu", db)
            for _, r in df_m.iterrows():
                col1, col2 = st.columns([4, 1])
                col1.write(f"**{r['nom']}** ({int(r['prix'])}F) - Stock: {r['stock']}")
                if col2.button("Supprimer", key=f"rm_{r['id']}"):
                    db.execute("DELETE FROM menu WHERE id=?", (r['id'],))
                    db.commit()
                    st.rerun()
