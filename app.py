import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse

# ==========================================
# 1. CONFIGURATION & NAVIGATION STABLE
# ==========================================
st.set_page_config(page_title="Teranga Gourmet", page_icon="🍽️", layout="wide")

# Initialisation critique pour bloquer la page actuelle
if "page" not in st.session_state:
    st.session_state.page = "🏠 Accueil"
if "cart" not in st.session_state:
    st.session_state.cart = {}

# Fonction pour changer de page sans réinitialisation sauvage
def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# ==========================================
# 2. BASE DE DONNÉES (AUTO-SYNC)
# ==========================================
def get_db():
    conn = sqlite3.connect("teranga_final_v9.db", check_same_thread=False)
    return conn

db = get_db()
db.execute("CREATE TABLE IF NOT EXISTS menu (id INTEGER PRIMARY KEY, nom TEXT, prix REAL, img TEXT, stock INTEGER)")
db.execute("CREATE TABLE IF NOT EXISTS commandes (id INTEGER PRIMARY KEY, articles TEXT, total REAL, detail TEXT, mode TEXT)")
db.commit()

# ==========================================
# 3. SIDEBAR (FORCÉE PAR L'ÉTAT)
# ==========================================
with st.sidebar:
    st.title("⭐ Teranga Gourmet")
    pages = ["🏠 Accueil", "📋 La Carte", "🛒 Panier", "⚙️ Admin"]
    # On force l'index pour que le bouton radio suive st.session_state.page
    current_index = pages.index(st.session_state.page) if st.session_state.page in pages else 0
    
    choice = st.radio("Menu", pages, index=current_index, key="nav_radio")
    
    # Si l'utilisateur clique physiquement sur la sidebar, on met à jour l'état
    if choice != st.session_state.page:
        st.session_state.page = choice
        st.rerun()

# ==========================================
# 4. PAGE : ACCUEIL PRO
# ==========================================
if st.session_state.page == "🏠 Accueil":
    st.markdown("""
    <div style="background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
    url('https://images.unsplash.com'); 
    background-size: cover; padding: 100px 20px; text-align: center; border-radius: 20px; border: 2px solid #d4af37;">
        <h1 style="color: #d4af37; font-size: 50px;">TERANGA GOURMET MBORO</h1>
        <p style="font-size: 20px; color: white;">L'excellence de la cuisine Sénégalaise</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("🚀 VOIR LE MENU ET COMMANDER", use_container_width=True):
        go_to("📋 La Carte")

# ==========================================
# 5. PAGE : LA CARTE (AVEC STOCK)
# ==========================================
elif st.session_state.page == "📋 La Carte":
    st.header("🍴 Notre Carte")
    df = pd.read_sql("SELECT * FROM menu", get_db())
    
    if df.empty:
        st.warning("Le menu est vide. Ajoutez des plats dans l'onglet Admin.")
    else:
        cols = st.columns(3)
        for idx, row in df.iterrows():
            with cols[idx % 3]:
                st.image(row['img'], use_container_width=True)
                st.subheader(row['nom'])
                st.markdown(f"**{int(row['prix'])} FCFA**")
                st.caption(f"Stock restant : {row['stock']}")
                
                if row['stock'] > 0:
                    if st.button(f"Ajouter {row['nom']}", key=f"add_{row['id']}"):
                        cid = str(row['id'])
                        if cid in st.session_state.cart:
                            st.session_state.cart[cid]['qty'] += 1
                        else:
                            st.session_state.cart[cid] = {'nom': row['nom'], 'prix': row['prix'], 'qty': 1, 'db_id': row['id']}
                        st.toast(f"✅ {row['nom']} ajouté au panier")
                else:
                    st.button("RUPTURE DE STOCK", disabled=True, key=f"out_{row['id']}")

# ==========================================
# 6. PAGE : PANIER & TUNNEL DE COMMANDE
# ==========================================
elif st.session_state.page == "🛒 Panier":
    st.header("🛒 Votre Panier")
    
    if not st.session_state.cart:
        st.info("Votre panier est vide.")
        if st.button("Retourner à la carte"): go_to("📋 La Carte")
    else:
        total = 0
        summary = ""
        for k, v in list(st.session_state.cart.items()):
            sub = v['prix'] * v['qty']
            total += sub
            summary += f"- {v['nom']} x{v['qty']}\n"
            c1, c2, c3 = st.columns([3,1,1])
            c1.write(f"**{v['nom']}**")
            c2.write(f"{int(sub)} F")
            if c3.button("🗑️", key=f"del_{k}"):
                del st.session_state.cart[k]
                st.rerun()
        
        st.divider()
        st.subheader(f"Total : {int(total)} FCFA")

        # LOGIQUE DE RÉCEPTION
        mode = st.radio("Comment souhaitez-vous recevoir votre commande ?", ["🚚 Livraison", "🏪 Sur place"], horizontal=True)
        
        final_detail = ""
        is_valid = False

        if mode == "Sur place":
            table = st.text_input("🔢 Numéro de votre table")
            if table:
                final_detail = f"SUR PLACE - Table N°{table}"
                is_valid = True
        else:
            c_tel, c_adr = st.columns(2)
            tel = c_tel.text_input("📞 Téléphone")
            adr = c_adr.text_input("📍 Adresse précise")
            if tel and adr:
                final_detail = f"LIVRAISON - Tel: {tel} | Adr: {adr}"
                is_valid = True

        if is_valid:
            msg_wa = f"COMMANDE TERANGA\n\n{summary}\nTOTAL : {int(total)} F\n\n{final_detail}"
            url_wa = f"https://wa.me{urllib.parse.quote(msg_wa)}"
            
            if st.button("🚀 VALIDER & ENVOYER SUR WHATSAPP", use_container_width=True):
                # 1. Enregistrement DB
                conn = get_db()
                conn.execute("INSERT INTO commandes (articles, total, detail, mode) VALUES (?,?,?,?)",
                             (summary, total, final_detail, mode))
                
                # 2. Mise à jour automatique des stocks
                for k, v in st.session_state.cart.items():
                    conn.execute("UPDATE menu SET stock = stock - ? WHERE id = ?", (v['qty'], v['db_id']))
                conn.commit()
                
                # 3. Reset panier
                st.session_state.cart = {}
                
                # 4. Redirection WhatsApp
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url_wa}">', unsafe_allow_html=True)
                st.success("Redirection vers WhatsApp...")
        else:
            st.warning("⚠️ Remplissez les informations (Table ou Adresse+Tel) pour commander.")

# ==========================================
# 7. ADMIN (AJOUT/SUPPRESSION)
# ==========================================
elif st.session_state.page == "⚙️ Admin":
    pwd = st.sidebar.text_input("Mot de passe", type="password")
    if pwd == "admin123":
        t1, t2 = st.tabs(["Commandes", "Gérer le Menu"])
        with t1:
            df_c = pd.read_sql("SELECT * FROM commandes ORDER BY id DESC", get_db())
            st.dataframe(df_c, use_container_width=True)
            
        with t2:
            st.subheader("Ajouter un plat")
            with st.form("add_p"):
                n = st.text_input("Nom")
                p = st.number_input("Prix", min_value=0)
                i = st.text_input("Lien Image URL")
                s = st.number_input("Stock", min_value=0, value=20)
                if st.form_submit_button("Ajouter"):
                    db.execute("INSERT INTO menu (nom, prix, img, stock) VALUES (?,?,?,?)", (n,p,i,s))
                    db.commit()
                    st.rerun()

            st.divider()
            st.subheader("Supprimer des plats")
            df_m = pd.read_sql("SELECT * FROM menu", get_db())
            for idx, r in df_m.iterrows():
                col1, col2 = st.columns([4,1])
                col1.write(f"**{r['nom']}** ({int(r['prix'])}F)")
                if col2.button("Supprimer", key=f"rm_{r['id']}"):
                    db.execute("DELETE FROM menu WHERE id=?", (r['id'],))
                    db.commit()
                    st.rerun()
    else:
        st.error("Accès Admin requis.")
