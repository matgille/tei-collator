# tei_collator

Projet qui contient les fichiers de l'outil de collation automatisée dont je me sers pour produire les fichiers de ma 
thèse de doctorat.


## Brique de lemmatisation



Ce script contient une brique de lemmatisation permet l'annotation grammaticale d'une source XML en castillan médiéval 
conforme TEI tout en conservant l'encodage de celle-ci.

## Dépendances

Ce script s'appuie grâce à plusieurs logiciels ou librairies pythons, donc les principales sont: 
- Freeling ([ici](http://nlp.lsi.upc.edu/freeling/))
- Pie ([ici](https://pypi.org/project/nlp-pie/))
- CollateX ([ici](https://pypi.org/project/collatex/))


## Fonctionnement


Le latin avec Pie le castillan médiéval (Freeling) sont supportés pour le moment. 

Les langues médiévales sont annotés de façon relativement exhaustive (lemmes, parties du discours, morphologie).

Les étiquettes de parties du discours sont les suivantes: 
- CATTEX pour le latin médiéval;
- EAGLES pour le castillan médiéval. Attention, EAGLES propose un jeu d'étiquettes qui fusionne parties du discours et 
morphologie. 

## Ce que permet ce programme

+ La collation automatisée de documents structurés en TEI *et pré-traités*. Un paramétrage permet d'indiquer la
 structure des documents, et les divisions à comparer (`tei:div[@type='chapitre']` par exemple, ou `tei:p`). Un 
 pré-alignement est nécessaire: un travail de mise en regard de chaque structure, à l'aide d'identifiant concordants 
 (pour l'instant, `@n`, mais cela est voué à être modifié) permet la collation paragraphe par paragraphe. 
+ La création de tableaux d'alignements division par division

## Ce que ne permet pas ce programme

+ Une analyse globale de la différence entre 2+ témoins non structurés. 
+ La production d'un document complet en sortie (pour l'instant, on divise la sortie division par division, chapitre, 
acte, scène, ou autre, mais ce sera amené à changer).

## *Caveat*

La tokénisation est ici propre au castillan médiéval, et fonctionne avec le latin; pour d'autres langues, il faudra 
probablement écrire des règles différentes. En ce qui concerne les éléments à prendre en compte lors de cette 
tokénisation (tei:hi qui peuvent être à cheval sur un token par exemple, ou tei:pb), les règles portent
sur mon propre corpus et devront aussi être modifiées. Ces règles n'affectent pas le fonctionnement du script sur
un encodage purement structurel.


## Projets sur lequel s'appuie `tei_collator`
Ce projet est fortement inspiré du projet [Falcon](https://github.com/CondorCompPhil/falcon) (Jean-Baptiste Camps, 
Lucence Ing et Elena Spadini), pour la méthode de collation (lemmatisation, alignement sur les lemmes, typage des 
variantes), ainsi que pour la possibilité de lemmatiser avec plusieurs outils, freeling ou pie, et sur le typage des 
variantes. La différence principale réside dans le travail sur la réinjection des apparats dans les documents XML-TEI
originels, entres autres informations (notes par exemple), dans le but de garder la structure originelle de chaque 
document représentant le texte
d'un témoin. 



## Remerciements, crédits et réferences
Merci à Jean-Baptiste Camps de m'avoir fait découvrir Freeling; merci à Thibault Clérice pour son aide sur pie. 

Pour collatex:
* Dekker, Ronald Haentjens. « Computer automated collation with CollateX and Python ». Presentation given at DH Benelux 
in The Hague, 2014, 12–13. 
[Abstract](https://2014.dhbenelux.org/wp-content/uploads/sites/11/2019/04/demo-haentjens-dekker.pdf).


Le modèle de lemmatisation présent sur le dépôt est celui entraîné par Thibault Clérice (ÉnC) sur les données du LASLA
([ici](https://github.com/chartes/deucalion-model-lasla)):
*   Thibault Clérice. (2019, February 1). chartes/deucalion-model-lasla: LASLA Latin Lemmatizer - Alpha (Version 0.0.1). 
Zenodo. http://doi.org/10.5281/zenodo.2554847, _latest version:_[Here](https://doi.org/10.5281/zenodo.2554846)

Pour Freeling ([site](http://nlp.lsi.upc.edu/freeling/)): 
* Lluís Padró and Evgeny Stanilovsky. *FreeLing 3.0: Towards Wider Multilinguality*. Proceedings of the Language 
Resources and Evaluation Conference (LREC 2012) ELRA. Istanbul, Turkey. May, 2012.

Pour Falcon:
* Camps, Jean-Baptiste, Lucence Ing, et Elena Spadini. « Collating Medieval Vernacular Texts: Aligning Witnesses, 
Classifying Variants », 2019. [Abstract](https://dev.clariah.nl/files/dh2019/boa/0882.html).
 
* Jean Baptiste Camps, Lucence Ing et Elena Spadini,  '**CondorCompPhil/falcon** (For Alignment, Lemmatization and 
CollatioN)', [dépôt git](https://github.com/CondorCompPhil/falcon), 2018-2019.

## Citer ce projet

Pour citer ce projet, merci d'en référer à ma thèse de doctorat (en préparation): 

`Matthias GILLE LEVENSON, La version B du "Regimiento de los prínçipes" glosé (1374-1494) : étude et éditions de la partie sur le gouvernement de la cité par temps de guerre (III,3), Thèse de doctorat en préparation sous la direction de Carlos HEUCH et de Jesús RODRÍGUEZ VELASCO.`

## Licence

Sauf indication contraire, les fichiers sont publiés [sous licence NPOSL-3.0](https://opensource.org/licenses/NPOSL-3.0). 

Le modèle de lemmatisation, produit par Thibault Clérice (`modele.tar`) ainsi que la version de saxon présente sur le 
dépôt sont distribués sous licence [Mozilla Public License version 2.0](https://www.mozilla.org/en-US/MPL/2.0/).
