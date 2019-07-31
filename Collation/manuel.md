# Collation semi-automatisée: manuel

Ce document présente le fonctionnement du répertoire Collation qui permet une collation 
semi-automatisée des transcriptions individuelles du Regimiento. 

Le script xml_to_json.sh permet d'automatiser le processus complet (sauf la première étape)
Voir ce script pour plus de détails. 
Les étapes 4 et 5 viennent du fait que Collatex ne gère pas les informations 
contextuelles en sortie (xml:id par exemple) 


## Étape 0

Travail de régularisation des textes. Pas encore trop fait. 
Question: sur quoi comparer ? Des tokens régularisés ou pas ?
Peut-être pas en fait. Problème, toujours, d'homogénéité du corpus.


## Première étape. Tokénisation du corpus


Problèmes rencontrés: la ponctuation. 
Je n'arrive pas à l'extraire correctement.
La feuille tokenisation.xsl est pas propre du tout, à reprendre correctement pour avoir
à la fin une copie de corpus.xml avec des token et des id.
## 

- xsl: tokenisation.xsl

- xml: corpus.xml

- sortie:groupe.xml

## Deuxième étape. Création des fichiers de chapitre

Par pure commodité

- xsl:scission_chapitres.xsl

- xml: groupe.xml

- sortie: collation.xml


## Troisième étape. Transformation en JSON

Collatex accepte les informations supplémentaires de token 
si le format d'entrée (et de sortie) est le JSON

- xsl:transformation_json.xsl

- xml:collation.xml

- sortie:juxtaposition.json

## Quatrième étape. Alignement avec collatex.


- Collatex prend juxtaposition.json et aligne les versions. Sortie: alignement_collatex.json



## Cinquième étape. Création des apparats

Une fois les alignements réalisés, il reste à créer les apparats.
Ceci consiste à identifier les lieux variants (si cinq textes alignés ne varient pas,
il n'y a pas lieu d'indiquer une entrée d'apparat), et de regrouper
la variation par manuscrits.
C'est ce que fait le script apparat.py. 
Il lui faut en entrée un fichier json qui est une liste de dictionnaires


À partir du fichier alignement_collatex.json:
- transformation de alignement_collatex.json en XML avec dicttoxml.
- réorganisation des texte alignés juxtaposés et regroupement des lieux variants
- (création d'une table d'alignement pour visualiser les différences)
- transformation en JSON
- processage du JSON et création de l'apparat final en XML avec les xml:id











