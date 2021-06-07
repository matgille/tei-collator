
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

