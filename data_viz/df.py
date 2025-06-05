import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
from pandas import DataFrame
from PIL import Image

# Configuration de la page
st.set_page_config(
    page_title="Pokémon TCG Pocket",
    page_icon="🃏",
    layout="wide"
)

# Connexion PostgreSQL portable
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'postgres'
DB_USER = 'postgres'


def connect_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER
        )
        return conn
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None
    
def table_wrk_decklists(conn):
    cur = conn.cursor()
    query=cur.execute('Select * From wrk_decklists;')
    rows=cur.fetchall()
    cur.execute("Select COLUMN_NAME from information_schema.columns where table_name = 'wrk_decklists'")
    names = cur.fetchall()
    names_l = []
    for l in names:
        names_l.append(l[0])
    decklists = pd.DataFrame(rows)
    decklists.columns = names_l
    return decklists
    
def table_wrk_cards(conn):
    cur = conn.cursor()
    query=cur.execute('Select * From wrk_cards;')
    rows=cur.fetchall()
    cur.execute("Select COLUMN_NAME from information_schema.columns where table_name = 'wrk_cards'")
    names = cur.fetchall()
    names_l = []
    for l in names:
        names_l.append(l[0])
    cards = pd.DataFrame(rows)
    cards.columns = names_l
    return cards    

def table_wrk_tournements(conn):
    cur = conn.cursor()
    query=cur.execute('Select * From wrk_tournaments;')
    rows=cur.fetchall()
    cur.execute("Select COLUMN_NAME from information_schema.columns where table_name = 'wrk_tournaments'")
    names = cur.fetchall()
    names_l = []
    for l in names:
        names_l.append(l[0])
    tournements = pd.DataFrame(rows)
    tournements.columns = names_l
    return tournements
    
def table_temp_decklist(decklists):
    st.write("Aperçu de la table decklists :")
    if st.checkbox("Afficher la table decklists"):
        st.dataframe(decklists.head(10))
        
def table_temp_cards(cards):
    st.write("Aperçu de la table cartes :")
    if st.checkbox("Afficher la table cards"):
        st.dataframe(cards.head(10))
        
def table_temp_tournaments(tournements):
    st.write("Aperçu de la table tournements :")
    if st.checkbox("Afficher la table tournements"):
        st.dataframe(tournements.head(10))
        
def nb_tournois(decklists):
    nb_tournois = decklists["tournament_id"].unique()
    st.write(f"Nombre de tournois: {len(nb_tournois)}")
    
def graphique_rep_carte_par_categorie(cards):
    option_saison = st.selectbox("Choisissez une saison", cards["set_number_id"].unique())
    # st.bar_chart(cards, x= "set_number_id")
    query1 = """
    SELECT 
        wd.tournament_id, 
        wd.card_name, 
        COUNT(wd.card_name) AS card_count,
        wc.set_number_id 
    FROM 
        wrk_decklists wd
    inner join wrk_cards wc on wd.card_url = wc.url_source 
    WHERE 
        wd.card_type = 'Pokemon'
    GROUP BY 
        wd.tournament_id, wd.card_name,
        wc.set_number_id 
    ORDER BY 
        card_count desc

    """
    nb_carte = pd.read_sql_query(query1, conn)
    query2 = """
    select wd.card_name , wc.set_number_id 
    from wrk_cards wc 
    inner join wrk_decklists wd on wc.url_source = wd.card_url
    """
    saison = pd.read_sql_query(query2, conn)
    
    merged_df = pd.merge(nb_carte, saison, on="card_name", how="outer").fillna(0)
    
    st.write(type(nb_carte))
    # st.bar_chart(nb_carte, x = 
    
# Main app
def main():
    conn = connect_db()
    if conn:
        st.success("Connexion réussie à PostgreSQL Portable !")
        cur = conn.cursor()
        cur.execute("SELECT version();")
        decklists = table_wrk_decklists(conn)
        cards = table_wrk_cards(conn)
        tournements = table_wrk_tournements(conn)
        cur.close()
        conn.close()



#--------------------------------------------------------------------------------------------STYLE CSS-----------------------------------------------------------------------------------------------------------#
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(#c9def4, #dfd5e4, #f5ccd4);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #333333;
    }
    h1, h2, h3 {
        color: #EF5350; /* rouge Pokémon */
        font-weight: 700;
    }
    .description {
        font-size: 18px;
        line-height: 1.6;
        margin-bottom: 20px;
    }
    .footer {
        text-align: center;
        color: gray;
        font-size: 14px;
        margin-top: 50px;
    }
    
    /* Sélecteur CSS pour la sidebar */
    [data-testid="stSidebar"] {
        background-color: #edf2fb !important;  
        color: black !important;
    }
    
    /* Chaque onglet (la "case" avec le titre) */
    [data-testid="stTab"] {
        background-color: none;
        color: black ;
        padding: 12px 26px !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    
    [aria-selected="true"] {
        background-color: #EF5350 !important;
        color: white !important;
        border: #EF5350 !important;
    }
    
    [data-baseweb="tab-highlight"] {
        background-color: #C3C6D7 !important;
    }
            
    /* Cible le conteneur metric principal */
    div[data-testid="stMetric"] {
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }

    /* Cible le label du metric */
    div[data-testid="stMetricLabel"] >  {
        font-size: 22px;
    }

    /* Cible la valeur du metric*/
    div[data-testid="stMetricValue"] > div:nth-child(1) {
        font-size: 40px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

#--------------------------------------------------------------------------------------------HEAD-----------------------------------------------------------------------------------------------------------#
st.title("Pokémon TCG Pocket")
st.markdown("Par Sergina Bakala, Kiran Derennes, Ifig Le Gonidec, Mattéo Rouanne ")

#-------------------------------------------------------------------------------------------SIDEBAR-----------------------------------------------------------------------------------------------------------#
conn = connect_db()
if conn:
    cur = conn.cursor()
    cur.execute("SELECT version();")
    decklists = table_wrk_decklists(conn)
    cards = table_wrk_cards(conn)
    tournements = table_wrk_tournements(conn)
st.sidebar.title("Filtres")
st.sidebar.markdown("## Tournois")
st.sidebar.slider("Nombre de joueur", 0, 100, value=(0, 100), key="slider_nb_joueur")
st.sidebar.multiselect("Nom de tournois", tournements["tournament_name"], key="multiselect_nom_tournois")
st.sidebar.markdown("## Decks")
choix_type = st.sidebar.radio("Type de deck", ["colorless", "water", "fire", "grass", "fighting", "electric", "psychic", "steel", "dark", "dragon"], key="type_deck")
st.sidebar.slider("Win-Rate", 0, 100, value=(0, 100), key="slider_winrate")

#--------------------------------------------------------------------------------------------ONGLETS-----------------------------------------------------------------------------------------------------------#
tab1, tab2, tab3= st.tabs(["Présentation", "⚔️ Stratégies", "Détails des decks"])

with tab1: 
    ## Onglet presentation
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(
            "GALqQYXtpbYyZRsX5ftVNdSCoN1980aiWtrBahZr.jpg",
            caption="Pokémon TCG Pocket",
            width=800,
        )

    ### Description du jeu
    st.markdown("""
    <div class="description">
    Pokémon Trading Card Game Pocket (souvent abrégé en Pokémon TCG Pocket) est une adaptation mobile gratuite du jeu de cartes à collectionner Pokémon (TCG), développée par Creatures Inc. et DeNA, et publiée par The Pokémon Company.
    Dans ce jeu, les joueurs construisent des decks composés d’ensembles de cartes et s’affrontent en ligne.
    </div>
    """, unsafe_allow_html=True)

    ### Fonctionnalités clés
    st.subheader("Objectif")
    st.markdown("""
    Vous avez été mandaté par votre client pour réaliser une analyse du métagame de ce jeu. Votre client souhaite savoir quelles cartes ont le taux de victoire le plus élevé, quelles cartes fonctionnent bien ensemble dans un même deck, quelles cartes utiliser contre les stratégies populaires, si certaines de ces tendances ont évolué depuis le lancement du jeu, ainsi que toute autre information utile que vous pouvez extraire des données. 
    """)

    ### Appel à l'action
    st.markdown("---")
    st.markdown("### Lien vers l'application")
    st.markdown("[📱 Télécharger sur Google Play](https://play.google.com/store/apps/details?id=jp.pokemon.pokemontcgp)")
    st.markdown("[🍎 Télécharger sur l'App Store](https://apps.apple.com/app/pokemon-tcgp-pocket/id1563916495)")

    ### Footer discret
    st.markdown("---")
    st.markdown('<div class="footer">© 2025 Pokémon TCGP Pocket - Application non officielle</div>', unsafe_allow_html=True)

with tab2: 
    ## Onglet strategie
    st.write("Téma la strat")
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT version();")
        decklists = table_wrk_decklists(conn)
        cards = table_wrk_cards(conn)
        tournements = table_wrk_tournements(conn)
        table_temp_decklist(decklists)
        table_temp_cards(cards)
        table_temp_tournaments(tournements)
        nb_tournois(decklists)
        graphique_rep_carte_par_categorie(cards)
        cur.close()
        conn.close() 

with tab3:
    ## Onglet détail deck
    option = ["bfsd", "55", "ddg"]
    st.selectbox("Rechercher un deck",option)
    col1, col2, col3= st.columns(3)
    with col1:
        st.image(
                "https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/pocket/A1a/A1a_017_EN.webp",
                caption="Carte principal du deck",
                width = 300
                
            )
    images_type = {
    "colorless": "colorless_energy_card_vector_symbol_by_biochao_dezrwzj-pre.png",
    "water": "water_energy_card_vector_symbol_by_biochao_dezrx5f-pre.png",
    "fire": "fire_energy_card_vector_symbol_by_biochao_dezrx2m-pre.png",
    "grass": "grass_energy_card_vector_symbol_by_biochao_dezrx3b-pre.png",
    "fighting": "fighting_energy_card_vector_symbol_by_biochao_dezrx1z-pre.png",
    "electric": "electric_energy_card_vector_symbol_by_biochao_dezrx16-pre.png",
    "psychic": "psychic_energy_card_vector_symbol_by_biochao_dezrx4c-pre.png",
    "steel": "steel_energy_card_vector_symbol_by_biochao_dezrx4z-pre.png",
    "dark": "dark_energy_card_vector_symbol_by_biochao_dezrx06-pre.png",
    "dragon": "dragon_energy_card_vector_symbol_by_biochao_dezrx0m-pre.png"
    }
    with col2:
        st.image(
                images_type[choix_type],
                caption="Type du deck",
                width = 300
                
            )
    with col3:
        st.metric("Win-Rate", 0.74)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

if __name__ == "__main__":
    main()

