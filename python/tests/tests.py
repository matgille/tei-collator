import glob
import unittest
from functools import reduce
import json

from lxml import etree
from lxml import isoschematron
import os
import datetime
import python.utils as utils

tei_namespace = 'http://www.tei-c.org/ns/1.0'
NSMAP = {'tei': tei_namespace}  # pour la recherche d'éléments avec la méthode xpath

svrl_namespaces = 'http://purl.oclc.org/dsdl/svrl'
svrlns = {'svrl': svrl_namespaces}


def test_word_alignment(div):
    """
    Cette fonction permet d'aller chercher les éléments qui empêcheraient un bon alignement: ce sont les éléments
    qui ne sont pas envoyés dans CollateX (tei:fw, tei:del, etc); si d'autre tei:w anormalement c'est qu'il y a un
    problème quelque part.
    """
    xpath_expression = "//tei:w[not(ancestor::tei:app|ancestor::tei:head)]/@xml:id"
    temoins = glob.glob(f'divs/div{div}/*_injected_punct.xml')
    comparison_list = []
    for i in temoins:
        with open(i, "r") as input_xml_file:
            f = etree.parse(input_xml_file)
        comparison_list.append([result for result in f.xpath(xpath_expression, namespaces=NSMAP)])
    # https://stackoverflow.com/a/25324329
    comparison_sets = [set(list_id) for list_id in comparison_list]
    difference = reduce(set.union, comparison_sets) - reduce(set.intersection, comparison_sets)
    # print(difference)

    good_tuple_list = []
    for element in difference:
        test = False
        while not test:
            for witness in temoins:
                with open(witness, "r") as input_xml_file:
                    f = etree.parse(input_xml_file)
                presence = f.xpath(f"boolean(//tei:w[@xml:id = '{element}'])", namespaces=NSMAP)
                if presence:
                    good_tuple_list.append((witness, element))
                    test = True

    print(f"Éléments tei:w qu'on ne retrouve que dans certains témoins: {good_tuple_list}")


def order_test(fichier_a_tester, temoin_tokenise, sigle, division, div_type):
    """
    Cette fonction teste si des tokens ont été perdus ou si leur ordre a été inversé lors de la collation.
    """
    print(f"Testing {fichier_a_tester} against {temoin_tokenise}")
    xml_temoins_tokenise = etree.parse(temoin_tokenise)
    try:
        root_a_tester = etree.parse(fichier_a_tester)
    except OSError:
        print("Témoin absent sur la division concernée.")
        return
    correct_ids = xml_temoins_tokenise.xpath(
        f"//tei:div[@type='{div_type}'][@n='{division}']/descendant::tei:w/@xml:id", namespaces=NSMAP)
    all_rdg_wit_a_tester = root_a_tester.xpath(
        f"//tei:div[@n='{division}']/descendant::tei:app[descendant::tei:rdg[contains(@wit, '{sigle}')]]/descendant::tei:rdg[tei:w][contains(@wit, '{sigle}')]/@wit",
        namespaces=NSMAP)
    all_rdg_id_a_tester = root_a_tester.xpath(
        f"//tei:div[@n='{division}']/descendant::tei:app[descendant::tei:rdg[contains(@wit, '{sigle}')]]/descendant::tei:rdg[@n][tei:w][contains(@wit, '{sigle}')]/@n | //tei:div[@n='{division}']/descendant::tei:app[descendant::tei:rdg[contains(@wit, '{sigle}')]]/descendant::tei:rdg[not(@n)][tei:w][contains(@wit, '{sigle}')]/@id",
        namespaces=NSMAP)

    if len(all_rdg_id_a_tester) != len(all_rdg_wit_a_tester):
        print("The length is not the same.")
        print(len(all_rdg_id_a_tester))
        print(len(all_rdg_wit_a_tester))

    zipped = zip(all_rdg_id_a_tester, all_rdg_wit_a_tester)
    list_of_ids = []
    for id, wits in zipped:
        splitted_wits = [wit.replace('#', '') if " " in wits else wits.replace('#', '') for wit in wits.split()]
        if "_" in id:
            splitted_ids = id.split("_")
        else:
            splitted_ids = [id]
        assert "" not in splitted_ids
        assert "" not in splitted_wits
        wit_position = [index for index, witness in enumerate(splitted_wits) if sigle in witness][0]
        try:
            corresponding_id = splitted_ids[wit_position]
        except IndexError:
            print("Error")
            exit(0)
        list_of_ids.append(corresponding_id)
    # Normalement avec ça on a deux listes, qui devraient être égales

    # Trouver comment comparer l'ordre des listes.
    if len(list_of_ids) != len(correct_ids):
        print("Something went wrong with the injections; some tokens have been lost.")
        exit(0)
    elif list_of_ids != correct_ids:
        # Ici on compare les listes
        print("Differences:")
        print([element for element in correct_ids if element not in list_of_ids])
        print("The order of some tokens has been modified.")
        identify_order_modification(list_of_ids, correct_ids)
        exit(0)

    identify_order_modification(list_of_ids, correct_ids)

    print("No tokens lost; order check passed.")

    # trouver un moyen de tester l'égalité des listes


def identify_order_modification(list_1, list_2):
    zipped = zip(list_1, list_2)
    compared_list = [(computed, target) for (computed, target) in zipped if computed != target]
    if compared_list != []:
        print("Order issue. Problematic tokens: ")
        print(compared_list)
    return


def test_lemmatization(localisation, div_type, temoin_leader):
    """
    This function checks whether the division has been lemmatized
    """

    ((div1_type, div1_n), (div2_type, div2_n), (div3_type, div3_n)) = localisation
    target_xpath = f"//tei:div[@type='{div1_type}'][@n={div1_n}]/descendant::tei:div[@type='{div2_type}'][@n={div2_n}]/descendant::tei:div[@type='{div3_type}'][@n={div3_n}]"

    with open(f"temoins_tokenises_regularises/{temoin_leader}.xml", "r") as input_xml_file:
        f = etree.parse(input_xml_file)

    target_div = f.xpath(target_xpath, namespaces=NSMAP)[0]
    first_token = target_div.xpath("descendant::tei:w[not(@ana='#annotation_manuelle')][1]", namespaces=NSMAP)[0]
    try:
        first_token.xpath("@lemma")[0]
        first_token.xpath("@pos")[0]
    except:
        return False
    return True


def witness_test(sigle, div):
    print(f"Checking if all tei:app contain each witness for {sigle}")
    target_value = 0
    for temoin in glob.glob('temoins_tokenises_regularises/*.xml'):
        f = etree.parse(temoin)
        if f.xpath(f"boolean(//tei:div[@type='chapitre'][@n='{div}'])", namespaces=NSMAP):  # universalité
            target_value += 1
    target_file = f'divs/div{div}/apparat_{sigle}_{div}_final.xml'
    if os.path.exists(target_file):
        f = etree.parse(target_file)
        # Certains apparats sont présents dans le corpus source (pour indiquer des lacunes par exemple): il faut les ignorer
        app_list = f.xpath(f"//tei:app[not(@type='manuel')]", namespaces=NSMAP)
        for apparat in app_list:
            try:
                token_id = apparat.xpath("descendant::tei:w[1]/@xml:id", namespaces=NSMAP)[0]
            except IndexError as _:
                print(f"List index out of range for witness {sigle}. "
                      f"A tei:app/tei:w has no xml:id. Segmentation problem?")
                exit(1)
            count_witnesses = "".join(apparat.xpath("descendant::tei:rdg[@wit]/@wit", namespaces=NSMAP)).count("#")
            if count_witnesses == target_value:
                pass
            else:
                print(f"Target: {target_value},\n  {sigle}: Issue with tei:app containing token {token_id}")
    else:
        print(f"{sigle} does not exist for div {div}.")


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


def test_collation_tokens(chemin_fichiers, portee, type_division):
    # On vérifie si les tokens ne sont pas perdus
    tokens_per_wits_collatex = {}
    tokens_per_wits_orig = {}

    aligned = glob.glob(f"{chemin_fichiers}/alignement_collatex*.json")
    aligned.sort(key=lambda x: x.replace("alignement_collatex", "").replace(".json", ""))
    for file in aligned:
        print(file)
        with open(file, "r") as json_file:
            as_json = json.load(json_file)
        for witness in as_json['table']:
            for token in witness:
                try:
                    try:
                        tokens_per_wits_collatex[token[0]['_sigil']].append(token[0]['xml:id'])
                    except KeyError:
                        tokens_per_wits_collatex[token[0]['_sigil']] = [token[0]['xml:id']]
                except TypeError:
                    pass

    # Maintenant on vérifie que les documents XML ont aussi les mêmes tokens

    ((div1_type, div1_n), (div2_type, div2_n), (div3_type, div3_n)) = portee
    for xml_file in glob.glob(f"temoins_tokenises_regularises/*.xml"):
        as_xml = etree.parse(xml_file)
        sigla = as_xml.xpath("@xml:id")[0]
        xpath_expression = f"descendant::tei:div[@type='{div1_type}'][@n='{div1_n}']/tei:div[@type='{div2_type}'][@n='{div2_n}']/tei:div[@type='{div3_type}'][@n='{div3_n}']"
        tokens_per_wits_orig[sigla] = as_xml.xpath(
            f"{xpath_expression}/descendant::tei:w/@xml:id", namespaces=NSMAP)

    with open(f"{chemin_fichiers}/tokens_after_collation.json", "w") as output_val_json:
        json.dump(tokens_per_wits_collatex, output_val_json)

    with open(f"{chemin_fichiers}/tokens_before_collation.json", "w") as output_target_json:
        json.dump(tokens_per_wits_orig, output_target_json)
    print(tokens_per_wits_orig.keys())
    for sigla, source_tokens in tokens_per_wits_orig.items():
        target_tokens = tokens_per_wits_collatex[sigla]
        if target_tokens == source_tokens:
            print(f"Wit {sigla} passed token test. No token lost in collation.")
        else:
            source_tokens_as_set = set(source_tokens)
            target_tokens_as_set = set(target_tokens)
            difference = list(source_tokens_as_set - target_tokens_as_set)
            print(f"Problem with witness {sigla}. One or more token lost during collation: {difference}. Exiting.")
            exit(0)


def validation_xml(corpus, schematron):
    """
    Cette fonction valide le corpus et cherche des erreurs fatales pour éviter
    de lancer la chaîne de traitement inutilement.
    Voir https://lxml.de/validation.html
    corpus: le chemin vers le corpus
    schema_rng: le chemin vers le schéma
    schematron: le chemin vers le schema schematron
    RETURNS: un tuple avec le résultat de la validation et l'erreur.
    """
    print("Pré-validation du corpus")
    parser = etree.XMLParser(load_dtd=False,
                             resolve_entities=False)
    corpus = etree.parse(corpus, parser=parser)
    corpus.xinclude()
    parsed_schematron = etree.parse(schematron)
    # https://stackoverflow.com/questions/10963206/schematron-report-issue-with-python-lxml
    schematron_validator = isoschematron.Schematron(parsed_schematron, store_report=True)
    schematron_validator.validate(corpus)
    report = schematron_validator.validation_report
    fatal_errors = report.xpath("//node()[@role='fatal']")

    if len(fatal_errors) == 0:
        valid = True
        print("Corpus valide. On continue.")
    else:
        fatal_errors = report.xpath("//svrl:failed-assert[@role='fatal']//descendant::svrl:text", namespaces=svrlns)
        valid = False

    return valid, fatal_errors
