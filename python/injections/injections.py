import math
import pickle
import re

import tqdm
from lxml import etree
import glob
import operator
import traceback
import multiprocessing as mp
import itertools
import numpy as np
import shutil
from operator import itemgetter
import subprocess

from typing import List

import python.utils.utils as utils


class Injector:
    def __init__(self, debug, div_n, elements_to_inject, saxon, chemin, coeurs, element_base,
                 type_division, lacuna_sensibility):
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

    def run_injections(self):
        self.injection_apparats()
        self.injection_omissions()
        self.injection_ponctuation_parallele()
        self.injection_intelligente()
        self.regroupement_omissions()

    def regroupement_omissions(self):
        for fichier_xml in glob.glob(f"divs/div{self.div_n}/*_injected_punct.xml"):
            print(f"Regroupement des omissions sur {fichier_xml.split('/')[-1]}")
            self.lacuna_identification(fichier_xml, output_file=fichier_xml.replace('.xml', '.lacuned.xml'))

    def injection_apparats(self):
        """
        Fonction qui réinjecte les apparats dans chaque transcription individuelle.
        Elle produit les fichiers "*_outc.xml".

        :param saxon: le moteur saxon
        :param chemin:  le chemin du dossier courant
        :param chapitre: le chapitre courant
        Fichier entrée: juxtaposition_orig.xml
        Fichiers sortie: "*final.xml"
        """
        print("---- INJECTION 1: apparats ----")
        param_division = f"chapitre={str(self.div_n)}"  # Premier paramètre passé à la xsl: le chapitre à processer
        param_chemin_sortie = f"chemin_sortie={self.chemin}/"  # Second paramètre: le chemin vers le fichier de sortie
        fichier_entree = f"{self.chemin}/juxtaposition_orig.xml"
        # fichiers de sortie: "*apparat_*_*.xml"
        # with Halo(text="Injection des apparats dans chaque transcription individuelle", spinner='dots'):
        #  première étape de l'injection. Apparats, noeuds textuels et suppression de la redondance
        chemin_injection = "xsl/post_alignement/injection_apparats.xsl"
        subprocess.run(
            ["java", "-jar", self.saxon, fichier_entree, chemin_injection, param_division, param_chemin_sortie])

        # seconde étape: noeuds non textuels
        print("\n---- INJECTION 2: suppression de la redondance ----")
        regular_expression = "apparat_[A-Z][a-z]{2,4}_[A-Z]_[0-9]{1,2}.xml"
        regular_expression_with_path = re.compile(f'{self.chemin}/{regular_expression}')
        # fichier de sortie: "*outb.xml"
        liste = glob.glob(f"{self.chemin}/*.xml")
        filtered_list = [element for element in liste if re.match(regular_expression_with_path, element)]
        chemin_injection2 = "xsl/post_alignement/injection_apparats2.xsl"
        self.parallel_transformation(chemin_injection2, param_division, filtered_list)

        print("\n---- INJECTION 2bis: suppression de la redondance ----")
        chemin_injection3 = "xsl/post_alignement/injection_apparats3.xsl"
        fichiers_apparat = f'{self.chemin}/apparat_*_*outb.xml'
        # fichier de sortie: "*outc.xml"
        liste = glob.glob(fichiers_apparat)
        self.parallel_transformation(chemin_injection3, param_division, liste)

        #  quatrième étape: gestion des lacunes
        print("\n---- INJECTION 3: lacunes ----")
        chemin_injection_lacunes = "xsl/post_alignement/gestion_lacunes.xsl"
        fichiers_apparat = f'{self.chemin}/apparat_*_*outc.xml'
        liste = glob.glob(fichiers_apparat)
        # Sortie: "*_final.xml"
        self.parallel_transformation(chemin_injection_lacunes, param_division, liste)
        print("Création des balises de lacunes ✓")

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

    def injection_omissions(self):
        '''
        Cette fonction récupère tous les apparats contenant des omissions.
        Entrée: des fichiers "*final.xml"
        Sortie: des fichiers "*omitted.xml"
        '''

        print("Injecting omitted text in each witness:")
        # Première étape: on récupère toutes les omissions
        liste_omissions = []
        self.liste_temoins = utils.chemin_fichiers_finaux(self.div_n)
        for temoin in self.liste_temoins:
            with open(temoin, "r") as input_xml:
                f = etree.parse(input_xml)
                apps_with_omission = f.xpath("//tei:app[descendant::tei:rdg[not(node())]]", namespaces=self.ns_decl)

            for apparat in apps_with_omission:
                temoins_affectes = apparat.xpath("descendant::tei:rdg[not(node())]/@wit", namespaces=self.ns_decl)[
                    0].replace(
                    "#",
                    "").split()
                try:
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
                except:
                    element_name = self.element_base
                    anchor = apparat.xpath(f"ancestor::tei:{element_name}/@n", namespaces=self.ns_decl)[0]

                liste_omissions.append((temoins_affectes, apparat, anchor, element_name))

        # Deuxième étape, on réinjecte
        for temoin in self.liste_temoins:
            with open(temoin, "r") as input_xml:
                f = etree.parse(input_xml)
                sigle = "_".join(f.xpath("@xml:id")[0].split("_")[0:2])
                print(f"Treating {sigle}")

            for omission in liste_omissions:
                target_witness, app, anchor_id, anchor_name = omission
                app.set("type", "omission")
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
                                print(f"Error for anchor {anchor_id}. \nOmission: {omission}.\n"
                                      f"Exiting.")
                                exit(0)
                            anchor_parent = anchor_element.getparent()
                            # Ici on va voir si il n'y a pas un élément juste après (ex. note) pour éviter de le décaler; il est
                            # peu probable qu'il y en ait plus d'un à la suite.
                            if anchor_element.xpath(
                                    f"boolean(following-sibling::node()[1][not(self::tei:app | self::tei:w | self::tei:pc)])",
                                    namespaces=self.ns_decl):
                                anchor_parent.insert(anchor_parent.index(anchor_element) + 2, app)
                            else:
                                anchor_parent.insert(anchor_parent.index(anchor_element) + 1, app)
                        elif anchor_name == "w":
                            anchor_element = \
                                f.xpath(f"descendant::tei:w[@xml:id = '{anchor_id}']", namespaces=self.ns_decl)[0]
                            anchor_parent = anchor_element.getparent()
                            anchor_parent.insert(anchor_parent.index(anchor_element) + 1, app)
                        elif anchor_name == self.element_base:
                            anchor_element = \
                                f.xpath(f"descendant::tei:{self.element_base}[@n = '{anchor_id}']",
                                        namespaces=self.ns_decl)[0]
                            anchor_element.insert(0, app)

            with open(temoin.replace('final', 'omitted'), "w") as input_xml:
                input_xml.write(etree.tostring(f, pretty_print=True).decode())

        # On vérifie que ça a marché: il faudrait le même nombre d'apparats partout.
        number_of_omissions = []
        for temoin in self.liste_temoins:
            with open(temoin.replace('final', 'omitted'), "r") as input_xml:
                f = etree.parse(input_xml)
            number_of_apps = len(f.xpath("//tei:app", namespaces=self.ns_decl))
            number_of_omissions.append(number_of_apps)

        if len(set(number_of_omissions)) == 1:
            print(f"Injection went well (all witnesses have the same number of tei:apps: {number_of_apps}).\n")
        else:
            print(f"Something went wrong with injection of the omissions:\n"
                  f"{number_of_omissions}.\n"
                  f"Exiting.")
            exit(0)

    def injection_ponctuation_parallele(self):
        """
        Cette fonction réinjecte la ponctuation de chaque témoin dans les témoins avec apparat.
        Sortie: "*omitted_punct.xml"
        """
        fichiers_apparat = f'{self.chemin}/apparat_*_*omitted.xml'
        # fichier de sortie: "*out.xml"
        liste = glob.glob(fichiers_apparat)
        pool = mp.Pool(processes=self.coeurs)
        print("Injection de la ponctuation: '*final.xml' -> '*omitted.xml'")
        command_list = [(fichier, self.type_division, self.div_n) for fichier in liste]
        pool.starmap(injection_ponctuation, command_list)
        print("Injection de la ponctuation ✓")

    def injection_intelligente(self):
        """
        Cette fonction permet d'injecter sur tous les fichiers les éléments d'un seul fichier. Elle produit les fichiers
        "*_injected_punct.xml"

        :return: None
        """

        with open(f".debug/injection.txt", "w+") as debug_file:
            debug_file.truncate(0)

        liste_temoins = [temoin.replace("final", "omitted_punct") for temoin in self.liste_temoins]

        self.recuperation_elements()
        print("Reinjecting elements in the other witnesses:")
        for witness in liste_temoins:
            self.reinjection_elements(target_file=witness)
            # on regarde le nombre d'exemples qui n'ont pas été injectés par temoin
            self.verification_injections(temoin_a_verifier=witness)

    def lacuna_identification(self, chemin, tree=None, n_it=0, output_file=None):
        """
        Définition de lacune: une suite d'éléments d'apparats qui contiennent un élément vide
        Cette fonction regroupe les apparats marqués commes des ommissions dans un tei:seg pointant vers l'analyse d'omission.
        Fonction récursive. Une itération de la fonction correspond au regroupement d'un ensemble d'omissions.
        param :sensibilite: le nombre minimum d'apparats consécutifs  pour que soit considérée la lacune.
        """
        if chemin:
            with open(chemin, "r") as file:
                xml_tree = etree.parse(file)
        elif tree:
            xml_tree = tree

        # Avec cette expression, on va chercher tous les tei:app[@type='omission'] qui suivent (directement ou pas=
        # un tei:app de type omission

        apps = xml_tree.xpath(
            "//tei:app[@type='omission'][not(ancestor::tei:seg)][preceding::tei:app[1][@type='omission']]",
            namespaces=self.ns_decl)
        positions = [int(app.xpath("count(preceding::tei:app)", namespaces=self.ns_decl)) for app in apps]
        ranges = []

        # https://stackoverflow.com/a/2154437 on veut regrouper les positions contigües.
        for k, g in itertools.groupby(enumerate(positions), lambda x: x[0] - x[1]):
            group = (map(itemgetter(1), g))
            group = list(map(int, group))
            ranges.append((group[0], group[-1]))

        # On récupère la position de nos groupes d'omissions. On soustrait 1 à a car on a cherché toutes les
        # omissions qui suivaient une omission. Il faut récupérer la première omission de chaque groupe.
        # Pourquoi on soustrait 1 à sensibilité (a et b étant les bornes):
        # - Deux apparats qui se suivent (sensibilité 2) <=> position b - a = 1
        # - Trois apparats (sensibilité 3) <=> position b - a = 2
        # - etc.
        omissions = [(a - 1, b) for a, b in ranges if b - a >= (self.lacuna_sensibility - 1)]


        # Quand il n'y a plus de groupe identifié, on peut arrêter le processus récursif.
        if len(omissions) == 0:
            print("Done !")
            with open(output_file, "w") as output_file:
                output_file.write(etree.tostring(xml_tree).decode())
            return


        # Maintenant que l'on a les positions des omissions, on peut mettre tous les app dans un tei:listApp de type omission
        position_inf, position_sup = omissions[0]

        # Reprendre ici, il y a un bug
        #if position_inf != 0:
        #    position_inf += 1
        rang = range(position_inf, position_sup + 1)
        omitted_apps = [xml_tree.xpath(f"//tei:app[@type='omission'][count(preceding::tei:app) = {pos}]",
                                       namespaces=self.ns_decl)[0] for pos in rang]
        current_node_is_boundary = False
        omissions_list = []
        omissions_list.append(omitted_apps[0])
        current_node = omitted_apps[0]
        # On va aller chercher les noeuds entre les deux apps qui font les bornes.
        while not current_node_is_boundary:
            current_node = current_node.getnext()
            if current_node is not None:
                omissions_list.append(current_node)
                current_node_is_boundary = current_node.xpath(f"boolean(self::tei:app[@type='omission'][count(preceding::tei:app) = {position_sup}])", namespaces=self.ns_decl)
            else:
                current_node_is_boundary = True
        omissions_list.append(omitted_apps[-1])

        first_omitted_app = xml_tree.xpath(f"//tei:app[@type='omission'][count(preceding::tei:app) = {position_inf}]",
                                           namespaces=self.ns_decl)[0]


        # https://stackoverflow.com/a/6045260
        namespace = '{%s}' % self.tei_ns
        omission_seg = etree.Element(namespace + 'seg')
        parent = first_omitted_app.getparent()
        parent.insert(parent.index(first_omitted_app), omission_seg)

        # On va insérer tous les éléments trouvés dans le tei:seg
        for i in omissions_list[0:]:
            omission_seg.insert(-1, i)
        # On ajoute le premier élément de la liste, sinon il est ajouté à la fin,
        # bug que je ne comprends pas
        omission_seg.insert(0, omissions_list[0])
        # On ajoute la balise de borne inférieure
        omission_seg.insert(0, first_omitted_app)


        # On va tester ici si l'omission est continue du point de vue des témoins
        list_of_lists = []
        for apparat in omission_seg.xpath("descendant::tei:app", namespaces=self.ns_decl):
            list_of_sets = []
            for reading in apparat.xpath("descendant::tei:rdg/@wit", namespaces=self.ns_decl):
                list_of_sets.append(set(reading.split()))
            list_of_lists.append(list_of_sets)
        # On va tester ici si l'omission est continue du point de vue des témoins
        # On a une liste listes de sets de la forme [[{A, B},{C}],[{A, B},{C}]]
        # qui décrivent nos groupes de témoins
        # On veut que toutes les listes soient égales entre elles
        binary_constant_omission = all(list_of_lists[n] == list_of_lists[0] for n in range(len(list_of_lists)))
        if binary_constant_omission:
            # Type le plus simple d'omission: deux groupes constants tout au long du passage: il n'y a pas de variation
            # au sein du texte
            omission_seg.set('ana', '#omission #binary')
            # @corresp indique le témoin qui conserve le texte omis
            omission_seg.set('corresp', omission_seg.xpath("descendant::tei:rdg[node()]/@wit", namespaces=self.ns_decl)[0])
        else:
            omission_seg.set('ana', '#omission')

        # On va essayer d'identifier les témoins qui sont omis tout au long de la lacune.
        list_of_witnesses = omission_seg.xpath("descendant::tei:app[1]/descendant::tei:rdg/@wit", namespaces=self.ns_decl)
        list_of_witnesses = [element.split() for element in list_of_witnesses]
        output_list = []
        [output_list.extend(element) for element in list_of_witnesses]
        full_wit_list = set(output_list)
        constant_list = []
        for witness in full_wit_list:
            list_of_witnesses = []
            for apparatus in omission_seg.xpath("descendant::tei:app/descendant::tei:rdg[not(node())]", namespaces=self.ns_decl):
                list_of_witnesses.append(" ".join(apparatus.xpath("@wit")).split())
            if all([witness in liste for liste in list_of_witnesses]):
                constant_list.append(witness)

        # La liste ne devrait pas être vide
        if len(constant_list) > 0:
            # Exclude indique les témoins qui omettent le texte (donc exclus du segment en quelque sorte)
            omission_seg.set("exclude", " ".join(constant_list))
        # Si la liste est vide c'est que l'on a deux omissions différentes adjacentes
        else:
            print("Issue with omission: two different omissions must have been joined")


        # Et on relance la fonction, avec une valeur d'itération supplémentaire.
        self.lacuna_identification(chemin=None, node=xml_tree, n_it=n_it + 1, output_file=output_file)

    def recuperation_elements(self):
        """
        Cette fonction va récupérer tous les éléments à injecter, et renvoie un tuple
        On produit une liste de tuples de la forme :
        [
        ('kNMdVRz', <Element {http://www.tei-c.org/ns/1.0}note at 0x7f08a90f9ac8>, 'Sev_R', position),
        ('oqcqYPq', <Element {http://www.tei-c.org/ns/1.0}note at 0x7f08a90f9c08>, 'Sal_J', position)
        ]
        Où:
        - le premier élément du tuple est l'ancre: l'élément du texte source où insérer l'élément à injecter
        - l'objet lxml.Element est l'élément à injecter
        - le sigle le fichier duquel provient l'élément
        - la position la position de l'ancre par rapport à l'élément à injecter.
        """
        for item in self.elements_to_inject:
            element, position = item
            if position == "before":
                following_or_preceding = "following"  # on va chercher le tei:w suivant
            else:
                following_or_preceding = "preceding"  # on va chercher le tei:w précédent
            elements_to_inject = []
            final_list_of_tokens_id = []
            final_witness_list = []
            before_or_after = []
            for file in glob.iglob(f"/home/mgl/Bureau/These/Edition/collator/divs/div{self.div_n}/*omitted_punct.xml"):
                try:
                    current_tree = etree.parse(file)
                except Exception as e:
                    print(f"Parsing error: \n {e}\n\n"
                          f"Please make sure there is no space in any tei:w element.")

                # On va d'abord récuperer et aligner chaque élément tei:note, l'xml:id du tei:w qui précède et le témoin concerné
                elements_list = current_tree.xpath(
                    f"//{element}[not(ancestor::tei:del|ancestor::tei:add[@type='commentaire'])]",
                    namespaces=self.ns_decl)
                # On est obligés d'ajouter une règle sur les tei:del et les gloses marginales pour l'instant; voir comment gérer ça plus tard.
                number_of_elements = len(elements_list)
                list_of_tokens_id = [current_element.xpath(
                    f'{following_or_preceding}::tei:w[1]/@xml:id',
                    namespaces=self.ns_decl)[0] for current_element in elements_list]
                witness_id = current_tree.xpath("//tei:div[@type='chapitre']/@xml:id", namespaces=self.ns_decl)[0]
                if witness_id:
                    witness_id = "_".join(witness_id.split("_")[0:2])
                    final_witness_list.extend(
                        [witness_id for _ in range(number_of_elements)])  # https://stackoverflow.com/a/4654446
                    before_or_after.extend([position for _ in range(number_of_elements)])
                final_list_of_tokens_id.extend(list_of_tokens_id)
                elements_to_inject.extend(elements_list)
            intermed_notes_tuples = list(
                zip(final_list_of_tokens_id, elements_to_inject, final_witness_list, before_or_after))

            self.processed_list.extend(intermed_notes_tuples)

    def reinjection_elements(self, target_file):
        """
        Cette fonction réinjecte dans chaque fichier l'ensemble des fichiers xml les éléments tei récupérés
        """
        current_xml_tree = etree.parse(target_file)
        # Chaque élément de la liste est de la forme: id de l'ancre, objet lxml, témoin d'origine, position de l'ancre
        # par rapport à l'élément à injecter
        for item in self.processed_list:
            anchor_id, element, temoin, position = item
            try:
                element_id = element.xpath("@xml:id")[0]
            except IndexError as e:
                print(f"Index error on element. Error: {e}\n")
                print(etree.tostring(element, pretty_print=True).decode())
                print(f"Exiting. Please make sure the element is identified by an @xml:id.")
                exit(0)
            if temoin in target_file:
                pass
            else:
                if position == "before":
                    operation = operator.sub  # et on injectera donc avant ce tei:w (index(tei:w) - 1)
                else:
                    operation = operator.add  # et on injectera donc après ce tei:w (index(tei:w) + 1)
                existing_element = current_xml_tree.xpath(f"boolean(//node()[@xml:id='{element_id}'])")
                if existing_element:
                    pass
                else:
                    sigla = "_".join(
                        current_xml_tree.xpath(f"//tei:div[@type='chapitre']/@xml:id", namespaces=self.ns_decl)[
                            0].split("_")[
                        0:2])
                    element_name = element.xpath("local-name()")
                    element_id = element.xpath("@xml:id")[0]
                    element.set("injected", "injected")  # il faudra nettoyer ça à la fin de la boucle.
                    element.set("corresp", f'#{temoin}')  # on indique de quel témoin provient l'élément.
                    try:
                        # Réécrire la fonction pour être plus spécifique sur l'exception.
                        word_to_change = \
                            current_xml_tree.xpath(f"//tei:w[@xml:id='{anchor_id}']", namespaces=self.ns_decl)[0]
                        # We want to inject the element in the tei:rdg containing our base witness.
                        if word_to_change.xpath("boolean(ancestor::tei:app)", namespaces=self.ns_decl):
                            # We check for omissions in target witness
                            if word_to_change.xpath(
                                    f"boolean(ancestor::tei:app/descendant::tei:rdg[contains(@wit, '{sigla}')]/node())",
                                    namespaces=self.ns_decl):
                                word_to_change = word_to_change.xpath(f"ancestor::tei:app/descendant::tei:rdg[contains("
                                                                      f"@wit, '{sigla}')]/tei:w",
                                                                      namespaces=self.ns_decl)[0]
                            else:
                                # If there is an omission, we will inject the element after or before the tei:app.
                                word_to_change = word_to_change.xpath(f"ancestor::tei:app", namespaces=self.ns_decl)[0]

                        # https://stackoverflow.com/questions/7474972/python-lxml-append-element-after-another-element
                        item_element = word_to_change.getparent()

                        # https://stackoverflow.com/a/54559513
                        index = operation(item_element.index(word_to_change), 1)

                        # index can be -1 in case of a tei:w in a tei:rdg.
                        if index == -1:
                            index = 0
                        item_element.insert(index, element)
                    except Exception as e:
                        print(f"Injection failed for witness {sigla}")
                        print(f"Element failed: {element_name}. Id: {element_id}. Original witness: {temoin}")
                        print(word_to_change.xpath("@xml:id")[0])

        with open(target_file.replace("omitted_punct", "injected_punct"), "w") as output_file:
            output_file.write(etree.tostring(current_xml_tree).decode())

    def verification_injections(self, temoin_a_verifier):
        """
        Cette fonction vérifie le nombre d'éléments injectés
        Elle retourne le nombre d'éléments inejctés et leur id.
        """

        debug_file = open(f".debug/injection.txt", "a")

        elements_a_verifier = [(element, temoin_origine, original_anchor) for
                               original_anchor, element, temoin_origine, position in self.processed_list if
                               temoin_origine not in temoin_a_verifier]
        temoin_a_verifier = temoin_a_verifier.replace("omitted", "injected")
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
    preceding_element_id = [punct.xpath("preceding-sibling::node()[@xml:id][not(self::tei:lb|self::tei:pb)][1]/@xml:id",
                                        namespaces=NSMAP1)[0]
                            for punct in punctuation]
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
    with open(fichier.replace("omitted", "omitted_punct"), "w") as output_file:
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
