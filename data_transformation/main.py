import sys
print(sys.executable)
import psycopg
import os
import json
import re
from datetime import datetime
from unidecode import unidecode

postgres_db=os.environ.get('POSTGRES_DB')
postgres_user=os.environ.get('POSTGRES_USER')
postgres_password=os.environ.get('POSTGRES_PASSWORD')
postgres_host=os.environ.get('POSTGRES_HOST')
postgres_port=os.environ.get('POSTGRES_PORT')

output_directory = "D:/SAE601_2025/data_collection/output"
output_directory2 = "C:/Users/kiran/OneDrive/Documents/BUT_SD/SAE601_2025/data_collection/cartes_pokemon"

def get_connection_string():
  return "postgresql://postgres@localhost:5432"

def execute_sql_script(path: str):
  with psycopg.connect(get_connection_string()) as conn:
    with conn.cursor() as cur:
      with open(path) as f:
        cur.execute(f.read())

def clean_text(text):
    if isinstance(text, str):
        # Nettoie le texte
        text = text.replace('é', 'e').replace('è', 'e').replace('à', 'a')
        text = re.sub(r'[^\x00-\x7F]+', '', text)  # Supprime les caracteres non-ASCII
        return text
    return text

def insert_wrk_tournaments():
  tournament_data = []
  for file in os.listdir(output_directory):
    with open(f"{output_directory}/{file}",encoding="utf-8") as f:
      tournament = json.load(f)
      tournament_data.append((
        tournament['id'], 
        clean_text(tournament['name']), 
        datetime.strptime(tournament['date'], '%Y-%m-%dT%H:%M:%S.000Z'),
        clean_text(tournament['organizer']), 
        clean_text(tournament['format']), 
        int(tournament['nb_players'])
        ))
  
  with psycopg.connect(get_connection_string()) as conn:
    with conn.cursor() as cur:
      cur.executemany("INSERT INTO public.wrk_tournaments values (%s, %s, %s, %s, %s, %s)", tournament_data)

def insert_wrk_decklists():
  decklist_data = []
  for file in os.listdir(output_directory):
    with open(f"{output_directory}/{file}", encoding="utf-8") as f:
      tournament = json.load(f)
      tournament_id = tournament['id']
      print(f"URL : {tournament_id}")
      for player in tournament['players']:
        player_id = player['id']
        for card in player['decklist']:
          decklist_data.append((
            tournament_id,
            player_id,
            clean_text(card['type']),
            clean_text(card['name']),
            clean_text(card['url']),
            int(card['count']),
          ))
  
  with psycopg.connect(get_connection_string()) as conn:
    with conn.cursor() as cur:
      cur.executemany("INSERT INTO public.wrk_decklists values (%s, %s, %s, %s, %s, %s)", decklist_data)
      

def insert_wrk_cards():
  card_data = []
  for file in os.listdir(output_directory2):
    with open(f"{output_directory2}/{file}", encoding="utf-8") as f:
      card = json.load(f)
      if card['categorie_carte'] =='Pokémon':
          url_source = clean_text(card['url_source'])
          categorie = clean_text(card['categorie_carte'])
          name = clean_text(card['name'])
          print(f"URL : {name}")
          image_url = clean_text(card['image_url'])
          set_number_id = clean_text(card['set_number_id'])
          card_number = card['card_number']
          artist = clean_text(card['artist'])
          stage_evolution = unidecode(card['Stage_devolution'])
          pre_evolution = clean_text(card['Pre_evolution'])
          type_ = clean_text(card['type'])
          heal_points = card['hp']
          weakness = clean_text(card['faiblesse'])
          retreat = card['retrait']
          attack_1_name = clean_text(card['Nom_attaque_1'])
          attack_1_cost = clean_text(card['Cout_attaque_1'])
          attack_1_damage = card['Degat_attaque_1']
          attack_2_name = clean_text(card['Nom_attaque_2'])
          attack_2_cost = clean_text(card['Cout_attaque_2'])
          attack_2_damage = card['Degat_attaque_2']
          card_data.append([url_source,categorie, name, image_url, set_number_id, card_number, artist, stage_evolution, pre_evolution, type_, heal_points, weakness, retreat, attack_1_name, attack_1_cost, attack_1_damage, attack_2_name, attack_2_cost, attack_2_damage])
      else :
          url_source = clean_text(card['url_source'])
          categorie = clean_text(card['categorie_carte'])
          name = clean_text(card['name'])
          print(f"URL : {name}")
          image_url = clean_text(card['image_url'])
          set_number_id = clean_text(card['set_number_id'])
          card_number = card['card_number']
          artist = clean_text(card['artist'])
          stage_evolution = "Inconnu"
          pre_evolution = "Inconnu"
          type_ = "Inconnu"
          heal_points = 0
          weakness = "Inconnu"
          retreat = 0
          attack_1_name = "Inconnu"
          attack_1_cost = "Inconnu"
          attack_1_damage = "Inconnu"
          attack_2_name = "Inconnu"
          attack_2_cost = "Inconnu"
          attack_2_damage = "Inconnu"
          card_data.append([url_source, categorie, name, image_url, set_number_id, card_number, artist, stage_evolution, pre_evolution, type_, heal_points, weakness, retreat, attack_1_name, attack_1_cost, attack_1_damage, attack_2_name, attack_2_cost, attack_2_damage])

    with psycopg.connect(get_connection_string()) as conn:
      with conn.cursor() as cur:
        cur.executemany("INSERT INTO public.wrk_cards values (%s, %s, %s, %s, %s, %s ,%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)", card_data)
    

print("creating work tables")
execute_sql_script("00_create_wrk_tables.sql")

print("insert raw tournament data")
insert_wrk_tournaments()

print("insert raw decklist data")
insert_wrk_decklists()

print("insert raw card data")
insert_wrk_cards()

print("construct card database")
execute_sql_script("01_dwh_cards.sql")
