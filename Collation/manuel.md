# Collation semi-automatisée: manuel

Le script xml_to_json fait tout ça automatiquement (sauf la première étape)
Voir ce script pour plus de détails. 
## Première étape

Tokénisation du corpus
xsl: tokenisation.xsl
xml: corpus.xml
sortie:groupe.xml

## Deuxième étape

Création des fichiers de chapitre
xsl:scission_chapitres.xsl
xml: groupe.xml
sortie: collation.xml


## Troisième étape

Pour l'instant il faut le faire chapitre par chapitre. 

Transformation en JSON
xsl:transformation_json.xsl
xml:collation.xml
sortie:collation.json

## Quatrième étape

Collation avec collatex. création de table d'alignement.



## Cinquième étape

Création des apparats avec du xslt. En cours. 














