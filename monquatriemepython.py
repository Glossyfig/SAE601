from bs4 import BeautifulSoup
import os
import json
import logging

# Configuration du logging
logging.basicConfig(filename='errors.log', level=logging.ERROR)

tournaments_folder_path = "C:/Users/matte/OneDrive/Bureau/SAE601_2025/data_collection/cache/tournament"
json_folder_path = "C:/Users/matte/OneDrive/Bureau/SAE601_2025/data_collection/output"

for root, dirs, files in os.walk(tournaments_folder_path):
    for file_name in files:
        if file_name == "standingsplayers.html":
            html_file_path = os.path.join(root, file_name)

            try:
                # Lecture du fichier HTML
                with open(html_file_path, "r", encoding="utf-8") as file:
                    soup = BeautifulSoup(file, "html.parser")
            except UnicodeDecodeError:
                try:
                    with open(html_file_path, "r", encoding="ISO-8859-1") as file:
                        soup = BeautifulSoup(file, "html.parser")
                except Exception as e:
                    logging.error(f"Erreur lors de la lecture du fichier {html_file_path}: {e}")
                    continue
            except Exception as e:
                logging.error(f"Erreur inattendue lors de la lecture du fichier {html_file_path}: {e}")
                continue

            # Extraction du nom du tournoi
            tournament_name = soup.title.string.replace("Standings: ", "").replace(" | Limitless", "").strip()

            # Extraction du code du tournoi
            tournament_script = soup.find("script", string=lambda text: text and "tournamentId" in text)
            tournament_id = None
            if tournament_script:
                for line in tournament_script.string.split(';'):
                    if "tournamentId" in line:
                        tournament_id = line.split('=')[1].strip().replace("'", "").replace(";", "").split(',')[0]

            players_tournaments_data = []
            for row in soup.select("div.standings table tr"):
                if row.get("data-name"):
                    try:
                        name = row["data-name"]
                        placing = int(row.get("data-placing", 0))
                        if placing != 0:
                            tds = row.find_all("td")
                            if len(tds) >= 5:
                                points_text = tds[3].text.strip()
                                record_text = tds[4].text.strip()

                                if not points_text:
                                    continue

                                points = int(points_text)
                                victories, losses, draws = map(int, record_text.split(" - "))

                                winrate = victories / (victories + losses + draws) if (victories + losses + draws) != 0 else 1

                                players_tournaments_data.append({
                                    "tournament_id": tournament_id,
                                    "tournament_name": tournament_name,
                                    "name": name,
                                    "placing": placing,
                                    "points": points,
                                    "victories": victories,
                                    "losses": losses,
                                    "draws": draws,
                                    "winrates": round(winrate, 3)
                                })
                    except ValueError as ve:
                        logging.error(f"Erreur de conversion pour le joueur {row.get('data-name')}: {ve}")
                        continue

            # Chargement du fichier JSON correspondant
            if tournament_id:
                json_file_path = os.path.join(json_folder_path, f"{tournament_id}.json")

                if os.path.exists(json_file_path):
                    try:
                        with open(json_file_path, "r", encoding="utf-8") as json_file:
                            tournament_data = json.load(json_file)
                    except UnicodeDecodeError:
                        try:
                            with open(json_file_path, "r", encoding="ISO-8859-1") as json_file:
                                tournament_data = json.load(json_file)
                        except Exception as e:
                            logging.error(f"Erreur lors de la lecture du fichier JSON {json_file_path}: {e}")
                            continue
                    except Exception as e:
                        logging.error(f"Erreur inattendue lors de la lecture du fichier JSON {json_file_path}: {e}")
                        continue

                    for player_data in players_tournaments_data:
                        player_name = player_data["name"]
                        for player in tournament_data.get("players", []):
                            if player.get("name") == player_name:
                                decklist = player.get("decklist", [])
                                deck_parts = []

                                for card in decklist:
                                    card_name = card.get("name")
                                    card_url = card.get("url")
                                    card_count = card.get("count")

                                    if card_url:
                                        parts = card_url.split('/')
                                        extension = parts[-2]
                                        card_number = parts[-1]
                                    else:
                                        extension = "Unknown"
                                        card_number = "Unknown"

                                    if f"({extension}-{card_number})" in card_name:
                                        deck_parts.append(f'"{card_name}" x{card_count}')
                                    else:
                                        deck_parts.append(f'"{card_name}" ({extension}-{card_number}) x{card_count}')

                                deck_string = ", ".join(deck_parts)
                                player_data["deck"] = deck_string
                                break

            print(f"\nPlayers with Decks for {tournament_name}:")
            for player in players_tournaments_data:
                print(player)


players_json_folder_path = "C:/Users/matte/OneDrive/Bureau/SAE601_2025/data_collection/tournament_win"

os.makedirs(players_json_folder_path, exist_ok=True)

# Parcourez les données des joueurs et enregistrez-les dans des fichiers JSON individuels
for player_data in players_tournaments_data:
    tournament_id = player_data["tournament_id"]
    player_name = player_data["name"]

    # Créez un nom de fichier sûr en remplaçant les caractères non valides
    safe_player_name = "".join(c if c.isalnum() else "_" for c in player_name)
    json_file_name = f"{tournament_id}_{safe_player_name}.json"
    json_file_path = os.path.join(players_json_folder_path, json_file_name)

    # Enregistrez les données du joueur dans un fichier JSON
    try:
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(player_data, json_file, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Erreur lors de l'écriture du fichier JSON {json_file_path}: {e}")


print(player_data)