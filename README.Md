# Projet Epitech  

## Installation librairies
```
pip install . &&\
pip install -r requirements.txt
```

## Path 
Se créer un fichier config avec : 
```
SNCF_gare = "path_you_want.csv"
Dataset = "path_you_want.csv"
Train = "path_you_want.csv"
Valid = "path_you_want.csv"
Test = "path_you_want.csv"
```

## Data
Pour obtenir le dataset
````
python src/data_process/build_dataset.py
````

Pour Split le dataset en train, valid et test
````
python /src/data_process/data_splitting.py
````

## Branch 
Toujours push dans Dev

## Style
Ce projet utilise `pre-commit` pour automatiser l'application de `black` et `ruff` à chaque commit.  
Cela garantit que le code respecte les normes de style définies.  

### Manuellement : 
```
black path_file.py 
ruff check path_file.py 
```
### Avec pre-commit : 
Lorsque vous faites un commit, pre-commit exécutera automatiquement black et ruff sur les fichiers modifiés.  
Si des problèmes sont détectés, vous devrez les corriger avant que le commit ne soit accepté. ( donc refaire git add . etc )  

## Authors 
Léna Oudjman : Lenoush  
Gabrielle : Gabrielle-F  
Thomas Chevalier : TooikLeChevalier  
Mathias :   


## Ameliorations retenues 
- Mettre le nom de ville en minuscule dans l'input => le model ne reverrai pas uniquement les mots avec une majuscule. 
- Rajouter des phrases entrainements avec des villes qui n'ont pas de gare sncf.
- Pourquoi ce voice recognition ? 
- Pour quoi ce model ? => Comparaison en cours. 
- Bien afficher toutes les erreurs : 
    - Pas en Francais 
    - Minimum 2 villes (départ/arrivée)
    - Ville non reconnue
- Inserer des critères dans la path finding :
    - Trajet direct 
    - Moins de correspondance possible 
    - Plus court possible 