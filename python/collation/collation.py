import fnmatch
import json
import os
import re
import random
import shutil
import subprocess
import xml.etree.ElementTree as ET
import glob
import dicttoxml
from collatex import *
from halo import Halo
from lxml import etree


def preparation_corpus(saxon, temoin_leader, scinder_par, element_base):
    with Halo(text='Scission du corpus, création de dossiers et de fichiers par chapitre', spinner='dots'):
        cmd = "java -jar %s temoins_tokenises_regularises/%s.xml xsl/pre_alignement/preparation_corpus.xsl " \
              "temoin_leader=%s scinder_par=%s element_base=%s" % (
                  saxon, temoin_leader, temoin_leader, scinder_par, element_base)
        subprocess.run(cmd.split())
    print("Scission du corpus, création de dossiers et de fichiers par chapitre ✓ \n")


# Étape avant la collation: transformation en json selon la structure voulue par CollateX.
# Voir https://collatex.net/doc/#json-input
def transformation_json(saxon, output_fichier_json, input_fichier_xml):
    subprocess.run(["java", "-jar", saxon, output_fichier_json, input_fichier_xml,
                    "xsl/pre_alignement/transformation_json.xsl"])


def alignement(fichier_a_collationer, numero, chemin, alignement='global'):
    """
        Alignement CollateX, puis regroupement des leçons communes en lieux variants
    """
    with open(fichier_a_collationer,
              "r") as entree_json0:  # ouvrir le fichier en mode lecture et le mettre dans une variable
        entree_json1 = entree_json0.read()
    # Export au format JSON (permet de conserver les xml:id)
    try:
        json_str = json.loads(entree_json1)  # permet de mieux gérer les sauts de ligne pour le
    except Exception as e:
        print("error in json [%s]: \n %s" % (fichier_a_collationer, e))
    # JSON: https://stackoverflow.com/a/29827074
    if alignement == 'global':
        resultat_json = collate(json_str, output="json")
    else:
        resultat_json = collate(json_str, output="json", segmentation=False)
    nom_fichier_sortie = "%s/alignement_collatex%s.json" % (chemin, numero)
    with open(nom_fichier_sortie, "w") as sortie_json:
        sortie_json.write(resultat_json)


def apparat_final(fichier_entree, chemin):
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
        root = etree.Element(tei + "root", nsmap=NSMAP0)  # https://lxml.de/tutorial.html#namespaces
        #  https://stackoverflow.com/questions/7703018/how-to-write-namespaced-element-attributes-with-lxml
        for dic in liste_dict:
            apparat = True
            dict_sortie = {}
            liste_lecons = []

            # Étape 1: déterminer si il y a variation ou pas
            for key, value in dic.items():
                id_token, lecon_depart, temoin = value[0], value[1], value[2]
                liste_lecons.append(lecon_depart)

            if len(liste_lecons) > 0:
                # Comparer chaque lecon à la première
                identite = all(elem == liste_lecons[0] for elem in liste_lecons)
                # Première étape. Si tous les lieux variants sont égaux 
                # entre eux,ne pas créer d'apparat mais imprimer 
                # directement le texte    
                app = etree.SubElement(root, tei + "app")
                if identite:
                    apparat = False
                else:
                    pass

                # La liste créée va permettre de vérifier si une leçon identique
                # a déjà été traitée auparavant. On la réinitialise
                # car on l'a déjà utilisée pour vérifier l'égalité entre leçons
                # dans le lieu variant précédent
                liste_lecons = []
                liste_lemme = []
                liste_pos = []
                for key, value in dic.items():
                    id_token, lecon_depart, temoin, lemme, pos = value[0], value[1], value[2], value[3], value[4]
                    # attention à bien faire la comparaison SSI le lemme/pos existe
                    # ajouter le lemme à la liste
                    liste_lemme.append(lemme)
                    liste_pos.append(pos)

                    # Si le lieu variant n'existe pas dans la liste,
                    # créer un item de dictionnaire
                    if lecon_depart not in liste_lecons:
                        # dict_sortie[lecon_depart] = [id_token, temoin]
                        dict_sortie[lecon_depart] = [id_token, temoin, lemme, pos]

                        # Ajouter le lieu variant dans la liste.
                        liste_lecons.append(lecon_depart)

                    # Si le lieu variant a déjà été rencontré
                    else:
                        temoin1 = dict_sortie.get(lecon_depart)[1]
                        token1 = dict_sortie.get(lecon_depart)[0]
                        lemme1 = dict_sortie.get(lecon_depart)[2]
                        pos1 = dict_sortie.get(lecon_depart)[3]
                        token2 = token1 + "_" + id_token
                        temoin2 = temoin1 + " " + temoin
                        lemme2 = lemme1 + "_" + lemme
                        pos2 = pos1 + " " + pos
                        dict_sortie[lecon_depart] = [token2, temoin2, lemme2, pos2]

                        # Mise à jour la liste
                        liste_lecons.append(lecon_depart)

                comparaison_lemme = all(elem == liste_lemme[0] for elem in liste_lemme)
                comparaison_pos = all(elem == liste_pos[0] for elem in liste_pos)
                # si tous les lemmes et tous les pos sont identiques: il s'agit d'une variante grapique.
                # Ici il faut se rappeler qu'il y a une différence entre les formes
                if not comparaison_lemme:  # si il y a une différence de lemmes seulement: "vraie variante"
                    type_apparat = "variante"
                ### TODO: ajouter une règle sur les noms propres. Si lemmes différent, mais pos = NP, alors variante
                ### d'entité nommée. Ça ne changera probablement rien à la fin mais l'encodage est plus fin comme ça.
                ### TODO: ajouter une règle si la différence est seulement une différence d'espaces. Idem pour les accents
                elif comparaison_lemme and not comparaison_pos:  # si seul le pos change
                    type_apparat = "personne_genre"
                elif comparaison_pos and comparaison_lemme:  # si lemmes et pos sont indentiques
                    if liste_lemme[0] == '' or liste_pos[0] == '':  # si égaux parce que nuls, variante
                        # indéterminée
                        type_apparat = "indetermine"
                    else:  # si on a un lemme et un PoS identiques, la variante est graphique
                        type_apparat = "graphique"
                if not apparat:
                    app.set("type", "not_apparat")
                else:
                    app.set("type", type_apparat)
            # Une fois le dictionnaire de sortie produit, le transformer en XML.
            temoins_complets = " ".join([f'#{fichier.split(".xml")[0].split("/")[-1]}' for fichier in glob.glob("temoins_tokenises_regularises/*.xml")])
            for key, value in dict_sortie.items():
                if not apparat:
                    lecon = str(key)
                    xml_id = value[0]
                    rdg = etree.SubElement(app, tei + "rdg")
                    # on indique que tous les témoins proposent la leçon
                    rdg.set("wit", temoins_complets)
                    rdg.set("{http://www.w3.org/XML/1998/namespace}id", xml_id)
                else:
                    lecon = str(key)
                    xml_id, temoin, lemmes, pos = value[0], value[1], value[2], value[3]
                    rdg = etree.SubElement(app, tei + "rdg")
                    rdg.set("lemma", lemmes)
                    rdg.set("pos", pos)
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
        sortie = "%s/apparat_collatex.xml" % chemin
        with open(sortie, "w+") as sortie_xml:
            output = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True).decode('utf8')
            sortie_xml.write(str(output))


def injection(saxon, chemin, chapitre):
    """
    Fonction qui réinjecte les apparats dans chaque transcription individuelle.
    :param saxon: le moteur saxon
    :param chemin:  le chemin du dossier courant
    :param chapitre: le chapitre courant
    :return: None
    TODO: il faudrait passer à du 100% python, pour être plus clair, c'est un peu
    l'usine à gaz là.
    """
    print("---- INJECTION 1: apparats ----")
    param_chapitre = "chapitre=" + str(chapitre)  # Premier paramètre passé à la xsl: le chapitre à processer
    param_chemin_sortie = "chemin_sortie=%s/" % chemin  # Second paramètre: le chemin vers le fichier de sortie
    fichier_entree = "%s/juxtaposition_orig.xml" % chemin
    # with Halo(text="Injection des apparats dans chaque transcription individuelle", spinner='dots'):
    #  première étape de l'injection. Apparats, noeuds textuels et suppression de la redondance
    chemin_injection = "xsl/post_alignement/injection_apparats.xsl"
    subprocess.run(["java", "-jar", saxon, fichier_entree, chemin_injection, param_chapitre, param_chemin_sortie])

    # seconde étape: noeuds non textuels
    print("\n---- INJECTION 2: suppression de la redondance ----")
    fichiers_apparat = '%s/apparat_*_*.xml' % chemin
    liste = glob.glob(fichiers_apparat)
    chemin_injection2 = "xsl/post_alignement/injection_apparats2.xsl"
    for i in liste:  # on crée une boucle car les fichiers on été divisés par la feuille précédente.
        if re.match(r'.*[0-9].xml',  i):
            print(i)
            sigle = i.split("apparat_")[1].split(".xml")[0].split("_")[0] + "_" \
                    + i.split("apparat_")[1].split(".xml")[0].split("_")[1]
            param_sigle = "sigle=" + sigle
            subprocess.run(["java", "-jar", saxon, i, chemin_injection2, param_chapitre, param_sigle])


    print("\n---- INJECTION 2bis: suppression de la redondance ----")
    chemin_injection2 = "xsl/post_alignement/injection_apparats3.xsl"
    fichiers_apparat = '%s/apparat_*_*outb.xml' % chemin
    liste = glob.glob(fichiers_apparat)
    for i in liste:  # on crée une boucle car les fichiers on été divisés par la feuille précédente.
        sigle = i.split("apparat_")[1].split(".xml")[0].split("_")[0] + "_" \
                + i.split("apparat_")[1].split(".xml")[0].split("_")[1]
        param_sigle = "sigle=" + sigle
        subprocess.run(["java", "-jar", saxon, i, chemin_injection2, param_chapitre, param_sigle])

    #  troisième étape: ponctuation
    print("\n---- INJECTION 3: ponctuation ----")
    chemin_injection_ponctuation = "xsl/post_alignement/injection_ponctuation.xsl"
    fichiers_apparat = '%s/apparat_*_*outc.xml' % chemin
    liste = glob.glob(fichiers_apparat)
    for i in liste:
        sigle = i.split("apparat_")[1].split(".xml")[0].split("_")[0] + "_" \
                + i.split("apparat_")[1].split(".xml")[0].split("_")[1]
        param_sigle = "sigle=" + sigle
        subprocess.run(["java", "-jar", saxon, i, chemin_injection_ponctuation, param_chapitre, param_sigle])
    print("Injection des apparats dans chaque transcription individuelle ✓")

    #  quatrième étape: gestion des lacunes
    print("\n---- INJECTION 4: lacunes ----")
    chemin_injection_ponctuation = "xsl/post_alignement/gestion_lacunes.xsl"
    fichiers_apparat = '%s/apparat_*_*out.xml' % chemin
    liste = glob.glob(fichiers_apparat)
    for i in liste:
        sigle = i.split("apparat_")[1].split(".xml")[0].split("_")[0] + "_" \
                + i.split("apparat_")[1].split(".xml")[0].split("_")[1]
        param_sigle = "sigle=" + sigle
        subprocess.run(["java", "-jar", saxon, i, chemin_injection_ponctuation, param_chapitre, param_sigle])
    print("Création des balises de lacunes ✓")


def fileExists(file):
    if os.path.exists(file):
        print("%s: check" % file)
    else:
        print("%s: n'est pas trouvé" % file)


def tableau_alignement(saxon, chemin):
    xsl_apparat = "xsl/post_alignement/tableau_alignement.xsl"
    with Halo(text='Création du tableau d\'alignement', spinner='dots'):
        cmd = "java -jar %s -o:%s/tableau_alignement.html %s/aligne_regroupe.xml %s" % (
            saxon, chemin, chemin, xsl_apparat)
        subprocess.run(cmd.split())
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
                continue
                # new_path = 'aux/' + file
                # shutil.move(os.path.abspath(file), new_path)

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
