import fnmatch
import glob
import os
import re
import shutil
import string
import subprocess
import random

from halo import Halo
from joblib._multiprocessing_helpers import mp


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


def run_subprocess(liste):
    subprocess.run(liste)


def nettoyage():
    # TODO: ranger les fichiers dans des dossiers
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
    for file in glob.glob(files):
        os.remove(file)

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

def generateur_id(size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
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
        print('%s: check' % file)
    else:
        print('%s: n\'est pas trouvé' % file)


def pool_function(function, args, coeurs):
    pool = mp.Pool(processes=coeurs)
    pool.map(function, args)