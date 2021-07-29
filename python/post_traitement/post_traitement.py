import math
import re
from lxml import etree
import glob
import operator
import traceback
import multiprocessing as mp
import itertools
import numpy as np

import python.utils.utils as utils
import python.post_traitement.embeddings as embeddings


def injection_en_masse(chapitre, element_tei, position, liste_temoins):
    """
    Cette fonction permet d'injecter sur tous les fichiers les éléments d'un seul fichier.
    :param chapitre: le chapitre à processer
    :param element_tei: les éléments à réinjecter
    :param position: la position: va-t-on chercher un point d'ancrage avant ou après l'élément ? (pour un tei:milestone,
    ce sera après, puisqu'un milestone a des chances de se trouver au début d'un tei:p, contrairement à une note)
    :param liste_temoins: la liste des témoins
    :return: None
    """
    fichiers_out = (injections_element(fichier_xml, chapitre, element_tei,
                                       position) for fichier_xml in liste_temoins)

    for xml_element in fichiers_out:
        with open(xml_element[1], "w") as output_file:
            output_file.write(etree.tostring(xml_element[0]).decode())


### ATTENTION, l'injection ne peut pas marcher en l'état absolument correctement.
# En effet, l'alignement n'est pas assez fin pour permettre de réinjecter les éléments au token près,
# ce qui pose des problèmes pour les milestones par exemple.
### SOLUTION: une solution possible serait de refaire des alignements au mot-à-mot avec collatex au niveau de chaque
# apparat: 1) alignement global 2) alignements microscopiques 3) réinjection en utilisant les index

def injections_element(temoin, n, tei_elements, position):
    # TODO gérer les omissions et les cas où deux éléments se trouveraient avant ou après le même mot
    # TODO: attention, ne gère par encore les non-apparats.
    """
    Cette fonction permet la réinjection d'éléments présents dans un témoin dans tous les autres témoins.
    Il s'appuie pour ce faire sur le tei:w qui suit ou précède l'élément ciblé, en fonction
    de cet élément.
    :param temoin: le témoin sur lequel appliquer les injections
    :param div: la division courante
    :param tei_elements: l'élément tei à injecter.
    :param position: Possibilités: "before" (le point d'ancrage est avant un tei:w, exemple: tei:milestone)
    ou "after" (le point d'ancrage se trouve après le tei:w, exemple, tei:note)
    :return: Un tuple comprenant l'objet lxml final et le nom du fichier à écrire correspondant.
    """
    print(f'\nInserting {tei_elements} into {temoin}')

    if position == "before":
        following_or_preceding = "following"  # on va chercher le tei:w suivant
        sign = operator.sub  # et on injectera donc avant ce tei:w (index(tei:w) - 1)
    else:
        following_or_preceding = "preceding"  # on va chercher le tei:w précédent
        sign = operator.add  # et on injectera donc après ce tei:w (index(tei:w) + 1)

    final_notes_list = []
    final_w_list = []
    final_witness_list = []
    tei_namespace = 'http://www.tei-c.org/ns/1.0'
    NSMAP1 = {'tei': tei_namespace}  # pour la recherche d'éléments avec la méthode xpath
    for file in glob.iglob(f"/home/mgl/Bureau/These/Edition/collator/divs/div{n}/*final.xml"):
        f = etree.parse(file)

        # On va d'abord récuperer et aligner chaque élément tei:note, l'xml:id du tei:w qui précède et le témoin concerné
        notes_list = f.xpath(f'//tei:div[@n=\'{n}\']//{tei_elements}', namespaces=NSMAP1)
        nombre_de_notes = len(notes_list)
        w_list = f.xpath(f'//tei:div[@n=\'{n}\']//{tei_elements}/{following_or_preceding}::tei:w[1]/@xml:id',
                         namespaces=NSMAP1)
        temoin_id = f.xpath(f'//tei:div[@n=\'{n}\']//{tei_elements}/ancestor::tei:div[@type=\'chapitre\']/@xml:id',
                            namespaces=NSMAP1)
        if temoin_id:
            temoin_id = "_".join(temoin_id[0].split("_")[0:2])
            final_witness_list.extend(
                [temoin_id for x in range(nombre_de_notes)])  # https://stackoverflow.com/a/4654446
        final_w_list.extend(w_list)
        final_notes_list.extend(notes_list)
    notes_tuples = list(zip(final_w_list, final_notes_list, final_witness_list))
    # On produit une liste de tuples de la forme :
    # [
    # ('kNMdVRz', <Element {http://www.tei-c.org/ns/1.0}note at 0x7f08a90f9ac8>, 'Sev_R'),
    # ('oqcqYPq', <Element {http://www.tei-c.org/ns/1.0}note at 0x7f08a90f9c08>, 'Sal_J')
    # ]
    print(f'{len(notes_tuples)} to insert.')
    for i in notes_tuples:
        print(f'{etree.tostring(i[1])} is {position} w[@xml:id=\'{i[0]}\']')
    # Puis on va parcourir le dictionnaire et insérer toutes les notes dans le témoin traité.
    current_xml_file = etree.parse(temoin)
    temoin_id_courant = "_".join(
        current_xml_file.xpath(f'//tei:div[@type=\'chapitre\']/@xml:id', namespaces=NSMAP1)[0].split("_")[0:2])
    print("--- Injection ---")
    print(len(notes_tuples))
    for item in notes_tuples:
        id_item, element, temoin_de_l_element = item[0], item[1], item[2]
        if element.xpath("@injected='injected'"):  # on évite ainsi de réinjecter des éléments déjà injectés
            # quand on passe au témoin suivant.
            pass
        else:
            print(f'Élément à injecter : {etree.tostring(element)}')
            element.set("injected", "injected")  # il faudra nettoyer ça à la fin de la boucle.
            element.set("corresp", f'#{temoin_de_l_element}')  # on indique de quel témoin provient l'élément.
            # Il y a un bug ici: puisque l'on modifie à la volée les textes, à chaque fois qu'on change de témoin
            # ça pose problème et le témoin dans le corresp est faux, ce qui
            # va biaiser la suite du processus... Il faut que cette fonction produise un nouveau document de sortie
            # On passe si le témoin de la réinjection est le même que le témoin de la note
            if temoin_de_l_element == temoin_id_courant:
                pass
            else:
                try:
                    # print(f"témoin: {temoin_id_courant}; id: {id_item}\n"
                    # f"contenu de l'élément: {etree.tostring(element)}")
                    word_to_change = current_xml_file.xpath(f'//tei:w[@xml:id=\'{id_item}\']', namespaces=NSMAP1)[0]
                    item_element = word_to_change.getparent()  # https://stackoverflow.com/questions/7474972/python-lxml-append
                    # -element-after-another-element
                    # print(sign)
                    index = sign(item_element.index(word_to_change), 1)  # https://stackoverflow.com/a/54559513
                    # print(f'index => {index}')
                    if index == -1:
                        index = 0
                    # On va tester la présence de l'élément à l'emplacement de l'injection
                    test_existence = current_xml_file.xpath(
                        f'//tei:div[@n=\'{n}\']//{tei_elements}[{following_or_preceding}::tei:w[@xml:id = \'{id_item}\']]',
                        namespaces=NSMAP1)
                    if len(test_existence) == 0:
                        item_element.insert(index, element)
                    else:
                        print(f'On n\'injecte pas l\'élément {etree.tostring(element)} dans {temoin}')
                except Exception as e:
                    print(f"Il y a un problème (omission?) dans {temoin.split('/')[-1]} qui empêche l'injection:"
                          f"\n {traceback.format_exc()}")
    print("--- Injection terminée ---")
    return current_xml_file, temoin


def raffinage_apparats(fichier, i):
    """
    Cette fonction permet de raffiner les apparats en rassemblant les variantes graphiques au sein d'un apparat qui
    comporte des variantes "vraies" ou morphosyntactiques. On va créer des tei:rdgGroup qui rassembleront les rdg.
    """
    # TODO: fusionner cette fonctiona avec la fonction de création d'apparat ?
    # TODO: il reste un problème dans le cas suivant (en amont): chaîne identique, (lemme?|)pos différent.
    sigle = fichier.split("apparat_")[1].split(f"_{i}_")[0]
    print(sigle)
    tei = {'tei': 'http://www.tei-c.org/ns/1.0'}
    parser = etree.XMLParser(load_dtd=True,
                             resolve_entities=True)
    f = etree.parse(fichier, parser=parser)  # https://lxml.de/tutorial.html#namespaces
    root = f.getroot()
    liste_apps = root.xpath(f"//tei:app[not(@type='graphique')]", namespaces=tei)
    for apparat in liste_apps:
        lecon = apparat.xpath(f"descendant::tei:rdg", namespaces=tei)
        # S'il n'y a que deux lemmes, pas besoin de raffiner l'apparat.
        if len(lecon) <= 2:
            pass

        # Sinon, les choses deviennent intéressantes
        else:
            print("\n")
            liste_de_lecons = apparat.xpath(f"tei:rdg", namespaces=tei)

            liste_annotations = []
            for lecon in liste_de_lecons:
                texte = " ".join(lecon.xpath("descendant::tei:w/descendant::text()", namespaces=tei))
                identifiant_rdg = lecon.xpath("@id", namespaces=tei)[0]
                lemme = lecon.xpath("@lemma")[0]
                pos = lecon.xpath("@pos")[0]
                pos_reduit = pos.split(" ")[0]
                lemme_reduit = "_".join(lemme.split("_")[:len(pos_reduit.split("_"))])
                liste_annotations.append((identifiant_rdg, pos_reduit, lemme_reduit))

            # On identifie les variants graphiques au sein
            # du lieu variant ( = les paires Pos/Lemmes qui se répètent)
            liste_d_analyses = set([(pos, lemma) for identifiant, pos, lemma in liste_annotations])
            dictionnaire_de_regroupement = {}
            for i in liste_d_analyses:
                for j in liste_annotations:  # on va récupérer l'identifiant
                    if all(x in j for x in i):
                        identifiant, pos, lemma = j
                        # https://www.geeksforgeeks.org/python-check-if-one-tuple-is-subset-of-other/
                        print(f"{i} is subset of {j}")
                        try:
                            dictionnaire_de_regroupement[i].append(identifiant)
                        except KeyError:
                            dictionnaire_de_regroupement[i] = [identifiant]
                        # Le dictionnaire est de la forme: {(pos, lemmes): [liste des identifiants]]}

            # Ce qui nous intéresse, c'est de produire les groupes: on ne garde que les valeurs
            # du dictionnaire
            rdg_groups = list(dictionnaire_de_regroupement.values())

            # On va pouvoir maintenant créer des rdgGroups autour des tei:rdg que l'on a identifiés
            # comme similaires.

            # Créons donc des tei:rdgGrp parents pour ces groupes
            for group in rdg_groups:
                tei_namespace = 'http://www.tei-c.org/ns/1.0'
                namespace = '{%s}' % tei_namespace
                rdg_grp = etree.SubElement(apparat, namespace + 'rdgGrp')
                for identifiant in group:
                    orig_rdg = apparat.xpath(f"tei:rdg[@id = '{identifiant}']", namespaces=tei)[0]
                    rdg_grp.append(orig_rdg)

    with open(fichier, 'w+') as sortie_xml:
        output = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True).decode('utf8')
        sortie_xml.write(str(output))


def gestion_inversions(chemin, sensibilité=3):
    pass


def gestion_lacunes(chemin, target_path, sensibilite=3):
    """
    Définition de lacune:
    Cette fonction crée des balises de lacunes en cas d'omissions répétées
    variable: sensibilite: le nombre d'apparats vides consécutifs pour que soit considérée la lacune
    """
    tei_namespace = 'http://www.tei-c.org/ns/1.0'
    tei = {'tei': tei_namespace}  # pour la recherche d'éléments avec la méthode xpath
    dict_index_omission = {}
    output_dict = {}
    for file in glob.glob(target_path):
        sigle = "_".join(file.split("_")[1:3])
        print(sigle)

        with open(file, "r") as file:
            parsed_file = etree.parse(file)
        apps = parsed_file.xpath("//tei:app", namespaces=tei)
        for index, app in enumerate(apps):
            inf, sup = verification_ngram(sensibilite, apps, index, sigle)
            if sup > sensibilite:
                try:
                    dict_index_omission[sigle].append((inf, inf + sup))
                except:
                    dict_index_omission[sigle] = [(inf, inf + sup)]
        for witness, liste in dict_index_omission.items():
            output_dict[witness] = utils.nettoyage_liste_positions(liste)
    print(f"Omissions of witness {chemin}")
    print(output_dict)


def verification_ngram(sensibilite, apps, borne_inferieure, sigle):
    """
    Fonction récursive qui permet d'estimer s'il y a une lacune pour un manuscrit donné
    """
    tei_namespace = 'http://www.tei-c.org/ns/1.0'
    tei = {'tei': tei_namespace}  # pour la recherche d'éléments avec la méthode xpath
    borne_superieure = sensibilite
    n_gram = [current_app for current_app in apps[borne_inferieure: (borne_inferieure + sensibilite)]]

    target_sigla = f"boolean(descendant::tei:rdg[contains(@wit, {sigle})][not(descendant::node())])"
    if all([apparat.xpath(target_sigla, namespaces=tei)
            for apparat in n_gram]):
        # print(sigle)
        # print(target_sigla)
        # print(f"\n\n{sigle}\n\n".join([etree.tostring(apparat).decode('utf-8') for apparat in n_gram]))
        borne_inferieure, borne_superieure = verification_ngram(sensibilite + 1, apps, borne_inferieure, sigle)
    return borne_inferieure, borne_superieure


def injection_python(chemin, chapitre):
    print("On réinjecte les apparats")
    tei_namespace = 'http://www.tei-c.org/ns/1.0'
    NSMAP1 = {'tei': tei_namespace}  # pour la recherche d'éléments avec la méthode xpath
    file = f"/home/mgl/Bureau/These/Edition/collator/divs/div{chapitre}/juxtaposition_orig.xml"
    apparat_file = f"/home/mgl/Bureau/These/Edition/collator/divs/div{chapitre}/apparat_collatex.xml"

    with open(file, "r") as opened_file:
        parsed_group_file = etree.parse(opened_file)
    with open(apparat_file, "r") as opened_apparat_file:
        parsed_apparat_file = etree.parse(opened_apparat_file)

    # On travaille sur chaque témoin
    for witness in parsed_group_file.xpath("//temoin"):
        siglum = witness.xpath("@n")[0]
        for word in witness.xpath("//tei:w", namespaces=NSMAP1):
            xml_id = word.xpath("@xml:id")[0]

        # On écrit finalement le fichier
        witness[0].getparent().tag = "div"
        witness[0].getparent().set("{http://www.w3.org/XML/1998/namespace}id", f'{siglum}_3_3_{chapitre}')
        witness[0].getparent().set("type", "chapitre")
        witness[0].getparent().set("n", str(chapitre))
        witness[0].set("xmlns", tei_namespace)  # on crée le namespace adéquat.

        list_word_id_apparat_collatex = zip(parsed_apparat_file.xpath("//tei:w", namespaces=NSMAP1),
                                            parsed_apparat_file.xpath("//tei:w/@xml:id", namespaces=NSMAP1))

        with open(f"/home/mgl/Documents/apparat_{siglum}_{chapitre}.xml", "w") as output_file:
            print("Outputting...")
            output_file.write(etree.tostring(witness).decode())


def injection_omissions(temoin_a_injecter, chemin):
    """
    Cette fonction permet d'injecter les leçons ommises par chaque témoin, qui sont ignorées par le témoin.
    :return:None
    """
    # idée: on prend apparat_collatex et on regarde tous les tei:rdg avec notre témoin qui est vide, pour le réinjecter.
    # Problème ici: si on change de division par exemple, ça va être problématique.
    print("On injecte les omissions")
    tei_namespace = 'http://www.tei-c.org/ns/1.0'
    NSMAP1 = {'tei': tei_namespace}
    # On récupère le sigle du témoin
    with open(temoin_a_injecter, "r") as opened_temoin:
        parsed_temoin = etree.parse(opened_temoin)
        sigle = "_".join(parsed_temoin.xpath("//tei:div/@xml:id", namespaces=NSMAP1)[0].split("_")[0:2])
        print(sigle)
    # Et on va chercher les listes d'apparats où le témoin commet une omission et leur emplacement / tei:w
    with open(f"{chemin}/apparat_collatex.xml", "r") as apparat_collatex:
        parsed_apparat_collatex = etree.parse(apparat_collatex)
        # Passer à du contains plutôt en cas d'omission par plusieurs témoins
        liste_omissions = parsed_apparat_collatex.xpath(
            f'//tei:app[tei:rdg[translate(@wit, \'#\', \'\')={sigle}][not(tei:w)]]', namespaces=NSMAP1)
        liste_emplacement = [omission.xpath(f'preceding::tei:app/tei:rdg[1]/@xml:id', namespaces=NSMAP1)[0] for omission
                             in liste_omissions]
        liste_finale = zip(liste_omissions, liste_emplacement)
        print(liste_finale)


def injection(saxon, chemin, chapitre, coeurs):
    """
    Fonction qui réinjecte les apparats dans chaque transcription individuelle.
    :param saxon: le moteur saxon
    :param chemin:  le chemin du dossier courant
    :param chapitre: le chapitre courant
    :return: None
    TODO: il faudrait passer à du 100% python, pour être plus clair, c'est un peu
    l'usine à gaz là.
    """
    print("---- INJECTION 1: apparats ----")
    param_chapitre = f"chapitre={str(chapitre)}"  # Premier paramètre passé à la xsl: le chapitre à processer
    param_chemin_sortie = f"chemin_sortie={chemin}/"  # Second paramètre: le chemin vers le fichier de sortie
    fichier_entree = f"{chemin}/juxtaposition_orig.xml"
    # with Halo(text="Injection des apparats dans chaque transcription individuelle", spinner='dots'):
    #  première étape de l'injection. Apparats, noeuds textuels et suppression de la redondance
    chemin_injection = "xsl/post_alignement/injection_apparats.xsl"
    subprocess.run(["java", "-jar", saxon, fichier_entree, chemin_injection, param_chapitre, param_chemin_sortie])

    # seconde étape: noeuds non textuels
    print("\n---- INJECTION 2: suppression de la redondance ----")
    fichiers_apparat = f'{chemin}/apparat_*_*.xml'
    liste = glob.glob(fichiers_apparat)
    chemin_injection2 = "xsl/post_alignement/injection_apparats2.xsl"
    parallel_transformation(saxon, chemin_injection2, param_chapitre, liste, coeurs, regexp=r'.*[0-9].xml')

    print("\n---- INJECTION 2bis: suppression de la redondance ----")
    chemin_injection3 = "xsl/post_alignement/injection_apparats3.xsl"
    fichiers_apparat = f'{chemin}/apparat_*_*outb.xml'
    liste = glob.glob(fichiers_apparat)
    parallel_transformation(saxon, chemin_injection3, param_chapitre, liste, coeurs)

    #  troisième étape: ponctuation
    print("\n---- INJECTION 3: ponctuation ----")
    chemin_injection_ponctuation = "xsl/post_alignement/injection_ponctuation.xsl"
    fichiers_apparat = f'{chemin}/apparat_*_*outc.xml'
    liste = glob.glob(fichiers_apparat)
    parallel_transformation(saxon, chemin_injection_ponctuation, param_chapitre, liste, coeurs)
    print("Injection des apparats dans chaque transcription individuelle ✓")

    #  quatrième étape: gestion des lacunes
    print("\n---- INJECTION 4: lacunes ----")
    chemin_injection_ponctuation = "xsl/post_alignement/gestion_lacunes.xsl"
    fichiers_apparat = f'{chemin}/apparat_*_*out.xml'
    liste = glob.glob(fichiers_apparat)
    parallel_transformation(saxon, chemin_injection_ponctuation, param_chapitre, liste, coeurs)
    print("Création des balises de lacunes ✓")


def calcul_similarite(fichier):
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

    with open("similarity_results.txt", "a") as similarity_file:
        similarity_file.truncate(0)

    # On processe les entrées pour sortir les paires à comparer, en supprimant la redondance et les omissions.
    embs = embeddings.Embeddings(model='python/post_traitement/model_embeddings.pt')

    # On va garder dans une liste la métrique pour tous les couples de mots
    global_similarity_list = []

    for lieu_variant in liste_d_apparats:
        # D'abord on récupère toutes les analyses, on supprime la redondance et on crée des paires
        id = lieu_variant.xpath("descendant::tei:w/@xml:id", namespaces=NSMAP)
        with open("similarity_results.txt", "a") as similarity_file:
            similarity_file.write(f"Identifiant:{id}\n")
        liste_de_lemmes = [lemme.split("_")[0] for lemme in
                           lieu_variant.xpath("descendant::tei:rdg/@lemma", namespaces=NSMAP)]
        liste_de_pos = [pos.split(" ")[0] for pos in lieu_variant.xpath("descendant::tei:rdg/@pos", namespaces=NSMAP)]
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

    with open(fichier.replace("final", "definitif"), "w+") as output_file:
        output_file.write(etree.tostring(fichier_parse, pretty_print=True).decode())



def parallel_transformation(moteur_transformation, chemin_xsl, param_chapitre, liste, coeurs, regexp=None):
    pool = mp.Pool(processes=coeurs)
    command_list = []
    if regexp is None:
        for i in liste:
            sigle = i.split("apparat_")[1].split(".xml")[0].split("_")[0] + "_" \
                    + i.split("apparat_")[1].split(".xml")[0].split("_")[1]
            param_sigle = "sigle=" + sigle
            command = ["java", "-jar", moteur_transformation, i, chemin_xsl, param_chapitre, param_sigle]
            command_list.append(command)
    else:
        for i in liste:
            if re.match(regexp, i):
                sigle = i.split("apparat_")[1].split(".xml")[0].split("_")[0] + "_" \
                        + i.split("apparat_")[1].split(".xml")[0].split("_")[1]
                param_sigle = "sigle=" + sigle
                command = ["java", "-jar", moteur_transformation, i, chemin_xsl, param_chapitre, param_sigle]
                command_list.append(command)

    pool.map(utils.run_subprocess, command_list)


