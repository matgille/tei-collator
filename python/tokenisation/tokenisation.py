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
        subprocess.run(["java", "-jar", saxon, "-xi:on", path,
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


def space_tokenisation(string):
    result = re.split("([,.:;\s])", string)
    result = [item for item in result if item != " "]
    return result

def ajout_pc(string):
    result = "<pc>%s</pc>" % string
    return result

def ajout_w(string):
    result = "<w>%s</w>" % string
    return result



def tokenisation_python(general_path, files_Xpath):
    # Problem now: the comments in the searched nodes create an issue
    """
    Fonction de tokénisation qui n'a pas recours au XSL
    :general_path: le chemin vers le fichier tei maître
    :files_Xpath: le chemin xpath vers chacun des fichiers TEI en cas de tei:teiCorpus
    :return: les fichiers xml tokénisés.
    """
    tei = {'tei': 'http://www.tei-c.org/ns/1.0', 'xi':'http://www.w3.org/2001/XInclude'}
    parser = etree.XMLParser(remove_comments=True)
    f = etree.parse(general_path, parser=parser)
    f.xinclude() # résoud les inclusions XInclude.
    root = f.getroot()
    print(files_Xpath)
    for tei_file in root.xpath(files_Xpath, namespaces=tei):
        parsed_file = tei_file.xpath("descendant::tei:body/descendant::tei:head|descendant::tei:body/descendant::tei:p", namespaces=tei) # on va charger chaque fichier xml
        ET.register_namespace('', "http://www.tei-c.org/ns/1.0")
        for element in parsed_file:
            element_info = {}
            element_info[element.tag] = element.attrib
            print(element_info)
            pattern = re.compile("\s+$")
            pattern2 = re.compile("\s+")
            for k in element_info:
                attributes = []
                for x in element_info[k]:
                    attributes.append("%s=\"%s\"" % (x, element_info[k][x]))
            if " ".join(attributes) != "":
                joined_attributes = " %s" % " ".join(attributes)
            else:
                joined_attributes = ""
            print(" ".join(attributes) == "")
            pattern3 = re.compile("^<%s xmlns=\"http://www.tei-c.org/ns/1.0\"%s>" % (element.tag.split("}")[-1], joined_attributes))
            pattern4 = re.compile("</%s>" % element.tag.split("}")[-1])
            prep = etree.tostring(element, encoding='utf8', method='xml').decode('utf8').replace("<?xml version=\'1.0\' encoding=\'utf8\'?>", "").replace("\n", "")
            prep = "%s" % pattern.sub("", prep)
            input_element = prep.replace("\n", "\s")
            input_element = pattern.sub("", input_element)
            input_element = pattern2.sub(" ", input_element)
            input_element = pattern3.sub("", input_element)
            input_element = pattern4.sub("", input_element)
            input_element = input_element.replace(r"> <", "><")
            # input_element = re.split("(?<!<[cp]b)\s", input_element)
            print(input_element)
            dict0 = {}
            try:
                pattern_between_quotes = re.finditer(">(.*?)<", input_element)
                for match in pattern_between_quotes:
                    dict0[match.span()] = match.group(1)
                pattern_between_quotes = [item for item in pattern_between_quotes]
            except:
                pattern_between_quotes = []
            try:
                beginning_pattern = re.search(r"^(.*?)<", input_element)
                beginning_pattern_span = beginning_pattern.span()
                beginning_pattern = beginning_pattern.group(1)
                dict0[beginning_pattern_span] = beginning_pattern
            except:
                beginning_pattern = "none"
            try:
                ending_pattern = re.search(r">([^>]*)$", input_element)
                ending_pattern_span = ending_pattern.span()
                ending_pattern = ending_pattern.group(1)
                dict0[ending_pattern_span] = ending_pattern
            except:
                ending_pattern = "none"
            pattern_between_quotes.insert(0, beginning_pattern)
            pattern_between_quotes.append(ending_pattern)
            newlist = [space_tokenisation(item) for item in pattern_between_quotes]
            liste1 = []
            for i in newlist:
                for j in i:
                    liste1.append(j)

            liste3 = []
            for key in dict0:
                liste3.append([key, dict0[key]])
            liste3.sort(reverse=True,key = lambda x: x[0])

            for idx, val in enumerate(liste3):
                liste4 = []
                val[1].replace("&amp;", "&")
                for token in re.split("([,.:;!?¿\s])", val[1]):
                    if re.match("[,.:;!?¿]", token):
                        liste4.append(ajout_pc(token))
                    elif re.match("\s", token):
                        pass
                    else:
                        liste4.append(ajout_w(token))
                liste3[idx] = [val[0], ["".join(liste4)]]
            input_element = list(input_element)
            for i in liste3:
                input_element[i[0][0]:i[0][1]] = i[1]
            for idx, val in enumerate(input_element):
                if len(val) > 1:
                    input_element[idx] = ">%s<" % val
            input_element = "".join(input_element).replace("<w></w>", "")
            input_element = input_element.replace("--><", "-->")
            input_element = input_element.replace(">w", "><w")
            input_element = re.sub("^>", "", input_element)
            input_element = re.sub("<$", "", input_element)
            element = element.tag.split("}")[1]
            input_element = "<%s>%s</%s>" % (element, input_element, element)
            print(input_element)
            ET.fromstring(input_element)