import random
import string
from halo import Halo
import os
import subprocess
import xml.etree.ElementTree as ET
from lxml import etree
import re


def generateur_lettre_initiale(size=1, chars=string.ascii_lowercase):  # éviter les nombres en premier caractère de
    # l'@xml:id (interdit)
    return ''.join(random.choice(chars) for _ in range(size))


def generateur_id(size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return generateur_lettre_initiale() + ''.join(random.choice(chars) for _ in range(size))


def ajoutXmlId(fichier_entree, fichier_sortie):
    """Création des xml:id pour chaque token.
    TODO: trouver un
    moyen de pouvoir actualiser la transcription sans avoir à
    re-générer des xml:id. Faire des groupes de n tokens pour retrouver les emplacements ?
    pour chaque token, récupérer le bi/trigramme suivant et aller le retrouver dans le fichier de sortie
    Si il est trouvé, copier l'id du token dans la fichier de sortie. Si il n'est pas trouvé, générer un
    xml:id. Je pense que ça peut marcher pour des modifications de faible volume (un mot); je ne sais pas
    ce que ça peut donner avec un ajout d'une phrase omise par inadvertance par exemple. Ou alors on peut utiliser
    collatex aussi. """
    tei = {'tei': 'http://www.tei-c.org/ns/1.0'}
    f = etree.parse(fichier_entree)
    root = f.getroot()
    tokens = root.xpath("//tei:w", namespaces=tei)
    for w in tokens:
        w.set("{http://www.w3.org/XML/1998/namespace}id", generateur_id())
    with open(fichier_sortie, "w+") as sortie_xml:
        string = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True).decode('utf8')
        sortie_xml.write(str(string))


def tokenisation(saxon, path):
    with Halo(text='Tokénisation du corpus parallélisé.', spinner='dots'):
        subprocess.run(["java", "-jar", saxon, "-xi:on", path,
                        "xsl/pre_alignement/tokenisation.xsl"])
        for transcription_individuelle in os.listdir("temoins_tokenises"):
            fichier_xml = "temoins_tokenises/" + transcription_individuelle
            ajoutXmlId(fichier_xml, fichier_xml)
        subprocess.run(["java", "-jar", saxon, "-xi:on", "temoins_tokenises/Sal_J.xml",
                        "xsl/pre_alignement/regularisation.xsl"])

    print("Tokénisation et régularisation du corpus pour alignement ✓")




