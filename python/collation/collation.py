import json
import os
import re
import subprocess
import multiprocessing as mp
import sys
import time

import Levenshtein
import python.utils.utils as utils

from lxml import etree
import glob
import collatex
from halo import Halo


class CorpusPreparation:
    def __init__(self, saxon, temoin_leader, type_division, element_base, liste_temoins, integrer_deplacements):
        self.saxon = saxon
        self.temoin_leader = temoin_leader
        self.type_division = type_division
        self.element_base = element_base
        self.liste_temoins = liste_temoins
        if integrer_deplacements is True:
            self.integrer_deplacements = 'True'
        else:
            self.integrer_deplacements = 'False'

    def prepare(self, div_number):
        """
        Cette fonction sépare chaque division en autant d'éléments base (exemple, en 10 paragraphes)
        qui seront donnés à CollateX pour alignement; elle produit aussi un fichier global qui rassemble l
        """
        ((div1_type, div1_n), (div2_type, div2_n), (div3_type, div3_n)) = div_number
        print(f"Scission du corpus, création de dossiers et de fichiers par chapitre.")
        cmd = f"java -jar {self.saxon} temoins_tokenises_regularises/{self.temoin_leader}.xml xsl/pre_alignement" \
              f"/preparation_corpus.xsl " \
              f"temoin_leader={self.temoin_leader} compare_with_shifting={self.integrer_deplacements} type_division={self.type_division} element_base={self.element_base} "\
               f"div1_type={div1_type} div2_type={div2_type} div3_type={div3_type} "\
               f'div1_n={div1_n} div2_n={div2_n} div3_n={div3_n}'
        subprocess.run(cmd.split())
        print("\nPréparation du corpus pour alignment ✓")


class Aligner:
    """
    La classe principale d'alignement.
    """
    def __init__(self, liste_fichiers_xml: list,
                 chemin: str,
                 moteur_transformation_xsl: str,
                 correction_mode: bool,
                 parametres_alignement: str,
                 nombre_de_coeurs,
                 align_on: int):
        self.nombre_de_coeurs = nombre_de_coeurs
        self.liste_fichiers_xml = liste_fichiers_xml
        self.chemin = chemin
        self.moteur_transformation_xsl = moteur_transformation_xsl
        self.correction_mode = correction_mode
        self.parametres_alignement = parametres_alignement

        if align_on != 1 and align_on != 2:
            raise ValueError("Le paramètre align_on doit valoir 1 "
                             "(on aligne sur les lemmes et les parties du discours) ou 2 "
                             "(on aligne sur les lemmes uniquement)")
        self.align_on = align_on

    def transformation_json(self, input_fichier_xml, output_fichier_json):
        """
        Étape avant la collation: transformation en json selon la structure voulue par CollateX.
        Voir https://collatex.net/doc/#json-input
        """
        param_align_on = f"align_on={str(self.align_on)}"
        subprocess.run(['java', '-jar', self.moteur_transformation_xsl, output_fichier_json, input_fichier_xml,
                        'xsl/pre_alignement/transformation_json.xsl', param_align_on])

    def alignement(self, fichier_a_collationer, numero):
        """
            Alignement CollateX, puis regroupement des leçons communes en lieux variants. La méthode collatex.collate() est
            ici trompeuse. CollateX ne fait que l'alignement; la collation (=déterminer s'il y a lieu
             variant ou pas, typer les variantes, identifier les omissions) est faite ensuite.
        """
        alignement = self.parametres_alignement
        # on réécrit la variable en cas de mode correction
        if self.correction_mode:
            alignement = 'mam'

        with open(fichier_a_collationer,
                  'r') as entree_json0:  # ouvrir le fichier en mode lecture et le mettre dans une variable
            entree_json1 = entree_json0.read()
        # Export au format JSON (permet de conserver les xml:id)
        try:
            json_str = json.loads(entree_json1)  # permet de mieux gérer les sauts de ligne pour le
        except Exception as e:
            print(f'error in json [{fichier_a_collationer}]: \n {e}')
        # JSON: https://stackoverflow.com/a/29827074
        if alignement == 'global':
            print("Global alignment")
            resultat_json = collatex.collate(json_str, output='json', segmentation=True, near_match=True, astar=False)
        else:
            resultat_json = collatex.collate(json_str, output='json', segmentation=False, near_match=False, astar=False,
                                             detect_transpositions=False)
            # segmentation=False permet une collation au mot-à-mot:
            # http://interedition.github.io/collatex/pythonport.html
        nom_fichier_sortie = f'{self.chemin}/alignement_collatex{numero}.json'
        with open(nom_fichier_sortie, 'w') as sortie_json:
            sortie_json.write(resultat_json)

    def alignement_collatex(self, fichier_xml):
        """
        Alignement avec collatex; il en sort du JSON
        """
        fichier_sans_extension = os.path.basename(fichier_xml).split(".")[0]
        numero = fichier_sans_extension.split("_")[1]
        fichier_json = f"{fichier_sans_extension}.json"
        fichier_json_complet = f"{self.chemin}/{fichier_json}"
        output_fichier_json = f"-o:{self.chemin}/{fichier_json}"
        input_fichier_xml = f"{self.chemin}/{fichier_xml}"
        # Étape avant la collation: transformation en json selon la structure voulue par CollateX
        self.transformation_json(input_fichier_xml, output_fichier_json)
        # Alignement avec CollateX. Il en ressort du JSON, encore
        self.alignement(fichier_json_complet, numero)
        print(f"{fichier_xml}: done !")

    def  run(self):
        with mp.Pool(processes=self.nombre_de_coeurs) as pool:
            # https://www.kite.com/python/answers/how-to-map-a-function-with-
            # multiple-arguments-to-a-multiprocessing-pool-in-python
            data = [
                (fichier_xml,)
                for fichier_xml in
                self.liste_fichiers_xml
            ]
            pool.starmap(self.alignement_collatex, data)
        print("Done !")


class Collateur:
    def __init__(self, log: bool, chemin_fichiers, div_n, div_type, temoin_base):
        self.log = log
        self.chemin_fichiers = chemin_fichiers
        self.div_n = div_n
        self.div_type = div_type
        self.tei_ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
        self.temoin_base = temoin_base

    def run_collation(self):
        self.produce_typed_apps(f'apparat_final.json')
        self.raffinage_apparats(f'divs/div{self.div_n}/apparat_collatex.xml')

    def produce_typed_apps(self, fichier_entree):
        """
            Cette fonction permet de passer de la table d'alignement (JSON) à
            l'apparat proprement dit, avec création d'apparat s'il y a
            variation, et regroupement des leçons identiques.
            Elle fonctionne avec une liste de dictionnaires au format JSON,
            chaque dictionnaire représentant un lieu variant. Les trois premiers items de la liste
            pourront être par exemple:

             liste_dict =
                [{
                    '0" : ["", "", "Phil_J", "LEMMA", "POS'],
                    '1" : ["a0a6f5ec2-a98u9ds98yh", "Ca iiii", "Mad_G", "LEMMA", "POS'],
                    '2" : ["a0a9f5dsc2-a9sdnjxcznk", "Ca iiii", "Phil_Z", "LEMMA", "POS']
                    }, {
                    '0" : ["a4d2587a-a98u98yh", "do", "Phil_J", "LEMMA", "POS'],
                    '1" : ["a0a6f5ec2-a98u9ds98yh", "do", "Mad_G", "LEMMA", "POS'],
                    '2" : ["a0a9f5dsc2-a9sdnjxcznk", "donde", "Phil_Z", "LEMMA", "POS'],
                    '3" : ["prout-cacau98yh", "onde", "Phil_K", "LEMMA", "POS'],
                    '4" : ["a4sde2587a-a9fu98yh", "donde", "Phil_U", "LEMMA", "POS'],
                    '5" : ["a4sd88888e2587a-a999999h", "do", "Phil_M", "LEMMA", "POS']
                    }, {
                    '0" : ["a4d2587a-a98u98yh", "muesstra", "Phil_J", "LEMMA", "POS'],
                    '1" : ["a0a6f5ec2-a98u9ds98yh", "muestra", "Mad_G", "LEMMA", "POS'],
                    '2" : ["a0a9f5dsc2-a9sdnjxcznk", "prueua", "Phil_Z", "LEMMA", "POS']
                }]

            Fonctionnement de la fonction:
            - ) Le texte aligné est une liste de dictionnaires, pour en garder la linéarité: voir plus haut pour la
                structure de cette liste.
            - ) Chaque lieu variant est représenté par un dictionnaire
            1 ) On va en un premier lieu comparer toutes les chaînes de caractères pour déterminer
                s'il y a lieu de créer un apparat. Si elles sont distinctes, on est face à des lieux
                variants, et on enclenche la suite.
            2 ) Si il y a des lieux variants, on fonctionne de la manière suivante. On a deux dictionnaires,
                un dictionnaire d'entrée (décrit plus haut), et un dictionnaire de sortie qui contiendra les
                informations d'apparat. On va créer une liste liste_lecons qui va nous permettre de comparer chaque chaîne
                aux chaînes précédentes.

                *Pour chaque item* du dictionnaire d'entrée, on vérifie que la chaîne, en position 1, n'est pas déjà présente
                dans la liste liste_lecons.
                    - Si elle n'est pas présente, on l'ajoute à la liste, et on crée un item
                    dans le dictionnaire de sortie dict_sortie. Cet item est organisé de la façon suivante:
                        'lieu_variant": ["témoin(s)", "id_token(s)", "lemme", "pos']
                        On le voit, la valeur correspondant à chaque clé est une liste.
                    - Si la chaîne existe déjà dans la liste liste_lecons, c'est qu'elle est aussi dans le
                    dictionnaire de sortie: on va donc modifier la valeur de l'item dont la clé est cette chaîne,
                    en ajoutant le témoin correspondant ainsi que les identifiants de token, de lemme et de pos.

            3 ) Une fois le dictionnaire créé, on le transforme en xml en suivant la grammaire de la TEI pour les apparats.

            4) On va effectuer une opération de comparaison des lemmes et des POS pour déterminer le type de variante

            5 ) La dernière étape est la réinitialisation de la liste liste_lecons et du dictionnaire dict_sortie,
                qui est en réalité en début de boucle.


            Pour l'instant, n'est traité que l'xml:id, mais aussi le POS et le lemma, mais on peut ajouter d'autres fonctions


        """
        fichier_entree = f"{self.chemin_fichiers}/{fichier_entree}"
        with open(fichier_entree, 'r+') as fichier:
            liste_dict = json.load(fichier)
            tei_namespace = 'http://www.tei-c.org/ns/1.0'
            tei = '{%s}' % tei_namespace
            NSMAP0 = {None: tei_namespace}  # the default namespace (no prefix)
            root = etree.Element(tei + 'root', nsmap=NSMAP0)  # https://lxml.de/tutorial.html#namespaces
            #  https://stackoverflow.com/questions/7703018/how-to-write-namespaced-element-attributes-with-lxml
            for dic in liste_dict:
                apparat = True
                dict_sortie = {}
                liste_lecons = []

                # Étape 1: déterminer si il y a variation ou pas
                for key, value in dic.items():
                    id_token, lecon_depart, temoin, lemme, pos = value
                    liste_lecons.append((lecon_depart, lemme, pos))

                if len(liste_lecons) > 0:
                    # Comparer chaque lecon à la première
                    identite_forme = all(forme == liste_lecons[0][0] for forme, lemme, pos in liste_lecons)
                    identite_lemme = all(lemme == liste_lecons[0][1] for forme, lemme, pos in liste_lecons)
                    identite_pos = all(pos == liste_lecons[0][2] for forme, lemme, pos in liste_lecons)
                    # Première étape. Si tous les lieux variants sont égaux ainsi que leur analyse grammaticale
                    # entre eux,ne pas créer d'apparat mais imprimer
                    # directement le texte
                    # On ne va pas utiliser les autres vérifcations car quand les formes sont identiques, il y a
                    # de très faibles chances que le mot soit un homographe dans le même contexte.
                    app = etree.SubElement(root, tei + 'app')
                    # if identite_forme and identite_lemme and identite_pos:
                    if identite_forme:
                        apparat = False
                    else:
                        pass

                    # La liste créée va permettre de vérifier si une leçon identique
                    # a déjà été traitée auparavant. On la réinitialise
                    # car on l'a déjà utilisée pour vérifier l'égalité entre leçons
                    # dans le lieu variant précédent
                    liste_lecons = []
                    liste_lemme = []
                    liste_pos = []
                    for key, value in dic.items():
                        id_token, lecon_depart, temoin, lemme, pos = value
                        # attention à bien faire la comparaison SSI le lemme/pos existe
                        # ajouter le lemme à la liste
                        liste_lemme.append(lemme)
                        liste_pos.append(pos)

                        # Si le lieu variant n'existe pas dans la liste,
                        # créer un item de dictionnaire
                        if lecon_depart not in liste_lecons:
                            # dict_sortie[lecon_depart] = [id_token, temoin]
                            dict_sortie[lecon_depart] = [id_token, temoin, lemme, pos]

                            # Ajouter le lieu variant dans la liste.
                            liste_lecons.append(lecon_depart)

                        # Si le lieu variant a déjà été rencontré
                        else:
                            temoin1 = dict_sortie.get(lecon_depart)[1]
                            token1 = dict_sortie.get(lecon_depart)[0]
                            lemme1 = dict_sortie.get(lecon_depart)[2]
                            pos1 = dict_sortie.get(lecon_depart)[3]
                            token2 = token1 + '_' + id_token
                            temoin2 = temoin1 + ' ' + temoin
                            lemme2 = lemme1 + '_' + lemme
                            pos2 = pos1 + ' ' + pos
                            dict_sortie[lecon_depart] = [token2, temoin2, lemme2, pos2]

                            # Mise à jour la liste
                            liste_lecons.append(lecon_depart)

                    type_apparat = self.typologie_variantes(liste_lemmes=liste_lemme,
                                                            liste_pos=liste_pos,
                                                            liste_lecons=liste_lecons)

                    # Si on a une omission, on refait un tour en supprimant les éléments vides
                    if type_apparat == "omission":
                        liste_lecons = [element for element in liste_lecons if element != ""]
                        liste_lemme = [element for element in liste_lemme if element != ""]
                        liste_pos = [element for element in liste_pos if element != ""]
                        type_apparat = self.typologie_variantes(liste_lemmes=liste_lemme,
                                                                liste_pos=liste_pos,
                                                                liste_lecons=liste_lecons)
                        if all(lecon == liste_lecons[0] for lecon in liste_lecons):
                            type_apparat = '#omission'
                        else:
                            premier_type = 'omission'
                            deuxieme_type = type_apparat
                            if deuxieme_type == 'graphique':
                                # Si il n'y a qu'un lemme dans la liste, on n'a pas une variation graphique mais simplement
                                # une omission face à des leçons concordantes
                                if len(liste_lemme) == 1:
                                    type_apparat = f"#{premier_type}"
                                    print("Cancelled type")
                                else:
                                    type_apparat = f"#{premier_type} #{deuxieme_type}"
                            else:
                                type_apparat = f"#{premier_type} #{deuxieme_type}"

                    else:
                        type_apparat = f"#{type_apparat}"

                    if self.log:
                        with open("logs/variant_log.txt", "a") as variants_log:
                            variants_log.write(f"Variante: {type_apparat}\n"
                                               f"Formes: {' '.join(liste_lecons)}\n"
                                               f"Lemmes: {' '.join(liste_lemme)}\n"
                                               f"Pos: {' '.join(liste_pos)}\n\n")

                    if not apparat:
                        app.set('ana', '#not_apparat')
                    else:
                        app.set('ana', type_apparat)
                # Une fois le dictionnaire de sortie produit, le transformer en XML.
                for key, value in dict_sortie.items():
                    if not apparat:
                        xml_id, temoin, lemmes, pos = value[0], value[1], value[2], value[3]
                        lecon = str(key)
                        rdg = etree.SubElement(app, tei + 'rdg')
                        # on indique que tous les témoins proposent la leçon
                        rdg.set('id', utils.generateur_id())
                        rdg.set('wit', temoin)
                        rdg.set('n', xml_id)
                        rdg.set('lemma', lemmes)
                        rdg.set('pos', pos)
                    else:
                        lecon = str(key)
                        xml_id, temoin, lemmes, pos = value[0], value[1], value[2], value[3]
                        rdg = etree.SubElement(app, tei + 'rdg')
                        rdg.set('id', utils.generateur_id())
                        rdg.set('lemma', lemmes)
                        rdg.set('pos', pos)
                        rdg.set('wit', temoin)
                        rdg.set('n',
                                f'{xml_id}')  # ensemble des id des tokens, pour la
                        # suppression de la redondance plus tard
                        # Re-créer les noeuds tei:w
                    liste_w = lecon.split()
                    liste_id = xml_id.split('_')
                    position_in_id = 0
                    for mot in liste_w:
                        nombre_mots = len(liste_w)
                        xml_id_courant = '_'.join(liste_id[position_in_id::nombre_mots])  # on va distribuer les xml:id:
                        # abcd > ac, db pour 2 témoins qui lisent la même chose (ab et cd sont les identifiants des deux
                        # tokens identiques, donc il faut distribuer pour identifier le premier token, puis le second)
                        word = etree.SubElement(rdg, tei + 'w')
                        word.set('{http://www.w3.org/XML/1998/namespace}id', xml_id_courant)
                        word.text = mot
                        position_in_id += 1

            # L'apparat est produit. Écriture du fichier xml
            sortie = '%s/apparat_collatex.xml' % self.chemin_fichiers
            with open(sortie, 'w+') as sortie_xml:
                output = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True).decode('utf8')
                sortie_xml.write(str(output))

    def typologie_variantes(self, liste_lemmes, liste_pos, liste_lecons):
        """
        Cette fonction permet de produire la typologie des variantes.
        Elle s'appuie notamment sur l'article de Camps, Spadini et Ing 2019:
        "Collating Medieval Vernacular Texts: Aligning Witnesses, Classifying Variants"
        On présuppose qu'il y a une variante graphique.
        """
        # TODO: remplacer les + par des espaces pour ignorer les crases qui sont souvent
        # TODO: uniquement des variantes graphiques: PR0CN00+PP3CSD0 > PR0CN00 PP3CSD0
        #  ignorer: como/cómo FAIT
        #  AQ0CS00 / AQ0FS00 / AO0MS00 avec un entier, on peut ignorer. (ignorer les analyses sur les cardinaux/ordinaux)
        #  Idem PT / PR avec une différence d'accent.
        # TODO: éventuellement, créer une liste pour ignorer certains lemmes dans la comparaison
        #  des POS: comme que par exemple, qu'il s'agira de corriger non pas sur le XML mais
        #  directement sur le TSV lors de la production du corpus. Ou alors, considérer que c'est
        #  une variante graphique si le terme n'est pas analysé comme un nom au moins une fois.

        # TODO: ajouter une règle si la différence est seulement une différence d'espaces. Idem pour les accents
        # TODO: idem, si adjectifs du même lemme, on peut ignorer le reste.

        # On commence par supprimer les accents: il est très peu probable que deux homographes se retrouvent
        # dans un même lieu variant. Ensuite, on normalise la casse et les ramistes, car les normes de transcription diffèrent
        # entre transcription manuelle et OCR/HTR

        comparaison_lemme = all(elem == liste_lemmes[0] for elem in liste_lemmes[1:])
        comparaison_pos = all(elem == liste_pos[0] for elem in liste_pos[1:])

        list_lecon_sans_accents = [utils.remove_accents(lecon) for lecon in liste_lecons]
        list_lecon_lower_case = [lecon.lower() for lecon in list_lecon_sans_accents]
        list_lecon_ramistes = [utils.normalize_ramistes(lecon) for lecon in list_lecon_lower_case]
        normalized_forms = list_lecon_ramistes

        list_lecon_corrected = [utils.compensate_freeling_normalisation(lecon) for lecon in liste_lecons]
        # On regarde si la différence ne tient qu'aux accents: si tel est le cas, on présuppose qu'il n'y a pas de variation

        similarity_not_normalized = all(elem == liste_lecons[0] for elem in liste_lecons[1:])
        similarity_normalized = all(elem == normalized_forms[0] for elem in normalized_forms[1:])
        if not similarity_not_normalized and similarity_normalized:
            normalization_discrepancy = True
        else:
            normalization_discrepancy = False

        similarity_freeling = all(elem == list_lecon_corrected[0] for elem in list_lecon_corrected[1:])

        if not similarity_not_normalized and similarity_freeling:
            freeling_discrepancy = True
        else:
            freeling_discrepancy = False

        similarity_accent = all(elem == list_lecon_sans_accents[0] for elem in list_lecon_sans_accents[1:])

        if not similarity_not_normalized and similarity_accent:
            accent_discrepancy = True
        else:
            accent_discrepancy = False

        # On a besoin de filtrer certaines erreurs dûes au fait que Freeling gère très mal l'homographie
        # Les éléments du filtre seront ignorés, soit parce que c'est trop coûteux
        # de corriger dans le XML ou car il n'y a pas d'intérêt à la variante.
        filtre_lemmes = [('como', 'cómo', 'commo'), ('et', 'e'), ('más', 'mas'), ('él', 'el'),
                         ('esta', 'está', 'ésta'), ('grande', 'gran'), ('el', 'lo'), ('uno', '1'),
                         ('probar', 'prueba'), ('daño', 'dañar'), ('atrever', 'atrevido')]

        # Idem pour les pos: on va ignorer les lieux variants avec POS dans le filtre et lemmes identiques.
        # Ce filtrage est à supprimer si le lemmatiseur est de meilleure qualité
        filtre_pos = [('AQ0MS0', 'PI0MS000'), ('SP', 'SPS00'),  ('NCMP000', 'AQ0MP0'), ('NCMS000', 'AQ0MS0'), ('NCFP000', 'NCMP000'),
                      ('PR000000', 'RG'), ('CS', 'PT000000', 'PR000000'),
                      ('VMIS3S0', 'VMIP1S0'), ('VMII1S0', 'VMII3S0'), ('VSSI3S0', 'VSSI1S0'),
                      ('Z', 'PI0FS000', 'DI0FS0'), ('PR0CN000', 'CS')]

        filtre_nombres = re.compile("\d+")

        # si tous les lemmes et tous les pos sont identiques: il s'agit d'une variante graphique.
        # Ici il faut se rappeler qu'il y a une différence entre les formes
        type_de_variante = None

        # on veut identifier correctement les problèmes de normalisation, et les distinguer des
        # variantes graphiques
        if freeling_discrepancy and not comparaison_pos:
            return "graphique"
        elif freeling_discrepancy and not comparaison_lemme:
            return "graphique"
        if normalization_discrepancy or accent_discrepancy:
            return "normalisation"

        if not comparaison_lemme:  # si il y a une différence de lemmes seulement: 'vraie variante'
            if all(pos.startswith('NP') for pos in liste_pos):
                type_de_variante = 'entite_nommee'
            else:
                # on cherche à vérifier si pour une entrée tous les lemmes (all) sont compris dans un des couples (any)
                if any(all(lemme in couple for lemme in liste_lemmes) for couple in filtre_lemmes):
                    type_de_variante = 'filtre'
                else:
                    if "" in list(set(liste_lemmes)):
                        type_de_variante = 'omission'
                    else:
                        type_de_variante = 'lexicale'
        elif comparaison_lemme and not comparaison_pos:  # si seul le pos change
            # On va identifier les variantes numerales, pas toujours intéressantes à montrer (ii° vs ii par exemple)
            if all(re.match(filtre_nombres, lemme) for lemme in liste_lemmes):
                type_de_variante = 'numerale'
            # On peut avoir un lemme identique et un pos qui change ('como' p.ex)
            elif any(all(lemme in couple for lemme in liste_lemmes) for couple in filtre_lemmes):
                if any(all(pos in couple for pos in liste_pos) for couple in filtre_pos):
                    type_de_variante = 'filtre'
                else:
                    type_de_variante = 'morphosyntaxique'
            elif all(pos.startswith('NC') for pos in liste_pos):
                # On rappelle la structure de l'étiquette du nom: NCMS000 pour un nom masculin singulier
                if all(pos[2] == liste_pos[0][2] for pos in liste_pos):
                    if all(pos[3] == liste_pos[0][3] for pos in liste_pos):
                        type_de_variante = "indetermine"
                    else:
                        type_de_variante = 'personne'
                else:
                    type_de_variante = 'genre'
            # On essaie d'identifier les variantes d'auxiliarité, pour les ignorer éventuellement, Freeling
            # n'étant pas très efficace sur ce point.
            elif all(pos.startswith('V') for pos in liste_pos):
                if all(pos[1] in ['A', 'M', 'S'] for pos in liste_pos) and all(
                        pos[2:] == liste_pos[0][2:] for pos in liste_pos):
                    type_de_variante = "auxiliarite"
                else:
                    if any(all(pos in couple for pos in liste_pos) for couple in filtre_pos):
                        type_de_variante = "filtre"
                    else:
                        type_de_variante = "morphosyntaxique"
            else:
                if any(all(pos in couple for pos in liste_pos) for couple in filtre_pos):
                    type_de_variante = "filtre"
                else:
                    type_de_variante = 'morphosyntaxique'
        elif comparaison_pos and comparaison_lemme:  # si lemmes et pos sont indentiques
            if liste_lemmes[0] == '' or liste_pos[0] == '':  # si égaux parce que nuls, variante
                # indéterminée
                type_de_variante = 'indetermine'
            else:  # si on a un lemme et un PoS identiques, la variante est graphique
                type_de_variante = 'graphique'
        else:
            print(f"Problème ici: variante indeterminée:"
                  f"\n{liste_lemmes}\n{liste_pos}")
            type_de_variante = "indetermine"
        return type_de_variante

    def raffinage_apparats(self, fichier):
        """
        Cette fonction permet de raffiner les apparats en rassemblant les variantes graphiques au sein d'un apparat qui
        comporte des variantes "vraies" ou morphosyntaxiques. On va créer des tei:rdgGroup qui rassembleront les rdg.
        La dernière étape est l'ordonnement des variantes par proximité avec la leçon du témoin-base.
        Cette fonction réécrit le fichier d'entrée.
        """
        # TODO: fusionner cette fonction avec la fonction de création d'apparat ?
        # TODO: il reste un problème dans le cas suivant (en amont): chaîne identique, (lemme?|)pos différent.
        parser = etree.XMLParser(load_dtd=True,
                                 resolve_entities=True)

        tei_namespace = 'http://www.tei-c.org/ns/1.0'
        namespace = '{%s}' % tei_namespace
        f = etree.parse(fichier, parser=parser)  # https://lxml.de/tutorial.html#namespaces
        root = f.getroot()

        # On travaille d'abord sur les apparats de type graphique: un seul tei:rdgGrp qui va tout englober
        liste_apps_graphique = root.xpath(
            f"//tei:app[@ana='#graphique'] | //tei:app[@ana='#normalisation'] | //tei:app[@ana='#filtre']",
            namespaces=self.tei_ns)
        for apparat in liste_apps_graphique:
            lecon = apparat.xpath(f"descendant::tei:rdg", namespaces=self.tei_ns)
            # S'il n'y a que deux lemmes, pas besoin de raffiner l'apparat, on crée des tei:rdgGrp pour plus de
            # simplicité de traitement ensuite.
            rdg_grp = etree.SubElement(apparat, namespace + 'rdgGrp')
            for rdg in lecon:
                rdg_grp.append(rdg)

        # Puis on s'intéresse aux autres apparats
        liste_apps = root.xpath(
            f"//tei:app[not(@ana='#graphique') and not(@ana='#normalisation') and not(@ana='#filtre')]",
            namespaces=self.tei_ns)
        for apparat in liste_apps:
            lecon = apparat.xpath(f"descendant::tei:rdg", namespaces=self.tei_ns)
            # S'il n'y a que deux lemmes, pas besoin de raffiner l'apparat, on crée des tei:rdgGrp pour plus de
            # simplicité de traitement ensuite.
            if len(lecon) <= 2:
                for rdg in lecon:
                    parent = rdg.getparent()
                    rdg_grp = etree.SubElement(parent, namespace + 'rdgGrp')
                    rdg_grp.append(rdg)


            # Sinon, les choses deviennent intéressantes
            else:
                liste_de_lecons = apparat.xpath(f"tei:rdg", namespaces=self.tei_ns)
                liste_annotations = []
                for lecon in liste_de_lecons:
                    texte = " ".join(lecon.xpath("descendant::tei:w/descendant::text()", namespaces=self.tei_ns))
                    identifiant_rdg = lecon.xpath("@id", namespaces=self.tei_ns)[0]
                    lemme = lecon.xpath("@lemma")[0]
                    pos = lecon.xpath("@pos")[0]
                    pos_reduit = pos.split(" ")[0]
                    wit = lecon.xpath("@wit")
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
                            try:
                                dictionnaire_de_regroupement[i].append(identifiant)
                            except KeyError:
                                dictionnaire_de_regroupement[i] = [identifiant]
                            # Le dictionnaire est de la forme: {(pos, lemmes): [liste des identifiants]]}

                # Ce qui nous intéresse, c'est de produire les groupes: on ne garde que les valeurs
                # du dictionnaire
                rdg_groups = list(dictionnaire_de_regroupement.values())
                groups_dict = {}
                for analyse, identifiants in dictionnaire_de_regroupement.items():
                    wit = []
                    for ident in identifiants:
                        wit.append(apparat.xpath(f"tei:rdg[@id = '{ident}']/@wit", namespaces=self.tei_ns)[0])
                    groups_dict[analyse] = (identifiants, wit)

                # On va pouvoir maintenant créer des rdgGroups autour des tei:rdg que l'on a identifiés
                # comme similaires.
                # TODO: adapter cet ordonnement à chaque témoin-base (pas possible pour l'instant)
                output_dict = {}
                # On itère sur les groupes constitués pour trouver le témoin-base et on initialise
                # le dictionnaire qui va contenir notre ordre final et nos identifiants
                for analyse, (identifiants, wits) in groups_dict.items():
                    if any([self.temoin_base in wit for wit in wits]):
                        output_dict[0] = identifiants
                        # On récupère la forme.
                        try:
                            forme_temoin_base = \
                                apparat.xpath(
                                    f"tei:rdg[contains(@wit, '{self.temoin_base}')]/descendant::tei:w/descendant::text()",
                                    namespaces=self.tei_ns)[0]
                        except IndexError:
                            forme_temoin_base = ''
                        del groups_dict[analyse]
                        break

                # On veut maintenant trier l'ordre d'apparition des leçons, en mettant toujours le témoin base
                # (ou, plus tard, le lemme retenu) en premier dans l'ordre, et les omissions des autres témoins en dernier.
                # Pour le reste, il s'agit de calculer des distances formelles.
                # Le but ici est de faire des distances de levenshtein sur chaque couple {base-autre} pour déterminer
                # l'ordre correct d'apparition par proximité lexicale. On travaille sur les formes et c'est p.e.
                # ce qui pêche ici cependant, mais travailler sur les lemmes poserait pb en cas de variante morphosyntaxique

                if len(rdg_groups) > 2:
                    assert len(rdg_groups) == len(groups_dict) + 1
                    idents_to_compare = [ident for analyse, (ident, wit) in groups_dict.items()]
                    forms_to_compare = []
                    for ident in idents_to_compare:
                        try:
                            corresponding_form = \
                                apparat.xpath(f"tei:rdg[@id = '{ident[0]}']/descendant::tei:w/descendant::text()",
                                              namespaces=self.tei_ns)[0]
                        except IndexError:
                            corresponding_form = ''
                        forms_to_compare.append(corresponding_form)
                    forms_and_idents = list(zip(forms_to_compare, idents_to_compare))

                    if forme_temoin_base == '':
                        # Cas où le témoin base omet: dans ce cas, on ordonne alphabétiquement
                        forms_and_idents.sort(key=lambda x: x[0])
                        output_dict = {**output_dict, **{index + 1:
                                                             identifiants for index, (forme, identifiants) in
                                                         enumerate(forms_and_idents)}}

                    elif len(forms_to_compare) == 2 and '' in forms_to_compare:
                        # Cas où on a 3 groupes de variantes, dont une omission
                        # L'ordre choisi est donc: temoin-base / temoin / omission
                        forms_and_idents.sort(key=lambda x: x[0], reverse=True)
                        output_dict = {**output_dict, **{index + 1:
                                                             identifiants for index, (forme, identifiants) in
                                                         enumerate(forms_and_idents)}}

                    else:
                        # Dans les autres cas seulement, on peut produire la distance de Levenstein.

                        # Par la suite il suffira de brancher l'analyseur sémantique ici pour améliorer le classement.

                        interm_list = []
                        for form, ident in forms_and_idents:
                            normalized_form = utils.remove_accents(form)
                            normalized_form = utils.normalize_ramistes(normalized_form)
                            normalized_temoin_base = utils.remove_accents(forme_temoin_base)
                            if form == "":
                                # On pénalise les formes vides pour pouvoir les classer en dernier par tri de distance.
                                distance = 20
                            else:
                                distance = Levenshtein.distance(normalized_temoin_base, normalized_form)
                            interm_list.append((distance, (form, ident)))

                        # Si la distance est la même, on trie par ordre alphabétique.
                        if all([distance == interm_list[0][0] for distance, (form, idents) in interm_list]):
                            interm_list = sorted(interm_list, key=lambda x: x[1][0])
                        else:
                            interm_list = sorted(interm_list, key=lambda x: x[0])
                        output_dict = {**output_dict,
                                       **{index + 1: value[1][1] for index, value in enumerate(interm_list)}}



                # Sinon, c'est simple (=2 groupes seulement)
                # il suffit juste d'ajouter en 2e position le 2e groupe de lieux variants
                else:
                    try:
                        output_dict[1] = [identifiants for analyse, (identifiants, wits) in groups_dict.items()][0]
                        output_dict = {key: identifiants for key, identifiants in output_dict.items()}
                    except IndexError:
                        print("Erreur dans l'ordonnement des apparats. "
                              "Cette erreur ne devrait pas exister, elle suppose un "
                              "apparat ne contenant qu'un rdgGrp et qui ne serait pas "
                              "classifié comme 'not_apparat'. En général, cela est dû à "
                              "un problème de lemmatisation ou d'analyse grammaticale.")
                        # Dans ce cas, c'est que le dictionnaire de compte qu'un item.
                        print(dictionnaire_de_regroupement)
                        output_dict = {0: list(dictionnaire_de_regroupement.values())[0]}

                # Modifier le nom de la variable une fois que ça marchera
                rdg_groups = [output_dict[index] for index in range(len(output_dict))]

                # Les lignes précédentes ne marchent pas. voir + tard
                # rdg_groups = list(dictionnaire_de_regroupement.values())
                # Créons donc des tei:rdgGrp parents pour ces groupes
                for group in rdg_groups:
                    tei_namespace = 'http://www.tei-c.org/ns/1.0'
                    namespace = '{%s}' % tei_namespace
                    rdg_grp = etree.SubElement(apparat, namespace + 'rdgGrp')
                    for identifiant in group:
                        try:
                            orig_rdg = apparat.xpath(f"tei:rdg[@id = '{identifiant}']", namespaces=self.tei_ns)[0]
                        except IndexError as error:
                            print(etree.tostring(apparat, pretty_print=True).decode())
                            print(f"Index error. Rdg's id: {identifiant}. \n"
                                  f"Error: {error}. Exiting.\n"
                                  f"The error could come from the lemmatization.")
                            exit(0)
                        rdg_grp.append(orig_rdg)
                # Enfin, on va trier les groupes par ordre de proximité formelle
                # avec la leçon du témoin-base, dans le cas de +2 groupes

        with open(fichier, 'w+') as sortie_xml:
            output = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True).decode('utf8')
            sortie_xml.write(str(output))
