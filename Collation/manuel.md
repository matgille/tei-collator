# Collation semi-automatisée: manuel

Le script xml_to_json fait tout ça automatiquement (sauf la première étape)
Voir ce script pour plus de détails. 

## Étape 0

Travail de régularisation des textes. Pas encore trop fait. 
Question: sur quoi comparer ? Des tokens régularisés ou pas ?
Peut-être pas en fait. Problème, toujours, d'homogénéité du corpus.


## Première étape. Tokénisation du corpus


Problèmes rencontrés: la ponctuation. 
Je n'arrive pas à l'extraire correctement.
La feuille tokenisation.xsl est pas propre du tout, à reprendre correctement pour avoir
à la fin une copie de corpus.xml avec des token et des id.

- xsl: tokenisation.xsl

- xml: corpus.xml

- sortie:groupe.xml

## Deuxième étape. Création des fichiers de chapitre



- xsl:scission_chapitres.xsl

- xml: groupe.xml

- sortie: collation.xml


## Troisième étape. Transformation en JSON


- xsl:transformation_json.xsl

- xml:collation.xml

- sortie:juxtaposition.json

## Quatrième étape. Collation avec collatex.

 Crée une table d'alignement.



## Cinquième étape. Création des apparats

 Avec du xslt. En cours. 














