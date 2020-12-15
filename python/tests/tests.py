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
        with open(orig_file, 'r') as orig:
            f = etree.parse(orig)
            final_orig_list = []
            tokens_list = f.xpath(f"//tei:w[ancestor::tei:div[@n='{div}']]", namespaces=NSMAP)
            for token in tokens_list:
                final_orig_list.append(token.xpath("@xml:id")[0])

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

        # https://www.kite.com/python/answers/how-to-get-the-difference-between-two-list-in-python
        set_difference = set(final_orig_list) - set(final_target_list)
        list_difference = list(set_difference)

        with open("tests/tokentest.log", "a") as testlog:
            testlog.write(f'On {datetime.datetime.now()}\n')
            if len(list_difference) != 0:
                testlog.write(f'Found {len(list_difference)} differences in div {div} for witness {sigle}:\n {list_difference} ')
            else:
                testlog.write(f'\tTest passed on div {div} for witness {sigle}')
            testlog.write(f'\n ------------------ \n\n')


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
