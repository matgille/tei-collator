import os
from halo import Halo
import glob
import subprocess
from lxml import etree
import itertools


import python.utils.utils as utils


def transformation_latex(saxon, fichier_xml, fusion, chemin='divs'):
    '''
    Production des fichiers pdf
    :param saxon:
    :param fichier_xml:
    :param fusion: produit-on un pdf commun ou un pdf pour une division en particulier ?
    :param chemin:
    :return:
    '''
    fichier_tex = f"{fichier_xml.split('.')[0]}.tex"
    fichier_tex_seul = f'{chemin}/{fichier_tex.split("/")[-1]}'
    fichier_sans_extension = fichier_tex_seul.replace(".tex", "")
    print(f"fichier tex seul: {chemin}/{fichier_tex_seul}")
    chemin_xsl_apparat = "xsl/post_alignement/conversion_latex.xsl"
    fichier_tex_sortie = f"-o:{fichier_tex_seul}"
    param_fusion = f'fusion={str(fusion)}'
    print("Création des fichiers pdf ✓")
    subprocess.run(["java", "-jar", saxon, "-xi:on", fichier_tex_sortie, fichier_xml, param_fusion, chemin_xsl_apparat])
    with open(fichier_tex_seul, "r") as input_tex_file:
        tex_file = input_tex_file.read()
        tex_file = tex_file.replace("%", "\%")
        tex_file.replace("\\%", "\%")
    with open(fichier_tex_seul, "w") as output_tex_file:
        output_tex_file.write(tex_file)
    print(f'current dir: {os.getcwd()}')
    utils.clean_spaces(fichier_tex_seul)
    subprocess.run(["latexmk", "-xelatex", f"-output-directory={chemin}", fichier_tex_seul])


def fusion_documents_tei(temoin_a_traiter):
    '''
    Cette fonction produit un document xml-tei maître permettant de lier chaque division entre elles.
    Ici l'universalité du code est cassée, il faut voir comment faire pour gérer ça
    :param temoin_a_traiter: le témoin à traiter sans extension pour l'instant
    :return: None
    '''
    tei = {'tei': 'http://www.tei-c.org/ns/1.0'}
    xi = {'xi': 'http://www.w3.org/2001/XInclude'}
    parser = etree.XMLParser(load_dtd=True,
                             resolve_entities=True)
    with open(f'temoins_tokenises/{temoin_a_traiter}.xml', "r") as xml_file:
        # On va copier la structure du document-base
        f = etree.parse(xml_file, parser=parser)

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
                    f"sur {temoin_a_traiter.replace('_', ' ')}</title>"
        titleStmt.insert(0, etree.fromstring(new_title))

        # On va chercher toutes les divisions traitées pour faire un lien vers elles dans le document
        # maître à l'aide de xi:include
        for i in range(1, 24):  # pas universel non plus, à corriger plus tard
            for fichier in glob.glob(f'divs/div*/apparat_{temoin_a_traiter}_{i}_final.xml'):
                partie = f.xpath("//div[@type='partie'][@n='3']", namespaces=tei)[0]
                x_include = f"<xi:include href=\"{('/').join(fichier.split('/')[1:])}\" xmlns:xi=\"http://www.w3.org/2001/XInclude\"/>"
                partie.insert(i, etree.fromstring(x_include))

    with open(f'divs/{temoin_a_traiter}.xml', "w") as xml_file:
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
