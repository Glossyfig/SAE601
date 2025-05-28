import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
from pandas import DataFrame

st.set_page_config(
    page_title="streamlit basics app",
    layout="centered"
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

# Interface principale
def head():
    st.header("Pokémon, TCG Pocket")
    st.write("Par Sergina Bakala, Kiran Derennes, Ifig Legonidec, Mattéo Rouanne ")

def layout():
    st.sidebar.title("Filtres")
    st.sidebar.write("Infos")
    
def table_wrk_decklists(conn):
    cur = conn.cursor()
    query=cur.execute('Select * From wrk_decklists;')
    rows=cur.fetchall()
    conn.commit()
    cur.execute("Select COLUMN_NAME from information_schema.columns where table_name = 'wrk_decklists'")
    names = cur.fetchall()
    names_l = []
    for l in names:
        names_l.append(l[0])
    bdd = pd.DataFrame(rows)
    bdd.columns = names_l
    bdd.head(5)
    return bdd 
    
def table_temp_decklist(bdd):
    bdd
def nb_tournois(bdd):
    nb_tournois = bdd["tournament_id"].unique()
    st.write(f"Nombre de tournois: {len(nb_tournois)}")
    


# Main app
def main():
    conn = connect_db()
    if conn:
        st.success("Connexion réussie à PostgreSQL Portable !")
        cur = conn.cursor()
        cur.execute("SELECT version();")
        bdd = table_wrk_decklists(conn)
        table_temp_decklist(bdd)
        nb_tournois(bdd)
        cur.close()
        conn.close()

head()
layout()


if __name__ == "__main__":
    main()
