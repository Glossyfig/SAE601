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

# winrate moyen d'une carte par saison, tournois
def analyse_usage_winrate_par_saison(decklists: pd.DataFrame, tournements: pd.DataFrame, win: pd.DataFrame, selected_card: str, selected_deck: str, selected_season):
    # Filtrer sur le deck sélectionné
    df = decklists[decklists['deck'] == selected_deck]
    
    # Fusionner avec tournements pour récupérer la saison (année)
    df = df.merge(tournements[['tournament_id', 'tournament_date_y']], on='tournament_id', how='left')
    
    # Filtrer sur la saison sélectionnée, si spécifiée
    if selected_season is not None:
        df = df[df['tournament_date_y'] == selected_season]
    
    # Filtrer sur la carte sélectionnée
    df_card = df[df['card_name'] == selected_card]
    if df_card.empty:
        return pd.DataFrame()  # Pas de données
    
    # Compter usage par saison
    usage_par_saison = df_card.groupby('tournament_date_y').agg(usage=('deck', 'count')).reset_index()
    
    # Pour calculer le winrate réel moyen par saison,
    # on récupère dans la table win les winrates pour le deck sélectionné par saison
    
    # Filtrer la table win pour garder seulement le deck sélectionné
    df_win = win[win['deck'] == selected_deck]
    
    # Fusionner avec tournements pour avoir la saison
    df_win = df_win.merge(tournements[['tournament_id', 'tournament_date_y']], on='tournament_id', how='left')
    
    # Filtrer sur la saison sélectionnée, si spécifiée
    if selected_season is not None:
        df_win = df_win[df_win['tournament_date_y'] == selected_season]
    
    # Calculer le winrate moyen réel par saison
    winrate_par_saison = df_win.groupby('tournament_date_y').agg(winrate_real=('winrates', 'mean')).reset_index()
    
    # Fusionner usage et winrate réel
    stats = usage_par_saison.merge(winrate_par_saison, on='tournament_date_y', how='left')
    
    return stats

    
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
st.markdown(" ")

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
#---------------------------------------------------------------------------------------------------------------------------------------------------------        
    # Rajout
    # Choix du deck
    decks_available = decklists['deck'].unique()
    selected_deck = st.selectbox("Choisir un deck", decks_available)
    
    # Filtrer la composition du deck choisi
    df_deck = decklists[decklists['deck'] == selected_deck]
    # Fusion pour enrichir avec infos cartes
    df_deck = df_deck.merge(cards, left_on='card_name', right_on='name', how='left')
    
    # Calcul winrate moyen du deck (moyenne des winrates des joueurs avec ce deck)
    mean_winrate = df_deck['winrate'].mean()
    
    # Top 3 faiblesses du deck
    top_weaknesses = df_deck['weakness'].value_counts().head(3)
    
    # Cartes adverses fréquentes dans les decks qui battent ce deck (winrate > 0.6 contre ce deck)
    # Ici on simplifie : on prend tous les decks différents de selected_deck avec winrate > 0.6
    decks_that_beat = decklists[(decklists['winrate'] > 0.6) & (decklists['deck'] != selected_deck)]
    cards_adverses = decks_that_beat['card_name'].value_counts().head(5)
    
    # --- Affichage esthétique ---
    
    st.markdown("### Composition du deck")
    st.dataframe(df_deck[['card_name', 'count', 'type_', 'weakness']])
    
    st.markdown("### KPIs du deck")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Nombre total de cartes", value=f"{df_deck['count'].sum()}")
    col2.markdown(f"<div style='color:red; font-weight:bold; font-size:24px;'>Winrate moyen : {mean_winrate:.2%}</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"<div style='color:red; font-weight:bold; font-size:24px;'>Faiblesses principales :</div>", unsafe_allow_html=True)
        for w, cnt in top_weaknesses.items():
            st.markdown(f"<div style='color:red;'>- {w} ({cnt} cartes)</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### Cartes adverses fréquentes qui battent ce deck")
    for card, count in cards_adverses.items():
        st.markdown(f"- **{card}** ({count} occurrences)")
#---------------------------------------------------------------------------------------------------------------------------------------------------------------        
#--------------------------------modif----------------------------------------------        
with tab3:
    ## Onglet détail deck
  conn = connect_db()
  if conn:
     decklists = table_wrk_decklists(conn)
     cards = table_wrk_cards(conn)
     tournements = table_wrk_tournements(conn)
     win= table_wrk_tournaments_win(conn)
      
     option = decklists['deck'].unique()
     selected_deck = st.selectbox("Rechercher un deck",option)
     
     seasons = tournements['tournament_date_y'].dropna().unique()
     seasons = sorted(seasons)
     selected_season = st.selectbox("Choisir une saison (année)", options=[None] + seasons, index=0)

     # Filtrer la table win selon le deck sélectionné
     filtered_win = win[win['deck'] == selected_deck]
     if not filtered_win.empty:
        winrate_reel = filtered_win['winrate'].iloc[0]  # prends le 1er winrate correspondant
     else:
         winrate_reel = None
     
     
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
            st.metric("Win-Rate réel", f"{winrate_reel:.2%}")
            
            
# Cartes du deck sélectionné
df_deck = decklists[decklists['deck'] == selected_deck]
unique_cards = df_deck['card_name'].unique()
selected_card = st.selectbox("Choisir une carte du deck", unique_cards)

if selected_card:
    df_stats = analyse_usage_winrate_par_saison(decklists, tournements, win, selected_card, selected_deck, selected_season)

    if df_stats.empty:
        st.warning("Pas de données disponibles pour cette carte / saison.")
    else:
        fig, ax1 = plt.subplots(figsize=(10, 5))
        
        # Bar plot usage
        ax1.bar(df_stats['tournament_date_y'], df_stats['usage'], color='skyblue', label='Usage (nombre de joueurs)')
        ax1.set_xlabel('Saison (année)')
        ax1.set_ylabel('Usage (nombre de joueurs)', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        # Line plot winrate réel moyen
        ax2 = ax1.twinx()
        ax2.plot(df_stats['tournament_date_y'], df_stats['winrate_real'], color='red', marker='o', label='Winrate réel moyen')
        ax2.set_ylabel('Winrate réel moyen', color='red')
        ax2.tick_params(axis='y', labelcolor='red')
        ax2.set_ylim(0, 1)

        plt.title(f"Usage et Winrate de la carte '{selected_card}' - Deck '{selected_deck}' - Saison '{selected_season or 'Toutes'}'")
        fig.tight_layout()
        st.pyplot(fig)

conn.close()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

if __name__ == "__main__":
    main()

