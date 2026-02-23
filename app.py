import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse
import segno
from io import BytesIO

# --- 1. CONFIGURATION & SÉCURITÉ ---
st.set_page_config(page_title="Menu Express Mboro", page_icon="🥘", layout="wide", initial_sidebar_state="collapsed")

# 🔴 CONFIGURATION
NUMERO_WHATSAPP = "221778615900" 
NUMERO_PAYEMENT = "778615900"
try:
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except:
    ADMIN_PASSWORD = "admin"

# --- 2. BASE DE DONNÉES (CORRECTION ERREUR SQLITE) ---
def get_connection():
    return sqlite3.connect('menu_express_v2.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # On s'assure que la table a TOUTES les colonnes nécessaires
    c.execute('''CREATE TABLE IF NOT EXISTS menu 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, prix REAL, img TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS commandes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, articles TEXT, total REAL, 
                  paiement TEXT, detail TEXT, date DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()

init_db()

# --- 3. GESTION DU PANIER (CORRECTION RÉACTUALISATION) ---
if 'cart' not in st.session_state:
    st.session_state.cart = {} # On utilise un dictionnaire pour garder les quantités

def add_to_cart(item_id, nom, prix):
    if str(item_id) in st.session_state.cart:
        st.session_state.cart[str(item_id)]['qty'] += 1
    else:
        st.session_state.cart[str(item_id)] = {'nom': nom, 'prix': prix, 'qty': 1}
    st.toast(f"✅ {nom} ajouté au panier !")

# --- 4. STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0c0c0c; color: white; }
    .plat-card { background:#1a1a1a; border-radius:15px; border: 1px solid #333; margin-bottom:20px; }
    .btn-whatsapp { display: block; width: 100%; background-color: #25D366; color: white !important; text-align: center; padding: 15px; border-radius: 12px; font-weight: bold; text-decoration: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1046/1046771.png", width=100)
    page = st.radio("MENU", ["Accueil", "La Carte", f"Mon panier ({sum(item['qty'] for item in st.session_state.cart.values())})", "Admin"])

# --- PAGE 1: ACCUEIL ---
if page == "Accueil":
    # Correction Image : Lien stable Unsplash
    st.image("https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?q=80&w=2070", use_container_width=True)
    st.markdown("<h1>TERANGA GOURMET</h1>", unsafe_allow_html=True)
    st.write("### Savourez l'instant à Mboro")

# --- PAGE 2: LA CARTE ---
elif page == "La Carte":
    st.header("🍴 Notre Carte")
    df_menu = pd.read_sql('SELECT * FROM menu', get_connection())
    
    if df_menu.empty:
        st.info("Le menu est vide. Ajoutez des plats dans l'onglet Admin.")
    else:
        for _, row in df_menu.iterrows():
            with st.container():
                col_img, col_txt = st.columns([1, 2])
                with col_img:
                    img_url = row['img'] if row['img'] else "https://via.placeholder.com/150"
                    st.image(img_url, use_container_width=True)
                with col_txt:
                    st.subheader(row['nom'])
                    st.write(f"Prix : **{int(row['prix'])} FCFA**")
                    # Bouton d'ajout sans rechargement bloquant
                    st.button(f"Ajouter au panier", key=f"btn_{row['id']}", 
                              on_click=add_to_cart, args=(row['id'], row['nom'], row['prix']))
            st.divider()

# --- PAGE 3: PANIER & PAIEMENT ---
elif "panier" in page:
    st.header("🛒 Votre Panier")
    if not st.session_state.cart:
        st.write("Votre panier est vide.")
    else:
        total = 0
        recap_wa = ""
        for item_id, details in list(st.session_state.cart.items()):
            subtotal = details['prix'] * details['qty']
            total += subtotal
            recap_wa += f"- {details['nom']} x{details['qty']}\n"
            
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{details['nom']}**")
            c2.write(f"x{details['qty']}")
            if c3.button("🗑️", key=f"del_{item_id}"):
                del st.session_state.cart[item_id]
                st.rerun()
        
        st.markdown(f"### Total : {int(total)} FCFA")
        
        st.divider()
        pay_method = st.selectbox("Mode de paiement", ["Wave", "Orange Money", "Espèces"])
        info_livraison = st.text_input("Adresse de livraison ou N° Table")

        if pay_method in ["Wave", "Orange Money"]:
            qr = segno.make(NUMERO_PAYEMENT)
            out = BytesIO()
            qr.save(out, kind='png', scale=10)
            st.image(out.getvalue(), width=200, caption=f"Scannez pour payer {int(total)} F")

        if st.button("🚀 VALIDER LA COMMANDE"):
            if not info_livraison:
                st.error("Précisez l'adresse ou la table.")
            else:
                # INSERTION SQLITE SÉCURISÉE
                conn = get_connection()
                conn.cursor().execute(
                    'INSERT INTO commandes (articles, total, paiement, detail) VALUES (?,?,?,?)', 
                    (recap_wa, total, pay_method, info_livraison)
                )
                conn.commit()
                
                msg = f"🥘 *COMMANDE*\n{recap_wa}\n💰 TOTAL: {int(total)} F\n💳 PAIEMENT: {pay_method}\n📍 LIEU: {info_livraison}"
                link = f"https://wa.me/{NUMERO_WHATSAPP}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{link}" target="_blank" class="btn-whatsapp">✅ ENVOYER SUR WHATSAPP</a>', unsafe_allow_html=True)

# --- PAGE 4: ADMIN ---
elif page == "Admin":
    if st.text_input("Code Secret", type="password") == ADMIN_PASSWORD:
        tab1, tab2 = st.tabs(["Ajouter Plat", "Commandes"])
        with tab1:
            with st.form("add_form", clear_on_submit=True):
                n = st.text_input("Nom"); p = st.number_input("Prix", step=500); i = st.text_input("Lien Image URL")
                if st.form_submit_button("Ajouter"):
                    get_connection().cursor().execute('INSERT INTO menu (nom, prix, img) VALUES (?,?,?)', (n,p,i)).connection.commit()
                    st.success("Plat ajouté !"); st.rerun()
        with tab2:
            df_c = pd.read_sql('SELECT * FROM commandes ORDER BY id DESC', get_connection())
            st.dataframe(df_c)