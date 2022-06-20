import copy
import json
import re
from ordered_set import OrderedSet

from lxml import etree
import glob
import operator
import multiprocessing as mp
import subprocess

from tqdm import tqdm

import python.utils.utils as utils


class Injector:
    def __init__(self, debug, div_n, elements_to_inject, saxon, chemin, coeurs, element_base,
                 type_division, lacuna_sensibility, liste_sigles, excluded_elements, temoin_base):
        """
        Classe injecteur: réalise les injections de ponctuation, des omissions et des éléments spécifiés
        par l'utilisateur.ice

        :param chapitre: le chapitre à processer :param element_tei: les éléments à réinjecter
        :param position: la
        position: va-t-on chercher un point d'ancrage avant ou après l'élément ? (pour un tei:milestone, ce sera après,
        puisqu'un milestone a des chances de se trouver au début d'un tei:p, contrairement à une note)
        :param liste_temoins: la liste des témoins
        """
        self.debug_mode = debug
        self.div_n = div_n
        self.elements_to_inject = elements_to_inject
        self.excluded_elements: list = excluded_elements
        self.processed_list = []  # ->  List[tuple]
        self.liste_temoins = None
        self.tei_ns = 'http://www.tei-c.org/ns/1.0'
        self.ns_decl = {'tei': self.tei_ns}  # pour la recherche d'éléments avec la méthode xpath
        self.saxon = saxon
        self.chemin = chemin
        self.coeurs = coeurs
        self.element_base = element_base
        self.type_division = type_division
        self.lacuna_sensibility = lacuna_sensibility
        self.liste_sigles = liste_sigles
        self.temoin_base = temoin_base

    def run_injections(self):
        self.injection_apparats()
        self.injection_omissions()
        self.same_word_identification(distance=10)
        self.injection_intelligente()
        self.injection_noeuds_non_textuels()
        self.regroupement_omissions()
        self.transposition_recognition()

    def detection_homeotheleuton(self):
        """TODO
        Cette fonction détecte parmi les lacunes identifiées les homéothéleutes
        Deux façons de faire:
        - soit en travaillant sur les lemmes
        - soit en travaillant sur des proximités formelles (mots proches à 60, 80%, ou qui commencent identiquement).
        """
        pass

    def regroupement_omissions(self):
        """
        Cette fonction lance l'identification des lacunes sur chaque témoin.
        INPUTS: *apparated.xml
        OUTPUTS: *apparated.lacuned.xml
        """
        output_filename = "_injected.apparated.lacuned.xml"
        print(f"Regroupement des omissions: *injected.apparated.xml => *{output_filename}")
        files = glob.glob(f"{self.chemin}/*.apparated.xml")
        assert len(files) > 0

        for fichier in files:
            self.lacuna_identification(chemin=fichier, output_file=fichier.replace('.xml', '.lacuned.xml'))
        print("Regroupement des omissions ✓")

    def injection_apparats(self):
        """
        Cette fonction prend chaque témoin tokénisé, et pour chaque tei:w, le remplace par le tei:app correspondant
        dans le fichier collationné.
        INPUTS: temoins_tokenises/*.xml + apparat_collatex.xml
        OUTPUTS: *out.xml
        """
        print("Injection des apparats dans les témoins d'origine")
        input_files = utils.filter_existing_divs(glob.glob("temoins_tokenises/*.xml"), div_n=self.div_n,
                                                 div_type=self.type_division)
        assert len(input_files) > 0

        for file in input_files:
            sigle = file.split("/")[-1].split(".xml")[0]
            print(sigle)
            fichier_tokenise = utils.parse_xml_file(file)
            apparat = f"{self.chemin}/alignement/apparat_collatex.xml"
            fichier_apparat = utils.parse_xml_file(apparat)
            # dans le fichier d'apparat, on va chercher tous les identifiants
            # On veut un dictionnaire de la forme {ID: élément tei:app}
            apps = fichier_apparat.xpath(f"//tei:app",
                                         namespaces=self.ns_decl)
            dictionnary = {}
            for app in apps:
                identifiants_rdg = utils.merge_list_of_lists(
                    [ID.split("_") for ID in app.xpath("descendant::tei:rdg/@n",
                                                       namespaces=self.ns_decl)])
                # On met à jour le dictionnaire.
                dictionnary = {**dictionnary, **{identifiant: app for identifiant in identifiants_rdg}}

            # Première étape, récupérer tous les tei:w du fichier tokénisé en ne filtrant que la division qui nous intéresse.
            try:
                current_division = fichier_tokenise.xpath(f"//tei:div[@n='{self.div_n}'][@type='{self.type_division}']",
                                                          namespaces=self.ns_decl)[0]
            # Quand la liste est vide, c'est que le témoin ne contient pas la division.
            except IndexError:
                continue
            words = current_division.xpath(f"descendant::tei:w",
                                           namespaces=self.ns_decl)
            IDs = current_division.xpath(f"descendant::tei:w/@xml:id", namespaces=self.ns_decl)

            IDs_and_words = list(zip(IDs, words))

            # Deuxième étape
            for identifier, word in IDs_and_words:
                parent_anchor = word.getparent()
                try:
                    corresponding_app = dictionnary[identifier]
                except KeyError as error:
                    print(f"There was a problem with the injection with witness {sigle}. "
                          f"Please check there is no tei:w where there should not be "
                          f"(in the notes for example). ID: {identifier}"
                          f"\nThe input files should be validated against the given schema.")
                    exit(0)
                parent_anchor.insert(parent_anchor.index(word), corresponding_app)
                parent_anchor.remove(word)

            output_file = f"{self.chemin}/apparat_{sigle}_{self.div_n}_out.xml"
            utils.save_xml_file(current_division, output_file)

        print("Fait !")

    def injection_noeuds_non_textuels(self):
        """
        Le but de cette fonction est d'aller enrichir chaque rdg des informations originelles contenues dans les tei:w
        de chaque témoin.
        INPUTS: *injected.xml
        OUTPUTS: *apparated.xml
        """

        print("Injection des noeuds non textuels")
        tei_namespace = 'http://www.tei-c.org/ns/1.0'
        tei = '{%s}' % tei_namespace
        paths_fichiers_collationes_orig = glob.glob(f"{self.chemin}/*injected.xml")
        assert len(paths_fichiers_collationes_orig) > 0

        # On va créer un dictionnaire dont les clés sont les sigles et les valeurs sont
        # des dictionnaires avec les éléments intéressants et leurs id
        dict_of_files = {}
        for sigle in self.liste_sigles:
            tokenised_file = utils.parse_xml_file(f"temoins_tokenises/{sigle}.xml")
            annotated_file = utils.parse_xml_file(f"temoins_tokenises_regularises/{sigle}.xml")

            try:
                tokenised_file.xpath(f"//tei:div[@n='{self.div_n}'][@type='{self.type_division}']",
                                     namespaces=self.ns_decl)[0]
            # Quand la liste est vide, c'est que le témoin ne contient pas la division.
            except IndexError:
                continue

            corresponding_ids = tokenised_file.xpath(
                f"//tei:div[@type='{self.type_division}'][@n='{self.div_n}']/descendant::tei:w[node()[not("
                "self::text())]]/@xml:id", namespaces=self.ns_decl)

            w_with_nodes = tokenised_file.xpath(
                f"//tei:div[@type='{self.type_division}'][@n='{self.div_n}']/descendant::tei:w[node()[not("
                "self::text())]]", namespaces=self.ns_decl)
            w_lemma = [annotated_file.xpath(
                f"//tei:div[@type='{self.type_division}'][@n='{self.div_n}']/descendant::tei:w[@xml:id = '{ID}']/@lemma",
                namespaces=self.ns_decl)[0] for ID in corresponding_ids]
            w_pos = [annotated_file.xpath(
                f"//tei:div[@type='{self.type_division}'][@n='{self.div_n}']/descendant::tei:w[@xml:id = '{ID}']/@pos",
                namespaces=self.ns_decl)[0] for ID in corresponding_ids]

            intermed_dict = {ID: (element, lemma, pos) for (ID, element, lemma, pos) in
                             zip(corresponding_ids, w_with_nodes, w_lemma, w_pos)}
            dict_of_files[sigle] = intermed_dict

        # On va boucler sur tous chaque témoin.
        for path_fichier_collatione_orig in paths_fichiers_collationes_orig:
            fichier_collatione_orig = utils.parse_xml_file(path_fichier_collatione_orig)
            sigle_output = [sigle for sigle in self.liste_sigles if sigle in path_fichier_collatione_orig][0]
            output_file = path_fichier_collatione_orig.replace(".xml", ".apparated.xml")
            print(sigle_output)

            # On récupère tous les ids. On va aller regarder dans chaque id dans le document original si
            # il y a un noeud non textuel
            # On re-boucle sur les sigles

            # https://stackoverflow.com/a/4843172
            list_of_sigla = [sigle for sigle in self.liste_sigles if
                             any(sigle in s for s in paths_fichiers_collationes_orig)]
            for sigle_input in list_of_sigla:
                for id, (element, lemma, pos) in dict_of_files[sigle_input].items():
                    corresponding_rdg = \
                        fichier_collatione_orig.xpath(f"descendant::tei:rdg[contains(tei:w/@xml:id, '{id}')]",
                                                      namespaces=self.ns_decl)[0]
                    corresponding_wits = corresponding_rdg.xpath("@wit")[0]
                    corresponding_lemmas = corresponding_rdg.xpath("@lemma")[0]
                    corresponding_pos = corresponding_rdg.xpath("@pos")[0]

                    # On vérifie qu'il y a un seul témoin

                    # Cas complexe: le rdg concerne plusieurs témoins, il faut donc extraire
                    # et créer un nouveau tei:rdg avec le noeud non textuel.
                    # La deuxième condition est une rustine.
                    if " " in corresponding_wits and " " != corresponding_wits:
                        # On supprime le témoin et l'identifiant du rdg
                        new_rdg = etree.SubElement(corresponding_rdg.getparent(), tei + 'rdg')
                        corresponding_rdg.set("lemma", corresponding_lemmas)  # il faudrait nettoyer mais compliqué
                        corresponding_rdg.set("pos", corresponding_pos)  # idem
                        corresponding_rdg.set("wit", utils.clean_spaces_from_string(
                            corresponding_wits.replace(f"#{sigle_input}", "")))  # idem
                        new_rdg.set('inj', 'true')
                        new_rdg.set('n', id)
                        new_rdg.set('lemma', lemma)
                        new_rdg.set('pos', pos)
                        new_rdg.set('wit', "#" + sigle_input)
                        new_rdg.insert(0, element)
                        if corresponding_rdg.xpath(f"descendant::node()[@corresp = '#{sigle_input}']"):
                            print("Moving a node")
                            corresponding_node = \
                                corresponding_rdg.xpath(f"descendant::node()[@corresp = '#{sigle_input}']")[0]
                            new_rdg.insert(corresponding_rdg.index(corresponding_node), corresponding_node)

                    # Cas simple: le rdg ne concerne qu'un témoin
                    else:
                        # On supprime le noeud
                        corresponding_w = corresponding_rdg.xpath("tei:w", namespaces=self.ns_decl)[0]
                        corresponding_w.getparent().remove(corresponding_w)
                        corresponding_rdg.insert(0, element)
                        if corresponding_rdg.xpath(f"descendant::node()[@corresp = '#{sigle_input}']"):
                            corresponding_node = \
                                corresponding_rdg.xpath(f"descendant::node()[@corresp = '#{sigle_input}']")[0]
                            corresponding_rdg.insert(corresponding_rdg.index(corresponding_node), corresponding_node)
                    corresponding_app = corresponding_rdg.xpath("ancestor::tei:app", namespaces=self.ns_decl)[0]
                    corresponding_app_typology = corresponding_app.xpath("@ana")[0]
                    # if not "#codico" in corresponding_app_typology:
                        # corresponding_app.set("ana", corresponding_app_typology + " #codico")

                # Enfin on supprime les éléments sans witness, qui signifie qu'ils ont tous été extraits individuellement.
                for rdg_with_empty_wits in fichier_collatione_orig.xpath("//tei:rdg[not(contains(@wit, '#'))]",
                                                                         namespaces=self.ns_decl):
                    parent = rdg_with_empty_wits.getparent()
                    parent.remove(rdg_with_empty_wits)

            with open(output_file, "w") as output_apparated_file:
                output_apparated_file.write(etree.tostring(fichier_collatione_orig, pretty_print=True).decode())
        print("Noeuds injectés !")

    def parallel_transformation(self, chemin_xsl, param_chapitre, liste):
        pool = mp.Pool(processes=self.coeurs)
        command_list = []
        for i in liste:
            sigle = i.split("apparat_")[1].split(".xml")[0].split("_")[0] + "_" \
                    + i.split("apparat_")[1].split(".xml")[0].split("_")[1]
            param_sigle = "sigle=" + sigle
            command = ["java", "-jar", self.saxon, i, chemin_xsl, param_chapitre, param_sigle]
            command_list.append(command)
        pool.map(utils.run_subprocess, command_list)

    def transposition_recognition(self):
        """
        Cette fonction détecte les transpositions de la forme inversion de mots
        INPUTS: *lacuned.xml
        OUTPUTS: *transposed.xml
        """
        print("Reconnaissance des transpositions")
        files = glob.glob(f"{self.chemin}/*lacuned.xml")
        assert len(files) > 0
        with open(".debug/debug_transp.txt", "w") as debug_file:
            debug_file.truncate(0)

            for file in files:
                debug_file.write(f"---\n\nAnalyzing {file}\n")
                print(f"File {file}")
                output_file = file.replace(".xml", ".transposed.xml")
                with open(file, "r") as input_file:
                    f = etree.parse(input_file)
                # On va travailler sur des n-grams de 3 à 5.
                for distance in range(2, 5):
                    # On exclut d'emblée
                    apps = f.xpath("//tei:app[not(preceding::tei:milestone[@ana='#transposition'][1][@type='start'])]",
                                   namespaces=self.ns_decl)

                    # D'abord on crée des bigrammes, et on va comparer chaque bigramme avec le suivant
                    # Il faudrait faire tourner cette fonction sur des bigrammes, puis des trigrammes, etc.
                    bigram_apps = [apps[i:i + distance] for i in range(len(apps))]

                    for index in range(len(bigram_apps)):
                        debug_file.write(f"New {str(distance)}-gram\n")
                        ordered_Set_list = []
                        set_list = []

                        # On crée des bigrammes de ces bigrammes
                        # (i.e., on aura trois apparats différents répartis dans deux couples avec l'apparat central en commun)
                        # On en extrait les analyses morphosyntaxiques et on en supprime la redondance
                        for groupe_apparat in bigram_apps[index:index + 2]:
                            ordered_set_tmp = []
                            set_tmp = []
                            for apparat in groupe_apparat:
                                list_of_lemmas = "_".join(
                                    apparat.xpath("descendant::tei:rdg/@*[name()='lemma']", namespaces=self.ns_decl)).split(
                                    "_")
                                list_of_pos = " ".join(
                                    apparat.xpath("descendant::tei:rdg/@*[name()='pos']", namespaces=self.ns_decl)).split(
                                    " ")
                                lemmas_and_pos = [pos + lemma if pos+lemma != "" else "om" for pos, lemma in list(zip(list_of_pos, list_of_lemmas))]
                                debug_file.write("|".join(lemmas_and_pos))
                                debug_file.write("\n")
                                ordered_set_tmp.append(OrderedSet(lemmas_and_pos))
                                set_tmp.append(set(lemmas_and_pos))
                            ordered_Set_list.append(ordered_set_tmp)
                            set_list.append(set_tmp)

                        # Résultat: une liste d'OrderedSets
                        # [
                        # [OrderedSet(['', 'AQ0CS0grande']), OrderedSet(['NCMS000cuidado'])], # premier, deuxième app
                        # [OrderedSet(['NCMS000cuidado']), OrderedSet(['AQ0CS0grande', ''])] # deuxième, troisième app
                        # ]

                        # Et une liste de sets
                        # [
                        # [{'', 'AQ0CS0grande'}, {'NCMS000cuidado'}], # premier, deuxième app
                        # [{'NCMS000cuidado'}, {'', 'AQ0CS0grande'}] # deuxième, troisième app
                        # ]

                        # Le but est de comparer un à un chaque élément (ordonnés) de ces listes. Si l'égalité est vraie pour les
                        # ensembles non ordonnés mais fausse pour les ensembles ordonnés, on a logiquement un changement d'ordre
                        # entre les éléments, donc une transposition.

                        # Il est possible que l'on laisse de côté certaines transpositions: si les sets ont la même longueur,
                        # on ne pourra pas ordonner les listes et donc les comparer.

                        # https://stackoverflow.com/a/7242838
                        ordered_set_equality = all(
                            sorted(ordered_Set_list[n], key=len) == sorted(ordered_Set_list[0], key=len) for n in
                            range(len(ordered_Set_list)))
                        unordered_set_equality = all(
                            sorted(set_list[n], key=len) == sorted(set_list[0], key=len) for n in range(len(set_list)))

                        if not ordered_set_equality and unordered_set_equality:
                            debug_file.write("Transposition detected.\n")
                            print("Transposition detected.")
                            list_of_positions = [int(apparat.xpath("count(preceding::tei:app)", namespaces=self.ns_decl))
                                                 for
                                                 apparat in groupe_apparat]
                            max_pos = max(list_of_positions)
                            min_pos = min(list_of_positions) - 1

                            # https://stackoverflow.com/a/6045260
                            concerned_apps = f.xpath(f"//tei:app", namespaces=self.ns_decl)[min_pos: max_pos + 1]
                            concerned_apps_typology = f.xpath(f"//tei:app/@ana", namespaces=self.ns_decl)[
                                                      min_pos: max_pos + 1]
                            first_app = concerned_apps[0]

                            # Let's update the typology for further use
                            for index, transposed_app in enumerate(concerned_apps):
                                transposed_app.set('ana', concerned_apps_typology[index] + ' #transposition')

                            last_app = concerned_apps[-1]

                            starting_transposition_milestone = etree.Element('{%s}' % self.tei_ns + 'milestone')
                            starting_transposition_milestone.set('ana', '#transposition')
                            starting_transposition_milestone.set("type", "start")

                            ending_transposition_milestone = etree.Element('{%s}' % self.tei_ns + 'milestone')
                            ending_transposition_milestone.set('ana', '#transposition')
                            ending_transposition_milestone.set("type", "end")

                            first_parent = first_app.getparent()
                            last_parent = last_app.getparent()

                            first_parent.insert(first_parent.index(first_app), starting_transposition_milestone)
                            last_parent.insert(last_parent.index(last_app) + 1, ending_transposition_milestone)

                with open(output_file, "w") as output_xml_file:
                    output_xml_file.write(etree.tostring(f, pretty_print=True).decode())

        print("Fait !")

    def injection_omissions(self):
        '''
        Cette fonction récupère tous les apparats contenant des omissions et les réinjecte dans les témoins.
        En effet,
        INPUTS: des fichiers "*out.xml"
        OUTPUTS: des fichiers "*omitted.xml"
        '''

        print("Injecting omitted text in each witness:")
        # Première étape: on récupère toutes les omissions
        liste_omissions = []
        liste_temoins = glob.glob(f"{self.chemin}/*out.xml")
        assert len(liste_temoins) > 0
        for temoin in liste_temoins:
            with open(temoin, "r") as input_xml:
                f = etree.parse(input_xml)
                apps_with_omission = f.xpath("//tei:app[descendant::tei:rdg[not(node())]]", namespaces=self.ns_decl)

            for apparat in apps_with_omission:
                temoins_affectes = apparat.xpath("descendant::tei:rdg[not(node())]/@wit", namespaces=self.ns_decl)[
                    0].replace(
                    "#",
                    "").split()
                try:
                    # TODO: il y a un problème d'ordre dans ce cas, voir comment régler cela.
                    # On va chercher l'élément soeur précédent (w ou app).
                    preceding_sibling = \
                        apparat.xpath("preceding-sibling::node()[self::tei:app|self::tei:w]", namespaces=self.ns_decl)[
                            -1]
                    anchor = \
                        preceding_sibling.xpath(
                            "descendant-or-self::node()/attribute::*[name()='xml:id' or name()='id']",
                            namespaces=self.ns_decl)[0]
                    element_name = preceding_sibling.xpath(
                        "descendant-or-self::node()/attribute::*[name()='xml:id' or name()='id']/parent::*",
                        namespaces=self.ns_decl)[0]
                    # https://stackoverflow.com/a/51972010
                    element_name = etree.QName(element_name).localname

                # En cas d'omission en premier enfant de l'élément base, on va chercher le @n de cet élément base.
                except IndexError as e:
                    try:
                        ancestor_anchor_node = \
                            apparat.xpath(f"ancestor::node()[self::tei:p | self::tei:head]", namespaces=self.ns_decl)[0]
                        anchor = ancestor_anchor_node.xpath("@n", namespaces=self.ns_decl)[0]
                        element_name = ancestor_anchor_node.xpath("local-name()", namespaces=self.ns_decl)
                    except IndexError as e:
                        utils.error_checklist()
                        print(e)

                liste_omissions.append((temoins_affectes, apparat, anchor, element_name))

        # Deuxième étape, on réinjecte chaque élément tour à tour en se servant du dernier élément injecté.
        for temoin in liste_temoins:
            with open(temoin, "r") as input_xml:
                f = etree.parse(input_xml)
                sigle = "_".join(f.xpath("@xml:id")[0].split("_")[0:2])
                print(f"Treating {sigle}")

            for omission in liste_omissions:
                target_witness, app, anchor_id, anchor_name = omission
                if sigle not in target_witness:
                    continue
                else:
                    id_target_element = app.xpath("descendant::tei:rdg/@id", namespaces=self.ns_decl)[0]
                    if f.xpath(f"boolean(descendant::tei:rdg[@id = '{id_target_element}'])", namespaces=self.ns_decl):
                        continue
                    else:
                        if anchor_name == "rdg":
                            try:
                                anchor_element = \
                                    f.xpath(f"descendant::tei:app[descendant::tei:rdg[@id = '{anchor_id}']]",
                                            namespaces=self.ns_decl)[0]
                            except IndexError as e:
                                print(f"File {temoin}")
                                print(f"Error for anchor {anchor_id}. \nOmission: {omission}.\n"
                                      f"Exiting. Error can come from a wrong alignment of the source files.")
                                print(e)
                                exit(0)
                            anchor_parent = anchor_element.getparent()
                            # Ici on va voir si il n'y a pas un élément juste après (ex. note) pour éviter de le décaler; il est
                            # peu probable qu'il y en ait plus d'un à la suite.
                            if anchor_element.xpath(
                                    f"boolean(following-sibling::node()[1][not(self::tei:app | self::tei:w | self::tei:pc)])",
                                    namespaces=self.ns_decl):
                                anchor_parent.insert(anchor_parent.index(anchor_element) + 1, app)
                            else:
                                anchor_parent.insert(anchor_parent.index(anchor_element) + 1, app)
                        elif anchor_name == "w":
                            try:
                                anchor_element = \
                                    f.xpath(f"descendant::tei:w[@xml:id = '{anchor_id}']", namespaces=self.ns_decl)[0]
                                anchor_parent = anchor_element.getparent()
                                anchor_parent.insert(anchor_parent.index(anchor_element) + 1, app)
                            except IndexError as e:
                                print(f"Index error for {sigle}. Anchor id: {anchor_id}. Failed to inject:")
                                print(etree.tostring(app, pretty_print=True))
                                print(f"Please check file {temoin}")
                                exit(0)
                        elif anchor_name in ["p", "head"]:
                            # TODO: il y a un problème d'ordre dans ce cas, voir comment régler cela.
                            try:
                                anchor_element = \
                                    f.xpath(f"descendant::tei:{anchor_name}[@n = '{anchor_id}']",
                                            namespaces=self.ns_decl)[0]
                                anchor_element.insert(0, app)
                            except IndexError as e:
                                print("Index error. You should check the file final.xml")
                                print(f"Expression: descendant::tei:{element_name}[@n = '{anchor_id}']")
                                print(f"Element base: {self.element_base}")
                                print(f"@n: {anchor_id}")
                                print(etree.tostring(app, pretty_print=True))
                                exit(0)

            with open(temoin.replace('out', 'omitted'), "w") as input_xml:
                input_xml.write(etree.tostring(f, pretty_print=True).decode())

        # On vérifie que ça a marché: il faudrait le même nombre d'apparats partout.
        number_of_omissions = []
        list_of_ids = []
        liste_temoins = glob.glob(f"{self.chemin}/*out.xml")
        for temoin in liste_temoins:
            with open(temoin.replace('out', 'omitted'), "r") as input_xml:
                f = etree.parse(input_xml)
            number_of_apps = len(f.xpath("//tei:app", namespaces=self.ns_decl))
            ids = f.xpath("//tei:app/descendant::tei:rdg[1]/@id", namespaces=self.ns_decl)
            list_of_ids.append(set(ids))
            number_of_omissions.append(number_of_apps)

        if len(set(number_of_omissions)) == 1:
            print(f"Injection went well (all witnesses have the same number of tei:apps: {number_of_apps}).\n")
        else:
            # https://stackoverflow.com/a/25324329
            problematic_apps_id = set.union(*list_of_ids) - set.intersection(*list_of_ids)
            print(problematic_apps_id)
            print(f"Something went wrong with injection of the omissions:\n"
                  f"{number_of_omissions}.\n"
                  f"The problematic apps are: {problematic_apps_id}\n"
                  f"Exiting.")
            exit(0)

    def injection_ponctuation_parallele(self):
        """
        Cette fonction réinjecte la ponctuation de chaque témoin dans les témoins avec apparat.
        Sortie: "*omitted_punct.xml"
        """
        fichiers_apparat = f'{self.chemin}/apparat_*_*omitted_with_nodes.xml'
        # fichier de sortie: "*out.xml"
        liste = glob.glob(fichiers_apparat)
        pool = mp.Pool(processes=self.coeurs)
        print("Injection de la ponctuation: '*final.xml' -> '*omitted.xml'")
        command_list = [(fichier, self.type_division, self.div_n) for fichier in liste]
        pool.starmap(injection_ponctuation, command_list)
        print("Injection de la ponctuation ✓")

    def injection_intelligente(self):
        """
        Cette fonction permet d'injecter sur tous les fichiers les éléments d'un seul fichier.
        INPUTS: *omitted.xml
        OUTPUTS: *injected.xml
        """

        with open(f".debug/injection.txt", "w+") as debug_file:
            debug_file.truncate(0)

        liste_temoins = utils.get_file_list(f"{self.chemin}/*omitted.xml")

        self.recuperation_elements()
        print("Reinjecting non apparatus elements in the other witnesses:")
        for witness in liste_temoins:
            print(witness)
            self.reinjection_elements(target_file=witness)
            # on regarde le nombre d'exemples qui n'ont pas été injectés par temoin
            # self.verification_injections(temoin_a_verifier=witness)
        print("Done !")

    def regroupement_apparats(self):
        """
        Cette fonction regroupe les apparats qui peuvent l'être. Si deux apparats
        consécutifs contiennent les mêmes groupes de témoins, on peut les fusionner.
        TODO: continuer ici.
        """
        file = "divs/div1/apparat_Sal_J_1_final.xml"

        xml_file = utils.parse_xml_file(file)

        # On veut récupérer les sigles groupés.
        apps = xml_file.xpath("//tei:app", namespaces=self.ns_decl)

        grouped_witnesses = {
            index: tuple(app.xpath("descendant::tei:rdgGrp/descendant::tei:rdg/@wit", namespaces=self.ns_decl))
            for index, app in enumerate(apps)}

        ## Pour regrouper les consécutifs, on peut faire le regroupement d'abord puis regarder si les clés sont consécutives.
        # https://stackoverflow.com/a/54249535
        d = {tuple([k for k in grouped_witnesses.keys() if grouped_witnesses[k] == n]): n for n in
             set(grouped_witnesses.values())}

        # print(list(d.keys()))
        d_list = d.keys()

        list_of_positions = utils.merge_list_of_lists(
            [utils.group_adjacent_positions(list(group)) for group in d_list if
             utils.group_adjacent_positions(list(group))])
        list_of_positions = [(first, last) for first, last in list_of_positions if first != last]
        list_of_positions.sort(key=lambda x: x[0])

        for first, last in list_of_positions:
            print(list_of_positions)
            # Ici on va prendre tous les apps et les fusionner en un seul
            # en gardant tous les autres noeuds.
            # Un problème va se poser avec la ponctuation.
            # TODO: gérer la possibilité que des groupes soient constants mais qu'ils disent une chose
            #  différente: ce n'est pas parce que ce sont les mêmes regroupements que la leçon est identique
            #  pour les mêmes groupes
            grouped_witnesses = [
                tuple(app.xpath("descendant::tei:rdgGrp/descendant::tei:rdg/@wit", namespaces=self.ns_decl)) for app in
                apps[first:last]]
            print(grouped_witnesses)
            exit(0)
            old_app = apps[first]
            parent = old_app.getparent()
            new_app = etree.SubElement(parent, self.tei_ns + "app")
            pass

    def lacuna_identification(self, chemin, output_file):
        """
        Définition de lacune: une suite d'éléments d'apparats qui contiennent un élément vide
        Cette fonction regroupe les apparats marqués commes des ommissions dans un tei:seg pointant vers l'analyse d'omission.
        Fonction récursive. Une itération de la fonction correspond au regroupement d'un ensemble d'omissions.
        param :sensibilite: le nombre minimum d'apparats consécutifs  pour que soit considérée la lacune.
        """
        with open(chemin, "r") as file:
            xml_tree = etree.parse(file)
        print(f"Treating {chemin}")

        liste_sigles = [f"#{sigle}" for sigle in self.liste_sigles]

        for sigle in liste_sigles:
            # On essaie de faire le moins de requête avec lxml car c'est très lent. On va chercher le plus possible des listes pythons en amont
            all_apps = xml_tree.xpath(
                "//tei:app",
                namespaces=self.ns_decl)
            xpath_expression = f"//tei:app[contains(@ana,'#omission')][preceding::tei:app[1][contains(@ana,'#omission')][descendant::tei:rdg[not(node())][contains(@wit, '{sigle}')]]][descendant::tei:rdg[not(node())][contains(@wit, '{sigle}')]]"
            apps = xml_tree.xpath(
                xpath_expression,
                namespaces=self.ns_decl)
            apps_with_omission_id = [app.xpath("descendant::tei:rdg[1]/@id", namespaces=self.ns_decl)[0] for app in
                                     apps]

            # Cette expression est très probablement le raison du ralentissement.
            all_apps_id = xml_tree.xpath("//tei:app/descendant::tei:rdg[1]/@id", namespaces=self.ns_decl)
            positions = [all_apps_id.index(app) for app in apps_with_omission_id]

            ranges: list = utils.group_adjacent_positions(positions)

            # We filter the list with a given threshold
            omissions = [(a - 1, b) for a, b in ranges if b - a >= (self.lacuna_sensibility - 1)]

            for index, omission_span in enumerate(omissions):
                position_inf, position_sup = omission_span

                first_omitted_app = all_apps[position_inf]

                namespace = '{%s}' % self.tei_ns

                start_ident: str = utils.generateur_id()
                end_ident: str = utils.generateur_id()
                witEnd = etree.Element(namespace + 'witEnd')
                witEnd.set('{http://www.w3.org/XML/1998/namespace}id', start_ident)
                witEnd.set('corresp', sigle)
                witEnd.set('next', f'#{end_ident}')

                witStart = etree.Element(namespace + 'witStart')
                witStart.set('{http://www.w3.org/XML/1998/namespace}id', end_ident)
                witStart.set('corresp', sigle)
                witStart.set('previous', f'#{start_ident}')

                first_parent = first_omitted_app.getparent()
                first_parent.insert(first_parent.index(first_omitted_app), witEnd)

                last_omitted_app = all_apps[position_sup]

                last_parent = last_omitted_app.getparent()
                last_parent.insert(last_parent.index(last_omitted_app) + 1, witStart)

                # On supprime tous les tei:rdg vides.
                omitted_apps = all_apps[position_inf:position_sup + 1]

                for apparat in omitted_apps:
                    try:
                        empty_rdg = apparat.xpath("descendant::tei:rdg[not(node())]", namespaces=self.ns_decl)[0]
                    except:
                        print("Error for apparatus. Try relauching the program.")
                        print(apparat)
                        print(etree.tostring(apparat))
                        id = apparat.xpath("descendant::tei:rdg[1]/@id", namespaces=self.ns_decl)[0]
                        print(id)
                        exit(0)
                    witnesses = apparat.xpath("descendant::tei:rdg[not(node())]/@wit", namespaces=self.ns_decl)[0]
                    pattern = re.compile(f"\s?{sigle}")
                    updated_wit_att = re.sub(pattern, '', witnesses)
                    empty_rdg.set('wit', updated_wit_att)

        utils.remove_elements(xml_tree, "//tei:rdg[@wit='']", self.ns_decl)
        utils.remove_elements(xml_tree, "//tei:rdgGrp[not(descendant::tei:rdg)]", self.ns_decl)

        # On va mettre à jour la typologie des variantes (à garder?)
        update_omissions = xml_tree.xpath("//tei:app[contains(@ana, '#omission')][not(descendant::tei:rdg[not(node("
                                          "))])]", namespaces=self.ns_decl)
        for omission in update_omissions:
            current_att = omission.xpath("@ana", namespaces=self.ns_decl)[0]

            # On change pour not_apparat si le type est seulement omission; sinon on supprime #omission.
            if " " in current_att:
                omission.set('ana', current_att.replace('#omission ', ''))
            else:
                omission.set('ana', current_att.replace('#omission', '#not_apparat'))


        # Ici on va regrouper tous les tei:witEnd et witStart individuels adjacents
        self.group_adjacent_nodes(xml_tree, 'witEnd')
        self.group_adjacent_nodes(xml_tree, 'witStart')

        # On va maintenant identifier les omissions simples où un seul témoin diverge
        # for witEnd in xml_tree.xpath("descendant::tei:witEnd", namespaces=self.ns_decl):
        #     witnesses = witEnd.xpath("@corresp")[0]
        #     if len(witnesses.split()) == len(self.liste_sigles) - 1:
        #         corresponding_witStart_id = witEnd.xpath("@next")[0].replace("#", "")
        #         witEnd.set("ana", "#omission_constante_temoin")
        #         print(corresponding_witStart_id)
        #         try:
        #             corresponding_witStart = witEnd.xpath(f"following::tei:witStart[@xml:id='{corresponding_witStart_id}']", namespaces=self.ns_decl)[0]
        #         except IndexError as e:
        #             print(output_file)
        #         corresponding_witStart.set("ana", "#omission_constante_temoin")
        #     # Sinon, on passer à l'itération suivante
        #     else:
        #         continue

        with open(output_file, "w") as output_file:
            output_file.write(etree.tostring(xml_tree).decode())
        print("Done !")

    def group_adjacent_nodes(self, tree, node):
        """
        Cette fonction va regrouper les éléments identiques adjacents en un seul élément avec un attribut en commun.
        Utilisé pour regrouper les witStart et les witEnd.
        """
        coexistent_nodes = tree.xpath(f"//tei:{node}[preceding-sibling::node()[1][self::tei:{node}]]",
                                      namespaces=self.ns_decl)
        positions = [int(element.xpath(f"count(preceding::tei:{node})", namespaces=self.ns_decl)) for element in
                     coexistent_nodes]

        ranges = [(a - 1, b) for a, b in utils.group_adjacent_positions(positions)]
        for adjacent_positions in ranges:
            pos_inf, pos_sup = adjacent_positions
            first_element = \
                tree.xpath(f"//tei:{node}[count(preceding::tei:{node}) = {pos_inf}]", namespaces=self.ns_decl)[0]
            corresp_attributes = [tree.xpath(f"//tei:{node}[count(preceding::tei:{node}) = {cur_pos}]/@corresp",
                                             namespaces=self.ns_decl)[0] for cur_pos in range(pos_inf, pos_sup + 1)]

            # linked_elements = [tree.xpath(f"//tei:{node}[count(preceding::tei:{node}) = {cur_pos}]/@{attribute}",
            # namespaces=self.ns_decl)[0] for cur_pos in range(pos_inf, pos_sup + 1)]
            corresp_attributes.sort()
            first_element.set('corresp', ' '.join(corresp_attributes))

        for element in coexistent_nodes:
            # xml_id = element.xpath("@xml:id")[0]
            # next = element.xpath("@next")[0].replace('#', '')
            # previous = element.xpath("@previous")[0].replace('#', '')
            comment = etree.Comment(etree.tostring(element))
            first_parent = element.getparent()
            first_parent.insert(first_parent.index(element), comment)
            element.getparent().remove(element)

    def recuperation_elements(self):
        """
        Cette fonction va récupérer tous les éléments à injecter, et renvoie un tuple
        On produit une liste de tuples de la forme :
        [
        ('kNMdVRz', <Element {http://www.tei-c.org/ns/1.0}note at 0x7f08a90f9ac8>, 'Sev_R', position, level),
        ('oqcqYPq', <Element {http://www.tei-c.org/ns/1.0}note at 0x7f08a90f9c08>, 'Sal_J', position, level)
        ]
        Où:
        - le premier élément du tuple est l'ancre: l'élément du texte source où insérer l'élément à injecter
        - l'objet lxml.Element est l'élément à injecter
        - le sigle le fichier duquel provient l'élément
        - la position la position de l'ancre par rapport à l'élément à injecter.
        - level, le niveau affecté par l'élément (oeuvre ou témoin)
        """
        for element, value in self.elements_to_inject.items():

            # The position wrt the anchor. A note will appear after a word; while a milestone would appear before in general
            position = value["position"]

            # The level of the element: is it work (describes the work, and therefore all witnesses;
            # or witness (affecting a single witness). This will affect the injection: in a rdg affecting a base witness,
            # or in the rdg containing the orig element.
            level = value["level"]
            if position == "before":
                following_or_preceding = "following"  # on va chercher le tei:w suivant
            else:
                following_or_preceding = "preceding"  # on va chercher le tei:w précédent
            elements_to_inject = []
            final_list_of_tokens_id = []
            final_witness_list = []
            before_or_after = []
            level_list = []
            for file in glob.iglob(f"/home/mgl/Bureau/These/Edition/collator/{self.chemin}/*omitted.xml"):
                sigla = file.split("/")[-1].split(f"_{self.div_n}")[0].replace("apparat_", "")
                try:
                    current_tree = etree.parse(file)
                except Exception as e:
                    print(f"Parsing error: \n {e}\n\n"
                          f"Please make sure there is no space in any tei:w element.")

                # On va d'abord récuperer et aligner chaque élément tei:note, l'xml:id du tei:w qui précède et le témoin concerné

                # On ne veut pas récupérer certains éléments contenus dans d'autres éléments non partagés
                # entre tous les témoins. Exemple: si on ne réinjecte pas les tei:del, ne pas aller chercher dans
                # les enfants de ces éléments
                if len(self.excluded_elements) > 0:
                    excluded_elements_xpath = "[not(ancestor::" + "|ancestor::".join(self.excluded_elements) + ")]"
                else:
                    excluded_elements_xpath = ""
                elements_list = current_tree.xpath(
                    f"//{element}{excluded_elements_xpath}",
                    namespaces=self.ns_decl)
                number_of_elements = len(elements_list)
                list_of_tokens_id = []
                for current_element in elements_list:
                    try:
                        list_of_tokens_id.append(current_element.xpath(
                            f'{following_or_preceding}::tei:w[ancestor::tei:rdg[contains(@wit, \'{sigla}\')]][1]/@xml:id',
                            namespaces=self.ns_decl)[0])
                    except IndexError as e:
                        print("Index error. The element should be the first of the division.")
                        print(witness_id)
                        print(etree.tostring(current_element))

                witness_id = \
                    current_tree.xpath(f"//tei:div[@type='{self.type_division}']/@xml:id", namespaces=self.ns_decl)[0]
                witness_id = "_".join(witness_id.split("_")[0:2])
                final_witness_list.extend(
                    [witness_id for _ in range(number_of_elements)])  # https://stackoverflow.com/a/4654446
                before_or_after.extend([position for _ in range(number_of_elements)])
                final_list_of_tokens_id.extend(list_of_tokens_id)
                elements_to_inject.extend(elements_list)
                level_list.extend([level for _ in range(number_of_elements)])
            intermed_notes_tuples = list(
                zip(final_list_of_tokens_id, elements_to_inject, final_witness_list, before_or_after, level_list))
            self.processed_list.extend(intermed_notes_tuples)

    def reinjection_elements(self, target_file):
        """
        Cette fonction réinjecte dans chaque fichier l'ensemble des fichiers xml les éléments tei récupérés
        """
        current_xml_tree = etree.parse(target_file)
        # Chaque élément de la liste est de la forme: id de l'ancre, objet lxml, témoin d'origine, position de l'ancre
        # par rapport à l'élément à injecter
        for item in self.processed_list:
            anchor_id, element_to_inject, orig_witness, position, level = item
            try:
                element_id = element_to_inject.xpath("@xml:id")[0]
            except IndexError as e:
                print(f"Index error on element. Error: {e}\n")
                print(etree.tostring(element_to_inject, pretty_print=True).decode())
                print(f"Exiting. Please make sure the element is identified by an @xml:id.")
                exit(0)
            if orig_witness in target_file:
                pass
            else:
                if position == "before":
                    index_shift = 0
                else:
                    index_shift = 1

                # Certains élément existent déjà (ceux du témoin de provenance)
                if current_xml_tree.xpath(f"boolean(//node()[@xml:id='{element_id}'])"):
                    pass
                else:
                    sigla_output_wit = "_".join(
                        current_xml_tree.xpath(f"//tei:div[@type='{self.type_division}']/@xml:id",
                                               namespaces=self.ns_decl)[
                            0].split("_")[
                        0:2])
                    element_name = element_to_inject.xpath("local-name()")
                    element_id = element_to_inject.xpath("@xml:id")[0]
                    element_to_inject.set("injected", "injected")  # il faudra nettoyer ça à la fin de la boucle.
                    element_to_inject.set("corresp",
                                          f'#{orig_witness}')  # on indique de quel témoin provient l'élément.
                    try:
                        # Réécrire la fonction pour être plus spécifique sur l'exception.
                        anchor_word = \
                            current_xml_tree.xpath(f"//tei:w[@xml:id='{anchor_id}']", namespaces=self.ns_decl)[0]

                        # We want to inject the element in the tei:rdg containing our base witness.
                        if anchor_word.xpath("boolean(ancestor::tei:app)", namespaces=self.ns_decl):
                            # If  level eq work, we can reinject outside the apparatus.
                            # Example: a general note can be injected in any rdg and it makes sense to inject it in the base wit rdg.
                            if level == "work":
                                anchor_word = anchor_word.xpath(f"ancestor::tei:app", namespaces=self.ns_decl)[0]

                            # If the level is witness, we have to search for the corresponding rdg.
                            # For instance, an addition should be injected in the corresponding rdg. It makes no sense to inject
                            # it in the base wit rdg
                            elif level == "witness":
                                if anchor_word.xpath(
                                        f"boolean(ancestor::tei:app/descendant::tei:rdg[contains(@wit, '{orig_witness}')]/node())",
                                        namespaces=self.ns_decl):
                                    anchor_word = anchor_word.xpath(f"ancestor::tei:app/descendant::tei:rdg[contains("
                                                                    f"@wit, '{orig_witness}')]/tei:w",
                                                                    namespaces=self.ns_decl)[0]
                                else:
                                    # If there is an omission, we will inject the element after or before the tei:app.
                                    anchor_word = anchor_word.xpath(f"ancestor::tei:app", namespaces=self.ns_decl)[0]

                        # https://stackoverflow.com/questions/7474972/python-lxml-append-element-after-another-element
                        parent_element = anchor_word.getparent()
                        index = parent_element.index(anchor_word) + index_shift

                        # index can be -1 in case of a tei:w in a tei:rdg.
                        if index == -1:
                            index = 0

                        parent_element.insert(index, element_to_inject)
                    except Exception as e:
                        print(f"Injection failed for witness {sigla_output_wit}")
                        print(f"Element failed: {element_name}. Id: {element_id}. Original witness: {orig_witness}")
                        print(f"Element: {etree.tostring(element_to_inject, pretty_print=True)}")
                        print(f"Anchor id: {anchor_id}")
                        print("Make sure the order of the injection is correct (wrapping element should be injected "
                              "first)")
                        print(anchor_word.xpath("@xml:id")[0])

        with open(target_file.replace("omitted", "omitted.injected"), "w") as output_file:
            output_file.write(etree.tostring(current_xml_tree).decode())

    def same_word_identification(self, distance):
        """
        Cette fonction identifie les mots qui se répètent dans un rayon donné par la variable {distance}
        Elle permet de désambiguiser ensuite les mots dans les apparats.
        """

        liste_temoins = f"{self.chemin}/*_omitted.xml"

        for temoin in glob.glob(liste_temoins):
            sigle = utils.get_sigla_from_path(temoin)
            print(sigle)

            tree = etree.parse(temoin)
            tei_words = tree.xpath(f"descendant::tei:w[ancestor::tei:rdg[contains(@wit, '{sigle}')]]",
                                   namespaces=self.ns_decl)

            forms = [word.text for index, word in enumerate(tei_words)]

            same_words = [index for index, word in enumerate(forms) if word in forms[index + 1:index + 1 + distance]
                          or word in forms[index - 1 - distance:index]]

            [tei_w.set("ana", "#same_word") for index, tei_w in enumerate(tei_words) if index in same_words]

            with open(temoin, "w") as output_file:
                output_file.write(etree.tostring(tree, pretty_print=True).decode())

    def verification_injections(self, temoin_a_verifier):
        """
        Cette fonction vérifie le nombre d'éléments injectés
        Elle retourne le nombre d'éléments inejctés et leur id.
        TODO: transformer cette fonction qui prend trop de ressources.
        """

        debug_file = open(f".debug/injection.txt", "a")
        elements_a_verifier = [(element, temoin_origine, original_anchor) for
                               original_anchor, element, temoin_origine, position, level in self.processed_list if
                               temoin_origine not in temoin_a_verifier]
        temoin_a_verifier = temoin_a_verifier.replace("apparated", "apparated.injected")
        with open(temoin_a_verifier, "r") as input_file:
            try:
                arbre_a_verifier = etree.parse(input_file)
            except etree.XMLSyntaxError as e:
                print(f"Parsing error on witness {temoin_a_verifier}:")
                print(e)
                exit(0)

        # On compte le nombre d'éléments à injecter, moins ceux du propre témoin
        target_length = len(elements_a_verifier)
        correct_injections = 0
        debug_file.write(f"\n\n\nVerifying {temoin_a_verifier}\n")
        for element, temoin_origine, original_anchor in elements_a_verifier:
            element_name: str = element.xpath("local-name()")
            id_element: str = element.xpath("@xml:id")[0]
            parsed: list = arbre_a_verifier.xpath(f"//node()[@xml:id='{id_element}']", namespaces=self.ns_decl)
            if len(parsed) == 1:
                correct_injections += 1
                debug_file.write(
                    f"Correct injection: element {element_name}, id {id_element} (from {temoin_origine})\n")
            else:
                debug_file.write(
                    f"Error: element {element_name}, id {id_element} (from {temoin_origine}, anchor {original_anchor})\n")

        print(f"Treating: {temoin_a_verifier.split('/')[-1]}: ✓ ({correct_injections}/{target_length})")
        debug_file.write(
            f"{correct_injections} out of {target_length} target injections for witness {temoin_a_verifier}\n")

        debug_file.close()


def gestion_inversions(chemin, sensibilité=3):
    pass


def injection_ponctuation(fichier, div_type, div_n):
    """
    On prend le fichier originel et on réinjecte dans le fichier d'apparat.
    Pas intégré à la classe à cause du fonctionnement de mp.pool:
    https://stackoverflow.com/a/8805244
    """
    tei_namespace = 'http://www.tei-c.org/ns/1.0'
    NSMAP1 = {'tei': tei_namespace}  # pour la recherche d'éléments avec la méthode xpath
    sigle = "_".join(fichier.split("/")[-1].split("_")[1:3])
    temoin_tokenise_correspondant = f"temoins_tokenises/{sigle}.xml"
    print(f"Treating {sigle}")

    # D'abord on récupère la ponctuation dans le fichier tokénisé
    with open(temoin_tokenise_correspondant, "r") as input_xml_file:
        f = etree.parse(input_xml_file)
    punctuation = f.xpath(f"//tei:pc[ancestor::tei:div[@type= '{div_type}'][@n = '{div_n}']]", namespaces=NSMAP1)
    # On va chercher tous les premiers éléments précédents avec un xml:id, sauf les pb et les cb qui peuvent être à l'intérieur
    # d'un tei:w et donc fausser le jeu.

    try:
        preceding_element_id = [
            punct.xpath("preceding-sibling::node()[@xml:id][not(self::tei:lb|self::tei:pb)][1]/@xml:id",
                        namespaces=NSMAP1)[0] for punct in punctuation]
    except IndexError as e:
        print(f"Index error for punctuation retrieval: {e}")
        print("The parser is looking for punctuation elements that are direct following"
              "siblings of another element. Please make sure no punctuation element"
              "starts a node.")
        exit(0)

    assert len(preceding_element_id) == len(punctuation)

    punctuation_and_anchor = zip(punctuation, preceding_element_id)

    with open(fichier, "r") as interm_file:
        f = etree.parse(interm_file)
    for punctuation_element in punctuation_and_anchor:
        punctuation, anchor_id = punctuation_element
        try:
            current_anchor = f.xpath(f"//node()[contains(@xml:id, '{anchor_id}')]")[0]
        except IndexError as e:
            print(f"{fichier}: index error with token {anchor_id}. Exiting.\n {e}")
            exit(0)

        parent_anchor = current_anchor.getparent()
        parent_anchor.insert(parent_anchor.index(current_anchor) + 1, punctuation)

    # Et on écrit le fichier.
    with open(fichier.replace("omitted_with_nodes", "omitted_punct"), "w") as output_file:
        output_file.write(etree.tostring(f, pretty_print=True).decode())


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
        borne_inferieure, borne_superieure = verification_ngram(sensibilite + 1, apps, borne_inferieure, sigle)
    return borne_inferieure, borne_superieure
