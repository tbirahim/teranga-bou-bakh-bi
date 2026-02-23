import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Menu Express Mboro", page_icon="🥘", layout="wide", initial_sidebar_state="collapsed")

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

# --- 3. SESSION STATE ---
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
    .stApp { background-color: #0c0c0c; color: white; }
    .btn-whatsapp { display: block; width: 100%; background-color: #25D366; color: white !important; text-align: center; padding: 15px; border-radius: 12px; font-weight: bold; text-decoration: none; margin-top: 10px;}
    .pay-btn-wave { display: block; width: 100%; background-color: #0096ff; color: white !important; text-align: center; padding: 15px; border-radius: 10px; font-weight: bold; text-decoration: none; }
    .pay-btn-om { display: block; width: 100%; background-color: #ff6600; color: white !important; text-align: center; padding: 15px; border-radius: 10px; font-weight: bold; text-decoration: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. NAVIGATION ---
nb_articles = sum(item['qty'] for item in st.session_state.cart.values())
with st.sidebar:
    st.title("Menu Express")
    page = st.radio("Aller vers :", ["Accueil", "La Carte", "Réserver", f"Panier ({nb_articles})", "Admin"])

# --- PAGE : ACCUEIL ---
if page == "Accueil":
    st.image("https://images.unsplash.com/photo-1555939594-58d7cb561ad1?q=80&w=2000", use_container_width=True)
    st.markdown("<h1 style='text-align: center;'>Bienvenue chez Menu Express</h1>", unsafe_allow_html=True)

# --- PAGE : LA CARTE ---
elif page == "La Carte":
    st.header("🍴 Notre Carte")
    df = pd.read_sql('SELECT * FROM menu', get_connection())
    if df.empty:
        st.info("Le menu est vide.")
    else:
        for _, row in df.iterrows():
            c1, c2 = st.columns([1, 2])
            with c1: st.image(row['img'] if row['img'] else "https://via.placeholder.com/150")
            with c2:
                st.subheader(row['nom'])
                st.write(f"**{int(row['prix'])} FCFA**")
                st.button(f"Ajouter au panier", key=f"btn_{row['id']}", on_click=add_to_cart, args=(row['id'], row['nom'], row['prix']), use_container_width=True)
            st.divider()

# --- PAGE : RÉSERVER (CORRIGÉ) ---
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
            st.markdown(f'<a href="{link}" target="_blank" class="btn-whatsapp">✅ CONFIRMER SUR WHATSAPP</a>', unsafe_allow_html=True)

# --- PAGE : PANIER ---
elif "Panier" in page:
    st.header("🛒 Votre Panier")
    if not st.session_state.cart:
        st.info("Panier vide.")
    else:
        total = sum(v['prix'] * v['qty'] for v in st.session_state.cart.values())
        txt_commande = "".join([f"- {v['nom']} (x{v['qty']})\n" for v in st.session_state.cart.values()])
        for k, v in list(st.session_state.cart.items()):
            st.write(f"**{v['nom']}** x{v['qty']} = {int(v['prix']*v['qty'])} F")
        
        st.markdown(f"### Total : {int(total)} FCFA")
        methode = st.radio("Paiement", ["Wave", "Orange Money", "Espèces"])
        adresse = st.text_input("Adresse / Table")
        
        if methode == "Wave":
            st.markdown(f'<a href="https://wave.com/pay/{NUMERO_MARCHAND_WAVE}" target="_blank" class="pay-btn-wave">📱 PAYER {int(total)} F PAR WAVE</a>', unsafe_allow_html=True)
        elif methode == "Orange Money":
            st.markdown(f'<a href="tel:#144#39#" class="pay-btn-om">📱 PAYER {int(total)} F PAR OM</a>', unsafe_allow_html=True)

        if st.button("🚀 VALIDER LA COMMANDE"):
            if not adresse: st.error("Lieu manquant.")
            else:
                get_connection().cursor().execute('INSERT INTO commandes (articles, total, paiement, detail) VALUES (?,?,?,?)', (txt_commande, total, methode, adresse)).connection.commit()
                msg = f"🥘 *COMMANDE*\n{txt_commande}💰 TOTAL: {int(total)} F\n💳 PAIEMENT: {methode}\n📍 LIEU: {adresse}"
                link = f"https://wa.me/{NUMERO_WHATSAPP}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{link}" target="_blank" class="btn-whatsapp">📲 ENVOYER SUR WHATSAPP</a>', unsafe_allow_html=True)

# --- PAGE : ADMIN (CORRIGÉ) ---
elif page == "Admin":
    st.header("🔐 Administration")
    if st.text_input("Code Secret", type="password") == ADMIN_PASSWORD:
        tab1, tab2, tab3 = st.tabs(["➕ Ajouter", "📋 Menu actuel", "📦 Commandes"])
        
        with tab1:
            with st.form("add"):
                n = st.text_input("Nom"); p = st.number_input("Prix", 0); i = st.text_input("Lien Image URL")
                if st.form_submit_button("Ajouter"):
                    get_connection().cursor().execute('INSERT INTO menu (nom, prix, img) VALUES (?,?,?)', (n,p,i)).connection.commit()
                    st.success("Plat ajouté !"); st.rerun()
        
        with tab2:
            df_m = pd.read_sql('SELECT * FROM menu', get_connection())
            for _, r in df_m.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{r['nom']}** - {int(r['prix'])} F")
                if c2.button("🗑️", key=f"del_{r['id']}"):
                    get_connection().cursor().execute('DELETE FROM menu WHERE id=?', (r['id'],)).connection.commit()
                    st.rerun()
        
        with tab3:
            df_c = pd.read_sql('SELECT * FROM commandes ORDER BY id DESC', get_connection())
            st.dataframe(df_c)
