# -*- coding: utf-8 -*-
import os
import re
import time
import json
from halo import Halo
import subprocess
import glob
import logging
import argparse
import dicttoxml
import multiprocessing as mp

dicttoxml.LOG.setLevel(logging.ERROR)

import python.collation.collation as collation
import python.tokenisation.tokenisation as tokenisation
import python.lemmatisation.lemmatisation as lemmatisation
import python.sorties.sorties as sorties
import python.injections.injections as injections
import python.semantic_analysis.embeddings as embeddings
import python.semantic_analysis.similarity as similarity
import python.settings
import python.tests.tests as tests
import python.utils.utils as utils


# IMPORTANT: pour la POO, considérer le corpus comme un objet ? En faire une classe qui permette de tout traiter
# à partir de là ? Suppose de demander un tei:teiCorpus

# TODO: URGENT ! vérifier pourquoi les tei:w/tei:sic sont supprimés. 
# TODO: nettoyer le tout / s'occuper de la conservation des xml:id pour ne pas avoir à les régénérer
# Remerciements: merci à Élisa Nury pour ses éclaircissements sur le fonctionnement de CollateX et ses
# conseils.
# Todo: faire du mot à mot et s'occuper de rassembler en plus gros apparats après. Si on fait du mot à mot, l'éclatement
# du TEI n'a plus aucun sens car il n'y a plus de risque de destructurer...


def main():
    t0 = time.time()
    saxon = "saxon9he.jar"
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--parameters", default="parametres/lemmatisation.json",
                        help="Path to the parameter file.")
    parser.add_argument("-d", "--division", help="Division to be treated.")
    parser.add_argument("-corr", "--correction", default=False,
                        help="Correction mode (outputs more information in xml files).")
    parser.add_argument("-to", "--tokenizeonly", default=False, help="Exit after tokenization.")
    parser.add_argument("-lo", "--lemmatizeonly", default=False, help="Exit after lemmatization.")
    parser.add_argument("-ao", "--align_only", default=False, help="Exit after alignment.")
    parser.add_argument("-cp", "--createpdf", default=False, help="Produce pdf and exit.")
    parser.add_argument("-io", "--injectiononly", default=False, help="Debug option: performs injection and exits")
    parser.add_argument("-To", "--testonly", default=False, help="Performs tests and exit.")

    ##### Settings
    args = parser.parse_args()
    correction = args.correction
    log = correction
    inject_only = args.injectiononly
    lemmatize_only = args.lemmatizeonly
    tokenize_only = args.tokenizeonly
    test_only = args.testonly
    pdf_only = args.createpdf
    align_only = args.align_only
    fichier_de_parametres = args.parameters
    division = args.division
    #####

    if division is None:
        division = "*"

    # On importe les paramètres en créant un objet parametres
    parametres = python.settings.Parametres(fichier_de_parametres)
    print(f'\n\n\n ---- Paramètres globaux: \n {parametres.__str__()}\n ')
    print("Attention, certains paramètres peuvent être modifiés par des options "
          "de la ligne de commande.")
    print(f'Lemmatisation seule: {lemmatize_only} \n')
    print(f'Mode correction: {correction} \n ---- \n')
    print(f'Injection seule: {inject_only} \n ---- \n')
    alignement = parametres.alignement
    if alignement == "global" and not align_only:
        print("WARNING: l'alignement global ne fonctionne pas encore (xml:id identiques sur les non-apparats). "
              "On switche à un alignement mot à mot.\n\n ---- \n\n")
        parametres.alignement = "mam"

    synonyms_datasets = parametres.create_synonym_dataset
    compute_similarity = parametres.compute_similarity

    liste_sigles = utils.sigles()
    if test_only:
        print(f'Tests en cours...')
        tests.test_word_alignment(division)
        for sigle in liste_sigles:
            tests.tokentest(sigle, division)
            tests.witness_test(sigle, division)
        exit(0)

    if inject_only:
        chemin = f"divs/div{division}"
        liste_fichiers_finaux = utils.chemin_fichiers_finaux(division)
        Injector = injections.Injector(debug=True,
                                       div_n=division,
                                       elements_to_inject=parametres.reinjection.items(),
                                       liste_temoins=liste_fichiers_finaux,
                                       saxon=saxon,
                                       chemin=chemin,
                                       coeurs=parametres.parallel_process_number,
                                       element_base=parametres.element_base,
                                       type_division=parametres.type_division)
        Injector.run_injections()
        exit(0)

    if pdf_only:
        chemin = f"divs/div{division}"
        print("On produit les fichiers pdf.")
        for fichier in glob.glob(f'{chemin}/apparat_*_*injected_punct.xml'):
            print(fichier)
            sorties.transformation_latex(saxon, fichier, False, chemin)
        sorties.nettoyage("divs")
        exit(0)

    if parametres.prevalidation:
        corpus = "/home/mgl/Bureau/These/Edition/hyperregimiento-de-los-principes/Dedans/XML/corpus/corpus.xml"
        schema_sch = "/home/mgl/Bureau/These/Edition/collator/python/tests/validator.sch"
        if not tests.validation_xml(corpus, schema_sch)[0]:
            print("Une erreur fatale est apparue. Merci de vérifier l'encodage.")
            print(f"Erreurs: {';'.join(element.text for element in tests.validation_xml(corpus, schema_sch)[1])}")
            exit(1)
        else:
            pass

    if tokenize_only:
        tokeniser = tokenisation.Tokenizer(saxon, temoin_leader=parametres.temoin_leader)
        tokeniser.tokenisation(parametres.corpus_path, correction)
        exit(0)

    if parametres.tokeniser:
        reponse = input(
            "Vous êtes en train de réécrire les fichiers et de relancer la lemmatisation. Continuer ? [o/n]\n")
        if reponse == "o":
            pass
        else:
            exit(0)
        print(parametres.corpus_path)
        tokeniser = tokenisation.Tokenizer(saxon, temoin_leader=parametres.temoin_leader)
        tokeniser.tokenisation(parametres.corpus_path, correction)

    if parametres.xmlId and not parametres.tokeniser:  # si le corpus est tokénisé mais sans xml:id
        for temoin in glob.glob('temoins_tokenises_regularises/*.xml'):
            temoin = f"temoins_tokenises_regularises/{temoin}"
            tokeniser.ajout_xml_id(temoin)

    if parametres.lemmatiser:
        print("Lemmatisation du corpus...")
        corpus_a_lemmatiser = lemmatisation.CorpusALemmatiser(
            liste_temoins=glob.glob('temoins_tokenises_regularises/*.xml'),
            langue=parametres.lang,
            moteur_transformation=saxon,
            nombre_coeurs=parametres.parallel_process_number
        )
        corpus_a_lemmatiser.lemmatisation_parallele(division)

    if lemmatize_only:
        t1 = time.time()
        temps_total = t1 - t0
        print(f"Fait en {round(temps_total)} secondes. \n")
        exit(0)

    if "-" in division:
        portee = range(int(division.split("-")[0]), int(division.split("-")[1]) + 1)
    else:
        argument = int(division)
        arg_plus_1 = argument + 1
        portee = range(argument, arg_plus_1)

    corpus_preparator = collation.CorpusPreparation(saxon=saxon,
                                                    temoin_leader=parametres.temoin_leader,
                                                    type_division=parametres.type_division,
                                                    element_base=parametres.element_base,
                                                    liste_temoins=utils.chemin_temoins_tokenises_regularises())

    for i in portee:
        chemin_fichiers = f"divs/div{str(i)}"
        print(f"Traitement de la division {str(i)}")
        corpus_preparator.prepare(i)
        pattern = re.compile(f"divs/div{i}/juxtaposition_\d+\.xml")
        fichiers_xml = [fichier.split('/')[-1] for fichier in glob.glob(f"{chemin_fichiers}/*.xml") if
                        re.match(pattern, fichier)]
        print("Alignement avec CollateX.")

        aligner = collation.Aligner(liste_fichiers_xml=fichiers_xml,
                                    chemin=chemin_fichiers,
                                    moteur_transformation_xsl=saxon,
                                    correction_mode=correction,
                                    parametres_alignement=parametres.alignement,
                                    nombre_de_coeurs=parametres.parallel_process_number)
        aligner.run()

        chemin_fichier_json = f"{chemin_fichiers}/final.json"
        # On va fusionner les fichiers individuels collationnés en un seul fichier.
        with open(chemin_fichier_json, "w") as out_json_file:
            dictionnaire_sortie = {'table': [], 'witnesses': []}
            par_nb = len(glob.glob(f"{chemin_fichiers}/alignement_collatex*.json"))  # on veut ordonner la
            # fusion des
            # documents pour le tableau d'alignement ensuite
            for par in range(par_nb):
                fichier = f"{chemin_fichiers}/alignement_collatex{par + 1}.json"
                with open(fichier, 'r') as file:
                    dictionnaire_entree = json.loads(file.read())
                    nombre_temoins = len(dictionnaire_entree['table'])  # nombre_temoins est le nombre de témoins
                    for index_temoin in range(nombre_temoins):  # pour chaque témoin
                        temoin = dictionnaire_entree['witnesses'][index_temoin]
                        if len(dictionnaire_sortie[
                                   'witnesses']) != nombre_temoins:  # tant que la liste des témoins nombre_temoins'est pas complète
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
            chemin_alignement = f"{chemin_fichiers}/alignement_collatex.xml"
            with open(chemin_alignement, "w+") as sortie_xml:
                with open(chemin_fichier_json, 'r') as fichier_json_a_xmliser:
                    obj = json.loads(fichier_json_a_xmliser.read())
                    vers_xml = dicttoxml.dicttoxml(obj).decode("utf-8")
                sortie_xml.write(vers_xml)

            chemin_regroupement = "xsl/post_alignement/regroupement.xsl"
            # Regroupement des lieux variants (témoin A puis témoin B puis témoin C
            # > lieu variant 1: A, B, C ; lieu variant 2: A, B, C)
            cmd = f"java -jar {saxon} -o:{chemin_fichiers}/aligne_regroupe.xml {chemin_fichiers}/alignement_collatex.xml " \
                  f"{chemin_regroupement}"
            subprocess.run(cmd.split())

            # C'est à ce niveau que l'étape de correction devrait avoir lieu. Y réfléchir.
            # Création de l'apparat: transformation de aligne_regroupe.xml en JSON
            chemin_xsl_apparat = "xsl/post_alignement/creation_apparat.xsl"
            cmd = f"java -jar {saxon} -o:{chemin_fichiers}/apparat_final.json {chemin_fichiers}/aligne_regroupe.xml " \
                  f"{chemin_xsl_apparat}"
            subprocess.run(cmd.split())
            # Création de l'apparat: suppression de la redondance, identification des lieux variants,
            # regroupement des lemmes

        collationeur = collation.Collateur(log=False,
                                           chemin_fichiers=chemin_fichiers,
                                           div_n=division)
        collationeur.run()
        print("Création des apparats ✓")

        # Création du tableau d'alignement pour visualisation
        if parametres.tableauxAlignement:
            sorties.tableau_alignement(saxon, chemin_fichiers)
        if align_only:
            t1 = time.time()
            temps_total = t1 - t0
            print(f"Fait en {round(temps_total)} secondes. \n")
            exit(0)

        # Réinjection des apparats.
        injections.injection_apparats(saxon=saxon,
                                      chemin=chemin_fichiers,
                                      n_division=i,
                                      coeurs=parametres.parallel_process_number,
                                      type_division=parametres.type_division)

        liste_fichiers_finaux = utils.chemin_fichiers_finaux(i)
        liste_fichiers_tokenises = utils.chemin_temoins_tokenises()

        Injecteur = injections.Injector(debug=False,
                                        div_n=division,
                                        elements_to_inject=parametres.reinjection.items(),
                                        liste_temoins=liste_fichiers_finaux,
                                        saxon=saxon,
                                        chemin=chemin_fichiers,
                                        coeurs=parametres.parallel_process_number,
                                        element_base=parametres.element_base,
                                        type_division=parametres.type_division)
        Injecteur.run_injections()
        # Ici on indique d'autres éléments tei à réinjecter.

        if compute_similarity:
            liste_fichiers_finale = glob.glob(f"{chemin_fichiers}/*_injected_punct.xml")
            similarity.compute_similarity(liste_fichiers_finale)

        if synonyms_datasets:
            similarity.similarity_eval_set_creator(i)

        # Tests de conformité
        print(f'Tests en cours...')
        for sigle in liste_sigles:
            tests.tokentest(sigle, i)
            tests.witness_test(sigle, i)
            tests.test_word_alignment(i)

    if parametres.fusion_documents:
        for temoin in liste_fichiers_tokenises:
            sigle = temoin.split('/')[1].split(".xml")[0]
            sorties.fusion_documents_tei(sigle)
        if parametres.latex:
            for fichier in glob.glob('divs/*.xml'):
                sorties.transformation_latex(saxon, fichier, True)

    if parametres.latex and not parametres.fusion_documents:
        for fichier in liste_fichiers_finaux:
            print(fichier)
            sorties.transformation_latex(saxon, fichier.replace("final", "injected"), False, chemin_fichiers)

    sorties.nettoyage("divs")
    t1 = time.time()
    temps_total = t1 - t0
    print(f"Fait en {round(temps_total)} secondes. \n")


if __name__ == "__main__":
    main()
