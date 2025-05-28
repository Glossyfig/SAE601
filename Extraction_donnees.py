import requests
from bs4 import BeautifulSoup
import re
import json
import os # Importe le module os pour gérer les chemins de fichiers et créer des dossiers

# URL de la page contenant les extensions
url = "https://pocket.limitlesstcg.com/cards/"
id_extension = []
id_carte = []
donnees_carte = []
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def recuperation_extension(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')
        extension_spans = soup.find_all("span", class_="code annotation")
        for span in extension_spans:
            id_extension.append(span.get_text(separator=",").strip())
    else:
        print(f"Erreur lors de la récupération des extensions : {response.status_code}")

def recup_id_carte():
    for id_ext in id_extension:
        url_extension = f"https://pocket.limitlesstcg.com/cards/{id_ext}"
        response_extension = requests.get(url_extension, headers=headers)
        if response_extension.status_code == 200:
            soup_extension = BeautifulSoup(response_extension.content, 'html.parser')
            main = soup_extension.find("main")
            if main:
                for a_tag in main.find_all("a", href=True):
                    id_carte.append(a_tag['href'].lstrip('/'))
        else:
            print(f"Erreur lors de la récupération des cartes pour l'extension {id_ext} : {response_extension.status_code}")

recuperation_extension(url)
recup_id_carte()

# Crée un dossier pour stocker les fichiers JSON si ce n'est pas déjà fait
# Le dossier sera créé dans le même répertoire que le script Python
output_directory = "cartes_pokemon"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)
for part_url in id_carte:
    url_carte = f"https://pocket.limitlesstcg.com/{part_url}"
    response_carte = requests.get(url_carte, headers=headers)
    if response_carte.status_code == 200:
        soup_carte = BeautifulSoup(response_carte.text, "html.parser")
        
        # Initialisation d'un dictionnaire pour la carte actuelle
        card_data = {}
        card_data["url_source"] = url_carte # Ajoute l'URL de la source pour référence
        
        # Type de carte
        type_carte_div = soup_carte.select_one(".card-text-type")
        type_carte = type_carte_div.text.strip() if type_carte_div else "Stage d'évolution inconnu"
        elements = [part.strip() for part in type_carte.split("-")]

        if elements[0] == "Trainer":
            # Nom de la carte
            name = soup_carte.select_one(".card-text-name a")
            card_name = name.text.strip() if name else "Nom inconnu"
            card_data["name"] = card_name
            
            # URL de l'image
            img = soup_carte.select_one(".card-image img")
            image_url = img['src'] if img else "Image non trouvée"
            card_data["image_url"] = image_url
            
            # Extension (set)
            set_span = soup_carte.select_one(".card-prints-current .text-lg")
            card_set = set_span.text.strip() if set_span else "Extension inconnue"
            match = re.search(r"\(([^)]+)\)", card_set)
            numero_extension = match.group(1) if match else "Numéro d'extension inconnu"
            card_data["set_number_id"] = numero_extension
            
            # Numéro de la carte
            card_number = soup_carte.select_one(".card-prints-current span:nth-of-type(2)")
            card_number_text = card_number.text.strip() if card_number else "Numéro inconnu"
            match = re.search(r"#(\d+)", card_number_text)
            numero_carte = int(match.group(1)) if match else "Numéro inconnu"
            card_data["card_number"] = numero_carte
            
            # Illustrateur
            illustrator = soup_carte.select_one(".card-text-artist a")
            artist_name = illustrator.text.strip() if illustrator else "Illustrateur inconnu"
            card_data["artist"] = artist_name
            
            # ---
            ### Exportation en JSON pour chaque carte

            # Crée un nom de fichier unique pour chaque carte
            # Utilise le numéro d'extension et le numéro de carte pour le nom du fichier
            # Pour une meilleure lisibilité dans le nom de fichier, on peut nettoyer le nom de la carte
            safe_card_name = "".join(c for c in card_name if c.isalnum() or c in (' ', '_')).rstrip()
            safe_card_name = safe_card_name.replace(' ', '_')
            
            # Le nom du fichier sera par exemple : "A1-001_Pikachu.json" ou "S1-042_Charizard.json"
            # On utilise numero_extension qui est maintenant garanti d'être une chaîne
            output_filename = os.path.join(output_directory, f"{numero_extension}-{numero_carte:03d}_{safe_card_name}.json")


            # Écriture des données de la carte dans son propre fichier JSON
            try:
                with open(output_filename, 'w', encoding='utf-8') as f:
                    json.dump(card_data, f, ensure_ascii=False, indent=4)
                print(f"Données de la carte {card_name} ({numero_extension}-{numero_carte}) exportées dans '{output_filename}'")
            except Exception as e:
                print(f"Erreur lors de l'écriture du fichier JSON pour la carte {card_name}: {e}")
            continue  # On passe à la carte suivante
        
        # Nom de la carte
        name = soup_carte.select_one(".card-text-name a")
        card_name = name.text.strip() if name else "Nom inconnu"
        card_data["name"] = card_name
        
        # URL de l'image
        img = soup_carte.select_one(".card-image img")
        image_url = img['src'] if img else "Image non trouvée"
        card_data["image_url"] = image_url
        
        # Extension (set)
        set_span = soup_carte.select_one(".card-prints-current .text-lg")
        card_set = set_span.text.strip() if set_span else "Extension inconnue"
        match = re.search(r"\(([^)]+)\)", card_set)
        numero_extension = match.group(1) if match else "Numéro d'extension inconnu"
        card_data["set_number_id"] = numero_extension
        
        # Numéro de la carte
        card_number = soup_carte.select_one(".card-prints-current span:nth-of-type(2)")
        card_number_text = card_number.text.strip() if card_number else "Numéro inconnu"
        match = re.search(r"#(\d+)", card_number_text)
        numero_carte = int(match.group(1)) if match else "Numéro inconnu"
        card_data["card_number"] = numero_carte
        
        # Illustrateur
        illustrator = soup_carte.select_one(".card-text-artist a")
        artist_name = illustrator.text.strip() if illustrator else "Illustrateur inconnu"
        card_data["artist"] = artist_name
        
        # Stage d'évolution et pré-évolution
        stage_evo = "Inconnu"
        poke_pre_evo = "Inconnu"
        if len(elements) > 1:
            stage_evo = elements[1]
        if len(elements) > 2:
            pre_evo_info = elements[2].strip()
            lines = pre_evo_info.split("\n")
            if len(lines) > 1:
                poke_pre_evo = lines[1]
            else:
                poke_pre_evo = pre_evo_info
        card_data["Stage d'évolution"] = stage_evo
        card_data["Pré-évolution"] = poke_pre_evo
        
        # Type et PV
        set_span = soup_carte.select_one(".card-text-title")
        card_info_comp = set_span.text.strip() if set_span else "Type inconnu - PV inconnu"
        elements_info = [part.strip() for part in card_info_comp.split("-")]
        type_ = elements_info[1] if len(elements_info) > 1 else "Type inconnu"
        pv = int(re.search(r'\d+', elements_info[2]).group()) if len(elements_info) > 2 and re.search(r'\d+', elements_info[2]) else "PV inconnu"
        card_data["type"] = type_
        card_data["hp"] = pv
        
        # Faiblesse et retrait
        set_span = soup_carte.select_one(".card-text-wrr")
        info_ = set_span.get_text(separator="\n").strip() if set_span else "Faiblesse inconnu"
        elements_wr = [part.strip() for part in info_.split("\n")]
        faiblesse = elements_wr[0].split(":")[1].strip() if len(elements_wr) > 0 and ":" in elements_wr[0] else "Faiblesse inconnue"
        retrait = int(re.search(r'\d+', elements_wr[2]).group()) if len(elements_wr) > 2 and re.search(r'\d+', elements_wr[2]) else "Cout de retrait inconnu"
        card_data["faiblesse"] = faiblesse
        card_data["retrait"] = retrait
        
        # Attaques
        set_span = soup_carte.find_all("p", class_="card-text-attack-info")
        attaque1, attaque2 = {}, {}
        if len(set_span) > 0:
            elements = set_span[0].get_text(separator="\n").strip().split("\n")
            attaque1 = {
                "Cout": elements[0] if len(elements) > 0 else "Inconnu",
                "Degat": int(re.search(r'\d+', elements[2]).group()) if len(elements) > 2 and re.search(r'\d+', elements[2]) else "Inconnu",
                "Nom": re.sub(r'\d+', '', elements[2]) if len(elements) > 2 else "Inconnu"
            }
        if len(set_span) > 1:
            elements = set_span[1].get_text(separator="\n").strip().split("\n")
            attaque2 = {
                "Cout": elements[0] if len(elements) > 0 else "Inconnu",
                "Degat": int(re.search(r'\d+', elements[2]).group()) if len(elements) > 2 and re.search(r'\d+', elements[2]) else "Inconnu",
                "Nom": re.sub(r'\d+', '', elements[2]) if len(elements) > 2 else "Inconnu"
            }
        card_data["Nom de l'attaque 1"] = attaque1.get("Nom", "Inconnu")
        card_data["Coût de l'attaque 1"] = attaque1.get("Cout", "Inconnu")
        card_data["Dégat de l'attaque 1"] = attaque1.get("Degat", "Inconnu")
        card_data["Nom de l'attaque 2"] = attaque2.get("Nom", "Inconnu")
        card_data["Coût de l'attaque 2"] = attaque2.get("Cout", "Inconnu")
        card_data["Dégat de l'attaque 2"] = attaque2.get("Degat", "Inconnu")
        
        # Affichage dans la console
        print(f"URL : {url_carte}")
        print(f"Nom : {card_name}")
        print(f"Image : {image_url}")
        print(f"Extension : {card_set}")
        print(f"Numéro extension : {numero_extension}")
        print(f"Numéro de carte : {numero_carte}")
        print(f"Stage d'évolution : {stage_evo}")
        print(f"Pré-évolution : {poke_pre_evo}")
        print(f"Type : {type_}")
        print(f"PV : {pv}")
        print(f"Faiblesse : {faiblesse}")
        print(f"Coût de retrait : {retrait}")
        print(f"Illustrateur : {artist_name}")
        print("-" * 30) # Séparateur pour une meilleure lisibilité

        # ---
        ### Exportation en JSON pour chaque carte

        # Crée un nom de fichier unique pour chaque carte
        # Utilise le numéro d'extension et le numéro de carte pour le nom du fichier
        # Pour une meilleure lisibilité dans le nom de fichier, on peut nettoyer le nom de la carte
        safe_card_name = "".join(c for c in card_name if c.isalnum() or c in (' ', '_')).rstrip()
        safe_card_name = safe_card_name.replace(' ', '_')
        
        # Le nom du fichier sera par exemple : "A1-001_Pikachu.json" ou "S1-042_Charizard.json"
        # On utilise numero_extension qui est maintenant garanti d'être une chaîne
        output_filename = os.path.join(output_directory, f"{numero_extension}-{numero_carte:03d}_{safe_card_name}.json")


        # Écriture des données de la carte dans son propre fichier JSON
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(card_data, f, ensure_ascii=False, indent=4)
            print(f"Données de la carte {card_name} ({numero_extension}-{numero_carte}) exportées dans '{output_filename}'")
        except Exception as e:
            print(f"Erreur lors de l'écriture du fichier JSON pour la carte {card_name}: {e}")

    else:
        print(f"Erreur lors du chargement de la page {url_carte} : {response_carte.status_code}")

print("\nProcessus de scraping terminé et fichiers JSON créés.")


 