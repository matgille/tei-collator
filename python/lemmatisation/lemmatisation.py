import subprocess
import sys
import re
import glob

import torch
from lxml import etree
import os
import tqdm
import pie
import multiprocessing as mp
from itertools import product


class CorpusXML:
    def __init__(self, liste_temoins: list, langue: str, moteur_transformation: str, core_number: int):
        self.chemin_vers_temoin = [f"temoins_tokenises_regularises/{temoin}" for temoin in liste_temoins]
        self.langue = langue
        self.moteur_transformation = moteur_transformation
        if self.langue == "lat_o":
            self.core_number = 1  # le multiprocessing n'a pas d'intérêt avec pie, il vaut mieux chercher
            # à utiliser la carte graphique s'il y en a une.
        else:
            self.core_number = core_number

    def lemmatisation_parallele(self, division="*"):
        with mp.Pool(processes=self.core_number) as pool:
            # https://www.kite.com/python/answers/how-to-map-a-function-with-multiple-arguments-to-a-multiprocessing-pool-in-python
            data = [(temoin, division) for temoin in self.chemin_vers_temoin]
            pool.starmap(self.lemmatisation, data)

    def lemmatisation(self, temoin, division):
        """
            Lemmatisation du fichier XML et réinjection dans le document xml originel.
            :param temoin: le temoin à lemmatiser
            """
        fichier = os.path.basename(temoin)
        print(f"Lemmatisation de {temoin}\n")
        fichier_sans_extension = os.path.splitext(fichier)[0]
        fichier_xsl = "xsl/lemmatisation/transformation_pre_lemmatisation.xsl"
        chemin_vers_fichier = "temoins_tokenises_regularises/" + str(fichier)
        fichier_entree_txt = 'temoins_tokenises_regularises/txt/' + fichier_sans_extension + '.txt'
        param_division = f"division={division}"
        param_sortie = f"sortie={fichier_entree_txt}"
        subprocess.run(["java", "-jar",
                        self.moteur_transformation,
                        chemin_vers_fichier,
                        fichier_xsl,
                        param_sortie,
                        param_division])
        if self.langue == "spa_o":
            fichier_lemmatise = 'temoins_tokenises_regularises/txt/' + fichier_sans_extension + '_lemmatise' + '.txt'
            cmd_sh = ["sh",
                      "python/lemmatisation/analyze.sh",
                      fichier_entree_txt,
                      fichier_lemmatise]  # je dois passer par un script externe car un subprocess tourne dans le vide,
            # pas trouvé pourquoi
            subprocess.run(cmd_sh)  # analyze est dans /usr/bin
            maliste = txt_to_liste(fichier_lemmatise)
            parser = etree.XMLParser(load_dtd=True,
                                     resolve_entities=True)  # inutile car les entités ont déjà été résolues
            # auparavant normalement, mais au cas où.
            temoin_tokenise = "temoins_tokenises_regularises/" + fichier
            f = etree.parse(temoin_tokenise, parser=parser)
            root = f.getroot()
            tei = {'tei': 'http://www.tei-c.org/ns/1.0'}
            if division != "*":
                groupe_words = f"//tei:w[ancestor::tei:div[@n='{str(division)}']]"
            else:
                groupe_words = f"//tei:w"
            tokens = root.xpath(groupe_words, namespaces=tei)
            fichier_lemmatise = temoin_tokenise
            n = 1
            for mot in tokens:
                if division != "*":
                    nombre_mots_precedents = int(
                                            mot.xpath(
                                            f"count(preceding::tei:w[ancestor::tei:div[@n='{str(division)}']])", namespaces=tei
                                            )
                                            )
                    nombre_ponctuation_precedente = int(mot.xpath(f"count(preceding::tei:pc[ancestor::tei:div[@n='{str(division)}']])", namespaces=tei))
                else:
                    nombre_mots_precedents = int(mot.xpath("count(preceding::tei:w)", namespaces=tei))
                    nombre_ponctuation_precedente = int(mot.xpath("count(preceding::tei:pc)", namespaces=tei))
                position_absolue_element = nombre_mots_precedents + nombre_ponctuation_precedente
                try:
                    liste_correcte = maliste[position_absolue_element]  # Ça marche bien si la lemmatisation se fait
                except Exception as ecxp:
                    xml_id = mot.xpath("@xml:id", namespaces=tei)[0]
                    print(f"Error in file {fichier}, token {xml_id}: \n {ecxp}. \n Last token of the file must be a "
                          f"punctuation mark. Otherwise, you should search for nested tei:w. Be careful of not adding tei:w in the header !")
                    exit(1)
                # sans retokenisation. Pour l'instant, ça bloque avec les chiffre (ochenta mill est fusionné). Voir
                # avec les devs de Freeling.
                n += 1
                lemme_position = liste_correcte[1]
                pos_position = liste_correcte[2]

                if mot.xpath("@lemma") and mot.xpath("@pos"):  # si l'analyse est déjà présente (cas des lemmes
                    # mal analysés par Freeling et donc corrigés à la main en amont), ne rien faire
                    pass
                elif mot.xpath("@lemma") and not mot.xpath("@pos"):
                    mot.set("pos", pos_position)
                elif mot.xpath("@pos") and not mot.xpath("@lemma"):
                    mot.set("lemma", lemme_position)
                else:
                    mot.set("lemma", lemme_position)
                    mot.set("pos", pos_position)

        elif self.langue == "lat_o":
            modele_latin = "model.tar"
            device = torch.device("cuda") if torch.cuda.is_available() else "cpu"
            cmd = f"pie tag --device {device} {fichier_entree_txt} <{modele_latin},lemma,pos,Person,Numb,Tense,Case,Mood>"
            print(cmd)
            subprocess.run(cmd.split())
            fichier_seul = os.path.splitext(fichier_entree_txt)[0]
            fichier_lemmatise = str(fichier_seul) + "-pie.txt"
            maliste = txt_to_liste(fichier_lemmatise)
            # Nettoyage de la liste
            maliste.pop(0)  # on supprime les titres de colonnes

            parser = etree.XMLParser(load_dtd=True,
                                     resolve_entities=True)  # inutile car les entités ont déjà été résolues
            # auparavant normalement, mais au cas où.
            temoin_tokenise = f"temoins_tokenises_regularises/{fichier}"
            f = etree.parse(temoin_tokenise, parser=parser)
            root = f.getroot()
            tei = {'tei': 'http://www.tei-c.org/ns/1.0'}
            groupe_words = "//tei:w"
            tokens = root.xpath(groupe_words, namespaces=tei)
            nombre_mots = int(root.xpath("count(//tei:w)", namespaces=tei))
            nombre_pc = int(root.xpath("count(//tei:pc)", namespaces=tei))
            nombre_tokens = nombre_mots + nombre_pc
            fichier_lemmatise = temoin_tokenise
            for mot in tqdm.tqdm(tokens):
                nombre_mots_precedents = int(mot.xpath("count(preceding::tei:w) + 1", namespaces=tei))
                nombre_ponctuation_precedente = int(
                    mot.xpath("count(preceding::tei:pc) + 1", namespaces=tei))
                position_absolue_element = nombre_mots_precedents + nombre_ponctuation_precedente  # attention à
                # enlever 1 quand on cherche dans la liste
                liste_correcte = maliste[position_absolue_element - 2]
                cas = liste_correcte[1]
                mode = liste_correcte[2]
                number = liste_correcte[3]
                person = liste_correcte[4]
                temps = liste_correcte[5]
                lemme = liste_correcte[6]
                pos = liste_correcte[7]
                # on nettoie la morphologie pour supprimer les entrées vides
                morph = f"CAS={cas}|MODE={mode}|NOMB.={number}|PERS.={person}|TEMPS={temps}"
                morph = re.sub("((?!\|).)*?_(?=\|)", "", morph)  # on supprime les traits non renseignés du milieu
                morph = re.sub("^\|*", "", morph)  # on supprime les pipes qui commencent la valeur
                morph = re.sub("(\|)+", "|", morph)  # on supprime les pipes suivis
                morph = re.sub("\|((?!\|).)*?_$", "", morph)  # on supprime les traits non renseignés de fin
                morph = re.sub("(?!\|).*_(?!\|)", "", morph)  # on supprime les traits non renseignés uniques
                #
                mot.set("lemma", lemme)
                mot.set("pos", pos)
                if morph:
                    mot.set("morph", morph)

        # Je n'arrive plus à installer les modèles de cltk donc on vire ça pour l'instant.
        # elif langue == "lat":  # 1) on transforme le fichier txt tokenise en txt_to_liste()
        #     nom_fichier_sans_rien = fichier.split(".")[0]
        #     ma_liste_tokenisee = txt_to_liste_latinclassique(
        #         "temoins_tokenises_regularises/txt/%s.txt" % nom_fichier_sans_rien)
        #     lemmatizer = BackoffLatinLemmatizer()
        #     ma_liste_lemmatisee = lemmatizer.lemmatize(ma_liste_tokenisee)
        #     parser = etree.XMLParser(load_dtd=True,
        #                              resolve_entities=True)  # inutile car les entités ont déjà été résolues
        #     # auparavant normalement, mais au cas où.
        #     temoin_tokenise = "temoins_tokenises_regularises/" + fichier
        #     f = etree.parse(temoin_tokenise, parser=parser)
        #     root = f.getroot()
        #     tei = {'tei': 'http://www.tei-c.org/ns/1.0'}
        #     groupe_words = "//tei:w"
        #     tokens = root.xpath(groupe_words, namespaces=tei)
        #     nombre_mots = int(root.xpath("count(//tei:w)", namespaces=tei))
        #     nombre_pc = int(root.xpath("count(//tei:pc)", namespaces=tei))
        #     nombre_tokens = nombre_mots + nombre_pc
        #     fichier_lemmatise = temoin_tokenise
        #     for mot in tokens:
        #         nombre_mots_precedents = int(mot.xpath("count(preceding::tei:w) + 1", namespaces=tei))
        #         nombre_ponctuation_precedente = int(
        #             mot.xpath("count(preceding::tei:pc) + 1", namespaces=tei))
        #         position_absolue_element = nombre_mots_precedents + nombre_ponctuation_precedente  # attention à
        #         # enlever 1 quand on cherche dans la liste
        #         liste_correcte = ma_liste_lemmatisee[position_absolue_element - 2]
        #         lemme = liste_correcte[1]
        #         mot.set("lemma", lemme)

        sortie_xml = open(fichier_lemmatise, "w+")
        a_ecrire = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True).decode(
            'utf8')
        sortie_xml.write(str(a_ecrire))
        sortie_xml.close()
        print("%s ✓" % fichier)


def txt_to_liste(filename):
    """
    Transforme le fichier txt produit par Freeling ou pie en liste de listes pour processage ultérieur.
    :param filename: le nom du fichier txt à transformer
    :return: une liste de listes: pour chaque forme, les différentes analyses
    """
    maliste = []
    fichier = open(filename, 'r')
    for line in fichier.readlines():
        if not re.match(r'^\s*$',
                        line):  # https://stackoverflow.com/a/3711884 élimination des lignes vides (séparateur de phrase)
            resultat = re.split(r'\s+', line)
            maliste.append(resultat)
    return maliste


def txt_to_liste_latinclassique(filename):
    """
    Transforme le fichier txt produit par Freeling ou pie en liste de listes pour processage ultérieur.
    :param filename: le nom du fichier txt à transformer
    :return: une liste de listes: pour chaque forme, les différentes analyses
    """
    maliste = []
    fichier = open(filename, 'r')
    for line in fichier.readlines():
        if not re.match(r'^\s*$',
                        line):  # https://stackoverflow.com/a/3711884 élimination des lignes vides (séparateur de phrase)
            resultat = re.split(r'\s+', line)
            maliste.append(resultat[0])
    return maliste


if __name__ == "__main__":
    print("Merci de lancer le script depuis la racine du dépôt.")
    temoins = glob.glob(sys.argv[1])
    langue = sys.argv[2]
    try:
        division = sys.argv[3]
    except IndexError:
        division = "*"
    corpus_a_lemmatiser = CorpusXML(
        liste_temoins=temoins,
        langue=langue,
        moteur_transformation="saxon9he.jar",
        core_number=mp.cpu_count()
    )
    corpus_a_lemmatiser.lemmatisation_parallele(division)
