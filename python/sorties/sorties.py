import os
from halo import Halo
import glob
import subprocess
from lxml import etree
import itertools


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
    print(f'current dir: {os.getcwd()}')
    subprocess.run(["xelatex", "-quiet", f"-output-directory={chemin}", fichier_tex_seul])
    subprocess.run(["biber", fichier_sans_extension])
    subprocess.run(["xelatex", "-quiet", f"-output-directory={chemin}", fichier_tex_seul])


def similarity_eval_set_creator(chapitre):
    """
    Cette fonction produit un document html simple pour estimer le degré de similarité au niveau des lieux variants
    """

    with open(f"divs/div{chapitre}/apparat_Mad_G_{chapitre}_final.xml", "r") as xml_file:
        f = etree.parse(xml_file)
    tei = {'tei': 'http://www.tei-c.org/ns/1.0'}
    apps_list = f.xpath("//tei:app[@type='lexicale']", namespaces=tei)
    output_list = []
    for app in apps_list:
        rdg_list = app.xpath("descendant::tei:rdg", namespaces=tei)
        readings = []
        for reading in rdg_list:
            if reading.xpath("tei:w", namespaces=tei):
                readings.append(reading.xpath("@lemma", namespaces=tei)[0].split("_")[0])
            else:
                readings.append("ø")
        pair_list = list(itertools.combinations(readings, 2))
        pair_list = list(set(pair_list))
        pair_list.sort()
        interm_list = [[word_a, word_b] for word_a, word_b in pair_list if word_a != word_b]
        interm_list = [tuple(sorted(element)) for element in interm_list if "ø" not in element]
        output_list.extend(interm_list)
    output_list = list(set(output_list))

    root = etree.Element("html")
    head = etree.SubElement(root, "head")
    jq_link = etree.SubElement(head, "script")
    jq_link.set("src", "/home/mgl/Bureau/These/Edition/collator/html/libs/jquery/jquery-3.6.0.min.js")
    jq_link.text = ""
    bootstrap_link = etree.SubElement(head, "link")
    bootstrap_link.set("rel", "stylesheet")
    bootstrap_link.set("href", "/home/mgl/Bureau/These/Edition/collator/html/libs/bootstrap-5.1.3-dist/css/bootstrap.min.css")
    bootstrap_link.text = ""


    css_link = etree.SubElement(head, "link")
    css_link.set("rel", "stylesheet")
    css_link.set("href", "/home/mgl/Bureau/These/Edition/collator/html/css/datafy.css")
    css_link.text = ""

    bootstrap_switch = etree.SubElement(head, "script")
    bootstrap_switch.set("src", "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-switch/3.3.4/js/bootstrap-switch.js")
    bootstrap_switch.set("data-turbolinks-track", "true")
    bootstrap_switch.text = ""
    js_link = etree.SubElement(head, "script")
    js_link.set("src", "/home/mgl/Bureau/These/Edition/collator/html/js/functions_semantic.js")
    js_link.text = ""
    title0 = etree.SubElement(head, "title")
    body = etree.SubElement(root, "body")
    title0.text = "Table de correction sémantique"
    table = etree.SubElement(body, "table")
    table_header = etree.SubElement(table, "thead")
    row = etree.SubElement(table_header, "tr")
    title1 = etree.SubElement(row, "th")
    title1.set("colspan", "2")
    title1.text = "Table title"
    tbody = etree.SubElement(table, "tbody")

    for apparat in output_list:
        if len(set(apparat)) == 1:
            continue
        tr = etree.SubElement(tbody, "tr")
        tr.set("semblable", "False")
        td0 = etree.SubElement(tr, "td")
        if 'ø' not in apparat:
            td0.set("class", "lemmes")
        else:
            td0.set("class", "omission")
        td0.text = "\t".join(apparat)



        dissemblable = etree.SubElement(tr, "td")
        dis_span = etree.SubElement(dissemblable, "span")
        dis_span.set("class", "dissemblable")
        dis_span.text = "Dissemblable"

        switch_row = etree.SubElement(tr, "td")
        # switch_row.set("class", "switch")
        switch_label = etree.SubElement(switch_row, "label")
        switch_label.set("class", "switch")
        input = etree.SubElement(switch_label, "input")
        input.set("type", "checkbox")
        span_element = etree.SubElement(switch_label, "span")
        span_element.set("class", "slider round")
        span_element.text = ""


        dissemblable = etree.SubElement(tr, "td")
        dissemblable.text = "Semblable"


        current_arrow = etree.SubElement(tr, "td")
        current_arrow.set("class", "current_arrow")
        current_arrow.set("style", "display:none;")
        current_arrow.text = "←"


    tr = etree.SubElement(tbody, "tr")
    save = etree.SubElement(tr, "td")
    save_button = etree.SubElement(save, "button")
    save_button.set("id", "enregistrer")
    save_button.text = "Enregistrer"

    with open(f"divs/div{chapitre}/apparat_Mad_G_final.html", "w") as xml_file:
        xml_file.write(etree.tostring(root, pretty_print=True).decode())


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
