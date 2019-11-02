# Collation semi-automatisée: manuel

Ce document présente le fonctionnement du répertoire Collation qui permet une collation 
semi-automatisée des transcriptions individuelles du Regimiento. 


Les étapes 3 et 4 viennent du fait que Collatex ne gère pas les informations
contextuelles en sortie (xml:id par exemple) 


## Étape 1 Tokénisation et régularisation

Travail de régularisation des textes. On va comparer les textes sur
des tokens régularisés (i.e, avec seulement des noeuds textuels. On régularise les tei:hi par exemple).
Deux dossiers sont produits: un dossier avec les fichiers tokénisés et régularisés, un dossier avec
les fichiers simplement tokénisés


- xml: corpus.xml (fichier TEI de la thèse)

- xsl: tokenisation.xsl, regularisation.xsl

- sortie: temoins_tokenises/ et temoins_tokenises_regularises



## Premièr étape bis: lemmatisation et POS-tagging puis regroupement

C'est ici doivent être lemmatisés et pos-taggés les fichiers. On lemmatise les fichiers régularisés. Output idem que Input.
J'utilise un script ailleurs dans mon dossier de thèse.

- entrée: temoins_tokenises_regularises

- xsl: regroupement.xsl

- sortie:groupe.xml



## Deuxième étape. Création des fichiers de chapitre

Par pure commodité

- xsl:scission_chapitres.xsl

- xml: groupe.xml

- sortie: par chapitre, collation.xml


## Troisième étape. Transformation en JSON

Collatex accepte les informations supplémentaires de token 
si le format d'entrée (et de sortie) est le JSON

- xsl:transformation_json.xsl

- xml:collation.xml

- sortie:juxtaposition.json


## Quatrième étape. Alignement avec collatex.

- Collatex prend juxtaposition.json et aligne les versions **sur les lemmes**. Sortie: alignement_collatex.json


## Cinquième étape. Création des apparats

Une fois les alignements réalisés, il reste à créer les apparats.
Ceci consiste à identifier les lieux variants (si cinq textes alignés ne varient pas,
il n'y a pas lieu d'indiquer une entrée d'apparat), et de regrouper
la variation par manuscrits; puis il y a typage des apparats avec les informations de lemmes et de pos.
Il lui faut en entrée un fichier json qui est une liste de dictionnaires:

À partir du fichier alignement_collatex.json:
- transformation de alignement_collatex.json en XML avec dicttoxml.
- réorganisation des texte alignés juxtaposés et regroupement des lieux variants avec une XSL (regroupement.xsl)
- (création d'une table d'alignement pour visualiser les différences)
- transformation en JSON
- processage du JSON et création de l'apparat final en XML avec les xml:id.

sortie: apparat_collatex.xml


## Sixième étape: réinjection dans les transcriptions tokénisées

On va avoir ici chaque transcription avec les informations d'apparat réinjectées.


injection_apparats.xsl (app + redondance). Entrée: temoins_tokenises/manuscrit_Y.xml comparé avec apparat_collatex.xml. Sortie: apparat_out.xml

injection_apparats2.xsl (noeuds non textuels dans les rdg). Entrée: apparat_outb.xml avec manuscrit_Y.xml. Sortie: apparat_outb.xml

injection_ponctuation.xsl. Entrée: apparat_out2.xml avec manuscrit_Y.xml. Sortie: apparat_manuscrit_Y_3_3_chapitre_out.xml


## Septième étape: transformation en LaTeX

entrée: apparat_manuscrit_Y_3_3_chapitre_out.xml
xsl: conversion_latex.xsl
sortie: du .tex.

Puis compilation et nettoyage.
