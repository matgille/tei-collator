import os
import shutil

from halo import Halo
import glob
import subprocess
from lxml import etree
import itertools

import python.utils.utils as utils


def fusion_documents_tei(chemin_fichiers, chemin_corpus, xpath_transcriptions, output_dir, div_n):
    '''
    Cette fonction produit un document xml-tei maître permettant de lier chaque division entre elles.
    Ici l'universalité du code est cassée, il faut voir comment faire pour gérer ça
    :param temoin_a_traiter: le témoin à traiter sans extension pour l'instant
    :output_dir: le chemin vers le dossier contenant les fichiers XML produits
    :return: None
    '''
    try:
        os.mkdir(f"{output_dir}/chapitres")
    except FileExistsError:
        pass
    try:
        os.mkdir(f"{output_dir}/temoins")
    except FileExistsError:
        pass

    file = glob.glob(f"{chemin_fichiers}/*{div_n}*final.xml")
    shutil.copy(file, f'{output_dir}/chapitres')
    print(chemin_corpus)
    tei = {'tei': 'http://www.tei-c.org/ns/1.0'}
    xi = {'xi': 'http://www.w3.org/2001/XInclude'}
    mapping = {**tei, **xi}
    parser = etree.XMLParser(load_dtd=True,
                             resolve_entities=True)
    with open(f'{chemin_corpus}', "r") as xml_file:
        # On va copier la structure du document-base
        root = etree.parse(xml_file, parser=parser)
        # https://lxml.de/1.3/api.html#xinclude-and-elementinclude
        root.xinclude()
    trancriptions = root.xpath(xpath_transcriptions, namespaces=mapping)

    if len(trancriptions) == 0:
        raise ValueError(
            "Something went wrong with the production of the main TEI file. Please check path to the corpus.")

    for f in trancriptions:
        id = f.xpath("@xml:id", namespaces=tei)[0]
        # Je ne comprends pas pourquoi mais il faut reparser le fichier
        # pour que ça se mette bien à jour.
        with open(f'results/{id}.xml', "w") as xml_file:
            xml_file.write(etree.tostring(f).decode())
        with open(f'results/{id}.xml', "r") as xml_file:
            f = etree.parse(xml_file)
            f = f.getroot()
            del f.attrib["{http://www.w3.org/XML/1998/namespace}base"]
        id = f.xpath("@xml:id", namespaces=tei)[0]
        # On va supprimer tout ce qu'il y a dans tei:div[@type='partie'] pour mettre notre contenu
        element = f.xpath("//tei:div[@type='partie'][@n='3']", namespaces=tei)[0]
        element.getparent().remove(element)
        livre = f.xpath("//tei:div[@type='livre']", namespaces=tei)[0]
        partie = etree.SubElement(livre, "div", nsmap={'tei': 'http://www.tei-c.org/ns/1.0'})
        partie.set("type", "partie")
        partie.set("n", "3")

        # On met à jour le titre du document
        titre = f.xpath("//tei:teiHeader//tei:title", namespaces=tei)[0]
        titre.getparent().remove(titre)
        titleStmt = f.xpath("//tei:titleStmt", namespaces=tei)[0]
        new_title = f"<title><foreign>Regimiento de los pr&#237;ncipes</foreign>, édition critique " \
                    f"sur {id.replace('_', ' ')}</title>"
        titleStmt.insert(0, etree.fromstring(new_title))
        # On va chercher toutes les divisions traitées pour faire un lien vers elles dans le document
        # maître à l'aide de xi:include
        for i in range(1, 24):  # pas universel non plus, à corriger plus tard
            # fichier = f'divs/results/apparat_{id}_{i}_injected_punct.transposed.xml'
            fichier = f'{output_dir}/chapitres/apparat_{id}_{i}_final.xml'
            if os.path.exists(fichier):
                partie = f.xpath("//div[@type='partie'][@n='3']", namespaces=tei)[0]
                x_include = f"<xi:include href=\"../chapitres/{fichier.split('/')[-1]}\" xmlns:xi=\"http://www.w3.org/2001/XInclude\"/>"
                partie.insert(i, etree.fromstring(x_include))

        with open(f'{output_dir}/temoins/{id}.xml', "w") as xml_file:
            xml_file.write(etree.tostring(f).decode())


def tableau_alignement(saxon, chemin):
    xsl_apparat = 'xsl/post_alignement/tableau_alignement.xsl'
    with Halo(text='Création du tableau d\'alignement', spinner='dots'):
        cmd = f'java -jar {saxon} -o:{chemin}/tableau_alignement.html {chemin}/aligne_regroupe.xml {xsl_apparat}'
        subprocess.run(cmd.split())
    print('Création du tableau d\'alignement ✓')


def nettoyage(directory):
    '''
    Nettoie les fichiers du dossier passé en paramètre
    :param directory: le dossier cible
    :return: None
    '''
    try:
        os.mkdir(f'{directory}/aux')
    except:
        pass

    try:
        os.mkdir(f'{directory}/tex')
    except:
        pass

    try:
        os.mkdir(f'{directory}/json')
    except:
        pass

    try:
        os.mkdir(f'{directory}/xml')
    except:
        pass

    for fichier_xml in glob.glob(f'{directory}/*.xml'):
        os.rename(fichier_xml, f"{directory}/xml/{fichier_xml.split('/')[1]}")

    for fichier_tex in glob.glob(f'{directory}/*.tex'):
        os.rename(fichier_tex, f"{directory}/tex/{fichier_tex.split('/')[1]}")

    for fichier_json in glob.glob(f'{directory}/*.json'):
        os.rename(fichier_json, f"{directory}/json/{fichier_json.split('/')[1]}")

    for autre in glob.glob(f'{directory}/*.log'):
        os.rename(autre, f"{directory}/aux/{autre.split('/')[1]}")
    for autre in glob.glob(f'{directory}/*.aux'):
        os.rename(autre, f"{directory}/aux/{autre.split('/')[1]}")
    for autre in glob.glob(f'{directory}/*.nav'):
        os.rename(autre, f"{directory}/aux/{autre.split('/')[1]}")
