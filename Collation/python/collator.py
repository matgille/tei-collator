# -*- coding: utf-8 -*-
import fnmatch
import os
import sys
import time

from collation.collation import *
from tokenisation.tokenisation import *
from lemmatisation.lemmatisation import *
import settings

# TODO: nettoyer le tout / s'occuper de la conservation des xml:id pour ne pas avoir à les régénérer
# Remerciements: merci à Élisa Nury pour ses éclaircissements sur le fonctionnement de CollateX et ses
# conseils.


t0 = time.time()


saxon = "/home/mgl/Bureau/These/Edition/hyperregimiento-de-los-principes/Collation/Saxon-HE-9.8.0-14.jar"

# saxon = "../Collation/Saxon-HE-9.8.0-14.jar"
# S'il y a un argument qui est une cdc, un fichier à traiter, passer directement à l'alignement
# le nom du script est le premier argument

if len(sys.argv) == 1: # si il n'y a pas d'argument
    if settings.tokeniser:
        tokenisation(saxon)
    if settings.xmlId and not settings.tokeniser: # si le corpus est tokénisé mais sans xml:id
        for temoin in os.listdir('../temoins_tokenises_regularises/'):
            if temoin.endswith('.xml'):
                ajoutXmlId(temoin, temoin)
    if settings.lemmatiser:
        for temoin in os.listdir('../temoins_tokenises_regularises/'):
            if temoin.endswith('.xml'):
                lemmatisation(temoin, saxon, settings.lang)
    portee = range(3, 23)
elif type(sys.argv[1]) is int:  # Si on passe un entier, c'est un chapitre à processer
    argument = int(argument)
    arg_plus_1 = argument + 1
    portee = range(argument, arg_plus_1)
elif type(sys.argv[1]) is str:
    argument = sys.argv[1]
    if argument == '--tokenisation' or argument == '-t':
        tokenisation(saxon)
        exit(0)
    elif argument == '--preparation' or argument == '-p':
        preparation_corpus(saxon)
        exit(0)
    elif argument == '--nettoyage' or argument == '-n':
        nettoyage()
        exit(0)
    elif argument == '--injection' or argument == '-i':
        chemin_sortie = '../chapitres/chapitre' + str(sys.argv[2]) + "/xml/"
        injection(saxon, '../', int(sys.argv[2]), True, chemin_sortie)
        exit(0)
    elif argument == '--lemmatisation' or argument == '-l':
        chemin = '../xsl/pre_alignement/'
        for temoin in os.listdir('../temoins_tokenises_regularises/'):
            if temoin.endswith('.xml'):
                lemmatisation(temoin, saxon, settings.lang)
        t1 = time.time()
        temps_total = t1 - t0
        print(temps_total)
        exit(0)
# Sinon, enclencher tout le processus de transformation, alignement, apparation.


chemin_xsl = "../../"

# tokenisation(saxon) désactivé pour l'instant (risque de perte de l'annotation grammaticale)

# On lemmatise ici.

preparation_corpus(saxon)

# Création des fichiers d'apparat
# with Halo(text='Alignement automatique par chapitre', spinner='dots'):
os.chdir("..")
for i in portee:
    start_time = time.time()
    chemin = "chapitres/chapitre" + str(i)
    print("Traitement du chapitre " + str(i))
    output_fichier_json = "-o:" + chemin + "/juxtaposition.json"
    input_fichier_xml = chemin + "/juxtaposition.xml"

    # Étape avant la collation: transformation en json selon la structure voulue par CollateX
    transformation_json(saxon, output_fichier_json, input_fichier_xml)

    # On se place dans le répertoire du chapitre à traiter
    os.chdir(chemin)

    # Alignement avec CollateX. Il en ressort du JSON, encore    
    alignement('juxtaposition.json', saxon, chemin_xsl)

    apparat_final('apparat_final.json')
    print("Création des apparats ✓")

    # Réinjection des apparats. 
    injection(saxon, chemin_xsl, i)

    # Création du tableau d'alignement pour visualisation (le rendre optionnel)
    tableau_alignement(saxon, chemin_xsl)

    # for fichier in os.listdir('.'):
    #     if fnmatch.fnmatch(fichier, 'apparat_*_*out.xml'):
    #         transformation_latex(saxon, fichier, chemin_xsl)

    nettoyage()
    # On revient à la racine du projet pour finir la boucle
    os.chdir("../../")

    print("Fait en %s secondes. \n" % (round(time.time() - start_time)))

t1 = time.time()
temps_total = t1 - t0
print(temps_total)
# concatenation_pdf()
