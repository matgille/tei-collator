import sys
from collatex import *
import json
import dicttoxml
from xml.etree.ElementTree import ElementTree, tostring
import xml.etree.ElementTree as ET
from lxml import etree

fichier_a_convertir=sys.argv[1]


document_source = open(fichier_a_convertir, "r")
contenu = document_source.read()
obj = json.loads(contenu)
resultat = dicttoxml.dicttoxml(obj)
resultat_xml = ET.fromstring(resultat)

resultat_xml2=tostring(resultat_xml, encoding="unicode")# règle un problème d'encodage, voir

collation_xml = open("collation_avec_id.xml", "w")
collation_xml.write(resultat_xml2)
collation_xml.close()
