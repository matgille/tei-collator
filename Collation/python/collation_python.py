#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import sys
import subprocess
from collatex import *
import json
import dicttoxml
collation=Collation()

fichier_a_collationer=sys.argv[1]

# Exception: si le fichier indiqué n'est pas au format JSON, 
# demander un nouveau fichier.
try:
    assert fichier_a_collationer.endswith(".json")
except:
    while not fichier_a_collationer.endswith('.json'):
        fichier_a_collationer = input("Le fichier indiqué n'est pas un fichier JSON. Veuillez indiquer un fichier. \n")



entree_json0 = open(fichier_a_collationer, "r") # ouvrir le fichier en mode lecture et le mettre dans une variable
entree_json1 = entree_json0.read()
entree_json0.close()

# Export au format TEI (plus lisible)
#print("Collation au format TEI")
#resultat_tei= collate(json.loads(entree_json1), output="tei")
#sortie_tei = open("apparat_collatex_tei.xml", "w")
#sortie_tei.write(resultat_tei)
#sortie_tei.close()


# Export au format JSON (permet de conserver les xml:id)
print("Alignement au format JSON")
resultat_json= collate(json.loads(entree_json1), output="json")
sortie_json = open("alignement_collatex.json", "w")
sortie_json.write(resultat_json)
sortie_json.close()
# Les résultats de la collation ne sont pas directement visible: on a la liste A puis la liste B: il faut transformer le tout pour avoir un réel alignement. Voir http://collatex.obdurodon.org/xml-json-conversion.xhtml pour la structure du résultat. 
# Le résultat de cette dernière transformation est une liste qui comprend elle-même une liste avec l'alignement. 

# Étape suivante: transformer le JSON en xml. Pour cela on peut utiliser dict2xml. 
sortie_xml=open("alignement_collatex.xml", "w+")
fichier_json_a_xmliser=open('alignement_collatex.json').read()
obj=json.loads(fichier_json_a_xmliser)

# Transformation du JSON en XML
vers_xml=dicttoxml.dicttoxml(obj)
vers_xml=vers_xml.decode("utf-8") 
sortie_xml.write(vers_xml)
sortie_xml.close()


# Regroupement des lieux variants (témoin A puis témoin B puis témoin C 
# > lieu variant 1: A, B, C ; lieu variant 2: A, B, C)
print("Création des apparats")
subprocess.run(["java","-jar", "../../Saxon-HE-9.8.0-14.jar", "-o:aligne_regroupe.xml", "alignement_collatex.xml", "../../xsl/post_alignement/regroupement.xsl"])

# Création du tableau d'alignement pour visualisation
print("Création du tableau d'alignement")
subprocess.run(["java","-jar", "../../Saxon-HE-9.8.0-14.jar", "-o:tableau_alignement.html", "aligne_regroupe.xml", "../../xsl/post_alignement/tableau_alignement.xsl"])


# C'est à ce niveau que l'étape de correction devrait avoir lieu. Y réfléchir.

# Création de l'apparat: transformation de aligne_regroupe.xml en JSON
subprocess.run(["java","-jar", "../../Saxon-HE-9.8.0-14.jar", "-o:apparat_final.json", "aligne_regroupe.xml", "../../xsl/post_alignement/creation_apparat.xsl"])

# Création de l'apparat: suppression de la redondance, identification des lieux variants, 
# regroupement des lemmes
subprocess.run(["python3", "../../python/apparat.py", "apparat_final.json"])

# Réinjection des apparats. Ne marche pas pour l'instant.
print("Injection des apparats dans chaque transcription individuelle")
subprocess.run(["java","-jar", "../../Saxon-HE-9.8.0-14.jar", "-o:sortie_finale.xml", "juxtaposition.xml", "../../xsl/post_alignement/injection_apparats.xsl", "chapitre=3"])

