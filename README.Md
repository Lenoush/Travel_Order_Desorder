# Projet Epitech  

## Installation librairies
```
pip install . &&\
pip install -r requirements.txt
```

## Path 
Se créer un fichier config.py avec : 
```
SNCF_gare = "path_you_want.csv"

Dataset_train  = "path_you_want.csv"
Train_train  = "path_you_want.csv"
Valid_train  = "path_you_want.csv"
Test_train  = "path_you_want.csv"

Dataset_vierge  = "path_you_want.csv"
Train_vierge  = "path_you_want.csv"
Valid_vierge  = "path_you_want.csv"
Test_vierge  = "path_you_want.csv"

Output_model  = "path_you_want.csv"
model_used_path = "path_model_you_want_to_use.model"

UPLOAD_FOLDER = ""
```

## How to use 
Pour obtenir le dataset complet , SNCF , et les splits dataset :
````
python src/data_process/build_dataset.py <vierge or train>
````

Pour entrainer le model :
````
python src/models/model_spacy/trainning.py {small, medium or large}
````

En function de votre choix small, medium ou large vous entrainez un model de spacy different.
Au prealable pour ceci, il faut avoir télécharger le model avec : (fr_core_news_sm, fr_core_news_md, fr_core_news_lg)
````
python -m spacy download {model}
````

Pour évaluer votre model sur le Valid dataset :
````
python src/models/model_spacy/evaluate.py {small, medium or large} 
````

## Branch 
Toujours push dans dev

## Style
Ce projet utilise `pre-commit` pour automatiser l'application de `black` et `ruff` à chaque push dans dev (pipeline).  
Cela garantit que le lint.

### Manuellement : 
```
black path_file.py 
ruff check path_file.py 
```
### Avec pre-commit : 
Lorsque vous faites un commit, pre-commit exécutera automatiquement black et ruff sur les fichiers modifiés.  
Si des problèmes sont détectés, vous devrez les corriger avant que le commit ne soit accepté. ( donc refaire git add . etc )  

### Correction : 
Apres utilisation nous avons decider de garder seulement lalibrairie "ruff"

## Authors & Pseudo Github
Léna Oudjman : Lenoush  
Gabrielle : Gabrielle-F  
Thomas Chevalier : TooikLeChevalier  
Mathias : matthiaspn


