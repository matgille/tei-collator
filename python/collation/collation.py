import json
import os
import re
import subprocess
import multiprocessing as mp

import python.utils.utils as utils

from lxml import etree
import glob
import collatex
from halo import Halo


class CorpusPreparation:
    def __init__(self, saxon, temoin_leader, type_division, element_base, liste_temoins):
        self.saxon = saxon
        self.temoin_leader = temoin_leader
        self.type_division = type_division
        self.element_base = element_base
        self.liste_temoins = liste_temoins

    def prepare(self, div_number):
        """
        Cette fonction sépare chaque division en autant d'éléments base (exemple, en 10 paragraphes)
        qui seront donnés à CollateX pour alignement; elle produit aussi un fichier global qui rassemble l
        """
        print(f'Scission du corpus, création de dossiers et de fichiers par chapitre sur {div_number}.')
        # Produit à la fois "juxtaposition_\d.xml" et "juxtaposition_orig.xml"
        cmd = f'java -jar {self.saxon} temoins_tokenises_regularises/{self.temoin_leader}.xml xsl/pre_alignement' \
              f'/preparation_corpus.xsl ' \
              f'temoin_leader={self.temoin_leader} type_division={self.type_division} element_base={self.element_base} numero_div={div_number}'
        subprocess.run(cmd.split())
        print("\nPréparation du corpus pour alignment ✓")


class Aligner:
    def __init__(self, liste_fichiers_xml: list, chemin: str, moteur_transformation_xsl: str, correction_mode: bool,
                 parametres_alignement: str,
                 nombre_de_coeurs):
        self.nombre_de_coeurs = nombre_de_coeurs
        self.liste_fichiers_xml = liste_fichiers_xml
        self.chemin = chemin
        self.moteur_transformation_xsl = moteur_transformation_xsl
        self.correction_mode = correction_mode
        self.parametres_alignement = parametres_alignement

    def transformation_json(self, input_fichier_xml, output_fichier_json):
        """
        Étape avant la collation: transformation en json selon la structure voulue par CollateX.
        Voir https://collatex.net/doc/#json-input
        """
        param_correction = f"correction={self.correction_mode}"
        subprocess.run(['java', '-jar', self.moteur_transformation_xsl, output_fichier_json, input_fichier_xml,
                        'xsl/pre_alignement/transformation_json.xsl', param_correction])

    def alignement(self, fichier_a_collationer, numero):
        """
            Alignement CollateX, puis regroupement des leçons communes en lieux variants
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
            resultat_json = collatex.collate(json_str, output='json', segmentation=True)
        else:
            resultat_json = collatex.collate(json_str, output='json', segmentation=False)
            # segmentation=False permet une collation au mot-à-mot:
            # http://interedition.github.io/collatex/pythonport.html
        nom_fichier_sortie = f'{self.chemin}/alignement_collatex{numero}.json'
        with open(nom_fichier_sortie, 'w') as sortie_json:
            sortie_json.write(resultat_json)

    def alignement_collatex(self, fichier_xml):
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

    def run(self):
        with mp.Pool(processes=self.nombre_de_coeurs) as pool:
            # https://www.kite.com/python/answers/how-to-map-a-function-with-
            # multiple-arguments-to-a-multiprocessing-pool-in-python
            data = [
                (fichier_xml,)
                for fichier_xml in
                self.liste_fichiers_xml
            ]
            pool.starmap(self.alignement_collatex, data)


class Collateur:
    def __init__(self, log: bool, chemin_fichiers, div_n):
        self.log = log
        self.chemin_fichiers = chemin_fichiers
        self.div_n = div_n
        self.tei_ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    def run(self):
        self.collate(f'apparat_final.json')
        # Continuer ici
        self.raffinage_apparats(f'divs/div{self.div_n}/apparat_collatex.xml')

    def collate(self, fichier_entree):
        """
            Cette fonction permet de passer de la table d'alignement à
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

            3 ) Une fois le dictionnaire créé, on le transforme en xml en suivant la grammaire de la TEI pour les apparat.

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
                    # Résultat de ça: on a des tei:app avec 1 seul tei:rdg si la graphie est identique mais l'analyse
                    # grammaticale distincte (signe d'une erreur de lemmatisation en général).
                    app = etree.SubElement(root, tei + 'app')
                    if identite_forme and identite_lemme and identite_pos:
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
                    #
                    type_apparat = self.typologie_variantes(liste_lemme, liste_pos)

                    if self.log:
                        with open("logs/variant_log.txt", "a") as variants_log:
                            variants_log.write(f"Variante: {type_apparat}\n"
                                               f"Formes: {' '.join(liste_lecons)}\n"
                                               f"Lemmes: {' '.join(liste_lemme)}\n"
                                               f"Pos: {' '.join(liste_pos)}\n\n")

                    if not apparat:
                        app.set('type', 'not_apparat')
                    else:
                        app.set('type', type_apparat)
                # Une fois le dictionnaire de sortie produit, le transformer en XML.
                temoins_complets = " ".join([f'#{fichier.split(".xml")[0].split("/")[-1]}'
                                             for fichier in glob.glob("temoins_tokenises_regularises/*.xml")])
                for key, value in dict_sortie.items():
                    if not apparat:
                        lecon = str(key)
                        xml_id = value[0]
                        rdg = etree.SubElement(app, tei + 'rdg')
                        # on indique que tous les témoins proposent la leçon
                        rdg.set('id', utils.generateur_id())
                        rdg.set('wit', temoins_complets)
                        rdg.set('n', xml_id)
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
                    n = 0
                    for mot in liste_w:
                        nombre_temoins = temoin.count('#')
                        nombre_mots = len(liste_w)
                        position_mot = liste_w.index(mot)
                        xml_id_courant = '_'.join(liste_id[n::nombre_mots])  # on va distribuer les xml:id:
                        # abcd > ac, db pour 2 témoins qui lisent la même chose (ab et cd sont les identifiants des deux
                        # tokens identiques, donc il faut distribuer pour identifier le premier token, puis le second)
                        word = etree.SubElement(rdg, tei + 'w')
                        word.set('{http://www.w3.org/XML/1998/namespace}id', xml_id_courant)
                        word.text = mot
                        n += 1

            # L'apparat est produit. Écriture du fichier xml
            sortie = '%s/apparat_collatex.xml' % self.chemin_fichiers
            with open(sortie, 'w+') as sortie_xml:
                output = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True).decode('utf8')
                sortie_xml.write(str(output))

    def typologie_variantes(self, liste_lemmes, liste_pos):
        """
        Cette fonction permet de produire la typologie des variantes.
        Elle s'appuie notamment sur l'article de Camps, Spadini et Ing 2019:
        "Collating Medieval Vernacular Texts: Aligning Witnesses, Classifying Variants"
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

        # TODO: ignorer les erreurs d'analyse probables: même lemmes, pos différent mais parce que
        #  changement de catégorie (= P <=> D, etc). Comme ça on affine le corpus sur tsv et pas sur
        #  xml.

        # TODO: Créer une catégorie de variante discursive ? et/e - o/e ?

        ### TODO: ajouter une règle si la différence est seulement une différence d'espaces. Idem pour les accents
        ## TODO: idem, si adjectifs du même lemme, on peut ignorer le reste.

        comparaison_lemme = all(elem == liste_lemmes[0] for elem in liste_lemmes[1:])
        comparaison_pos = all(elem == liste_pos[0] for elem in liste_pos[1:])

        ## Les éléments du filtre seront ignorés, soit parce que c'est trop coûteux
        # de corriger dans le XML ou car il n'y a pas d'intérêt à la variante.
        filtre_lemmes = [('como', 'cómo'), ('et', 'e'), ('más', 'mas'), ('que', 'ca'), ('él', 'el'),
                         ('esta', 'está', 'ésta'), ('grande', 'gran')]
        # si tous les lemmes et tous les pos sont identiques: il s'agit d'une variante graphique.
        # Ici il faut se rappeler qu'il y a une différence entre les formes
        type_de_variante = None
        if not comparaison_lemme:  # si il y a une différence de lemmes seulement: 'vraie variante'
            if all(pos.startswith('NP') for pos in liste_pos):
                type_de_variante = 'entite_nommee'
            else:
                # on cherche à vérifier que tous les lemmes (all) soºnt dans une des deux listes (any)
                if any(all(lemme in couple for lemme in liste_lemmes) for couple in filtre_lemmes):
                    type_de_variante = 'filtre'
                else:
                    type_de_variante = 'lexicale'
        elif comparaison_lemme and not comparaison_pos:  # si seul le pos change
            # On peut avoir un lemme identique et un pos qui change ('como' p.ex)
            if any(all(lemme in couple for lemme in liste_lemmes) for couple in filtre_lemmes):
                type_de_variante = 'filtre'
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
                    type_de_variante = "morphosyntactique"
            else:
                type_de_variante = 'morphosyntactique'
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
        comporte des variantes "vraies" ou morphosyntactiques. On va créer des tei:rdgGroup qui rassembleront les rdg.
        À intégrer à la classe Collateur puisque c'est une partie de la collation.
        Cette fonction réécrit le fichier d'entrée.
        """
        # TODO: fusionner cette fonction avec la fonction de création d'apparat ?
        # TODO: il reste un problème dans le cas suivant (en amont): chaîne identique, (lemme?|)pos différent.
        parser = etree.XMLParser(load_dtd=True,
                                 resolve_entities=True)
        f = etree.parse(fichier, parser=parser)  # https://lxml.de/tutorial.html#namespaces
        root = f.getroot()
        liste_apps = root.xpath(f"//tei:app[not(@type='graphique')]", namespaces=self.tei_ns)
        for apparat in liste_apps:
            lecon = apparat.xpath(f"descendant::tei:rdg", namespaces=self.tei_ns)
            # S'il n'y a que deux lemmes, pas besoin de raffiner l'apparat.
            if len(lecon) <= 2:
                pass

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

                # On va pouvoir maintenant créer des rdgGroups autour des tei:rdg que l'on a identifiés
                # comme similaires.

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
                            print(f"Raffinage des apparats sur {fichier}.\n"
                                  f"Index error. Rdg's id: {identifiant}. \n"
                                  f"Error: {error}. Exiting.")
                            exit(0)
                        rdg_grp.append(orig_rdg)

        with open(fichier, 'w+') as sortie_xml:
            output = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True).decode('utf8')
            sortie_xml.write(str(output))
