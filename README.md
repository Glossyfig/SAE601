# SAE601
<img src="https://upload.wikimedia.org/wikipedia/commons/c/c2/Pokemon_TCG_Pocket_logo.png" width="500" />

## Descriptif :memo:
Il s'agit d'un travail collaboratif réalisé en équipe sur le développement d'un outil et d'analyses autour du métagame Pocket, le jeu de carte à collectionner Pokémon. Notre objectif était d'identifier les cartes avec un taux de victoire élevé, leurs fonctionnements et évolutions. Derrière ces observations, il est aussi question de <ins> mesurer l'impact de ces cartes sur les stratégies adoptées lors des tournois et d'explorer les moyens de les contrer </ins>. \
Site web d'intérêt : [Limitless TCG](https://play.limitlesstcg.com/)

## Logiciels/langages/ principaux packages utilisés :pushpin:
- **python** : Le langage de programmation utilisé pour tous la plupart des codes à exécuter (*collecte des données,...*)
- **BeautifulSoup** : Bibliothèque python utilisé pour le scrapping des données web
- **PostgreSQL** :  Serveur de base de données utilisé
- **Streamlit** : Bibliothèque python utilisé pour l'application web
- **Dbeaver** : Interface utilisé pour accéder à la base de données

## Utilisation des fichiers :hammer_and_wrench: 
L'organisation de ce repository est similaire à l'ordre dans lequel les différents fichiers doivent être exécuter ou étudier : Collection, transformation et application web.

### Data collection
Dans ce dossier le premier script à exécuter est :
- le script python du fichier [Extraction_donnees_cartes.py](data_collection/Extraction_donnees_carte.py), scrappe les données en ligne des cartes et les stock sous formes de fichiers JSON dans des dossiers (output, cache, ...).

### Data transformation
Une fois les fichiers à disposition, exécuter le script [main.py](./data_transformation/main.py) qui crée et insère les données dans les tables de decklist, cartes, et tournois. 

Il faut cependant s'assurer avant de le lancer:
- que les données sont bien stockées dans le répertoire sur lequel pointent les variables output_directory et output_directory2 : datacollection/output (Les modifier si nécessaires)
- que la base de données créée porte bien le nom *postgresql* et que le port local de votre machine est le 5432 (Les modifier si nécessaires)
- Vérifier les autres paramètres de connexion

```
postgres_db=os.environ.get('POSTGRES_DB')
postgres_user=os.environ.get('POSTGRES_USER')
postgres_password=os.environ.get('POSTGRES_PASSWORD')
postgres_host=os.environ.get('POSTGRES_HOST')
postgres_port=os.environ.get('POSTGRES_PORT')

output_directory = "D:/SAE601_2025/data_collection/output"
output_directory2 = "C:/.../.../.../.../BUT_SD/SAE601_2025/data_collection/cartes_pokemon"

def get_connection_string():
  return "postgresql://postgres@localhost:5432"
```
A noté qu'aucun ETL n'a été utilisé pour les transformations, seul des scripts python ont été utilisés. Le fichier <ins>main.py</ins> contient donc une fonction d'anonymisation pour les identifiants des joueurs et exécute le script sql qui en plus de l'insertion des données dans les tables, décompose la date en élément de jours, mois et année. 

### Data visualisation 
Pour lancer l'application web streamlit en local sur votre machine, exécuter la commande suivante dans un terminal, après s'être placé dans le répertoire qui contient le fichier (application) : 
```
streamlit run app.py
```
Une fenêtre s'ouvrira dans votre navigateur.

## Contributeurs :technologist:
- [@Kila-ht](https://github.com/Kila-ht)
- [@matiornn](https://github.com/matiornn)
- [@gina_ju](https://github.com/ginaju)
- [@glossyfig](https://github.com/Glossyfig)
