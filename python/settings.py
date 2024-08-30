import json
from json_minify import json_minify
import multiprocessing as mp


class Parametres:
    def __init__(self, file):
        """
        On initialise l'instance avec les paramètres qui sont dans le fichier json indiqué.
        :param file:
        """
        with open(file, "r") as f:
            self.settings = json.loads(json_minify(f.read()))
        self.tokeniser = not self.settings['corpus']['tokenized']
        self.xmlId = not self.settings['corpus']['xmlIdentifiers']
        if not self.settings['corpus']['lemmatized'] and self.settings['lemmatize'] is True:
            self.lemmatiser = True
        else:
            self.lemmatiser = False
        self.fusion_documents = self.settings['sortie']['fusion_divs']
        self.prevalidation = self.settings['prévalidation']
        # self.annotation_obligatoire = self.settings['mandatory_annotation']
        self.reinjection = self.settings['reinjection']
        self.temoin_leader = self.settings['fichier_leader'].replace(".xml", "")
        self.element_base = self.settings['scission']['element_base']
        self.type_division = self.settings['scission']['scinder_par']
        self.corpus_path = self.settings['localisation_fichiers']
        self.structuration_auto = self.settings['structurer_documents']
        self.files_path = self.settings['chemin_vers_TEI']
        self.output_dir = self.settings['output_dir']
        self.alignement = self.settings['alignement']
        self.temoin_base = self.settings['temoin_base']
        self.lacuna_sensibility = self.settings['sensibilite_lacunes']
        self.path = self.settings['structure']
        self.lang = self.settings['lang']
        self.teiCorpus = self.settings['tei:teiCorpus']
        self.tableauxAlignement = self.settings['sortie']['tableaux_alignement']
        self.exclude_descendant_of: list = self.settings['exclude_descendant_of']

        self.compute_similarity = self.settings['compute_similarity']
        self.create_synonym_dataset = self.settings['create_synonym_dataset']
        self.align_on = self.settings['align_on']

        if isinstance(self.settings['parallel_process_number'], int):
            self.parallel_process_number = self.settings['parallel_process_number']
        elif self.settings['parallel_process_number'] is None:
            self.parallel_process_number = 1
        else:
            self.parallel_process_number = mp.cpu_count()

    def __str__(self):
        """
        Imprimer les paramètres.
        :return:
        """
        return json.dumps(self.settings, indent=4, sort_keys=True)
