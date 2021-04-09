import unittest
from lxml import etree
import os
import datetime

tei_namespace = 'http://www.tei-c.org/ns/1.0'
NSMAP = {'tei': tei_namespace}  # pour la recherche d'éléments avec la méthode xpath

def tokentest(sigle, div):
    '''
    Cette fonction permet de faire une comparaison simple entre le dernier fichier xml produit et le fichier
    original, et d'indiquer quels sont les tei:w qui disparaissent entre les deux
    :param sigle: le sigle du témoin à analyse
    :param div: la division du témoin à analyser
    :return: à voir
    '''
    target_file = f'divs/div{div}/apparat_{sigle}_{div}_final.xml'
    orig_file = f'temoins_tokenises/{sigle}.xml'
    if os.path.exists(target_file):

        # On va créer la liste de tous les tei:w d'une division donnée dans le fichier tokénisé originel
        with open(orig_file, 'r') as orig:
            f = etree.parse(orig)
            final_orig_list = []
            # attention, on casse l'universalité du code ici.
            tokens_list = f.xpath(f"//tei:w[ancestor::tei:div[@type='chapitre'][@n='{div}']]", namespaces=NSMAP)
            for token in tokens_list:
                final_orig_list.append(token.xpath("@xml:id")[0])

        # Ainsi que la liste de tous les tei:w de la même division dans le fichier final produit par collator
        with open(target_file, 'r') as target:
            f = etree.parse(target)
            final_target_list = []
            tokens_list = f.xpath("//tei:w", namespaces=NSMAP)
            for token in tokens_list:
                # Cas des apparats
                if token.xpath(f"ancestor::tei:rdg[contains(@wit, '{sigle}')]", namespaces=NSMAP):
                    # Si on a un seul témoin
                    if "_" not in token.xpath("@xml:id")[0]:
                        final_target_list.append(token.xpath("@xml:id")[0])
                    else:
                        listWit = token.xpath("ancestor::tei:rdg/@wit", namespaces=NSMAP)[0].split()
                        goodIndex = [listWit.index(item) for item in listWit if sigle in item][0]
                        final_target_list.append(token.xpath("@xml:id")[0].split("_")[goodIndex])

                # Si le rdg ne contient pas le témoin traité, on passe
                elif token.xpath(f"parent::tei:rdg[not(contains(@wit, '{sigle}'))]", namespaces=NSMAP):
                    pass

                # Cas tokens hors apparat, avec plusieurs wit donc.
                else:
                    final_target_list.append(token.xpath("@xml:id")[0])

        # Et on va comparer les deux listes, et sortir les identifiants qui ne sont pas dans la seconde.
        # https://www.kite.com/python/answers/how-to-get-the-difference-between-two-list-in-python
        set_difference = set(final_orig_list) - set(final_target_list)
        list_difference = list(set_difference)

        with open("test_results/tokentest.log", "a") as testlog:
            testlog.write(f'On {datetime.datetime.now()}\n')
            if len(list_difference) != 0:
                if len(list_difference) > 20:
                    testlog.write(f'Found {len(list_difference)} differences in div {div} for witness {sigle}:'
                                  f'\n [{[item for item in list_difference[:20]]}, etc...] ')
                else:
                    testlog.write(f'Found {len(list_difference)} differences in div {div} for witness {sigle}:'
                                  f'\n {list_difference} ')
            else:
                testlog.write(f'\tTest passed for div {div}, witness {sigle}')
            testlog.write(f'\n ------------------ \n\n')


def notes_test():
    '''
    Cette fonction a vocation à tester la qualité de l'injection des notes dans chacun des témoins.
    Le nombre de notes du document cible doit être égal à la somme du nombre de notes du documen tokénisé originel.
    :return:
    '''
    pass

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
