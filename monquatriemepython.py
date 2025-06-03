from bs4 import BeautifulSoup
import os
import json

# Chemin vers le dossier contenant les sous-dossiers de tournois
tournaments_folder_path = "C:/Users/matte/OneDrive/Bureau/SAE601_2025/data_collection/cache/tournament"

# Chemin vers le dossier contenant les fichiers JSON
json_folder_path = "C:/Users/matte/OneDrive/Bureau/SAE601_2025/data_collection/output"

# Parcourir les sous-dossiers dans le dossier des tournois
for root, dirs, files in os.walk(tournaments_folder_path):
    for file_name in files:
        if file_name == "standingsplayers.html":
            html_file_path = os.path.join(root, file_name)

            try:
                # Essayer d'abord avec UTF-8
                with open(html_file_path, "r", encoding="utf-8") as file:
                    soup = BeautifulSoup(file, "html.parser")
            except UnicodeDecodeError:
                try:
                    # Si UTF-8 échoue, essayer avec ISO-8859-1
                    with open(html_file_path, "r", encoding="ISO-8859-1") as file:
                        soup = BeautifulSoup(file, "html.parser")
                except Exception as e:
                    print(f"Erreur lors de la lecture du fichier {html_file_path}: {e}")
                    continue

            # Extraire le nom du tournoi
            tournament_name = soup.title.string.replace("Standings: ", "").replace(" | Limitless", "").strip()

            # Extraire le code du tournoi depuis le script
            tournament_script = soup.find("script", string=lambda text: text and "tournamentId" in text)
            tournament_id = None
            if tournament_script:
                for line in tournament_script.string.split(';'):
                    if "tournamentId" in line:
                        # Extraire uniquement la partie avant la virgule
                        tournament_id = line.split('=')[1].strip().replace("'", "").replace(";", "").split(',')[0]

            # Trouver le tableau des joueurs
            players_tournaments_data = []
            for row in soup.select("div.standings table tr"):
                if row.get("data-name"):  # ligne avec joueur
                    try:
                        name = row["data-name"]
                        placing = int(row.get("data-placing", 0))
                        if placing != 0:  # Vérifier si le joueur a un classement
                            tds = row.find_all("td")
                            if len(tds) >= 5:
                                points_text = tds[3].text.strip()
                                record_text = tds[4].text.strip()

                                # Vérifier que les données sont valides
                                if not points_text:
                                    continue

                                points = int(points_text)
                                victories, losses, draws = map(int, record_text.split(" - "))

                                if losses + draws == 0:
                                    winrate = 1
                                else:
                                    winrate = victories / (victories + losses + draws)

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
                        print(f"Erreur de conversion pour le joueur {row.get('data-name')}: {ve}")
                        continue

            # Charger le fichier JSON correspondant à l'ID du tournoi
            if tournament_id:
                json_file_path = os.path.join(json_folder_path, f"{tournament_id}.json")

                # Charger le fichier JSON
                if os.path.exists(json_file_path):
                    try:
                        with open(json_file_path, "r", encoding="utf-8") as json_file:
                            tournament_data = json.load(json_file)
                    except UnicodeDecodeError:
                        try:
                            with open(json_file_path, "r", encoding="ISO-8859-1") as json_file:
                                tournament_data = json.load(json_file)
                        except Exception as e:
                            print(f"Erreur lors de la lecture du fichier JSON {json_file_path}: {e}")
                            continue

                    # Parcourir les joueurs et ajouter les informations de deck
                    for player_data in players_tournaments_data:
                        player_name = player_data["name"]

                        # Trouver le joueur correspondant dans tournament_data
                        for player in tournament_data.get("players", []):
                            if player.get("name") == player_name:
                                decklist = player.get("decklist", [])
                                deck_parts = []

                                for card in decklist:
                                    card_name = card.get("name")
                                    card_url = card.get("url")
                                    card_count = card.get("count")

                                    # Extraire l'extension et le numéro de la carte de l'URL
                                    if card_url:
                                        parts = card_url.split('/')
                                        extension = parts[-2]
                                        card_number = parts[-1]
                                    else:
                                        extension = "Unknown"
                                        card_number = "Unknown"

                                    # Vérifier si le nom de la carte contient déjà une extension et un numéro de carte
                                    if f"({extension}-{card_number})" in card_name:
                                        deck_parts.append(f'"{card_name}" x{card_count}')
                                    else:
                                        deck_parts.append(f'"{card_name}" ({extension}-{card_number}) x{card_count}')

                                # Joindre les parties du deck avec une virgule
                                deck_string = ", ".join(deck_parts)
                                player_data["deck"] = deck_string
                                break

            # Afficher les données mises à jour
            print(f"\nPlayers with Decks for {tournament_name}:")
            for player in players_tournaments_data:
                print(player)
