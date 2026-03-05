import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse
from datetime import datetime

# ==========================================
# 1. CONFIGURATION NATIONALE & STYLE
# ==========================================
st.set_page_config(page_title="Teranga Gourmet Mboro", page_icon="🇸🇳", layout="wide")

# Couleurs du Sénégal revisité en mode Luxe
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com');
    
    .stApp { background-color: #040a04; color: #f4f4f4; font-family: 'Poppins', sans-serif; }
    
    /* Hero Banner */
    .hero {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url('https://images.unsplash.com');
        background-size: cover; padding: 80px 20px; text-align: center;
        border-radius: 30px; border: 2px solid #d4af37; margin-bottom: 30px;
    }
    .hero h1 { font-family: 'Playfair Display', serif; color: #d4af37; font-size: 55px; margin-bottom: 10px; }
    
    /* Carte Produit */
    .product-card {
        background: #0d1a0d; border-radius: 20px; border: 1px solid #1a331a;
        padding: 0px; margin-bottom: 20px; transition: 0.4s;
    }
    .product-card:hover { border-color: #d4af37; transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.5); }
    
    .price-tag { background: #d4af37; color: black; padding: 5px 15px; border-radius: 50px; font-weight: bold; }
    
    /* Boutons */
    div.stButton > button {
        background: linear-gradient(90deg, #d4af37, #b8860b) !important;
        color: black !important; border: none !important; border-radius: 12px !important;
        font-weight: 600 !important; height: 45px; transition: 0.3s;
    }
    div.stButton > button:hover { transform: scale(1.02); opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MOTEUR DE DONNÉES (PERSISTANT)
# ==========================================
def init_db():
    conn = sqlite3.connect("teranga_gourmet_v11.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS menu 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, prix REAL, img TEXT, stock INTEGER)""")
    c.execute("""CREATE TABLE IF NOT EXISTS commandes 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, items TEXT, total REAL, detail TEXT, mode TEXT, date DATETIME)""")
    conn.commit()
    return conn

db_conn = init_db()

# Initialisation Session State
if "page" not in st.session_state: st.session_state.page = "🏠 Accueil"
if "cart" not in st.session_state: st.session_state.cart = {}

# ==========================================
# 3. LOGIQUE DE NAVIGATION (ANTI-BUG)
# ==========================================
def navigate(target):
    st.session_state.page = target
    st.rerun()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com", width=100)
    st.title("Teranga Menu")
    nb_panier = sum(v['qty'] for v in st.session_state.cart.values())
    
    nav = st.radio("Aller vers", ["🏠 Accueil", "📋 La Carte", f"🛒 Panier ({nb_panier})", "⚙️ Administration"], 
                   index=["🏠 Accueil", "📋 La Carte", "🛒 Panier", "⚙️ Administration"].index(st.session_state.page[:2] if "(" in st.session_state.page else st.session_state.page[:2]) if any(x in st.session_state.page for x in ["Accueil", "Carte", "Panier", "Admin"]) else 0)
    
    # Correction dynamique du nom de page pour le radio
    if "🏠 Accueil" in nav: st.session_state.page = "🏠 Accueil"
    elif "📋 La Carte" in nav: st.session_state.page = "📋 La Carte"
    elif "🛒 Panier" in nav: st.session_state.page = "🛒 Panier"
    elif "⚙️" in nav: st.session_state.page = "⚙️ Administration"

# ==========================================
# 4. PAGE : ACCUEIL (PRO & PATRIOTE)
# ==========================================
if st.session_state.page == "🏠 Accueil":
    st.markdown(f"""
    <div class="hero">
        <h1>TERANGA GOURMET</h1>
        <p style="font-size: 20px; opacity: 0.9;">L'excellence de la Gastronomie Sénégalaise au cœur de Mboro</p>
        <div style="margin-top:20px;">
            <span style="border: 1px solid #d4af37; padding: 8px 20px; border-radius: 50px; font-size: 14px;">📍 Quartier Escale, Mboro</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🥣 Tradition")
        st.write("Recettes authentiques transmises de génération en génération.")
    with col2:
        st.markdown("### 🚚 Mboro Express")
        st.write("Livraison chaude et rapide partout dans la ville.")
    with col3:
        st.markdown("### 💎 Prestige")
        st.write("Un service de qualité digne de la légendaire Teranga.")

    st.write("")
    if st.button("✨ DÉCOUVRIR NOTRE CARTE", use_container_width=True):
        navigate("📋 La Carte")

# ==========================================
# 5. PAGE : LA CARTE (VISUEL PREMIUM)
# ==========================================
elif st.session_state.page == "📋 La Carte":
    st.markdown("<h2 style='text-align:center; color:#d4af37;'>Nos Saveurs du Jour</h2>", unsafe_allow_html=True)
    df = pd.read_sql("SELECT * FROM menu", db_conn)
    
    if df.empty:
        st.info("Le Chef prépare les fourneaux. Revenez dans quelques instants.")
    else:
        for i in range(0, len(df), 3):
            cols = st.columns(3)
            for j, row in df.iloc[i:i+3].iterrows():
                with cols[j % 3]:
                    st.markdown(f"""
                    <div class="product-card">
                        <img src="{row['img']}" style="width:100%; border-radius:20px 20px 0 0; height:220px; object-fit:cover;">
                        <div style="padding:20px;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <h3 style="margin:0;">{row['nom']}</h3>
                                <span class="price-tag">{int(row['prix'])} F</span>
                            </div>
                            <p style="color:#888; font-size:13px; margin-top:10px;">Disponibilité : {row['stock']} portions</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if row['stock'] > 0:
                        if st.button(f"Sélectionner {row['nom']}", key=f"p_{row['id']}", use_container_width=True):
                            pid = str(row['id'])
                            if pid in st.session_state.cart: st.session_state.cart[pid]['qty'] += 1
                            else: st.session_state.cart[pid] = {'nom': row['nom'], 'prix': row['prix'], 'qty': 1, 'id': row['id']}
                            st.toast(f"Ajouté : {row['nom']}")
                            st.rerun()
                    else:
                        st.button("Épuisé", disabled=True, key=f"sold_{row['id']}", use_container_width=True)

# ==========================================
# 6. PAGE : PANIER & TUNNEL DE COMMANDE
# ==========================================
elif st.session_state.page == "🛒 Panier":
    st.title("🛒 Votre Sélection")
    
    if not st.session_state.cart:
        st.warning("Votre panier attend vos envies gourmandes.")
        if st.button("⬅️ Retourner au Menu"): navigate("📋 La Carte")
    else:
        total = 0
        detail_msg = ""
        for k, v in list(st.session_state.cart.items()):
            sub = v['prix'] * v['qty']
            total += sub
            detail_msg += f"• {v['nom']} (x{v['qty']})\n"
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{v['nom']}**")
            c2.write(f"{int(sub)} F")
            if c3.button("❌", key=f"rm_{k}"):
                del st.session_state.cart[k]
                st.rerun()
        
        st.markdown(f"<h2 style='text-align:right; color:#d4af37;'>Total : {int(total)} FCFA</h2>", unsafe_allow_html=True)
        st.divider()

        # TUNNEL DE COMMANDE PRÉCIS
        st.subheader("📍 Détails de la réception")
        mode_choisi = st.selectbox("Où dégustez-vous ?", ["-- Choisir un mode --", "🏪 Sur place (Restaurant)", "🚚 Livraison à domicile (Mboro)"])
        
        final_info = ""
        is_ready = False

        if "Sur place" in mode_choisi:
            table_num = st.text_input("🔢 Numéro de votre table", placeholder="Ex: Table 04")
            if table_num:
                final_info = f"SUR PLACE - Table N°{table_num}"
                is_ready = True
        elif "Livraison" in mode_choisi:
            col_t, col_a = st.columns(2)
            tel = col_t.text_input("📞 Numéro de Téléphone")
            adr = col_a.text_input("📍 Quartier / Adresse précise")
            if tel and adr:
                final_info = f"LIVRAISON\n📞 Tel: {tel}\n📍 Adr: {adr}"
                is_ready = True

        if is_ready:
            # Préparation WhatsApp
            wa_text = f"*TERANGA GOURMET - COMMANDE*\n\n{detail_msg}\n*TOTAL : {int(total)} FCFA*\n\n*INFO CLIENT :*\n{final_info}"
            wa_url = f"https://wa.me{urllib.parse.quote(wa_text)}"
            
            if st.button("🚀 VALIDER & ENVOYER SUR WHATSAPP", use_container_width=True):
                # Enregistrement & Stock
                c = db_conn.cursor()
                c.execute("INSERT INTO commandes (items, total, detail, mode, date) VALUES (?,?,?,?,?)",
                           (detail_msg, total, final_info, mode_choisi, datetime.now()))
                for k, v in st.session_state.cart.items():
                    c.execute("UPDATE menu SET stock = stock - ? WHERE id = ?", (v['qty'], v['id']))
                db_conn.commit()
                
                # Reset & Redirect
                st.session_state.cart = {}
                st.markdown(f'<meta http-equiv="refresh" content="0; url={wa_url}">', unsafe_allow_html=True)
                st.success("Commande envoyée !")
        else:
            if mode_choisi != "-- Choisir un mode --":
                st.warning("⚠️ Merci de compléter les informations pour confirmer.")

# ==========================================
# 7. PAGE : ADMIN (CONTRÔLE TOTAL)
# ==========================================
elif "Admin" in st.session_state.page:
    st.title("⚙️ Gestion Teranga")
    code = st.sidebar.text_input("Code d'accès", type="password")
    
    if code == "admin123":
        tab1, tab2 = st.tabs(["📊 Commandes", "🍱 Menu & Stocks"])
        
        with tab1:
            cmd_df = pd.read_sql("SELECT * FROM commandes ORDER BY date DESC", db_conn)
            st.dataframe(cmd_df, use_container_width=True)
        
        with tab2:
            with st.expander("➕ AJOUTER UN NOUVEAU PLAT"):
                with st.form("new_dish"):
                    n = st.text_input("Nom du plat")
                    p = st.number_input("Prix", min_value=0)
                    i = st.text_input("Lien Image URL")
                    s = st.number_input("Stock initial", min_value=0, value=20)
                    if st.form_submit_button("Sauvegarder"):
                        db_conn.execute("INSERT INTO menu (nom, prix, img, stock) VALUES (?,?,?,?)", (n,p,i,s))
                        db_conn.commit()
                        st.rerun()
            
            st.write("### Plats en vente")
            df_m = pd.read_sql("SELECT * FROM menu", db_conn)
            for idx, r in df_m.iterrows():
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.write(f"**{r['nom']}** | {int(r['prix'])}F | Stock: {r['stock']}")
                if col2.button("Modifier", key=f"edit_{r['id']}"):
                    st.info("Fonction bientôt disponible")
                if col3.button("Supprimer", key=f"del_{r['id']}"):
                    db_conn.execute("DELETE FROM menu WHERE id=?", (r['id'],))
                    db_conn.commit()
                    st.rerun()
    else:
        st.error("Accès Réservé")
