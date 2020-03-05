# -*- coding: utf-8 -*-
import fnmatch
import os
import sys
import time

from python.collation.collation import *
from python.tokenisation.tokenisation import *
from python.lemmatisation.lemmatisation import *
import python.settings

# TODO: nettoyer le tout / s'occuper de la conservation des xml:id pour ne pas avoir à les régénérer
# Remerciements: merci à Élisa Nury pour ses éclaircissements sur le fonctionnement de CollateX et ses
# conseils.


t0 = time.time()

saxon = "saxon9he.jar"
current_dir = os.getcwd()


# S'il y a un argument qui est une cdc, un fichier à traiter, passer directement à l'alignement
# le nom du script est le premier argument


def isInt(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


if len(sys.argv) == 1:  # si il n'y a pas d'argument
    if settings.tokeniser:
        tokenisation(saxon)
    if settings.xmlId and not settings.tokeniser:  # si le corpus est tokénisé mais sans xml:id
        for temoin in os.listdir('temoins_tokenises_regularises/'):
            if temoin.endswith('.xml'):
                temoin = "temoins_tokenises_regularises/%s" % temoin
                ajoutXmlId(temoin, temoin)
    if settings.lemmatiser:
        for temoin in os.listdir('temoins_tokenises_regularises/'):
            if temoin.endswith('.xml'):
                temoin = "temoins_tokenises_regularises/%s" % temoin
                lemmatisation(temoin, saxon, settings.lang)
    portee = range(3, 23)
elif isInt(sys.argv[1]):  # Si on passe un entier, c'est un chapitre à processer
    argument = int(sys.argv[1])
    arg_plus_1 = argument + 1
    portee = range(argument, arg_plus_1)
elif type(sys.argv[1]) is str:
    argument = sys.argv[1]
    if argument == '--tokenisation' or argument == '-t':
        tokenisation(saxon)
        exit(0)
    elif argument == '--preparation' or argument == '-p':
        preparation_corpus(saxon)
        exit(0)
    elif argument == '--nettoyage' or argument == '-n':
        nettoyage()
        exit(0)
    elif argument == '--injection' or argument == '-i':
        chemin_sortie = 'divs/div' + str(sys.argv[2]) + "/xml/"
        injection(saxon, '', int(sys.argv[2]), True, chemin_sortie)
        exit(0)
    elif argument == '--lemmatisation' or argument == '-l':
        chemin = 'xsl/pre_alignement/'
        for temoin in os.listdir('temoins_tokenises_regularises/'):
            if temoin.endswith('.xml'):
                temoin = "temoins_tokenises_regularises/%s" % temoin
                lemmatisation(temoin, saxon, python.settings.lang)
        t1 = time.time()
        temps_total = t1 - t0
        print(temps_total)
        exit(0)
# Sinon, enclencher tout le processus de transformation, alignement, apparation.


chemin_xsl = ""

# tokenisation(saxon) désactivé pour l'instant (risque de perte de l'annotation grammaticale)

# On lemmatise ici.

preparation_corpus(saxon, python.settings.temoin_leader, python.settings.scinder_par, python.settings.element_base)

# Création des fichiers d'apparat
# with Halo(text='Alignement automatique par chapitre', spinner='dots'):

for i in portee:
    start_time = time.time()
    chemin = "divs/div" + str(i)
    print("Traitement de la division " + str(i))
    for fichier_xml in os.listdir(chemin):
        pattern = re.compile("juxtaposition_[1-9].*xml")
        if pattern.match(fichier_xml):
            fichier_sans_extension = os.path.basename(fichier_xml).split(".")[0]
            numero = fichier_sans_extension.split("_")[1]
            fichier_json = "%s.json" % fichier_sans_extension
            fichier_json_complet = "%s/%s" % (chemin, fichier_json)
            output_fichier_json = "-o:%s/%s" % (chemin, fichier_json)
            input_fichier_xml = "%s/%s" % (chemin, fichier_xml)
            # Étape avant la collation: transformation en json selon la structure voulue par CollateX
            transformation_json(saxon, output_fichier_json, input_fichier_xml)

            # Alignement avec CollateX. Il en ressort du JSON, encore
            alignement(fichier_json_complet, saxon, chemin_xsl, numero, chemin)

    chemin_chapitre = "divs/div%s" % i
    chemin_final = "%s/final.json" % chemin_chapitre
    with open(chemin_final, "w") as final:  # ici on prend tous les json d'alignement et on les fonde en un gros
        # fichier json
        final_dict = {'table': [], 'witnesses': []}
        n = 0
        for k in os.listdir(chemin_chapitre):
            pattern = re.compile("alignement_collatex[1-9].*")
            if pattern.match(k):  # pour chaque fichier créé qui correspond à chaque paragraphe
                n += 1
        for l in range(1, n + 1):
            fichier = "%s/alignement_collatex%s.json" % (chemin_chapitre, l)
            with open(fichier, 'r') as file:
                dict0 = json.loads(file.read())  # on charge le fichier comme un dictionnaire
                n = len(dict0['table'])  # n est le nombre de témoins
                for j in range(n):  # pour chaque témoin
                    witness = dict0['witnesses'][j]
                    if len(final_dict['witnesses']) != n:  # tant que la liste des témoins n'est pas complète
                        final_dict['witnesses'].append(witness)
                    if len(final_dict['table']) != n:  #
                        liste_vide = []
                        final_dict['table'].append(liste_vide)
                    for element in dict0['table'][j]:
                        final_dict['table'][j].append(element)
        json.dump(final_dict, final)

    # On compare les lieux variants et on en déduit les <app>
    with Halo(text='Création des apparats', spinner='dots'):
        # Étape suivante: transformer le JSON en xml. Pour cela on peut utiliser dict2xml.
        chemin_alignement = "%s/alignement_collatex.xml" % chemin_chapitre
        with open(chemin_alignement, "w+") as sortie_xml:
            with open(chemin_final, 'r') as fichier_json_a_xmliser:
                obj = json.loads(fichier_json_a_xmliser.read())
                vers_xml = dicttoxml.dicttoxml(obj)
                vers_xml = vers_xml.decode("utf-8")
            sortie_xml.write(vers_xml)

        chemin_xsl = ""
        chemin_regroupement = "xsl/post_alignement/regroupement.xsl"
        # Regroupement des lieux variants (témoin A puis témoin B puis témoin C
        # > lieu variant 1: A, B, C ; lieu variant 2: A, B, C)
        cmd = "java -jar %s -o:%s/aligne_regroupe.xml %s/alignement_collatex.xml %s" % (
        saxon, chemin_chapitre, chemin_chapitre, chemin_regroupement)
        subprocess.run(cmd.split())

        # C'est à ce niveau que l'étape de correction devrait avoir lieu. Y réfléchir.
        # Création de l'apparat: transformation de aligne_regroupe.xml en JSON
        chemin_xsl_apparat = "xsl/post_alignement/creation_apparat.xsl"
        cmd = "java -jar %s -o:%s/apparat_final.json %s/aligne_regroupe.xml %s" % (
        saxon, chemin_chapitre, chemin_chapitre, chemin_xsl_apparat)
        subprocess.run(cmd.split())
        # Création de l'apparat: suppression de la redondance, identification des lieux variants,
        # regroupement des lemmes

    apparat_final('%s/apparat_final.json' % chemin, chemin)
    print("Création des apparats ✓")

    # Réinjection des apparats.
    injection(saxon, chemin, i)

    # Création du tableau d'alignement pour visualisation
    if python.settings.tableauxAlignement:
        tableau_alignement(saxon, chemin_xsl)

    if python.settings.latex:
        for fichier in os.listdir(chemin):
            if fnmatch.fnmatch(fichier, 'apparat_*_*out.xml'):
                transformation_latex(saxon, fichier, chemin_xsl)

    # nettoyage()
    # On revient à la racine du projet pour finir la boucle

t1 = time.time()
temps_total = t1 - t0
print("Fait en %s secondes. \n" % (round(temps_total)))
