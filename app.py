import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse

# ==========================================
# CONFIGURATION & ETAT DE SESSION
# ==========================================
st.set_page_config(page_title="Teranga Gourmet", page_icon="🍽️", layout="wide")

# Initialisation des états pour éviter les retours à l'accueil
if "page" not in st.session_state:
    st.session_state.page = "🏠 Accueil"
if "cart" not in st.session_state:
    st.session_state.cart = {}

# ==========================================
# BASE DE DONNÉES
# ==========================================
def get_db():
    conn = sqlite3.connect("teranga_v8.db", check_same_thread=False)
    return conn

conn = get_db()
conn.execute("CREATE TABLE IF NOT EXISTS menu (id INTEGER PRIMARY KEY, nom TEXT, prix REAL, img TEXT, stock INTEGER)")
conn.execute("CREATE TABLE IF NOT EXISTS commandes (id INTEGER PRIMARY KEY, articles TEXT, total REAL, detail TEXT, type TEXT, statut TEXT DEFAULT 'En attente')")
conn.commit()

# ==========================================
# NAVIGATION LATERALE
# ==========================================
with st.sidebar:
    st.title("Teranga Gourmet")
    nb_panier = sum(v['qty'] for v in st.session_state.cart.values())
    choice = st.radio("Navigation", ["🏠 Accueil", "📋 La Carte", f"🛒 Panier ({nb_panier})", "⚙️ Admin"], 
                      index=["🏠 Accueil", "📋 La Carte", f"🛒 Panier ({nb_panier})", "⚙️ Admin"].index(st.session_state.page) if st.session_state.page in ["🏠 Accueil", "📋 La Carte", "⚙️ Admin"] else 0)
    st.session_state.page = choice

# ==========================================
# ACCUEIL PRO
# ==========================================
if "Accueil" in st.session_state.page:
    st.markdown("""
    <div style="background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('https://images.unsplash.com'); 
    background-size: cover; padding: 120px 20px; text-align: center; border-radius: 25px; color: white; border: 2px solid #d4af37;">
        <h1 style="font-size: 60px; color: #d4af37; margin-bottom: 10px;">TERANGA GOURMET</h1>
        <p style="font-size: 22px; font-weight: 300;">L'excellence culinaire de Mboro, de notre cuisine à votre table.</p>
        <br>
        <p style="color: #d4af37; font-size: 18px;">📍 Mboro - Sénégal | 🕒 11h - 23h</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📖 Consulter le Menu", use_container_width=True):
        st.session_state.page = "📋 La Carte"
        st.rerun()

# ==========================================
# LA CARTE
# ==========================================
elif "La Carte" in st.session_state.page:
    st.header("📋 Notre Sélection")
    df = pd.read_sql("SELECT * FROM menu", get_db())
    
    if df.empty:
        st.info("Le menu est en cours de mise à jour.")
    else:
        cols = st.columns(3)
        for idx, row in df.iterrows():
            with cols[idx % 3]:
                st.markdown(f"""
                <div style="border: 1px solid #333; border-radius: 15px; padding: 10px; background: #111; margin-bottom: 10px;">
                    <img src="{row['img']}" style="width:100%; border-radius:10px; height:200px; object-fit:cover;">
                    <h3 style="color:#d4af37; margin-top:10px;">{row['nom']}</h3>
                    <p style="font-size:20px; font-weight:bold;">{int(row['prix'])} FCFA</p>
                    <p style="color:#888; font-size:12px;">Stock disponible : {row['stock']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if row['stock'] > 0:
                    if st.button(f"Ajouter au panier", key=f"btn_{row['id']}", use_container_width=True):
                        pid = str(row['id'])
                        if pid in st.session_state.cart:
                            st.session_state.cart[pid]['qty'] += 1
                        else:
                            st.session_state.cart[pid] = {'nom': row['nom'], 'prix': row['prix'], 'qty': 1}
                        st.toast(f"✅ {row['nom']} ajouté !")
                else:
                    st.button("Épuisé", disabled=True, key=f"sold_{row['id']}", use_container_width=True)

# ==========================================
# PANIER AVEC TUNNEL DE COMMANDE STRICT
# ==========================================
elif "Panier" in st.session_state.page:
    st.header("🛒 Finaliser ma commande")
    
    if not st.session_state.cart:
        st.warning("Votre panier est vide.")
        if st.button("Retour au menu"):
            st.session_state.page = "📋 La Carte"
            st.rerun()
    else:
        total = 0
        txt_items = ""
        for k, v in list(st.session_state.cart.items()):
            sub = v['prix'] * v['qty']
            total += sub
            txt_items += f"• {v['nom']} (x{v['qty']})\n"
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{v['nom']}**")
            c2.write(f"{int(sub)} F")
            if c3.button("🗑️", key=f"del_{k}"):
                del st.session_state.cart[k]
                st.rerun()
        
        st.divider()
        st.subheader(f"Total à payer : {int(total)} FCFA")

        # CHOIX DU MODE
        mode = st.radio("📍 Mode de service :", ["🚚 Livraison à domicile", "🏪 Sur place (Restaurant)"], horizontal=True)
        
        details = ""
        ready_to_order = False

        if "Livraison" in mode:
            col_tel, col_adr = st.columns(2)
            tel = col_tel.text_input("📞 Numéro de téléphone (Obligatoire)")
            adr = col_adr.text_input("📍 Adresse de livraison (Quartier/Rue)")
            if tel and adr:
                details = f"LIVRAISON\n📞 Tel: {tel}\n📍 Adr: {adr}"
                ready_to_order = True
        else:
            num_table = st.text_input("🔢 Numéro de votre table")
            if num_table:
                details = f"SUR PLACE\n🔢 Table N°: {num_table}"
                ready_to_order = True

        st.divider()
        
        # LE BOUTON UNIQUE DE VALIDATION
        if ready_to_order:
            # On prépare le message WhatsApp
            msg_wa = f"NOUVELLE COMMANDE TERANGA\n\n{txt_items}\n💰 TOTAL : {int(total)} FCFA\n\n{details}"
            encoded_msg = urllib.parse.quote(msg_wa)
            url_whatsapp = f"https://wa.me{encoded_msg}"

            # Lien stylisé en bouton qui déclenche aussi l'enregistrement en DB
            if st.button("🚀 CONFIRMER & ENVOYER SUR WHATSAPP", use_container_width=True):
                # 1. Enregistrement Base de données
                db = get_db()
                db.execute("INSERT INTO commandes (articles, total, detail, type) VALUES (?,?,?,?)",
                           (txt_items, total, details, mode))
                db.commit()
                
                # 2. Vider le panier
                st.session_state.cart = {}
                
                # 3. Ouvrir WhatsApp (via JavaScript)
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url_whatsapp}">', unsafe_allow_html=True)
                st.success("Commande envoyée ! Redirection vers WhatsApp...")
        else:
            st.warning("⚠️ Veuillez remplir vos coordonnées pour débloquer la commande.")

# ==========================================
# ADMIN
# ==========================================
elif "Admin" in st.session_state.page:
    pwd = st.sidebar.text_input("Code Secret", type="password")
    if pwd == "admin123":
        t1, t2 = st.tabs(["📦 Commandes", "🥘 Menu & Stocks"])
        with t1:
            df_orders = pd.read_sql("SELECT * FROM commandes ORDER BY id DESC", get_db())
            st.dataframe(df_orders, use_container_width=True)
        with t2:
            with st.expander("➕ Ajouter un nouveau plat"):
                n = st.text_input("Nom du plat")
                p = st.number_input("Prix", min_value=0)
                i = st.text_input("URL de l'image")
                s = st.number_input("Stock", min_value=0, value=20)
                if st.button("Sauvegarder"):
                    db = get_db()
                    db.execute("INSERT INTO menu (nom, prix, img, stock) VALUES (?,?,?,?)", (n, p, i, s))
                    db.commit()
                    st.success("Plat ajouté !")
                    st.rerun()
            
            st.subheader("Plats actuels")
            df_menu = pd.read_sql("SELECT * FROM menu", get_db())
            for idx, r in df_menu.iterrows():
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{r['nom']}** ({int(r['prix'])}F)")
                if c2.button("Supprimer", key=f"del_menu_{r['id']}"):
                    db = get_db()
                    db.execute("DELETE FROM menu WHERE id=?", (r['id'],))
                    db.commit()
                    st.rerun()
    else:
        st.error("Accès Admin requis.")
