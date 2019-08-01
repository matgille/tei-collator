#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import sys
import os
import collation_python
import subprocess
from collatex import *
from halo import Halo
import json
import dicttoxml


# S'il y a un argument, un fichier à traiter, passer directement à l'alignement
if len(sys.argv) > 1:
    argument = sys.argv[1]
    if argument.endswith('.json'):
        saxon = input("Veuillez indiquer l'emplacement absolu de votre moteur de transformation saxon.\n")
        chemin_xsl = ""
        collation_python.alignement(argument, saxon, chemin_xsl)
        print("Alignement CollateX ✓")
        collation_python.apparat_final("apparat_final.json")
        print("Création des apparats ✓")# Réinjection des apparats. Ne marche pas pour l'instant.
        collation_python.injection(saxon,chemin_xsl)        
        # Création du tableau d'alignement pour visualisation
        collation_python.tableau_alignement(saxon,chemin_xsl)        
        collation_python.nettoyage()
        

# Sinon, enclencher tout le processus de transformation, alignement, apparation.      
else:
    saxon = "/Users/squatteur/Desktop/These/hyperregimiento-de-los-principes/Collation/Saxon-HE-9.8.0-14.jar"
    chemin_xsl = "../../"
    # Nettoyage et tokénisation du corpus parallélisé.
    # Ne fonctionne pas. Il faut Saxon PE pour pouvoir bénéficier des fonctions étendues comme exslt:random()
    # echo "Nettoyage et tokénisation du corpus"
    # fichier_origine="../../Dedans/XML/corpus/corpus.xml"
    # java -jar $saxon -o:../temoins/groupe.xml $fichier_origine ../xsl/pre_alignement/tokenisation.xsl
    
    
    # Scission du corpus en dossiers de chapitres
    with Halo(text = 'Scission du corpus, création de dossiers et de fichiers par chapitre', spinner='dots'):
        subprocess.run(["java","-jar", saxon, "-o:../tmp/tmp.tmp", "../temoins/groupe.xml", "../xsl/pre_alignement/scission_chapitres.xsl"])
    print("Scission du corpus, création de dossiers et de fichiers par chapitre ✓ \n")
    
    # Création des fichiers d'apparat
    #with Halo(text='Alignement automatique par chapitre', spinner='dots'):
    os.chdir("..")
    for i in range(3,24):
        chemin = "chapitres/chapitre" + str(i)
        print("Traitement du chapitre " + str(i))
        output_fichier_json = "-o:"+ chemin + "/juxtaposition.json"
        intput_fichier_xml = chemin + "/juxtaposition.xml"
        
        collation_python.transformation_json(saxon, output_fichier_json, intput_fichier_xml)
        
        os.chdir(chemin)        
            
        collation_python.alignement("juxtaposition.json", saxon, chemin_xsl)
        
        collation_python.apparat_final("apparat_final.json")
        print("Création des apparats ✓")        
        
        # Réinjection des apparats. Ne marche pas pour l'instant.
        collation_python.injection(saxon,chemin_xsl)
        
        # Création du tableau d'alignement pour visualisation
        collation_python.tableau_alignement(saxon,chemin_xsl)
        
        collation_python.nettoyage()        
        os.chdir("../../")
        print("Fait! \n")





