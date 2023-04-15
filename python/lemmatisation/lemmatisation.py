import collections
import subprocess
import sys
import re
import glob
import traceback

import torch
from lxml import etree
import os
import multiprocessing as mp

import python.utils.utils as utils


class CorpusALemmatiser:
    def __init__(self, liste_temoins: list, langue: str, moteur_transformation: str, nombre_coeurs: int):
        self.chemin_vers_temoin = [f"temoins_tokenises_regularises/{temoin}" for temoin in liste_temoins]
        self.langue = langue
        self.moteur_transformation = moteur_transformation
        if self.langue == "lat_o":
            self.nombre_coeurs = 1  # le multiprocessing n'a pas d'intérêt avec pie, il vaut mieux chercher
            # à utiliser la carte graphique s'il y en a une.
        else:
            self.nombre_coeurs = nombre_coeurs
        self.nsmap = {'tei': 'http://www.tei-c.org/ns/1.0'}

    def lemmatisation_parallele(self, division="*"):
        with mp.Pool(processes=self.nombre_coeurs) as pool:
            # https://www.kite.com/python/answers/how-to-map-a-function-with-
            # multiple-arguments-to-a-multiprocessing-pool-in-python
            data = [(temoin, division) for temoin in self.chemin_vers_temoin]
            pool.starmap(self.lemmatisation, data)

    def normalize_spelling(self):
        '''
        On normalise avec des expressions régulières avant d'envoyer à la lemmatisation, pour adapter au mieux
        aux normes attendues par Freeling.
        IN: *tokenized.txt
        OUT: *.tokenized.normalized.txt
        '''

        # Attention à l'ordre.
        table_normalisation = collections.OrderedDict({
            re.compile(r'^rr(.*)'): r'r\g<1>',
            re.compile(r'(.*)mm(.*)'): r'\g<1>m\g<2>',
            # Provoque ne erreur dans `sujudgado`
            # re.compile(r'uj([aeiouyáéíóúý])'): r'vi\g<1>',
            re.compile(r'lv([aeiouyáéíóúý])'): r'lu\g<1>',
            re.compile(r'([aeiouyáéíóúý])v([aeiouyáéíóúý])'): r'\g<1>u\g<2>',
        })

        normalisation = {'á': 'a',
                          'é': 'e',
                          'í': 'i',
                          'ó': 'o',
                          'ú': 'u',
                          'ý': 'y'}

        for text_file in glob.glob("temoins_tokenises_regularises/txt/*tokenized.txt"):
            with open(text_file, "r") as input_text_file:
                list_of_words = {index: line.replace('\n', '') for index, line in
                                 enumerate(input_text_file.readlines())}

            normalized_list = []
            for index, form in list_of_words.items():
                for orig, reg in table_normalisation.items():
                    form = re.sub(orig, reg, form)
                normalized_list.append(form)
            normalized_list.append("")
            text = "\n".join(normalized_list)
            for orig, reg in normalisation.items():
                text = text.replace(orig, reg)

            with open(text_file.replace('.txt', '.normalized.txt'), "w") as output_text_file:
                output_text_file.write(text)

    def lemmatisation(self, temoin, division):
        """
            Lemmatisation du fichier XML et réinjection dans le document xml originel.
            :param temoin: le temoin à lemmatiser
            :param division: la division à traiter
            """
        fichier = os.path.basename(temoin)
        fichier_sans_extension = os.path.splitext(fichier)[0]
        fichier_xsl = "xsl/lemmatisation/transformation_pre_lemmatisation.xsl"
        chemin_vers_fichier = f"temoins_tokenises_regularises/{str(fichier)}"
        fichier_entree_txt = f'temoins_tokenises_regularises/txt/{fichier_sans_extension}_tokenized.txt'
        fichier_normalized = f'temoins_tokenises_regularises/txt/{fichier_sans_extension}_tokenized.normalized.txt'
        param_division = f"division={division}"
        param_sortie = f"sortie={fichier_entree_txt}"
        subprocess.run(["java", "-jar",
                        self.moteur_transformation,
                        chemin_vers_fichier,
                        fichier_xsl,
                        param_sortie,
                        param_division])

        if self.langue == "spa_o":
            self.normalize_spelling()
            fichier_lemmatise = f'temoins_tokenises_regularises/txt/{fichier_sans_extension}.lemmatized.txt'
            cmd_sh = ["sh",
                      "python/lemmatisation/analyze.sh",
                      fichier_normalized,
                      fichier_lemmatise]  # je dois passer par un script externe car un subprocess tourne dans le vide,
            # pas trouvé pourquoi
            subprocess.run(cmd_sh)
            texte_lemmatise = utils.txt_to_liste(fichier_lemmatise)
            temoin_tokenise = f"temoins_tokenises_regularises/{fichier}"
            parser = etree.XMLParser(load_dtd=True,
                                     resolve_entities=True)
            f = etree.parse(temoin_tokenise, parser=parser)
            root = f.getroot()
            if division != "*":
                groupe_words = f"//node()[self::tei:w|self::tei:pc][ancestor::tei:div[@n='{str(division)}']]"
            else:
                groupe_words = f"//node()[self::tei:w|self::tei:pc]"
            tokens = root.xpath(groupe_words, namespaces=self.nsmap)
            fichier_lemmatise = temoin_tokenise
            n = 1
            for index, mot in enumerate(tokens):
                # Ça marche bien si la lemmatisation se fait
                # sans retokenisation. Pour l'instant, ça bloque avec les chiffre (ochenta mill est fusionné). Voir
                # avec les devs de Freeling.
                try:
                    _, lemme_position, pos_position, *autres_analyses = texte_lemmatise[index]
                except Exception as ecxp:
                    print(f"Error in file {fichier}: \n {ecxp}. \n Last token of the file must be a "
                          f"punctuation mark. Otherwise, you should search for nested tei:w. Be careful of not adding "
                          f"any tei:w in the header !")
                    print("You should check for empty tei:w in tokenized files.")
                    print(f"{mot}, {[previous_token.text for previous_token in tokens[index - 10: index]]}")
                    xml_id = mot.xpath("@xml:id", namespaces=self.nsmap)[0]
                    exit(0)

                # On injecte les analyses.
                if mot.xpath("@lemma") and mot.xpath("@pos"):  # si l'analyse est déjà présente (cas des lemmes
                    # mal analysés par Freeling et donc corrigés à la main en amont), ne rien faire
                    pass
                # Sinon on ajoute l'analyse de Freeling.
                elif mot.xpath("@lemma") and not mot.xpath("@pos"):
                    mot.set("pos", pos_position)
                elif mot.xpath("@pos") and not mot.xpath("@lemma"):
                    mot.set("lemma", lemme_position)
                else:
                    mot.set("lemma", lemme_position)
                    mot.set("pos", pos_position)

        elif self.langue == "lat_o":
            modele_latin = "python/lemmatisation/model.tar"
            device = torch.device("cuda") if torch.cuda.is_available() else "cpu"
            cmd = f"pie tag --device {device} {fichier_entree_txt} " \
                  f"<{modele_latin},lemma,pos,Person,Numb,Tense,Case,Mood>"
            print(cmd)
            subprocess.run(cmd.split())
            fichier_seul = os.path.splitext(fichier_entree_txt)[0]
            fichier_lemmatise = str(fichier_seul) + "-pie.txt"
            maliste = utils.txt_to_liste(fichier_lemmatise)
            # Nettoyage de la liste
            maliste.pop(0)  # on supprime les titres de colonnes
            temoin_tokenise = f"temoins_tokenises_regularises/{fichier}"
            parser = etree.XMLParser(load_dtd=True,
                                     resolve_entities=True)
            f = etree.parse(temoin_tokenise, parser=parser)
            root = f.getroot()
            groupe_words = "//node()[self::tei:w|self::tei:pc]"
            tokens = root.xpath(groupe_words, namespaces=self.nsmap)
            fichier_lemmatise = temoin_tokenise
            for index, mot in enumerate(tokens):
                liste_correcte = maliste[index]
                _, cas, mode, nombre, personne, temps, lemme, pos, *autres_arguments = liste_correcte

                # on nettoie la morphologie pour supprimer les entrées vides
                morph = f"CAS={cas}|MODE={mode}|NOMB.={nombre}|PERS.={personne}|TEMPS={temps}"
                morph = re.sub("((?!\|).)*?_(?=\|)", "", morph)  # on supprime les pipes non renseignés du milieu
                morph = re.sub("^\|*", "", morph)  # on supprime les pipes qui commencent la valeur
                morph = re.sub("(\|)+", "|", morph)  # on supprime les pipes suivis
                morph = re.sub("\|((?!\|).)*?_$", "", morph)  # on supprime les pipes non renseignés de fin
                morph = re.sub("(?!\|).*_(?!\|)", "", morph)  # on supprime les pipes non renseignés uniques
                #
                mot.set("lemma", lemme)
                mot.set("pos", pos)
                if morph:
                    mot.set("morph", morph)

        with open(fichier_lemmatise, "w+") as sortie_xml:
            a_ecrire = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True).decode(
                'utf8')
            sortie_xml.write(str(a_ecrire))
        print("%s ✓" % fichier)


if __name__ == "__main__":
    print("Merci de lancer le script depuis la racine du dépôt.")
    temoins = glob.glob(sys.argv[1])
    langue = sys.argv[2]
    try:
        division = sys.argv[3]
    except IndexError:
        division = "*"
    corpus_a_lemmatiser = CorpusALemmatiser(
        liste_temoins=temoins,
        langue=langue,
        moteur_transformation="saxon9he.jar",
        nombre_coeurs=mp.cpu_count()
    )
    corpus_a_lemmatiser.lemmatisation_parallele(division)
