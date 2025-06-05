# SAE601
<img src="https://upload.wikimedia.org/wikipedia/commons/c/c2/Pokemon_TCG_Pocket_logo.png" width="500" />

## Description :memo:
This is a collaborative team work on the development of a decisional tool and analysis related to the Pocket metagame, the Pokémon trading card game . Our main objective was to identify high win-rate cards and to understand their mechanics and evolution over time. Beyond this observations, the goal was also <ins>  to assess the impact of these cards on the strategies adopted during tournaments and to explore possible countermeasures </ins>. 
web site of interest : [Limitless TCG](https://play.limitlesstcg.com/)

## Software / Languages / Key Packages Used :pushpin:
- **Python**: The main programming language used for most of the code execution (e.g., data collection, etc.)
- **BeautifulSoup**: Python library used for web data scraping
- **PostgreSQL**: Database server used for data storage and querying
- **Streamlit**: Python library used to develop the web application
- **DBeave**r: Interface used to access and manage the database

## File usage :hammer_and_wrench: 
The structure of this repository follows the logical order in which the files should be executed or reviewed: data collection, transformation, and web application (data visualization).

### Data collection
The first script to run in this folder is:
- the file [Extraction_donnees_cartes.py](data_collection/Extraction_donnees_carte.py), it scrapes online card data and stores it as JSON files in folders (output, cache, etc.).

### Data transformation
Once the files are available, proceed by running the script [main.py](./data_transformation/main.py), which creates and inserts data into the decklist, cards, and tournaments tables.

Before running the script, please ensure the following:
- The data files are correctly stored in the directories specified by the variables ```output_directory``` and ```output_directory2```: datacollection/output (modify these paths if necessary).
- The database has been created with the name *postgresql* and that your local machine’s port is set to 5432 (adjust these settings if needed).
- Verify all other connection parameters to ensure proper access

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
It's importante to notice that no ETL tools were used for data transformations; only Python scripts were employed. <ins> the main.py</ins> file includes a function for anonymizing player identifiers and executes the SQL script which, in addition to inserting data into the tables, parses the date into separate components: day, month, and year.
### Data visualisation 
To launch the streamlit web application locally on your machine, open a terminal and run the following command after navigating to the directory containing the application file:

```
streamlit run app.py
```
A window will open in your browser.

## Contributors :technologist:
- [@Kila-ht](https://github.com/Kila-ht)
- [@matiornn](https://github.com/matiornn)
- [@gina_ju](https://github.com/ginaju)
- [@glossyfig](https://github.com/Glossyfig)
