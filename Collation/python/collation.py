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
collation=Collation()

oxygen = "../Saxon-HE-9.8.0-14.jar"
oxygen2 = "Saxon-HE-9.8.0-14.jar"
# Nettoyage et tokénisation du corpus parallélisé.
# Ne fonctionne pas. Il faut Saxon PE pour pouvoir bénéficier des fonctions étendues comme exslt:random()
# echo "Nettoyage et tokénisation du corpus"
# fichier_origine="../../Dedans/XML/corpus/corpus.xml"
# java -jar "../$oxygen" -o:../temoins/groupe.xml $fichier_origine ../xsl/pre_alignement/tokenisation.xsl


# Scission du corpus en dossiers de chapitres
with Halo(text = 'Scission du corpus, création de dossiers et de fichiers par chapitre', spinner='dots'):
    subprocess.run(["java","-jar", oxygen, "-o:../tmp/tmp.tmp", "../temoins/groupe.xml", "../xsl/pre_alignement/scission_chapitres.xsl"])


# Création des fichiers d'apparat
#with Halo(text='Alignement automatique par chapitre', spinner='dots'):
os.chdir("..")
for i in range(3,5):
    chemin = "chapitres/chapitre" + str(i)
    print("Traitement du chapitre " + str(i))
    output_fichier_json = "-o:"+ chemin + "/juxtaposition.json"
    intput_fichier_xml = chemin + "/juxtaposition.xml"
    
    with Halo(text = 'Transformation en json', spinner='dots'):
        subprocess.run(["java","-jar", oxygen2, output_fichier_json, intput_fichier_xml, "xsl/pre_alignement/transformation_json.xsl"])
    
    
    annonce_collation_chapitre = "Collation du chapitre" + str(i)
    with Halo(text = annonce_collation_chapitre, spinner='dots'):
        os.chdir(chemin)        
        
    collation_python.main("juxtaposition.json")
    
    with Halo(text = "Nettoyage du dossier", spinner='dots'):
        os.remove("juxtaposition.json")
        os.remove("alignement_collatex.json")
        os.chdir("../../")
    print("Fait!")





