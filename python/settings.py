import json
from json_minify import json_minify


class parameters_importing:
    def __init__(self, file):
        """
        On initialise l'instance avec les paramètres qui sont dans le fichier json indiqué.
        :param file:
        """
        with open(file, "r") as f:
            self.settings = json.loads(json_minify(f.read()))
        self.tokeniser =  not self.settings['corpus']['tokenized']
        self.xmlId = not self.settings['corpus']['xmlIdentifiers']
        if not self.settings['corpus']['lemmatized'] and self.settings['lemmatize'] is True:
            self.lemmatiser = True
        else:
            self.lemmatiser = False
        self.fusion_documents = self.settings['sortie']['fusion_divs']
        self.reinjection = self.settings['reinjection']
        self.temoin_leader = self.settings['fichier_leader'].split(".")[0]
        self.element_base = self.settings['scission']['element_base']
        self.scinder_par = self.settings['scission']['scinder_par']
        self.corpus_path = self.settings['localisation_fichiers']
        self.files_path = self.settings['chemin_vers_TEI']
        self.alignement = self.settings['alignement']
        self.path = self.settings['structure']
        self.lang = self.settings['lang']
        self.teiCorpus = self.settings['tei:teiCorpus']
        self.tableauxAlignement = self.settings['sortie']['tableaux_alignement']
        self.latex = self.settings['sortie']['LaTeX']
        self.parallel_process_number = self.settings['parallel_process_number']

    def __str__(self):
        """
        Imprimer les paramètres.
        :return:
        """
        return json.dumps(self.settings, indent=4, sort_keys=True)