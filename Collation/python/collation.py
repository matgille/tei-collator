# -*- coding: utf-8 -*-
import fnmatch
import os
import sys
import time

import fonctions

# TODO: nettoyer le tout / s'occuper de la conservation des xml:id pour ne pas avoir à les régénérer
# Remerciements: merci à Élisa Nury pour ses éclaircissements sur le fonctionnement de CollateX et ses
# conseils.


saxon = "/home/mgl/Desktop/These/Edition/hyperregimiento-de-los-principes/Collation/Saxon-HE-9.8.0-14.jar"
# saxon = "../Collation/Saxon-HE-9.8.0-14.jar"
# S'il y a un argument qui est une cdc, un fichier à traiter, passer directement à l'alignement
if len(sys.argv) >= 2:  # le nom du script est le premier argument
    if type(sys.argv[1]) is str:
        argument = sys.argv[1]
        if argument.endswith('.json'):
            saxon = input("Veuillez indiquer l'emplacement absolu de votre moteur de transformation saxon.\n")
            chemin_xsl = ""
            start_time = time.time()
            fonctions.alignement(argument, saxon, chemin_xsl)
            print("Alignement CollateX ✓")
            fonctions.apparat_final("apparat_final.json")
            print("Création des apparats ✓")  # Réinjection des apparats.
            fonctions.injection(saxon, chemin_xsl)
            # Création du tableau d'alignement pour visualisation
            fonctions.tableau_alignement(saxon, chemin_xsl)
            fonctions.nettoyage()
            print("Fait en %s secondes. \n" % (time.time() - start_time))
        elif argument == '--bornes' or argument == '-b':
            borne_min = int(sys.argv[2])
            borne_max = int(sys.argv[3])
            portee = range(borne_min, borne_max)
        elif argument == '--tokenisation' or argument == '-t':
            fonctions.tokenisation(saxon)
            exit(0)
        elif argument == '--scission' or argument == '-s':
            fonctions.preparation_corpus(saxon)
            exit(0)
        elif argument == '--injection' or argument == '-i':
            chemin_sortie = '../chapitres/chapitre' + str(sys.argv[2]) + "/xml/"
            fonctions.injection(saxon, '../', int(sys.argv[2]), True, chemin_sortie)
            exit(0)
# Sinon, enclencher tout le processus de transformation, alignement, apparation.      

if not len(sys.argv) >= 2:
    portee = range(3, 23)  # Chapitres processables pour l'instant
elif len(sys.argv) is 2:
    if type(int(sys.argv[1])) is int:  # Vérifier si c'est convertible en entier (pas très propre), utiliser les
        # exceptions plutôt
        argument = int(argument)
        arg_plus_1 = argument + 1
        portee = range(argument, arg_plus_1)
chemin_xsl = "../../"

# fonctions.tokenisation(saxon)

# On lemmatise ici. À intégrer ou à faire par ses propres moyens

fonctions.preparation_corpus(saxon)

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
    fonctions.transformation_json(saxon, output_fichier_json, input_fichier_xml)

    # On se place dans le répertoire du chapitre à traiter
    os.chdir(chemin)

    # Alignement avec CollateX. Il en ressort du JSON, encore    
    fonctions.alignement('juxtaposition.json', saxon, chemin_xsl)

    fonctions.apparat_final('apparat_final.json')
    print("Création des apparats ✓")

    # Réinjection des apparats. 
    fonctions.injection(saxon, chemin_xsl, i)

    # Création du tableau d'alignement pour visualisation (le rendre optionnel)
    fonctions.tableau_alignement(saxon, chemin_xsl)

    #for file in os.listdir('.'):
    #    if fnmatch.fnmatch(file, 'apparat_*_*.xml'):
    #        fonctions.transformation_latex(saxon, file, chemin_xsl)

    fonctions.nettoyage()
    # On revient á la racine du projet pour finir la boucle      
    os.chdir("../../")

    print("Fait en %s secondes. \n" % (round(time.time() - start_time)))

# fonctions.concatenation_pdf()
