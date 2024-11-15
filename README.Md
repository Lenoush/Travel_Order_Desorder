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

## How to use 
Pour obtenir le dataset complet , SNCF , et les splits dataset :
````
python src/data_process/build_dataset.py
````

Pour entrainer le model :
````
python src/models/model_spacy/small/trainning.py {small, medium or large}
````

En function de votre choix small, medium ou large vous entrainez un model de spacy different.
Au prealable pour ceci, il faut avoir télécharger le model avec : (fr_core_news_sm, fr_core_news_md, fr_core_news_lg)
````
python -m spacy download {model}
````

Pour évaluer votre model sur le Valid dataset :
````
python src/models/model_spacy/small/pretrained.py {small, medium or large} 
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
Mathias : matthiaspn


## Ameliorations retenues 
- Mettre le nom de ville en minuscule dans l'input => le model ne reverrai pas uniquement les mots avec une majuscule. 
- Rajouter dans le dataset des phrases d'entrainements avec des villes qui n'ont pas de gare sncf.
- Rajouter dans le dataset des phrases d'entrainements "ville-ville".
- Rajouter dans le dataset Valid et Test des phrases uniques qui ne sont pas dans Train.
- Pourquoi ce voice recognition ? 
- Pour quoi ce model ? Accuracy

| **Modèle**                        | **Accuracy (%)**      |
|------------------------------------|-----------------------|
| **Small without rule**            | 7.84%                 |
| **Small with rule**               | 9.68%                 |
| **Small trained without rule**    | 61.05%                |
| **Small trained with rule**       | 64.95%                |
|------------------------------------|-----------------------|
| **Medium without rule**           | 8.11%                 |
| **Medium with rule**              | 10.16%                |
| **Medium trained without rule**   | 48.97%                |
| **Medium trained with rule**      | 63.75%                |
|------------------------------------|-----------------------|
| **Large without rule**            | 10.66%                |
| **Large with rule**               | 13.73%                |
| **Large trained without rule**    | 50.62%                |
| **Large trained with rule**       | 86.15%                |

- Bien afficher toutes les erreurs : 
    - Pas en Francais 
    - Minimum 2 villes (départ/arrivée)
    - Ville non reconnue
- Inserer des critères dans la path finding :
    - Trajet direct 
    - Moins de correspondance possible 
    - Plus court possible 