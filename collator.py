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
import argparse

import python.collation.collation as collation
import python.tokenisation.tokenisation as tokenisation
import python.lemmatisation.lemmatisation as lemmatisation
import python.sorties.sorties as sorties
import python.injection.injection as injection
import python.settings
import python.tests.tests as tests
# IMPORTANT: pour la POO, considérer le corpus comme un objet ? En faire une classe qui permette de tout traiter
# à partir de là ? Suppose de demander un tei:teiCorpus


# TODO: nettoyer le tout / s'occuper de la conservation des xml:id pour ne pas avoir à les régénérer
# Remerciements: merci à Élisa Nury pour ses éclaircissements sur le fonctionnement de CollateX et ses
# conseils.
# Todo: faire du mot à mot et s'occuper de rassembler en plus gros apparats après. Si on fait du mot à mot, l'éclatement
# du TEI n'a plus aucun sens car il n'y a plus de risque de destructurer...




def main():
    t0 = time.time()
    saxon = "saxon9he.jar"
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--parameters", default="lemmatisation.json", help="Path to the parameter file.")
    parser.add_argument("-d", "--division", help="Division to be treated.")
    args = parser.parse_args()
    fichier_de_parametres = args.parameters
    division = args.division


    # On importe les paramètres en créant un objet parametres
    parametres = python.settings.parameters_importing(fichier_de_parametres)
    print(f'\n\n\n ---- \n {parametres.__str__()}\n ---- \n')



    if parametres.tokeniser:
        reponse = input("Vous êtes en train de réécrire les fichiers et de relancer la lemmatisation. Continuer ? [o/n]\n")
        if reponse == "o":
            pass
        else:
            exit(0)
        tokenisation.tokenisation(saxon, parametres.corpus_path)
    if parametres.xmlId and not parametres.tokeniser:  # si le corpus est tokénisé mais sans xml:id
        for temoin in glob.glob('temoins_tokenises_regularises/*.xml'):
            temoin = f"temoins_tokenises_regularises/{temoin}"
            tokenisation.ajoutXmlId(temoin, temoin)
    if parametres.lemmatiser:
        print("Lemmatisation du corpus...")
        for temoin in glob.glob('temoins_tokenises_regularises/*.xml'):
            temoin = f"temoins_tokenises_regularises/{temoin}"
            try:
                lemmatisation.lemmatisation(temoin, saxon, parametres.lang)
            except Exception as exception:
                print(f"Error: {temoin} \n {exception}")

    if "-" in division:
        portee = range(int(division.split("-")[0]), int(division.split("-")[1]) + 1)
    else:
        argument = int(division)
        arg_plus_1 = argument + 1
        portee = range(argument, arg_plus_1)


    collation.preparation_corpus(saxon, parametres.temoin_leader, parametres.scinder_par, parametres.element_base)

    # Création des fichiers d'apparat
    # Les xsl permettent de créer autant de fichiers xml à processer que de divisions (ici, tei:p):
    # cela permet d'éviter d'avoir un apparat qui court sur deux divisions distinctes
    for i in portee:
        start_time = time.time()
        chemin = "divs/div" + str(i)
        print(f"Traitement de la division {str(i)}")
        for fichier_xml in os.listdir(chemin):
            # Ici on travaille sur des petits fichiers qui correspondent aux divisions indiquées en paramètres
            # pour éviter d'avoir des apparats qui se chevauchent
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
                collation.alignement(fichier_json_complet, numero, chemin, parametres.alignement)

        chemin_chapitre = f"divs/div{i}"
        chemin_fichier_json = f"{chemin_chapitre}/final.json"
        # On va fusionner les fichiers individuels collationnés en un seul.
        with open(chemin_fichier_json, "w") as out_json_file:
            dictionnaire_sortie = {'table': [], 'witnesses': []}
            for fichier in glob.glob(f"{chemin_chapitre}/alignement_collatex*.json"):
                with open(fichier, 'r') as file:
                    dictionnaire_entree = json.loads(file.read())
                    nombre_temoins = len(dictionnaire_entree['table'])  # nombre_temoins est le nombre de témoins
                    for index_temoin in range(nombre_temoins):  # pour chaque témoin
                        temoin = dictionnaire_entree['witnesses'][index_temoin]
                        if len(dictionnaire_sortie['witnesses']) != nombre_temoins:  # tant que la liste des témoins nombre_temoins'est pas complète
                            dictionnaire_sortie['witnesses'].append(temoin)
                        if len(dictionnaire_sortie['table']) != nombre_temoins:  #
                            liste_vide = []
                            dictionnaire_sortie['table'].append(liste_vide)
                        for element in dictionnaire_entree['table'][index_temoin]:
                            dictionnaire_sortie['table'][index_temoin].append(element)
            json.dump(dictionnaire_sortie, out_json_file)



        # On compare les lieux variants et on en déduit les <app>
        with Halo(text='Création des apparats', spinner='dots'):
            # Étape suivante: transformer le JSON en xml. Pour cela on peut utiliser dict2xml.
            chemin_alignement = f"{chemin_chapitre}/alignement_collatex.xml"
            with open(chemin_alignement, "w+") as sortie_xml:
                with open(chemin_fichier_json, 'r') as fichier_json_a_xmliser:
                    obj = json.loads(fichier_json_a_xmliser.read())
                    vers_xml = dicttoxml.dicttoxml(obj).decode("utf-8")
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

        # Création du tableau d'alignement pour visualisation
        if parametres.tableauxAlignement:
            collation.tableau_alignement(saxon, chemin)


        collation.apparat_final(f'{chemin}/apparat_final.json', chemin)
        print("Création des apparats ✓")

        # injection.injection_omissions(f'{chemin}/apparat_Mad_G_22_final.xml', chemin)
        # Réinjection des apparats.
        injection.injection(saxon, chemin, i)

        liste_fichiers_in = glob.glob(f'{chemin}/apparat_*_*final.xml')
        # Ici on indique d'autres éléments tei à réinjecter.
        for element, position in parametres.reinjection.items():
            injection.injection_en_masse(chapitre=division, element_tei=element, position=position,
                                         liste_temoins=liste_fichiers_in)




    if parametres.fusion_documents:
        for temoin in glob.glob('temoins_tokenises/*.xml'):
            sigle = temoin.split('/')[1].split(".xml")[0]
            sorties.fusion_documents_tei(sigle)
        if parametres.latex:
            for fichier in glob.glob('divs/*.xml'):
                sorties.transformation_latex(saxon, fichier, True)

    if parametres.latex and not parametres.fusion_documents:
        for fichier in glob.glob(f'{chemin}/apparat_*_*final.xml'):
            print(fichier)
            sorties.transformation_latex(saxon, fichier, False, chemin)

    ## Tests de conformité
    corpus = Corpus()
    print(f'Comparing input file and output file tei:w...')
    for temoin in corpus.sigles:
        tests.tokentest(temoin, i)

    sorties.nettoyage("divs")
    t1 = time.time()
    temps_total = t1 - t0
    print(f"Fait en {round(temps_total)} secondes. \n")


class Corpus():
    def __init__(self):
        self.sigles = [fichier.split("/")[1].split(".xml")[0] for fichier in glob.glob('temoins_tokenises/*.xml')]


if __name__ == "__main__":
    main()
