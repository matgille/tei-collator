import random
import string
from halo import Halo
import os
import subprocess
from lxml import etree


class Tokenizer:
    def __init__(self, saxon: int):
        self.saxon = saxon

    def generateur_lettre_initiale(self, size=1, chars=string.ascii_lowercase):
        # éviter les nombres en premier caractère de
        # l'@xml:id (interdit)
        return ''.join(random.choice(chars) for _ in range(size))

    def generateur_id(self, size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
        return self.generateur_lettre_initiale() + ''.join(random.choice(chars) for _ in range(size))

    def ajout_xml_id(self, temoin):
        """Création des xml:id pour chaque token.
        TODO: trouver un
        moyen de pouvoir actualiser la transcription sans avoir à
        re-générer des xml:id. Faire des groupes de n tokens pour retrouver les emplacements ?
        pour chaque token, récupérer le bi/trigramme suivant et aller le retrouver dans le fichier de sortie
        Si il est trouvé, copier l'id du token dans la fichier de sortie. Si il n'est pas trouvé, générer un
        xml:id. Je pense que ça peut marcher pour des modifications de faible volume (un mot); je ne sais pas
        ce que ça peut donner avec un ajout d'une phrase omise par inadvertance par exemple. Ou alors on peut utiliser
        collatex aussi. """
        tei = {'tei': 'http://www.tei-c.org/ns/1.0'}
        f = etree.parse(temoin)
        root = f.getroot()
        # on va marquer les balises autofermantes pour être sûr de les injecter correctement après.
        liste_elements_vides = root.xpath("//tei:*[not(child::node())]", namespaces=tei)
        for element in liste_elements_vides:
            element.set("{http://www.w3.org/XML/1998/namespace}id", self.generateur_id())

        liste_w = root.xpath("//tei:w", namespaces=tei)
        for w in liste_w:
            w.set("{http://www.w3.org/XML/1998/namespace}id", self.generateur_id())
        with open(temoin, "w+") as sortie_xml:
            string = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True).decode('utf8')
            sortie_xml.write(str(string))

    def tokenisation(self, path, correction=False):
        with Halo(text='Tokénisation du corpus parallélisé.', spinner='dots'):
            subprocess.run(["java", "-jar", self.saxon, "-xi:on", path,
                            "xsl/pre_alignement/tokenisation.xsl"])
            for transcription_individuelle in os.listdir("temoins_tokenises"):
                fichier_xml = f"temoins_tokenises/{transcription_individuelle}"
                self.ajout_xml_id(fichier_xml)
            param_correction = f"correction={correction}"
            subprocess.run(["java", "-jar", self.saxon, "-xi:on", "temoins_tokenises/Sal_J.xml",
                            "xsl/pre_alignement/regularisation.xsl", param_correction])
        print("Tokénisation et régularisation du corpus pour alignement ✓")
