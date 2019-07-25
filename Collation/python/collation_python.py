#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import sys
import subprocess
from collatex import *
import json
import dicttoxml
collation=Collation()

fichier_a_collationer=sys.argv[1]

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
print("Collation au format JSON")
resultat_json= collate(json.loads(entree_json1), output="json")
sortie_json = open("alignement_collatex.json", "w")
sortie_json.write(resultat_json)
sortie_json.close()
# Les résultats de la collation ne sont pas directement visible: on a la liste A puis la liste B: il faut transformer le tout pour avoir un réel alignement. Voir http://collatex.obdurodon.org/xml-json-conversion.xhtml pour la structure du résultat. 
# Le résultat de cette dernière transformation est une liste qui comprend elle-même une liste avec l'alignement. 

# Étape suivante: transformer le JSON en xml. Pour cela on peut utiliser dict2xml. 
print("Transformation du JSON en xml")
sortie_xml=open("alignement_collatex.xml", "w+")
fichier_json_a_xmliser=open('alignement_collatex.json').read()
obj=json.loads(fichier_json_a_xmliser)

# Transformation du JSON en XML
vers_xml=dicttoxml.dicttoxml(obj)
# Conversion de l'objet créé en chaîne de caractère (str)
vers_xml=vers_xml.decode("utf-8") 
sortie_xml.write(vers_xml)
sortie_xml.close()

# Création du tableau d'alignement
print("Création du tableau d'alignement")
subprocess.run(["java","-jar", "../../Saxon-HE-9.8.0-14.jar", "-o:tableau_alignement.html", "apparat_final0.xml", "../../xsl/post_alignement/tableau_alignement.xsl"])


# Passage de la table d'alignement à l'apparat
print("Création des apparats")
subprocess.run(["java","-jar", "../../Saxon-HE-9.8.0-14.jar", "-o:apparat_final0.xml", "alignement_collatex.xml", "../../xsl/post_alignement/apparat0.xsl"])


#AF Suppression de la redondance
# subprocess.run(["java","-jar", "../../Saxon-HE-9.8.0-14.jar", "-o:apparat_final.xml", "apparat_final0.xml", "../../xsl/post_alignement/apparat.xsl"])

