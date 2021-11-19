import itertools
import math

import embeddings as embeddings
import lxml.etree as etree

import itertools

import numpy as np


def compute_similarity(fichier):
    """
    Fonction qui calcule les similarités entre variants dans chaque lieu variant lexical.
    On se sert pour l'instant de plongements de mots entraînés par un modèle très simple de
    prédiction par contexte. Modèle entraîné sur le propre corpus lemmatisé.
    Idée originelle de JB Camps.
    Il reste à trouver une façon de faire parler les chiffres, et à injecter ça dans le XML proprement.
    """
    tei_namespace = 'http://www.tei-c.org/ns/1.0'
    NSMAP = {'tei': tei_namespace}  # pour la recherche d'éléments avec la méthode xpath

    with open(fichier, "r") as opened_file:
        fichier_parse = etree.parse(opened_file)
    print(fichier)
    liste_d_apparats = fichier_parse.xpath("//tei:app[@type='lexicale'][count(descendant::tei:rdg) > 1]",
                                           namespaces=NSMAP)

    with open("embeddings_results/similarity_results.txt", "a") as similarity_file:
        similarity_file.truncate(0)

    # On processe les entrées pour sortir les paires à comparer, en supprimant la redondance et les omissions.
    embs = embeddings.Embeddings(model='python/post_traitement/model_embeddings.pt', device='cpu')

    # On va garder dans une liste la métrique pour tous les couples de mots
    global_similarity_list = []

    for lieu_variant in liste_d_apparats:
        # D'abord on récupère toutes les analyses, on supprime la redondance et on crée des paires
        id = lieu_variant.xpath("descendant::tei:w/@xml:id", namespaces=NSMAP)
        with open("embeddings_results/similarity_results.txt", "a") as similarity_file:
            similarity_file.write(f"Identifiant:{id}\n")
        liste_de_lemmes = [lemme.split("_")[0] for lemme in
                           lieu_variant.xpath("descendant::tei:rdg/@lemma", namespaces=NSMAP)]
        liste_de_pos = [pos.split(" ")[0] for pos in
                        lieu_variant.xpath("descendant::tei:rdg/@pos", namespaces=NSMAP)]
        lemmes = [lemme for lemme in liste_de_lemmes if lemme != ""]
        pos = [pos for pos in liste_de_pos if pos != ""]
        analyses_regroupees = list(set([f"{pos}{lemme}" for pos, lemme in zip(pos, lemmes)]))
        paires_a_analyser = list(itertools.combinations(analyses_regroupees, 2))

        # On calcule ensuite la similarité pour chacune des paires
        similarity_dict = dict()
        mean_similarity = embs.mean_similarity
        for paire in paires_a_analyser:
            with open("similarity_results.txt", "a") as similarity_file:
                similarity_file.write(f"Paire à analyser: {paire}\n")
                cosine_metric, test_metric, test_words = embs.compute_similarity(cosine_similarity=True, pair=paire)
                similarity_file.write(f"Distance: {cosine_metric}\n")
                similarity_file.write(f"Distance moyenne entre 100 paires: {mean_similarity}\n")
                similarity_file.write(f"Distance entre deux vecteurs aléatoires: ({test_words}) {test_metric}\n")
            global_similarity_list.append((cosine_metric.item(), paire))
            similarity_dict[paire] = cosine_metric.item()

        lieu_variant.set("subtype", similarity_dict.__repr__())
        global_similarity_list = [(metric, couple) for metric, couple in global_similarity_list if
                                  math.isnan(metric) is False]
        with open("similarity_results.txt", "a") as similarity_file:
            similarity_file.write(f"Dict: {global_similarity_list}")
            similarity_file.write("\n\n Nouveau lieu variant. \n\n")

    print(mean_similarity)
    print(embs.median_similarity)
    liste_de_similarites = [similarity for similarity, _ in global_similarity_list if math.isnan(similarity) is False]
    similarite_maximum = np.max(np.array(liste_de_similarites))
    similarite_minimum = np.min(np.array(liste_de_similarites))

    similarity_threshold = None
    # Ici il faut trouver une façon de déterminer le seuil de similarité. À la main une fois les embeddings produits
    # et un premier tour de comparaison fait entre tous les lieux variant ?

    # On ordonne la liste de similarité puis on imprime.
    global_similarity_list = list(set(global_similarity_list))
    global_similarity_list.sort(key=lambda x: x[0])
    with open("similarity_dict.list", "w") as similarity_list_file:
        similarity_list_file.write(f"Similarité minimum: {similarite_minimum}\n"
                                   f"Similarité maximum: {similarite_maximum}\n")
        similarity_list_file.write(f"Moyenne de similarités (10000 couples): {embs.mean_similarity}\n")
        similarity_list_file.write("\n".join([f"{x}: ({y[0]}/{y[1]})" for x, y in global_similarity_list]))

    with open(fichier, "w+") as output_file:
        output_file.write(etree.tostring(fichier_parse, pretty_print=True).decode())
    return embs


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
    bootstrap_link.set("href",
                       "/home/mgl/Bureau/These/Edition/collator/html/libs/bootstrap-5.1.3-dist/css/bootstrap.min.css")
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
