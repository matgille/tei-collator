import glob
import re
import subprocess


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