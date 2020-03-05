import random
import string
from halo import Halo
import os
import subprocess
import xml.etree.ElementTree as ET
from lxml import etree


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


def tokenisation(saxon):
    # for fichier in os.listdir(
    #         '/home/mgl/Bureau/These/Edition/hyperregimiento-de-los-principes/Dedans/XML/temoins/castillan/'):
    #     print(fichier)
    #     if fnmatch.fnmatch(fichier, 'Sev_R.xml'):
    #         chemin_fichier = "/home/mgl/Bureau/These/Edition/hyperregimiento-de-los-principes/Dedans/XML/temoins/castillan/" + fichier
    #         parser = etree.XMLParser(load_dtd=True, resolve_entities=False)
    #         f = etree.parse(chemin_fichier, parser=parser)
    #         f.xinclude()  # https://lxml.de/3.3/api.html#xinclude-and-elementinclude
    #         root = f.getroot()
    #         text_root = str(etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True))
    #         text_root = text_root.replace("&", "±")
    #         text_root = text_root.replace(";", "™")
    #         text_root = text_root.replace("\\n", "")
    #         tree = ET.ElementTree(ET.fromstring(text_root))
    #         print(text_root)
    #         chemin_fichier_test = "/home/mgl/Bureau/These/Edition/hyperregimiento-de-los-principes/Dedans/XML/temoins/test/" + fichier
    #         with open(chemin_fichier_test, "w+") as sortie_xml:
    #             sortie_xml.write(text_root)
    # tei = {'tei': 'http://www.tei-c.org/ns/1.0', 'xi': 'http://www.w3.org/2001/XInclude',
    #        'xml': 'http://www.w3.org/XML/1998/namespace'}
    with Halo(text='Tokénisation du corpus parallélisé.', spinner='dots'):
        subprocess.run(["java", "-jar", saxon, "-xi:on", "../Dedans/XML/corpus/corpus.xml",
                        "xsl/pre_alignement/tokenisation.xsl"])
        for transcription_individuelle in os.listdir("temoins_tokenises"):
            fichier_xml = "temoins_tokenises/" + transcription_individuelle
            ajoutXmlId(fichier_xml, fichier_xml)
        subprocess.run(["java", "-jar", saxon, "-xi:on", "temoins_tokenises/Sal_J.xml",
                        "xsl/pre_alignement/regularisation.xsl"])

    print("Tokénisation et régularisation du corpus pour alignement ✓")


# def nouvelle_tokenisation():
#     parser = etree.XMLParser(load_dtd=True,
#                              resolve_entities=True)  # inutile car les entités ont déjà été résolues
#     # auparavant normalement, mais au cas où.
#     fichier_xml = "/home/mgl/Bureau/These/Edition/hyperregimiento-de-los-principes/Dedans/XML/corpus/corpus.xml"
#     f = etree.parse(fichier_xml, parser=parser)
#     f.xinclude()  # https://lxml.de/3.3/api.html#xinclude-and-elementinclude
#     root = f.getroot()
#     tei = {'tei': 'http://www.tei-c.org/ns/1.0', 'xi': 'http://www.w3.org/2001/XInclude',
#            'xml': 'http://www.w3.org/XML/1998/namespace'}
#     fichiers_tei = root.xpath("descendant::tei:TEI[ancestor::tei:teiCorpus[@xml:id='castB']][@type='transcription']",
#                               namespaces=tei)
#     for fichier in fichiers_tei:
#         groupe_paragraphes = "descendant::tei:p"
#         paragraphes = fichier.xpath(groupe_paragraphes, namespaces=tei)
#         for paragraphe in paragraphes:
#             paragraphe.xpath('tokenize(., "\s+")')
#             test = etree.tostring(paragraphe, pretty_print=True)
#             print(test.decode().split(' '))
#         identifiant_fichier = fichier.xpath('@xml:id', namespaces=tei)
#         fichier_sortie = "/home/mgl/Bureau/These/Edition/hyperregimiento-de-los-principes/Collation/temoins_tokenises/" + str(
#             identifiant_fichier[0]) + ".xml"
#         os.makedirs(os.path.dirname(fichier_sortie),
#                     exist_ok=True)  # https://stackoverflow.com/a/12517490 (si le dossier n'existe pas)
#         with open(fichier_sortie, "w+") as sortie_xml:
#             chaine = etree.tostring(fichier, pretty_print=True, encoding='utf-8', xml_declaration=True).decode('utf8')
#             sortie_xml.write(str(chaine))
