import collections
import glob
import random
import string
from halo import Halo
import os
import subprocess
from lxml import etree
import re
import sys

import python.utils.utils as utils


class Tokenizer:
    def __init__(self, saxon: int, nodes_to_reinject: dict = {}, temoin_leader: str = "Sal_J",
                 regularisation: bool = True):
        self.saxon = saxon
        self.temoin_leader = temoin_leader
        self.nodes_to_reinject = nodes_to_reinject
        self.tei_ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
        self.regularisation = regularisation

    def ajout_xml_id(self, temoin: str):
        """Ajout de xml:id à chaque token."""
        f = etree.parse(temoin)
        root = f.getroot()
        # on va marquer les balises autofermantes pour être sûr de les injecter correctement après. On ignore les
        # éléments qui ont déjà un identifiant.
        liste_elements_vides = root.xpath("//tei:*[not(child::node())][not(@xml:id)]", namespaces=self.tei_ns)
        for element in liste_elements_vides:
            element.set("{http://www.w3.org/XML/1998/namespace}id", utils.generateur_id())

        # On inclut les tei:pc pour faciliter le debuggage
        token_list = root.xpath("//node()[self::tei:w or self::tei:pc]", namespaces=self.tei_ns)
        for token in token_list:
            token.set("{http://www.w3.org/XML/1998/namespace}id", utils.generateur_id())

        # On va ajouter des xml:id aux éléments à réinjecter s'ils n'en n'ont pas:
        for node_to_reinject in self.nodes_to_reinject.keys():
            for node in root.xpath(f"descendant::{node_to_reinject}", namespaces=self.tei_ns):
                if not node.xpath("boolean(@xml:id)"):
                    node.set("{http://www.w3.org/XML/1998/namespace}id", utils.generateur_id())

        with open(temoin, "w+") as sortie_xml:
            tree_as_string = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True).decode(
                'utf8')
            sortie_xml.write(str(tree_as_string))

    def tokenisation(self, path: str, correction_mode: bool = False):
        """
        Tokénise le corpus
        :path: le chemin vers les fichiers d'entré
        :correction_mode: le mode correction
        :regularisation: produire un fichier régularisé ? Défaut: oui
        """
        with Halo(text='Tokénisation du corpus parallélisé.', spinner='dots'):
            subprocess.run(["java", "-jar", self.saxon, "-xi:on", path,
                            "xsl/pre_alignement/tokenisation.xsl"])
            for transcription_individuelle in os.listdir("temoins_tokenises"):
                fichier_xml = f"temoins_tokenises/{transcription_individuelle}"
                self.ajout_xml_id(fichier_xml)
            if self.regularisation:
                param_correction = f"correction={correction_mode}"
                print(["java", "-jar", self.saxon, "-xi:on", f"temoins_tokenises/{self.temoin_leader}.xml",
                                "xsl/pre_alignement/regularisation.xsl", param_correction])
                subprocess.run(["java", "-jar", self.saxon, "-xi:on", f"temoins_tokenises/{self.temoin_leader}.xml",
                                "xsl/pre_alignement/regularisation.xsl", param_correction])
        print("Tokénisation et régularisation du corpus pour alignement ✓")


if __name__ == '__main__':
    saxon = "saxon9he.jar"
    tokeniser = Tokenizer(saxon=saxon, regularisation=False)
    tokeniser.tokenisation(path=sys.argv[1])
