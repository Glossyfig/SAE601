import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
from PIL import Image

# Configuration de la page
st.set_page_config(
    page_title="Pokémon TCG Pocket",
    page_icon="🃏",
    layout="wide"
)

# Paramètres de connexion
DB_PARAMS = {
    'host': 'localhost',
    'port': '5432',
    'dbname': 'postgres',
    'user': 'postgres'
}

# Connexion à la base
@st.cache_resource
def connect_db():
    try:
        return psycopg2.connect(**DB_PARAMS)
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None

# Récupération d'une table PostgreSQL
def load_table(conn, table_name):
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {table_name};")
        rows = cur.fetchall()
        cur.execute(f"""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = '{table_name}';
        """)
        columns = [col[0] for col in cur.fetchall()]
    return pd.DataFrame(rows, columns=columns)

# Aperçus de données
def display_table(df, name):
    st.write(f"Aperçu de la table **{name}** :")
    if st.checkbox(f"Afficher la table {name}"):
        st.dataframe(df.head(10))

# Nombre de tournois
def show_nb_tournois(decklists):
    nb_tournois = decklists["tournament_id"].nunique()
    st.metric("Nombre de tournois", nb_tournois)

def graphique_rep_cartes_par_saison(conn):
    st.subheader("Répartition des cartes les plus jouées par saison")

    query1 = """
    SELECT
        c.name,
        t.tournament_date_y,
        COUNT(*) AS play_count
    FROM wrk_decklists d
    JOIN wrk_cards c ON d.card_id = c.card_id
    JOIN wrk_tournaments t ON d.tournament_id = t.tournament_id
    GROUP BY c.name, t.tournament_date_y
    ORDER BY t.tournament_date_y, freq DESC;
    """
    
    df1 = pd.read_sql_query(query1, conn)

    if df1.empty:
        st.info("Aucune donnée à afficher pour les cartes par saison.")
        return

    # Ne garder que les 5 cartes les plus jouées par saison
    df1_top = df1.groupby("tournament_date_y").apply(lambda x: x.nlargest(5, "freq")).reset_index(drop=True)

    seasons1 = df1_top["tournament_date_y"].unique()
    for season in seasons1:
        df1_season = df1_top[df1_top["tournament_date_y"] == season]
        fig1, ax = plt.subplots()
        ax.barh(df1_season["name"], df1_season["freq"], color="#FFCC00")
        ax.set_title(f"Top 5 des cartes les plus jouées - {season}")
        ax.set_xlabel("Nombre d'apparitions")
        ax.invert_yaxis()
        st.pyplot(fig1)


def graphique_meilleur_win_rate(conn):
    st.subheader("Répartition des deck avec les meilleurs win-rate")

    query2 = """
    SELECT
        t.tournament_date_y,
        tw.deck,
        tw.winrates,
        tw.victories,
        tw.losses
    FROM wrk_tournaments_win tw
    JOIN wrk_tournaments t ON tw.tournament_id = t.tournament_id
    GROUP BY t.tournament_date_y, tw.deck
    ORDER BY tw.winrates DESC;
    """
    
    df2 = pd.read_sql_query(query, conn)

    if df2.empty:
        st.info("Aucune donnée à afficher pour les cartes par saison.")
        return

    # Ne garder que les 5 decks les plus gagnants par saison
    df2_top = df.groupby("tournament_date_y").apply(lambda x: x.nlargest(5, "winrates")).reset_index(drop=True)

    seasons2 = df2_top["tournament_date_y"].unique()
    for season in seasons2:
        df2_season = df2_top[df2_top["tournament_date_y"] == season]
        fig2, ax = plt.subplots()
        ax.barh(df2_season["deck"], df2_season["winrates"], color="#FFCC00")
        ax.set_title(f"Top 5 des decks les plus gagnants - {season}")
        ax.set_xlabel("Win-rate")
        ax.invert_yaxis()
        st.pyplot(fig2)

# Style CSS
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

# Connexion unique
conn = connect_db()
if not conn:
    st.stop()

decklists = load_table(conn, "wrk_decklists")
cards = load_table(conn, "wrk_cards")
tournaments = load_table(conn, "wrk_tournaments")

# SIDEBAR
st.sidebar.title("Filtres")
st.sidebar.markdown("## Tournois")
st.sidebar.slider("Nombre de joueurs", 0, 100, (0, 100))
st.sidebar.multiselect("Nom de tournois", tournaments["tournament_name"].unique())
st.sidebar.markdown("## Decks")
choix_type = st.sidebar.radio("Type de deck", [
    "colorless", "water", "fire", "grass", "fighting", "electric", 
    "psychic", "steel", "dark", "dragon"
])
st.sidebar.slider("Win-Rate", 0, 100, (0, 100))

# TITRE
st.title("Pokémon TCG Pocket")
st.markdown("Par Sergina Bakala, Kiran Derennes, Ifig Le Gonidec, Mattéo Rouanne ")

# ONGLET 1 : Présentation
tab1, tab2, tab3 = st.tabs(["Présentation", "⚔️ Stratégies", "Détails des decks"])

with tab1:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("GALqQYXtpbYyZRsX5ftVNdSCoN1980aiWtrBahZr.jpg", width=800)
    
    st.markdown("""
    <div class="description">
    Pokémon TCG Pocket est une adaptation mobile gratuite du jeu de cartes à collectionner Pokémon (TCG).
    Les joueurs construisent des decks et s’affrontent en ligne.
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Objectif")
    st.markdown("""
    Vous devez analyser le métagame : cartes gagnantes, combinaisons efficaces, contre-stratégies, évolutions temporelles…
    """)

    st.markdown("### Lien vers l'application")
    st.markdown("[📱 Google Play](https://play.google.com/store/apps/details?id=jp.pokemon.pokemontcgp)")
    st.markdown("[🍎 App Store](https://apps.apple.com/app/pokemon-tcgp-pocket/id1563916495)")
    st.markdown("---")
    st.markdown('<div class="footer">© 2025 Pokémon TCGP Pocket - Application non officielle</div>', unsafe_allow_html=True)

# ONGLET 2 : Stratégies
with tab2:
    display_table(decklists, "decklists")
    display_table(cards, "cards")
    display_table(tournaments, "tournaments")
    show_nb_tournois(decklists)
    graphique_rep_cartes_par_saison(conn)

# ONGLET 3 : Détails des decks
with tab3:
    st.selectbox("Rechercher un deck", ["bfsd", "55", "ddg"])
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/pocket/A1a/A1a_017_EN.webp", caption="Carte principale", width=300)
    
    type_images = {
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
        st.image(type_images[choix_type], caption="Type du deck", width=300)
    with col3:
        st.metric("Win-Rate", "74 %")
