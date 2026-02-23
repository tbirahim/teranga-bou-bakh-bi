import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Menu Express Mboro", page_icon="🥘", layout="wide", initial_sidebar_state="collapsed")

# CONFIGURATION COMMERCIALE
NUMERO_WHATSAPP = "221778615900"
NUMERO_MARCHAND_WAVE = "221778615900"

try:
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except:
    ADMIN_PASSWORD = "admin"

# --- 2. BASE DE DONNÉES ---
def get_connection():
    return sqlite3.connect('menu_express_v_final.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS menu (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, prix REAL, img TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS commandes (id INTEGER PRIMARY KEY AUTOINCREMENT, articles TEXT, total REAL, paiement TEXT, detail TEXT, date DATETIME DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()

init_db()

# --- 3. SESSION STATE (PANIER) ---
if 'cart' not in st.session_state:
    st.session_state.cart = {}

def add_to_cart(item_id, nom, prix):
    item_id = str(item_id)
    if item_id in st.session_state.cart:
        st.session_state.cart[item_id]['qty'] += 1
    else:
        st.session_state.cart[item_id] = {'nom': nom, 'prix': prix, 'qty': 1}
    st.toast(f"✅ {nom} ajouté !")

# --- 4. STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0c0c0c; color: white; font-family: 'Arial', sans-serif; }
    .btn-whatsapp { display: block; width: 100%; background-color: #25D366; color: white !important; text-align: center; padding: 15px; border-radius: 12px; font-weight: bold; text-decoration: none; margin-top: 10px;}
    .pay-btn-wave { display: block; width: 100%; background-color: #0096ff; color: white !important; text-align: center; padding: 15px; border-radius: 10px; font-weight: bold; text-decoration: none; }
    .pay-btn-om { display: block; width: 100%; background-color: #ff6600; color: white !important; text-align: center; padding: 15px; border-radius: 10px; font-weight: bold; text-decoration: none; }
    .plat-card { background:#1a1a1a; padding:10px; border-radius:15px; border: 1px solid #333; margin-bottom:10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. NAVIGATION ---
nb_articles = sum(item['qty'] for item in st.session_state.cart.values())
with st.sidebar:
    st.title("🍔 Menu Express")
    page = st.radio("Aller vers :", ["Accueil", "La Carte", "Réserver", f"Panier ({nb_articles})", "Admin"])
    st.divider()
    st.write("📍 Mboro, Sénégal")

# --- PAGE : ACCUEIL ---
if page == "Accueil":
    st.image("https://assets.zyrosite.com/cdn-cgi/image/format=auto,w=1032,h=579,fit=crop/mp866EK3ZZCwpq0W/lateranga_hero01-AQEJ7vDMyGsRRZwD.jpg", use_container_width=True)
    st.markdown("<h1 style='text-align: center; color:#d4af37;'>Teranga Gourmet Mboro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Découvrez le goût authentique. Livraison rapide et paiement sécurisé.</p>", unsafe_allow_html=True)
    if st.button("Voir la Carte", use_container_width=True):
        st.switch_page = "La Carte" # Note: switch_page simple pour streamlit

# --- PAGE : LA CARTE ---
elif page == "La Carte":
    st.header("🍴 Notre Carte")
    df = pd.read_sql('SELECT * FROM menu', get_connection())
    if df.empty:
        st.info("Le menu est vide. (Admin : ajoutez des plats)")
    else:
        for _, row in df.iterrows():
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(row['img'] if row['img'] else "https://via.placeholder.com/150", use_container_width=True)
                with c2:
                    st.subheader(row['nom'])
                    st.markdown(f"<h4 style='color:#d4af37;'>{int(row['prix'])} FCFA</h4>", unsafe_allow_html=True)
                    st.button(f"Ajouter au panier", key=f"btn_{row['id']}", on_click=add_to_cart, args=(row['id'], row['nom'], row['prix']), use_container_width=True)
            st.divider()

# --- PAGE : RÉSERVER ---
elif page == "Réserver":
    st.header("📅 Réserver une table")
    with st.form("form_res"):
        nom = st.text_input("Votre Nom")
        date = st.date_input("Date")
        heure = st.time_input("Heure")
        pers = st.number_input("Nombre de personnes", 1, 10, 2)
        if st.form_submit_button("Vérifier la disponibilité"):
            msg = f"📝 *RÉSERVATION*\n👤 Nom: {nom}\n📅 Date: {date}\n⏰ Heure: {heure}\n👥 Pers: {pers}"
            link = f"https://wa.me/{NUMERO_WHATSAPP}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{link}" target="_blank" class="btn-whatsapp">✅ ENVOYER SUR WHATSAPP</a>', unsafe_allow_html=True)

# --- PAGE : PANIER ---
elif "Panier" in page:
    st.header("🛒 Votre Panier")
    if not st.session_state.cart:
        st.info("Votre panier est vide.")
    else:
        total = 0
        txt_commande = ""
        for k, v in list(st.session_state.cart.items()):
            sub = v['prix'] * v['qty']
            total += sub
            txt_commande += f"- {v['nom']} (x{v['qty']})\n"
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{v['nom']}** ({int(v['prix'])} F)")
            c2.write(f"x{v['qty']}")
            if c3.button("🗑️", key=f"del_{k}"):
                del st.session_state.cart[k]
                st.rerun()
        
        st.markdown(f"<h2 style='text-align:right;'>Total : {int(total)} FCFA</h2>", unsafe_allow_html=True)
        st.divider()
        
        methode = st.radio("Mode de paiement", ["Wave", "Orange Money", "Espèces"])
        adresse = st.text_input("📍 Adresse de livraison précise / N° Table")
        
        if methode == "Wave":
            st.markdown(f'<a href="https://wave.com/pay/{NUMERO_MARCHAND_WAVE}" target="_blank" class="pay-btn-wave">📱 PAYER {int(total)} F PAR WAVE</a>', unsafe_allow_html=True)
        elif methode == "Orange Money":
            st.markdown(f'<a href="tel:#144#39#" class="pay-btn-om">📱 PAYER {int(total)} F PAR OM</a>', unsafe_allow_html=True)

        if st.button("🚀 VALIDER LA COMMANDE", use_container_width=True):
            if not adresse:
                st.error("Veuillez indiquer une adresse.")
            else:
                get_connection().cursor().execute('INSERT INTO commandes (articles, total, paiement, detail) VALUES (?,?,?,?)', (txt_commande, total, methode, adresse)).connection.commit()
                msg = f"🥘 *NOUVELLE COMMANDE*\n{txt_commande}💰 TOTAL: {int(total)} F\n💳 PAIEMENT: {methode}\n📍 LIEU: {adresse}"
                link = f"https://wa.me/{NUMERO_WHATSAPP}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{link}" target="_blank" class="btn-whatsapp">📲 ENVOYER LE REÇU SUR WHATSAPP</a>', unsafe_allow_html=True)

# --- PAGE : ADMIN ---
elif page == "Admin":
    st.header("🔐 Espace Administration")
    code = st.text_input("Entrez le code secret", type="password")
    
    if code == ADMIN_PASSWORD:
        tab1, tab2, tab3 = st.tabs(["➕ Ajouter", "📋 Menu actuel", "📦 Commandes"])
        
        with tab1:
            with st.form("add_form", clear_on_submit=True):
                n = st.text_input("Nom du plat")
                p = st.number_input("Prix", min_value=0, step=100)
                i = st.text_input("URL de l'image")
                if st.form_submit_button("Ajouter à la carte"):
                    get_connection().cursor().execute('INSERT INTO menu (nom, prix, img) VALUES (?,?,?)', (n,p,i)).connection.commit()
                    st.success("Plat ajouté !")
                    st.rerun()
        
        with tab2:
            st.subheader("Gestion des produits")
            df_m = pd.read_sql('SELECT * FROM menu', get_connection())
            for _, r in df_m.iterrows():
                col_n, col_d = st.columns([4, 1])
                col_n.write(f"**{r['nom']}** - {int(r['prix'])} F")
                if col_d.button("Effacer", key=f"d_{r['id']}"):
                    get_connection().cursor().execute('DELETE FROM menu WHERE id=?', (r['id'],)).connection.commit()
                    st.rerun()
        
        with tab3:
            st.subheader("Historique des ventes")
            df_c = pd.read_sql('SELECT * FROM commandes ORDER BY id DESC', get_connection())
            st.dataframe(df_c, use_container_width=True)
            if st.button("Vider l'historique"):
                get_connection().cursor().execute('DELETE FROM commandes').connection.commit()
                st.rerun()
