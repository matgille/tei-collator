import fnmatch
import glob
import itertools
from operator import itemgetter
import os
import re
import shutil
import string
import subprocess
import random
from lxml import etree

from halo import Halo
from joblib._multiprocessing_helpers import mp

tei_ns = {'tei': 'http://www.tei-c.org/ns/1.0'}


def nettoyage_liste_positions(liste_de_tuples):
    """
    Cette fonction permet de nettoyer une liste de la forme:
    [(24, 30), (25, 30), (26, 30), (27, 30), (28, 30), (29, 30), (36, 51), (37, 51), (38, 51), (39, 51), (40, 51), (41, 51),
    (42, 51), (43, 51), (44, 51), (45, 51), (46, 51), (47, 51)]
    Pour sortir une liste de la forme:
    [(24, 30), (36, 51)]
    Ces tuples correspondent à la localisation des omissions dans le texte
    """
    result = []

    # La valeur maximale est la borne supérieure de nos omissions/lacunes
    maximal_values = list(set([couple[1] for couple in liste_de_tuples]))
    for max_value in maximal_values:
        # on cherche la liste des index qui correspondent à chaque valeur maximale
        liste = [couple for couple in liste_de_tuples if couple[1] == max_value]
        # on cherche la valeur minimale
        minimal_value = min([couple[0] for couple in liste])
        # on renvoie le tuple avec les bornes.
        result.append((minimal_value, max_value))

    # Et on trie parce que c'est beau
    result.sort(key=lambda tup: tup[0])
    return result


def get_file_list(path):
    """
    Return list of files and check if they exist.
    """

    file_list = glob.glob(path)
    assert len(file_list) > 0
    return file_list


def run_subprocess(liste):
    subprocess.run(liste)


def nettoyage():
    with Halo(text='Nettoyage du dossier', spinner='dots'):
        for i in ['tex', 'xml', 'aux', 'json']:
            if not os.path.exists(i):
                os.makedirs(i)
        for file in os.listdir('.'):
            path = os.path.join('', file)
            if os.path.isdir(path):
                continue
            if fnmatch.fnmatch(file, '*.xml'):
                new_path = 'xml/' + file
                shutil.move(os.path.abspath(file), new_path)
            elif fnmatch.fnmatch(file, '*.json'):
                new_path = 'json/' + file
                shutil.move(os.path.abspath(file), new_path)
            elif fnmatch.fnmatch(file, '*.tex'):
                new_path = 'tex/' + file
                shutil.move(os.path.abspath(file), new_path)
            elif fnmatch.fnmatch(file, '*.html') or fnmatch.fnmatch(file, '*.pdf'):
                continue
            else:
                continue
                # new_path = 'aux/' + file
                # shutil.move(os.path.abspath(file), new_path)

    print('Nettoyage du dossier ✓')


def txt_to_liste(filename):
    """
    Transforme le fichier txt produit par Freeling ou pie en liste de listes pour processage ultérieur.
    :param filename: le nom du fichier txt à transformer
    :return: une liste de listes: pour chaque forme, les différentes analyses
    """
    output_list = []
    fichier = open(filename, 'r')
    for ligne in fichier.readlines():
        if not re.match(r'^\s*$',
                        ligne):  # https://stackoverflow.com/a/3711884 élimination des lignes vides (séparateur de phrase)
            ligne_splittee = re.split(r'\s+', ligne)
            output_list.append(ligne_splittee)
    return output_list


def remove_files(files):
    """
    This function removes all files given path (with wildcard)
    """
    for file in glob.glob(files):
        try:
            os.remove(file)
        except:
            shutil.rmtree(file)


def move_files(files: list, output_dir: str) -> None:
    try:
        os.mkdir(output_dir)
    except:
        pass
    for file in files:
        if os.path.isfile(file):
            shutil.move(file, output_dir)


def clean_xml_file(input_file, output_file):
    """
    This function removes unwanted attributes from the xml file to produce a "final" version
    """

    tree = parse_xml_file(input_file)

    # First, the tei:rdg
    readings = tree.xpath("//tei:rdg", namespaces=tei_ns)

    for reading in readings:
        # https://stackoverflow.com/a/2720418
        for attr in ["lemma", "pos", "n", "id"]:
            try:
                reading.attrib.pop(attr)
            except:
                continue

    # Then, the tei:w
    words = tree.xpath("//tei:w", namespaces=tei_ns)

    for word in words:
        # https://stackoverflow.com/a/2720418
        [word.attrib.pop(attr) for attr in ['{http://www.w3.org/XML/1998/namespace}id']]

    with open(output_file, "w") as output_file:
        output_file.write(etree.tostring(tree, pretty_print=True).decode())

def clean_spaces_from_string(string) -> str:
    regexp_1 = re.compile(r"^\s | \s$")
    regexp_2 = re.compile(r"\s+")
    string = re.sub(regexp_2, " ", string)
    string = re.sub(regexp_1, "", string)
    return string

def remove_debug_files():
    for file in glob.glob(".debug/*"):
        os.remove(file)


def append_to_file(file, string):
    """
    This function appends to some file a given string.
    """

    with open(file, "a") as input_file:
        input_file.write(string)

def clean_underscode_from_string(string) -> str:
    """
    This function removes all redundant, trailing or leading underscore
    """
    regexp_1 = re.compile(r"^_")
    regexp_2 = re.compile(r"_$")
    regexp_3 = re.compile(r"_+")
    string = re.sub(regexp_1, "", string)
    string = re.sub(regexp_2, "", string)
    string = re.sub(regexp_3, "_", string)

    return string

def filter_existing_divs(list_of_files, div_n, div_type) -> list:
    files_with_div = []
    for file in list_of_files:
        tree = etree.parse(file)
        presence = tree.xpath(f"boolean(//tei:div[@type =  '{div_type}'][@n = '{div_n}'])", namespaces=tei_ns)
        if presence:
            files_with_div.append(file)

    return files_with_div

def get_sigla_from_path(path: str) -> str:
    """
    Cette fonction retourne le sigle à partir d'un chemin (qui doit contenir le sigle)
    """
    return [file.split('/')[-1].split('.xml')[0] for file in glob.glob("temoins_tokenises/*.xml")
            if file.split('/')[-1].split('.xml')[0] in path][0]


def save_xml_file(xml_object, path):
    with open(path, "w") as output_file:
        output_file.write(etree.tostring(xml_object, pretty_print=True).decode())


def clean_spaces(file):
    with open(file, "r") as input_file:
        file_to_clean = input_file.read()

    pattern_in_tag = re.compile("\{\s+")
    pattern_spaces = re.compile("\s+")

    file_to_clean = re.sub(pattern_in_tag, "{", file_to_clean)
    file_to_clean = re.sub(pattern_spaces, " ", file_to_clean)

    with open(file, "w") as output_file:
        output_file.write(file_to_clean)


def generateur_lettre_initiale(chars=string.ascii_lowercase):
    # Génère une lettre aléatoire
    return random.choice(chars)[0]


def generateur_id(size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits) -> str:
    random_letter = generateur_lettre_initiale()
    random_string = ''.join(random.choice(chars) for _ in range(size))
    return random_letter + random_string


def sigles():
    """
    Cette fonction retourne une liste de sigles à partir de tous les témoins
    """
    return [fichier.split("/")[1].split(".xml")[0] for fichier in glob.glob('temoins_tokenises/*.xml')]


def chemin_fichiers_finaux(div: str):
    """
    Cette fonction retourne la liste des fichiers XML finaux d'une division donnée
    """
    return [fichier for fichier in glob.glob(f'divs/div{div}/apparat_*_{div}_final.xml')]


def chemin_temoins_tokenises():
    """
    Cette fonction retourne la liste des chemins vers les fichiers tokénisés
    """
    return [fichier for fichier in glob.glob('temoins_tokenises/*.xml')]


def chemin_temoins_tokenises_regularises():
    """
    Cette fonction retourne la liste des chemins vers les fichiers tokénisés
    """
    return [fichier for fichier in glob.glob('temoins_tokenises_regularises/*.xml')]


def fileExists(file):
    if os.path.exists(file):
        return True
    else:
        return False


def pool_function(function, args, coeurs):
    pool = mp.Pool(processes=coeurs)
    pool.map(function, args)


def error_checklist():
    print("Une erreur est survenue. Merci de regarder en amont:\n"
          "- que toutes les divisions à comparer sont correctement identifiées;\n"
          "- ")


def merge_list_of_lists(list_to_merge):
    return list(itertools.chain.from_iterable(list_to_merge))


def accent_removal(string_to_process):
    # https://www.tutorialsteacher.com/python/string-maketrans
    accents = 'áéíóúý'
    no_accents = 'aeiouy'

    # Je ne comprends pas pourquoi maketrans est une méthode de classe str.
    mapping_table = accents.maketrans(accents, no_accents)

    # Mais ça marche donc ne posons pas trop de questions.
    translated_string = string_to_process.translate(mapping_table)

    return translated_string


def group_adjacent_positions(positions: list) -> list:
    """
    Regroupe en une liste de tuples les entiers adjacents à partir d'une liste
     d'entiers
    """
    ranges = []
    # https://stackoverflow.com/a/2154437 on veut regrouper les positions contigües.
    for k, g in itertools.groupby(enumerate(positions), lambda x: x[0] - x[1]):
        group = (map(itemgetter(1), g))
        group = list(map(int, group))
        ranges.append((group[0], group[-1]))

    return ranges


def return_adjacent_positions(positions: list) -> list:
    """
    Regroupe en une liste de tuples les entiers adjacents d'une liste
    """
    ranges = []
    # https://stackoverflow.com/a/2154437 on veut regrouper les positions contigües.
    print(f"Input: {positions}")
    for k, g in itertools.groupby(enumerate(positions), lambda x: x[0] - x[1]):
        group = (map(itemgetter(1), g))
        group = list(map(int, group))
        if len(group) > 1:
            print(f"Output: {group}")
            return group
        else:
            print(f"Output: None")
            return

def remove_accents(string):
    accent_mapping = {'á': 'a',
                      'é': 'e',
                      'í': 'i',
                      'ó': 'o',
                      'ú': 'u',
                      'ý': 'y'}
    for orig, reg in accent_mapping.items():
        string = string.replace(orig, reg)

    return string


def parse_xml_file(file):
    with open(file, "r") as input_xml:
        return etree.parse(input_xml)


def remove_elements(xml_tree, xpath_expression, namespace):
    """
    This function deletes all elements that match a given xpath expression
    """
    xpath_selection = xml_tree.xpath(xpath_expression, namespaces=namespace)
    for element in xpath_selection:
        element.getparent().remove(element)
