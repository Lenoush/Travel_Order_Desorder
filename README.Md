## Projet Epitech  

## Installation 
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
