# -*- coding: utf-8 -*-
import sys
import fnmatch
import os
import time
import fonctions
import subprocess
from collatex import *
from halo import Halo
import json
import dicttoxml

# Remerciements: merci à Élisa Nury pour ses éclaircissements sur le fonctionnement de CollateX et ses
# conseils.


# S'il y a un argument qui est une cdc, un fichier à traiter, passer directement à l'alignement
if len(sys.argv) >= 2:
    if type(sys.argv[1]) is str:
        argument = sys.argv[1]
        if argument.endswith('.json'):
            saxon = input("Veuillez indiquer l'emplacement absolu de votre moteur de transformation saxon.\n")
            chemin_xsl = ""
            start_time = time.time() 
            fonctions.alignement(argument, saxon, chemin_xsl)
            print("Alignement CollateX ✓")
            fonctions.apparat_final("apparat_final.json")
            print("Création des apparats ✓")# Réinjection des apparats. Ne marche pas pour l'instant.
            fonctions.injection(saxon,chemin_xsl)        
            # Création du tableau d'alignement pour visualisation
            fonctions.tableau_alignement(saxon,chemin_xsl)        
            fonctions.nettoyage()
            print("Fait en %s secondes. \n" % (time.time() - start_time))
        
     

# Sinon, enclencher tout le processus de transformation, alignement, apparation.      

if not len(sys.argv) >= 2:
    portee = range(3,11) #Chapitres processables pour l'instant
else:    
    if type(int(sys.argv[1])) is int:#Vérifier si c'est convertible en entier (pas très propre)
        argument = int(argument)
        arg_plus_1 = argument + 1
        portee = range(argument, arg_plus_1)
saxon = "/Users/squatteur/Desktop/These/hyperregimiento-de-los-principes/Collation/Saxon-HE-9.8.0-14.jar"
chemin_xsl = "../../"

fonctions.tokenisation(saxon)

fonctions.scission_corpus(saxon)


# Création des fichiers d'apparat
#with Halo(text='Alignement automatique par chapitre', spinner='dots'):
os.chdir("..")
for i in portee:
    start_time = time.time()
    chemin = "chapitres/chapitre" + str(i)
    print("Traitement du chapitre " + str(i))
    output_fichier_json = "-o:"+ chemin + "/juxtaposition.json"
    input_fichier_xml = chemin + "/juxtaposition.xml"
    
    # Étape avant la collation: transformation en json selon la structure voulue par CollateX
    fonctions.transformation_json(saxon, output_fichier_json, input_fichier_xml)
    
    # On se place dans le répertoire du chapitre à traiter
    os.chdir(chemin)        
    
    # Alignement avec CollateX. Il en ressort du JSON, encore    
    fonctions.alignement("juxtaposition.json", saxon, chemin_xsl)
    
    
    
    fonctions.apparat_final("apparat_final.json")
    print("Création des apparats ✓")        
    
    # Réinjection des apparats. 
    fonctions.injection(saxon,chemin_xsl, i)
    
    # Création du tableau d'alignement pour visualisation (le rendre optionnel)
    fonctions.tableau_alignement(saxon,chemin_xsl)
    
    for file in os.listdir('.'):
        if fnmatch.fnmatch(file, 'apparat_*_*.xml'):
            fonctions.transformation_latex(saxon, file, chemin_xsl)
        
    fonctions.nettoyage()  
    
    # On revient á la racine du projet pour finir la boucle      
    os.chdir("../../")
    print("Fait en %s secondes. \n" % (round(time.time() - start_time)))





