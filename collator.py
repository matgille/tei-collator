# -*- coding: utf-8 -*-
import fnmatch
import os
import sys
import time
import re
import json
import random
import string
from halo import Halo
import xml.etree.ElementTree as ET
from lxml import etree
import shutil
import subprocess
import glob
import operator
import dicttoxml
import collatex

import python.collation.collation as collation
import python.tokenisation.tokenisation as tokenisation
import python.lemmatisation.lemmatisation as lemmatisation
import python.sorties.sorties as sorties
import python.injection.injection as injection
import python.settings

# TODO: nettoyer le tout / s'occuper de la conservation des xml:id pour ne pas avoir à les régénérer
# Remerciements: merci à Élisa Nury pour ses éclaircissements sur le fonctionnement de CollateX et ses
# conseils.
# Todo: faire du mot à mot et s'occuper de rassembler en plus gros apparats après. Si on fait du mot à mot, l'éclatement
# du TEI n'a plus aucun sens car il n'y a plus de risque de destructurer...

def main():
    t0 = time.time()

    saxon = "saxon9he.jar"
    current_dir = os.getcwd()

    # S'il y a un argument qui est une cdc, un fichier à traiter, passer directement à l'alignement
    # le nom du script est le premier argument


    settings = python.settings.parameters_importing("sans_lemmatisation.json")

    if settings.tokeniser:
        tokenisation.tokenisation(saxon, settings.corpus_path)
    if settings.xmlId and not settings.tokeniser:  # si le corpus est tokénisé mais sans xml:id
        for temoin in os.listdir('temoins_tokenises_regularises/'):
            if temoin.endswith('.xml'):
                temoin = f"temoins_tokenises_regularises/{temoin}"
                tokenisation.ajoutXmlId(temoin, temoin)
    if settings.lemmatiser:
        print("Lemmatisation du corpus...")
        for temoin in os.listdir('temoins_tokenises_regularises/'):
            if temoin.endswith('.xml'):
                temoin = f"temoins_tokenises_regularises/{temoin}"
                try:
                    lemmatisation.lemmatisation(temoin, saxon, settings.lang)
                except Exception as exception:
                    print(f"Error: {temoin} \n {exception}")
    argument = int(sys.argv[1])
    arg_plus_1 = argument + 1
    portee = range(argument, arg_plus_1)


    collation.preparation_corpus(saxon, settings.temoin_leader, settings.scinder_par, settings.element_base)

    # Création des fichiers d'apparat
    # Les xsl permettent de créer autant de fichiers xml à processer que de divisions (ici, tei:p):
    # cela permet d'éviter d'avoir un apparat qui court sur deux divisions distinctes
    for i in portee:
        start_time = time.time()
        chemin = "divs/div" + str(i)
        print(f"Traitement de la division {str(i)}")
        for fichier_xml in os.listdir(chemin):
            pattern = re.compile("juxtaposition_[1-9]{1,2}.*xml")
            if pattern.match(fichier_xml):
                fichier_sans_extension = os.path.basename(fichier_xml).split(".")[0]
                numero = fichier_sans_extension.split("_")[1]
                fichier_json = f"{fichier_sans_extension}.json"
                fichier_json_complet = f"{chemin}/{fichier_json}"
                output_fichier_json = f"-o:{chemin}/{fichier_json}"
                input_fichier_xml = f"{chemin}/{fichier_xml}"
                # Étape avant la collation: transformation en json selon la structure voulue par CollateX
                collation.transformation_json(saxon, output_fichier_json, input_fichier_xml)

                # Alignement avec CollateX. Il en ressort du JSON, encore
                collation.alignement(fichier_json_complet, numero, chemin, settings.alignement)

        chemin_chapitre = f"divs/div{i}"
        chemin_final = f"{chemin_chapitre}/final.json"
        with open(chemin_final, "w") as final:  # ici on prend tous les json d'alignement et on les fonde en un gros
            # fichier json
            final_dict = {'table': [], 'witnesses': []}
            n = 0
            for fichier in os.listdir(chemin_chapitre):
                pattern = re.compile("alignement_collatex[1-9]{1,2}.*")
                if pattern.match(fichier):  # pour chaque fichier créé qui correspond à chaque paragraphe
                    n += 1
            for l in range(1, n + 1):
                fichier = f"{chemin_chapitre}/alignement_collatex{l}.json"
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
            chemin_alignement = f"{chemin_chapitre}/alignement_collatex.xml"
            with open(chemin_alignement, "w+") as sortie_xml:
                with open(chemin_final, 'r') as fichier_json_a_xmliser:
                    obj = json.loads(fichier_json_a_xmliser.read())
                    vers_xml = dicttoxml.dicttoxml(obj)
                    vers_xml = vers_xml.decode("utf-8")
                sortie_xml.write(vers_xml)


            chemin_regroupement = "xsl/post_alignement/regroupement.xsl"
            # Regroupement des lieux variants (témoin A puis témoin B puis témoin C
            # > lieu variant 1: A, B, C ; lieu variant 2: A, B, C)
            cmd = f"java -jar {saxon} -o:{chemin_chapitre}/aligne_regroupe.xml {chemin_chapitre}/alignement_collatex.xml " \
                  f"{chemin_regroupement}"
            subprocess.run(cmd.split())

            # C'est à ce niveau que l'étape de correction devrait avoir lieu. Y réfléchir.
            # Création de l'apparat: transformation de aligne_regroupe.xml en JSON
            chemin_xsl_apparat = "xsl/post_alignement/creation_apparat.xsl"
            cmd = f"java -jar {saxon} -o:{chemin_chapitre}/apparat_final.json {chemin_chapitre}/aligne_regroupe.xml " \
                  f"{chemin_xsl_apparat}"
            subprocess.run(cmd.split())
            # Création de l'apparat: suppression de la redondance, identification des lieux variants,
            # regroupement des lemmes


        collation.apparat_final(f'{chemin}/apparat_final.json', chemin)
        print("Création des apparats ✓")

        # Réinjection des apparats.
        injection.injection(saxon, chemin, i)

        fichiers_apparat = f'{chemin}/apparat_*_*final.xml'
        liste = glob.glob(fichiers_apparat)
        for fichier_xml in liste:
            print(f' fichier_xml => {fichier_xml}')
            injection.injections_element(fichier_xml, int(sys.argv[1]), 'tei:note[@type=\'general\']', "after")
            injection.injections_element(fichier_xml, int(sys.argv[1]), 'tei:note[@subtype=\'variante\']', "after")
            injection.injections_element(fichier_xml, int(sys.argv[1]), 'tei:milestone[@unit][ancestor::tei:div[contains(@xml:id, \'Sev_Z\')]]', "before")

        # Création du tableau d'alignement pour visualisation
        if settings.tableauxAlignement:
            collation.tableau_alignement(saxon, chemin)

        if settings.latex:
            for fichier in os.listdir(chemin):
                if fnmatch.fnmatch(fichier, 'apparat_*_*final.xml'):
                    fichier = f"{chemin}/{fichier}"
                    sorties.transformation_latex(saxon, fichier, chemin)

        # nettoyage()

    t1 = time.time()
    temps_total = t1 - t0
    print(f"Fait en {round(temps_total)} secondes. \n")


if __name__ == "__main__":
    main()