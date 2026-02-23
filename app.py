import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse

# ==========================================
# 1. CONFIGURATION DU RESTAURANT
# ==========================================
st.set_page_config(
    page_title="Menu Express Mboro", 
    page_icon="🥘", 
    layout="wide", 
    initial_sidebar_state="collapsed" # Menu caché par défaut (style mobile)
)

# 🔴 TES NUMÉROS (À MODIFIER SI BESOIN)
NUMERO_WHATSAPP = "221778615900"     # Pour recevoir les commandes
NUMERO_MARCHAND_WAVE = "221778615900" # Pour le lien de paiement Wave

# MOT DE PASSE ADMIN
try:
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except:
    ADMIN_PASSWORD = "admin" # Mot de passe par défaut si non configuré sur Streamlit Cloud

# ==========================================
# 2. BASE DE DONNÉES (SÉCURISÉE)
# ==========================================
def get_connection():
    # On utilise la v4 pour être sûr de repartir sur une base propre sans erreurs
    return sqlite3.connect('menu_express_v4.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Table pour les plats
    c.execute('''CREATE TABLE IF NOT EXISTS menu 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, prix REAL, img TEXT)''')
    # Table pour l'historique des commandes
    c.execute('''CREATE TABLE IF NOT EXISTS commandes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, articles TEXT, total REAL, 
                  paiement TEXT, detail TEXT, date DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()

init_db()

# ==========================================
# 3. GESTION DU PANIER (INTELLIGENT)
# ==========================================
if 'cart' not in st.session_state:
    st.session_state.cart = {} # Utilisation d'un dictionnaire pour gérer les quantités sans bug

def add_to_cart(item_id, nom, prix):
    item_id = str(item_id)
    if item_id in st.session_state.cart:
        st.session_state.cart[item_id]['qty'] += 1
    else:
        st.session_state.cart[item_id] = {'nom': nom, 'prix': prix, 'qty': 1}
    st.toast(f"✅ {nom} ajouté au panier !")

# ==========================================
# 4. DESIGN & STYLE CSS
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #0c0c0c; color: white; }
    .plat-card { background:#1a1a1a; border-radius:15px; border: 1px solid #333; margin-bottom:20px; overflow: hidden; }
    .btn-whatsapp { display: block; width: 100%; background-color: #25D366; color: white !important; text-align: center; padding: 15px; border-radius: 12px; font-weight: bold; text-decoration: none; margin-top: 20px;}
    .pay-btn-wave { display: block; width: 100%; background-color: #0096ff; color: white !important; text-align: center; padding: 15px; border-radius: 12px; font-weight: bold; text-decoration: none; margin: 10px 0; }
    .pay-btn-om { display: block; width: 100%; background-color: #ff6600; color: white !important; text-align: center; padding: 15px; border-radius: 12px; font-weight: bold; text-decoration: none; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 5. NAVIGATION LATÉRALE
# ==========================================
# Calcul du nombre d'articles dans le panier
nb_articles = sum(item['qty'] for item in st.session_state.cart.values())

with st.sidebar:
    st.title("🍔 Menu Express")
    page = st.radio(
        "Navigation", 
        ["Accueil", "La Carte", f"🛒 Mon Panier ({nb_articles})", "🔐 Admin"]
    )
    st.write("---")
    st.write("📞 Service Client : 77 861 59 00")

# ==========================================
# 6. PAGES DE L'APPLICATION
# ==========================================

# --- PAGE : ACCUEIL ---
if page == "Accueil":
    try:
        st.image("https://images.unsplash.com/photo-1504674900247-0877df9cc836?q=80&w=2070", use_container_width=True)
    except:
        pass
    st.markdown("<h1 style='text-align: center; color: #d4af37;'>Menu Express Mboro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Votre fast-food et restaurant digital. Commandez en un clic !</p>", unsafe_allow_html=True)

# --- PAGE : LA CARTE ---
elif page == "La Carte":
    st.header("🍴 Notre Menu")
    df_menu = pd.read_sql('SELECT * FROM menu', get_connection())
    
    if df_menu.empty:
        st.info("Le menu est en cours de préparation. Revenez vite !")
    else:
        for _, row in df_menu.iterrows():
            col_img, col_txt = st.columns([1, 2])
            with col_img:
                img_url = row['img'] if row['img'] else "https://via.placeholder.com/150?text=Plat"
                try:
                    st.image(img_url, use_container_width=True)
                except:
                    st.image("https://via.placeholder.com/150?text=Image+Indisponible", use_container_width=True)
            with col_txt:
                st.subheader(row['nom'])
                st.markdown(f"<h3 style='color: #d4af37; margin-top: -10px;'>{int(row['prix'])} FCFA</h3>", unsafe_allow_html=True)
                st.button(f"Ajouter au panier", key=f"btn_{row['id']}", 
                          on_click=add_to_cart, args=(row['id'], row['nom'], row['prix']), use_container_width=True)
            st.divider()

# --- PAGE : PANIER & PAIEMENT ---
elif "Panier" in page:
    st.header("🛒 Votre Commande")
    
    if not st.session_state.cart:
        st.info("Votre panier est vide pour le moment.")
    else:
        total = 0
        recap_commande = ""
        
        # Affichage des articles
        for item_id, details in list(st.session_state.cart.items()):
            subtotal = details['prix'] * details['qty']
            total += subtotal
            recap_commande += f"- {details['nom']} (x{details['qty']})\n"
            
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{details['nom']}**")
            c2.write(f"x{details['qty']}")
            if c3.button("🗑️", key=f"del_{item_id}"):
                del st.session_state.cart[item_id]
                st.rerun()
        
        st.markdown(f"<h2 style='text-align: right; color: #d4af37;'>Total : {int(total)} FCFA</h2>", unsafe_allow_html=True)
        st.divider()
        
        # Logistique et Paiement
        st.subheader("📍 Informations de Livraison")
        details_livraison = st.text_input("Votre adresse de livraison ou N° de table :", placeholder="Ex: Quartier Escale, Maison Diop...")
        
        st.subheader("💳 Mode de Paiement")
        pay_method = st.radio("Choisissez comment payer :", ["Wave", "Orange Money", "Espèces à la livraison"], horizontal=True)

        # Affichage des liens dynamiques selon le choix
        if pay_method == "Wave":
            lien_wave = f"https://wave.com/pay/{NUMERO_MARCHAND_WAVE}"
            st.markdown(f"""
                <div style="background:#f0f9ff; padding:20px; border-radius:15px; text-align:center; margin-top: 10px;">
                    <p style="color: black;">Appuyez sur le bouton pour ouvrir Wave et payer <b>{int(total)} F</b></p>
                    <a href="{lien_wave}" target="_blank" class="pay-btn-wave">📱 PAYER DIRECTEMENT AVEC WAVE</a>
                    <p style="font-size:0.8rem; color:#666; margin-top:10px;">Une fois le paiement fait, validez votre commande ci-dessous.</p>
                </div>
            """, unsafe_allow_html=True)

        elif pay_method == "Orange Money":
            st.markdown(f"""
                <div style="background:#fff5ee; padding:20px; border-radius:15px; text-align:center; margin-top: 10px;">
                    <p style="color: black;">Appuyez sur le bouton pour ouvrir votre clavier téléphonique</p>
                    <a href="tel:#144#39#" class="pay-btn-om">📱 PAYER AVEC ORANGE MONEY</a>
                    <p style="font-size:0.8rem; color:#666; margin-top:10px;">Composez le code pour envoyer <b>{int(total)} F</b>, puis validez ci-dessous.</p>
                </div>
            """, unsafe_allow_html=True)

        # Bouton final
        st.write("---")
        if st.button("🚀 VALIDER MA COMMANDE", use_container_width=True):
            if not details_livraison:
                st.error("⚠️ Veuillez entrer votre adresse de livraison ou votre numéro de table.")
            else:
                # Sauvegarde dans la base de données
                conn = get_connection()
                conn.cursor().execute(
                    'INSERT INTO commandes (articles, total, paiement, detail) VALUES (?,?,?,?)', 
                    (recap_commande, total, pay_method, details_livraison)
                )
                conn.commit()
                
                # Génération du lien WhatsApp
                msg_whatsapp = f"🥘 *NOUVELLE COMMANDE - MENU EXPRESS*\n\n*Plats :*\n{recap_commande}\n💰 *TOTAL :* {int(total)} FCFA\n💳 *PAIEMENT :* {pay_method}\n📍 *ADRESSE :* {details_livraison}"
                lien_whatsapp = f"https://wa.me/{NUMERO_WHATSAPP}?text={urllib.parse.quote(msg_whatsapp)}"
                
                st.success("Commande enregistrée ! Appuyez sur le bouton vert pour nous l'envoyer.")
                st.markdown(f'<a href="{lien_whatsapp}" target="_blank" class="btn-whatsapp">📲 ENVOYER LE REÇU SUR WHATSAPP</a>', unsafe_allow_html=True)

# --- PAGE : ADMIN ---
elif page == "Admin":
    st.header("🔐 Espace Gérant")
    if st.text_input("Code Secret", type="password") == ADMIN_PASSWORD:
        st.success("Accès autorisé")
        
        tab_ajout, tab_menu, tab_histo = st.tabs(["➕ Ajouter Plat", "📋 Gérer le Menu", "📦 Commandes"])
        
        with tab_ajout:
            with st.form("add_form", clear_on_submit=True):
                nom_plat = st.text_input("Nom du plat")
                prix_plat = st.number_input("Prix (FCFA)", step=500, min_value=0)
                img_plat = st.text_input("Lien de l'image (URL Google Images/Unsplash)")
                
                if st.form_submit_button("Enregistrer le plat"):
                    conn = get_connection()
                    conn.cursor().execute('INSERT INTO menu (nom, prix, img) VALUES (?,?,?)', (nom_plat, prix_plat, img_plat))
                    conn.commit()
                    st.success(f"{nom_plat} ajouté avec succès !")
                    st.rerun()
                    
        with tab_menu:
            df_m = pd.read_sql('SELECT * FROM menu', get_connection())
            for _, r in df_m.iterrows():
                c1, c2, c3 = st.columns([1, 3, 1])
                c2.write(f"**{r['nom']}** - {int(r['prix'])} F")
                if c3.button("🗑️ Supprimer", key=f"del_plat_{r['id']}"):
                    conn = get_connection()
                    conn.cursor().execute('DELETE FROM menu WHERE id=?', (r['id'],))
                    conn.commit()
                    st.rerun()
                    
        with tab_histo:
            if st.button("🔄 Actualiser les commandes"):
                st.rerun()
            df_c = pd.read_sql('SELECT * FROM commandes ORDER BY id DESC', get_connection())
            st.dataframe(df_c, use_container_width=True)
