import fnmatch
import json
import os
import re
import random
import shutil
import string
import subprocess
import glob
import xml.etree.ElementTree as ET

import dicttoxml
from collatex import *
from halo import Halo
from lxml import etree


def generateur_lettre_initiale(size=1, chars=string.ascii_lowercase):  # éviter les nombres en premier caractère de
    # l'@xml:id (interdit)
    return ''.join(random.choice(chars) for _ in range(size))


def generateur_id(size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return generateur_lettre_initiale() + ''.join(random.choice(chars) for _ in range(size))


def ajout_xmlid(fichier_entree, fichier_sortie):
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
    f = etree.parse(fichier_entree)
    root = f.getroot()
    tokens = root.xpath("//tei:w", namespaces=tei)
    for w in tokens:
        w.set("{http://www.w3.org/XML/1998/namespace}id", generateur_id())
    sortie_xml = open(fichier_sortie, "w+")
    string = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True).decode('utf8')
    sortie_xml.write(str(string))
    sortie_xml.close()


def tokenisation(saxon):
    # for fichier in os.listdir(
    #         '/home/mgl/Desktop/These/Edition/hyperregimiento-de-los-principes/Dedans/XML/temoins/castillan/'):
    #     print(fichier)
    #     if fnmatch.fnmatch(fichier, 'Sev_R.xml'):
    #         chemin_fichier = "/home/mgl/Desktop/These/Edition/hyperregimiento-de-los-principes/Dedans/XML/temoins/castillan/" + fichier
    #         parser = etree.XMLParser(load_dtd=True, resolve_entities=False)
    #         f = etree.parse(chemin_fichier, parser=parser)
    #         f.xinclude()  # https://lxml.de/3.3/api.html#xinclude-and-elementinclude
    #         root = f.getroot()
    #         text_root = str(etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True))
    #         text_root = text_root.replace("&", "±")
    #         text_root = text_root.replace(";", "™")
    #         text_root = text_root.replace("\\n", "")
    #         tree = ET.ElementTree(ET.fromstring(text_root))
    #         print(text_root)
    #         chemin_fichier_test = "/home/mgl/Desktop/These/Edition/hyperregimiento-de-los-principes/Dedans/XML/temoins/test/" + fichier
    #         with open(chemin_fichier_test, "w+") as sortie_xml:
    #             sortie_xml.write(text_root)
    # tei = {'tei': 'http://www.tei-c.org/ns/1.0', 'xi': 'http://www.w3.org/2001/XInclude',
    #        'xml': 'http://www.w3.org/XML/1998/namespace'}
    with Halo(text='Tokénisation du corpus parallélisé.', spinner='dots'):
        subprocess.run(["java", "-jar", saxon, "-xi:on", "../../Dedans/XML/corpus/corpus.xml",
                        "../xsl/pre_alignement/tokenisation.xsl"])
        for transcription_individuelle in os.listdir("../temoins_tokenises"):
            fichier_xml = "../temoins_tokenises/" + transcription_individuelle
            ajout_xmlid(fichier_xml, fichier_xml)
        subprocess.run(["java", "-jar", saxon, "-xi:on", "../temoins_tokenises/Sal_J.xml",
                        "../xsl/pre_alignement/regularisation.xsl"])

    print("Tokénisation et régularisation du corpus pour alignement ✓")


# def nouvelle_tokenisation():
#     parser = etree.XMLParser(load_dtd=True,
#                              resolve_entities=True)  # inutile car les entités ont déjà été résolues
#     # auparavant normalement, mais au cas où.
#     fichier_xml = "/home/mgl/Desktop/These/Edition/hyperregimiento-de-los-principes/Dedans/XML/corpus/corpus.xml"
#     f = etree.parse(fichier_xml, parser=parser)
#     f.xinclude()  # https://lxml.de/3.3/api.html#xinclude-and-elementinclude
#     root = f.getroot()
#     tei = {'tei': 'http://www.tei-c.org/ns/1.0', 'xi': 'http://www.w3.org/2001/XInclude',
#            'xml': 'http://www.w3.org/XML/1998/namespace'}
#     fichiers_tei = root.xpath("descendant::tei:TEI[ancestor::tei:teiCorpus[@xml:id='castB']][@type='transcription']",
#                               namespaces=tei)
#     for fichier in fichiers_tei:
#         groupe_paragraphes = "descendant::tei:p"
#         paragraphes = fichier.xpath(groupe_paragraphes, namespaces=tei)
#         for paragraphe in paragraphes:
#             paragraphe.xpath('tokenize(., "\s+")')
#             test = etree.tostring(paragraphe, pretty_print=True)
#             print(test.decode().split(' '))
#         identifiant_fichier = fichier.xpath('@xml:id', namespaces=tei)
#         fichier_sortie = "/home/mgl/Desktop/These/Edition/hyperregimiento-de-los-principes/Collation/temoins_tokenises/" + str(
#             identifiant_fichier[0]) + ".xml"
#         os.makedirs(os.path.dirname(fichier_sortie),
#                     exist_ok=True)  # https://stackoverflow.com/a/12517490 (si le dossier n'existe pas)
#         with open(fichier_sortie, "w+") as sortie_xml:
#             chaine = etree.tostring(fichier, pretty_print=True, encoding='utf-8', xml_declaration=True).decode('utf8')
#             sortie_xml.write(str(chaine))


def preparation_corpus(saxon):
    with Halo(text='Scission du corpus, création de dossiers et de fichiers par chapitre', spinner='dots'):
        subprocess.run(["java", "-jar", saxon, "../temoins_tokenises_regularises/Sal_J.xml",
                        "../xsl/pre_alignement/preparation_corpus.xsl"])
    print("Scission du corpus, création de dossiers et de fichiers par chapitre ✓ \n")


# Étape avant la collation: transformation en json selon la structure voulue par CollateX.
# Voir https://collatex.net/doc/#json-input
def transformation_json(saxon, output_fichier_json, input_fichier_xml):
    with Halo(text='Transformation en json', spinner='dots'):
        subprocess.run(["java", "-jar", saxon, output_fichier_json, input_fichier_xml,
                        "xsl/pre_alignement/transformation_json.xsl"])
    print("Transformation en json pour alignement ✓")


def alignement(fichier_a_collationer, saxon, chemin_xsl):
    """
        Alignement CollateX, puis regroupement des leçons communes en lieux variants
    """

    try:
        assert fichier_a_collationer.endswiths(".json")
    except:
        while not fichier_a_collationer.endswith('.json'):
            fichier_a_collationer = input("Le fichier indiqué n'est pas un fichier JSON. Veuillez indiquer un fichier.")
    entree_json0 = open(fichier_a_collationer, "r")  # ouvrir le fichier en mode lecture et le mettre dans une variable
    entree_json1 = entree_json0.read()
    entree_json0.close()

    # Export au format TEI (plus lisible)
    def collation_tei():
        with Halo(text='Collation au format TEI - CollateX', spinner='dots'):
            resultat_tei = collate(json.loads(entree_json1), output="tei")
            sortie_tei = open("apparat_collatex_tei.xml", "w")
            sortie_tei.write(resultat_tei)
            sortie_tei.close()

    # Export au format JSON (permet de conserver les xml:id)
    def alignement_json():
        with Halo(text='Alignement CollateX', spinner='dots'):
            json_str = json.loads(entree_json1)  # permet de mieux gérer les sauts de ligne pour le
            # JSON: https://stackoverflow.com/a/29827074
            resultat_json = collate(json_str, output="json")
            sortie_json = open("alignement_collatex.json", "w")
            sortie_json.write(resultat_json)
            sortie_json.close()
        print("Alignement CollateX ✓")

    alignement_json()

    # Les résultats de la collation ne sont pas directement visibles: on a la liste A puis la liste B: il faut
    # transformer le tout pour avoir un réel alignement. Voir http://collatex.obdurodon.org/xml-json-conversion.xhtml
    # pour la structure du résultat. Le résultat de cette dernière transformation est une liste qui comprend
    # elle-même une liste avec l'alignement.

    # Création des apparats proprement dite: on compare les lieux variants et on réduit les app.
    with Halo(text='Création des apparats', spinner='dots'):
        # Étape suivante: transformer le JSON en xml. Pour cela on peut utiliser dict2xml. 
        sortie_xml = open("alignement_collatex.xml", "w+")
        fichier_json_a_xmliser = open('alignement_collatex.json').read()
        obj = json.loads(fichier_json_a_xmliser)
        vers_xml = dicttoxml.dicttoxml(obj)
        vers_xml = vers_xml.decode("utf-8")
        sortie_xml.write(vers_xml)
        sortie_xml.close()

        chemin_regroupement = chemin_xsl + "xsl/post_alignement/regroupement.xsl"
        chemin_xsl_apparat = chemin_xsl + "xsl/post_alignement/creation_apparat.xsl"
        # Regroupement des lieux variants (témoin A puis témoin B puis témoin C 
        # > lieu variant 1: A, B, C ; lieu variant 2: A, B, C)
        subprocess.run(
            ["java", "-jar", saxon, "-o:aligne_regroupe.xml", "alignement_collatex.xml", chemin_regroupement])

        # C'est à ce niveau que l'étape de correction devrait avoir lieu. Y réfléchir.    
        # Création de l'apparat: transformation de aligne_regroupe.xml en JSON
        subprocess.run(["java", "-jar", saxon, "-o:apparat_final.json", "aligne_regroupe.xml", chemin_xsl_apparat])
        # Création de l'apparat: suppression de la redondance, identification des lieux variants, 
        # regroupement des lemmes


def apparat_final(fichier_entree):
    """
        Cette fonction permet de passer de la table d'alignement à 
        l'apparat proprement dit, avec création d'apparat s'il y a
        variation, et regroupement des leçons identiques. 
        Elle fonctionne avec une liste de dictionnaires au format JSON,
        chaque dictionnaire représentant un lieu variant. Les trois premiers items de la liste
        pourront être par exemple:
        
         liste_dict = 
            [{
                "0" : ["", "", "Phil_J", "LEMMA", "POS"],
                "1" : ["a0a6f5ec2-a98u9ds98yh", "Ca iiii", "Mad_G", "LEMMA", "POS"],
                "2" : ["a0a9f5dsc2-a9sdnjxcznk", "Ca iiii", "Phil_Z", "LEMMA", "POS"]
                }, {
                "0" : ["a4d2587a-a98u98yh", "do", "Phil_J", "LEMMA", "POS"],
                "1" : ["a0a6f5ec2-a98u9ds98yh", "do", "Mad_G", "LEMMA", "POS"],
                "2" : ["a0a9f5dsc2-a9sdnjxcznk", "donde", "Phil_Z", "LEMMA", "POS"],
                "3" : ["prout-cacau98yh", "onde", "Phil_K", "LEMMA", "POS"],
                "4" : ["a4sde2587a-a9fu98yh", "donde", "Phil_U", "LEMMA", "POS"],
                "5" : ["a4sd88888e2587a-a999999h", "do", "Phil_M", "LEMMA", "POS"]
                }, {
                "0" : ["a4d2587a-a98u98yh", "muesstra", "Phil_J", "LEMMA", "POS"],
                "1" : ["a0a6f5ec2-a98u9ds98yh", "muestra", "Mad_G", "LEMMA", "POS"],
                "2" : ["a0a9f5dsc2-a9sdnjxcznk", "prueua", "Phil_Z", "LEMMA", "POS"]
            }]
        
        Fonctionnement de la fonction: 
        - ) Le texte aligné est une liste de dictionnaires, pour en garder la linéarité: voir plus haut pour la
            structure de cette liste.
        - ) Chaque lieu variant est représenté par un dictionnaire
        1 ) On va en un premier lieu comparer toutes les chaînes de caractères pour déterminer
            s'il y a lieu de créer un apparat. Si elles sont distinctes, on est face à des lieux
            variants, et on enclenche la suite. 
        2 ) Si il y a des lieux variants, on fonctionne de la manière suivante. On a deux dictionnaires, 
            un dictionnaire d'entrée (décrit plus haut), et un dictionnaire de sortie qui contiendra les 
            informations d'apparat. On va créer une liste liste_lecons qui va nous permettre de comparer chaque chaîne
            aux chaînes précédentes. 
            
            *Pour chaque item* du dictionnaire d'entrée, on vérifie que la chaîne, en position 1, n'est pas déjà présente
            dans la liste liste_lecons. 
                - Si elle n'est pas présente, on l'ajoute à la liste, et on crée un item
                dans le dictionnaire de sortie dict_sortie. Cet item est organisé de la façon suivante:
                    "lieu_variant": ["témoin(s)", "id_token(s)", "lemme", "pos"]
                    On le voit, la valeur correspondant à chaque clé est une liste.
                - Si la chaîne existe déjà dans la liste liste_lecons, c'est qu'elle est aussi dans le 
                dictionnaire de sortie: on va donc modifier la valeur de l'item dont la clé est cette chaîne, 
                en ajoutant le témoin correspondant ainsi que les identifiants de token, de lemme et de pos.

        3 ) Une fois le dictionnaire créé, on le transforme en xml en suivant la grammaire de la TEI pour les apparat.

        4) On va effectuer une opération de comparaison des lemmes et des POS pour déterminer le type de variante

        5 ) La dernière étape est la réinitialisation de la liste liste_lecons et du dictionnaire dict_sortie,
            qui est en réalité en début de boucle.
            
            
        Pour l'instant, n'est traité que l'xml:id, mais aussi le POS et le lemma, mais on peut ajouter d'autres fonctions
        
           
    """

    with open(fichier_entree, 'r+') as fichier:
        liste_dict = json.load(fichier)

        tei_namespace = "http://www.tei-c.org/ns/1.0"
        tei = "{%s}" % tei_namespace
        NSMAP0 = {None: tei_namespace}  # the default namespace (no prefix)
        NSMAP1 = {'tei': tei_namespace}  # pour la recherche d'éléments avec la méthode xpath
        root = etree.Element(tei + "root", nsmap=NSMAP0)  # https://lxml.de/tutorial.html#namespaces
        #  https://stackoverflow.com/questions/7703018/how-to-write-namespaced-element-attributes-with-lxml
        for dic in liste_dict:
            dict_sortie = {}
            liste_lecons = []

            # Étape 1: déterminer si il y a variation ou pas
            for key in dic:
                id_token = dic.get(key)[0]
                lecon_depart = dic.get(key)[1]
                temoin = dic.get(key)[2]
                liste_lecons.append(lecon_depart)

            result = False;
            if len(liste_lecons) > 0:
                # Comparer chaque lecon à la première
                result = all(elem == liste_lecons[0] for elem in liste_lecons)

                # Première étape. Si tous les lieux variants sont égaux 
                # entre eux,ne pas créer d'apparat mais imprimer 
                # directement le texte    
                if result:
                    myElement = root.find('app', NSMAP0)
                    if myElement is None:
                        root.text = lecon_depart
                    else:
                        # root.xpath va sortir une liste: il faut aller chercher les items 
                        # individuels de cette liste, même si il n'y en n'a qu'un
                        dernier_app = root.xpath('tei:app[last()]', namespaces=NSMAP1)
                        for i in dernier_app:
                            i.tail = lecon_depart


                else:  # Si les leçons sont différentes: étape 2

                    app = etree.SubElement(root, tei + "app")

                    # La liste créée va permettre de vérifier si une leçon identique
                    # a déjà été traitée auparavant. On la réinitialise
                    # car on l'a déjà utilisée pour vérifier l'égalité entre leçons
                    # dans le lieu variant précédent
                    liste_lecons = []
                    liste_lemme = []
                    liste_pos = []
                    for key in dic:
                        id_token = dic.get(key)[0]
                        lecon_depart = dic.get(key)[1]
                        temoin = dic.get(key)[2]
                        lemme = dic.get(key)[3]  # attention à bien faire la comparaison SSI le lemme/pos existe
                        pos = dic.get(key)[4]  # idem

                        # ajouter le lemme à la liste
                        # si tous les lemmes et tous les pos sont identiques: il s'agit d'une variante grapique.
                        # comparaison_lemme = all(elem == liste_lemme[0] for elem in liste_lemme)
                        liste_lemme.append(lemme)
                        liste_pos.append(pos)

                        # Si le lieu variant n'existe pas dans la liste, 
                        # créer un item de dictionnaire
                        if lecon_depart not in liste_lecons:
                            dict_sortie[lecon_depart] = [id_token, temoin]
                            # dict_sortie[lecon_depart] = [id_token, temoin, lemme, pos]

                            # Ajouter le lieu variant dans la liste.
                            liste_lecons.append(lecon_depart)

                        # Si le lieu variant a déjà été rencontré
                        else:
                            temoin1 = dict_sortie.get(lecon_depart)[1]
                            token1 = dict_sortie.get(lecon_depart)[0]
                            # lemme1 = dict_sortie.get(lecon_depart)[2]
                            # pos1 = dict_sortie.get(lecon_depart)[3]
                            token2 = token1 + "_" + id_token
                            temoin2 = temoin1 + " " + temoin
                            # lemme2 = lemme1 + "_" + lemme
                            # pos2 = pos1 + " " + pos
                            # dict_sortie[lecon_depart] = [token2, temoin2, lemme2, pos2]
                            dict_sortie[lecon_depart] = [token2, temoin2]

                            # Mise à jour la liste
                            liste_lecons.append(lecon_depart)

                    comparaison_lemme = all(elem == liste_lemme[0] for elem in liste_lemme)
                    comparaison_pos = all(elem == liste_pos[0] for elem in liste_pos)
                    # Ici il faut se rappeler qu'il y a une différence entre les formes
                    if not comparaison_lemme:  # si il y a une différence de lemmes seulement: "vraie variante"
                        type_apparat = "variante"
                    elif comparaison_lemme and not comparaison_pos:  # si seul le pos change
                        type_apparat = "personne_genre"
                    elif comparaison_pos and comparaison_lemme:  # si lemmes et pos sont indentiques
                        if liste_lemme[0] == '' or liste_pos[0] == '':  # si égaux parce que nuls, variante
                            # indéterminée
                            type_apparat = "indetermine"
                        else:  # si on a un lemme et un PoS identiques, la variante est graphique
                            type_apparat = "graphique"
                    app.set("type", type_apparat)

            # Une fois le dictionnaire de sortie produit, le transformer en XML.
            for key in dict_sortie:
                lecon = str(key)
                xml_id = dict_sortie.get(key)[0]
                temoin = dict_sortie.get(key)[1]
                # lemmes = dict_sortie.get(key)[2] # si on veut ajouter les informations grammaticales à l'output
                # pos = dict_sortie.get(key)[3] # idem
                rdg = etree.SubElement(app, tei + "rdg")
                rdg.set("wit", temoin)
                rdg.set("{http://www.w3.org/XML/1998/namespace}id", xml_id)  # ensemble des id des tokens, pour la
                # suppression de la redondance plus tard
                # Re-créer les noeuds tei:w
                liste_w = lecon.split()
                liste_id = xml_id.split('_')
                n = 0
                for mot in liste_w:
                    nombre_temoins = temoin.count("#")
                    nombre_mots = len(liste_w)
                    position_mot = liste_w.index(mot)
                    position_finale = (nombre_temoins * (position_mot + 1))
                    position_initiale = position_finale - nombre_temoins
                    xml_id_courant = "_".join(liste_id[n::nombre_mots])  # on va distribuer les xml:id:
                    # abcd > ac, db pour 2 témoins qui lisent la même chose (ab et cd sont les identifiants des deux
                    # tokens identiques, donc il faut distribuer pour identifier le premier token, puis le second)
                    word = etree.SubElement(rdg, tei + "w")
                    word.set("{http://www.w3.org/XML/1998/namespace}id", xml_id_courant)
                    word.text = mot
                    n = n + 1

        # L'apparat est produit. Écriture du fichier xml
        sortie_xml = open("apparat_collatex.xml", "w+")
        output = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True).decode('utf8')
        sortie_xml.write(str(output))
        sortie_xml.close()


def injection(saxon, chemin, chapitre, standalone=False, chemin_sortie=''):
    param_chapitre = "chapitre=" + str(chapitre)  # Premier paramètre passé à la xsl: le chapitre à processer
    param_chemin_sortie = "chemin_sortie=" + str(chemin_sortie)  # Second paramètre: le chemin vers le fichier de sortie
    if not standalone:  # Si la fonction est appelée dans le cadre du processus complet (toujours question de chemin)
        fichier_entree = "juxtaposition_orig.xml"
    else:  # Si la fonction est appelée seule, le chemin est à partir du fichier python
        fichier_entree = "../chapitres/chapitre9/xml/juxtaposition_orig.xml"
    with Halo(text="Injection des apparats dans chaque transcription individuelle", spinner='dots'):
        #  première étape de l'injection. Apparats, noeuds textuels et suppression de la redondance
        chemin_injection = chemin + "xsl/post_alignement/injection_apparats.xsl"
        subprocess.run(["java", "-jar", saxon, fichier_entree, chemin_injection, param_chapitre, param_chemin_sortie])
        fichiers_apparat = 'apparat_*_*.xml'
        liste = glob.glob(fichiers_apparat)

        # seconde étape: noeuds non textuels
        chemin_injection2 = chemin + "xsl/post_alignement/injection_apparats2.xsl"
        for i in liste:  # on crée une boucle car les fichiers on été divisés par la feuille précédente.
            sigle = i.split("apparat_")[1].split(".xml")[0].split("_")[0] + "_" \
                    + i.split("apparat_")[1].split(".xml")[0].split("_")[1]
            param_sigle = "sigle=" + sigle
            subprocess.run(["java", "-jar", saxon, i, chemin_injection2, param_chapitre, param_sigle])
            os.remove(i)

        #  troisième étape: ponctuation
        chemin_injection_ponctuation = chemin + "xsl/post_alignement/injection_ponctuation.xsl"
        fichiers_apparat = 'apparat_*_*outb.xml'
        liste = glob.glob(fichiers_apparat)
        for i in liste:
            sigle = i.split("apparat_")[1].split(".xml")[0].split("_")[0] + "_" \
                    + i.split("apparat_")[1].split(".xml")[0].split("_")[1]
            param_sigle = "sigle=" + sigle
            subprocess.run(["java", "-jar", saxon, i, chemin_injection_ponctuation, param_chapitre, param_sigle])
            os.remove(i)
    print("Injection des apparats dans chaque transcription individuelle ✓")


def tableau_alignement(saxon, chemin):
    chemin_xsl_apparat = chemin + "xsl/post_alignement/tableau_alignement.xsl"
    with Halo(text='Création du tableau d\'alignement', spinner='dots'):
        subprocess.run(["java", "-jar", saxon, "-o:tableau_alignement.html", "aligne_regroupe.xml", chemin_xsl_apparat])
    print("Création du tableau d\'alignement ✓")


def nettoyage():
    # TODO: ranger les fichiers dans des dossiers
    with Halo(text="Nettoyage du dossier", spinner='dots'):
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
                new_path = 'aux/' + file
                shutil.move(os.path.abspath(file), new_path)

    print("Nettoyage du dossier ✓")


def txt_to_liste(filename):
    '''
        Transforme le fichier txt produit par Freeling en liste de listes pour processage ultérieur.
    '''
    maliste = []
    fichier = open(filename, 'r')
    for line in fichier.readlines():
        if not re.match(r'^\s*$',
                        line):  # https://stackoverflow.com/a/3711884 élimination des lignes vides (séparateur de phrase)
            resultat = re.split(r'\s+', line)
            maliste.append(resultat)
    return maliste


def lemmatisation(chemin, saxon):
    for fichier in os.listdir(
            '/home/mgl/Desktop/These/Edition/hyperregimiento-de-los-principes/Collation/temoins_tokenises_regularises/'):
        if fnmatch.fnmatch(fichier, '*.xml'):
            fichier_sans_extension = os.path.splitext(fichier)[0]
            fichier_xsl = chemin + "transformation_freeling.xsl"
            print("Lemmatisation de: " + str(fichier_sans_extension))
            chemin_vers_fichier = "../temoins_tokenises_regularises/" + str(fichier)

            fichier_entree_txt = '/home/mgl/Desktop/These/Edition/hyperregimiento-de-los-principes/Collation' \
                                 '/temoins_tokenises_regularises/txt/' + fichier_sans_extension + '.txt'
            param_sortie = "sortie="+ fichier_entree_txt
            subprocess.run(["java", "-jar", saxon, chemin_vers_fichier, fichier_xsl, param_sortie])

            fichier_sortie = '/home/mgl/Desktop/These/Edition/hyperregimiento-de-los-principes/Collation' \
                             '/temoins_tokenises_regularises/txt/' + fichier_sans_extension + '_lemmatise' + '.txt'
            cmd_sh = ["analyze.sh", fichier_entree_txt,
                      fichier_sortie]  # je dois passer par un script externe car ça tourne dans le vide, pas trouvé pourquoi
            subprocess.run(cmd_sh) # analyze est dans /usr/bin
            maliste = txt_to_liste(fichier_sortie)
            parser = etree.XMLParser(load_dtd=True,
                                     resolve_entities=True)  # inutile car les entités ont déjà été résolues
            # auparavant normalement, mais au cas où.
            fichier_xml = "/home/mgl/Desktop/These/Edition/hyperregimiento-de-los-principes/Collation/temoins_tokenises_regularises/" + fichier
            f = etree.parse(fichier_xml, parser=parser)
            root = f.getroot()
            tei = {'tei': 'http://www.tei-c.org/ns/1.0'}
            groupe_words = "//tei:w"
            tokens = root.xpath(groupe_words, namespaces=tei)
            for mot in tokens:
                nombre_mots_precedents = int(mot.xpath("count(preceding::tei:w) + 1", namespaces=tei))
                nombre_ponctuation_precedente = int(mot.xpath("count(preceding::tei:pc) + 1", namespaces=tei))
                position_absolue_element = nombre_mots_precedents + nombre_ponctuation_precedente  # attention à enlever 1 quand on cherche dans la liste
                liste_correcte = maliste[position_absolue_element - 2] # ne marche pas parfaitement, avec J ça coince. Marche avec U. Voir ce qui se passe.
                lemme_position = liste_correcte[1]
                pos_position = liste_correcte[2]
                mot.set("lemma", lemme_position)
                mot.set("pos", pos_position)
            fichier_sortie = fichier_xml
            sortie_xml = open(fichier_sortie, "w+")
            string = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True).decode('utf8')
            sortie_xml.write(str(string))
            sortie_xml.close()


def transformation_latex(saxon, fichier_xml, chemin):
    fichier_tex = fichier_xml.split('.')[0] + ".tex"
    chemin_xsl_apparat = chemin + "xsl/post_alignement/conversion_latex.xsl"
    fichier_tex_sortie = "-o:" + fichier_tex
    print("Création des fichiers pdf ✓")
    subprocess.run(["java", "-jar", saxon, fichier_tex_sortie, fichier_xml, chemin_xsl_apparat])
    subprocess.run(["xelatex", fichier_tex])
    subprocess.run(["xelatex", fichier_tex])


def concatenation_pdf():
    with Halo(text='Création d\'un fichier unique d\'apparat ✓', spinner='dots'):
        subprocess.run(["pdftk", "chapitres/chapitre*/*.pdf", "output", "III_3_apparat.pdf"])
    print("Création d'un fichier unique d'apparat ✓")
