# -*- coding: utf-8 -*-
import collections
import os
import re
import shutil
import time
import json
from halo import Halo
import subprocess
import glob
import logging
import argparse
import dicttoxml

dicttoxml.LOG.setLevel(logging.ERROR)

import python.collation.collation as collation
import python.tokenisation.tokenisation as tokenisation
import python.structuration.structuration as structuration
import python.lemmatisation.lemmatisation as lemmatisation
import python.sorties.sorties as sorties
import python.injections.injections as injections
import python.semantic_analysis.similarity as similarity
import python.settings
import python.tests.tests as tests
import python.utils.utils as utils


# Remerciements: merci à Élisa Nury pour ses éclaircissements sur le fonctionnement de CollateX et ses
# conseils.


def main():
    t0 = time.time()
    saxon = "saxon/saxon-he-12.7.jar"
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--parameters", default="parametres/lemmatisation.json",
                        help="Path to the parameter file.")
    parser.add_argument("-d", "--division", help="Division to be treated.", default={'livre': '1',
                                                                                     'partie': '2',
                                                                                     'chapitre': '2'})
    parser.add_argument("-corr", "--correction", default=False,
                        help="Correction mode (outputs more information in xml files).")
    parser.add_argument("-to", "--tokenizeonly", default=False, help="Exit after tokenization.")
    parser.add_argument("-lo", "--lemmatizeonly", default=False, help="Exit after lemmatization.")
    parser.add_argument("-ao", "--align_only", default=False, help="Exit after alignment.")
    parser.add_argument("-eat", "--exit_after_table_creation", default=False, help="Exit after alignment table production.")
    parser.add_argument("-cp", "--createpdf", default=False, help="Produce pdf and exit.")
    parser.add_argument("-io", "--injectiononly", default=False, help="Debug option: performs injection and exits")
    parser.add_argument("-To", "--testonly", default=False, help="Performs tests and exit.")
    parser.add_argument("-so", "--similarityonly", default=False, help="Performs similarity computation and exit.")
    parser.add_argument("-w", "--witness", default="*", help="Witness to process")
    parser.add_argument("-fo", "--fusiononly", default=False, help="Create final xml document with xi:includes")
    parser.add_argument("-id", "--integrer_deplacements", default=False, type=bool,
                        help="On visualise la collation avec les déplacements (ne permet pas de les integrer a l edition)")

    ##### Settings
    args = parser.parse_args()
    similarity_only = args.similarityonly
    print(similarity_only)
    correction = args.correction
    deplacements = args.integrer_deplacements
    log = correction
    inject_only = args.injectiononly
    lemmatize_only = args.lemmatizeonly
    tokenize_only = args.tokenizeonly
    test_only = args.testonly
    pdf_only = args.createpdf
    align_only = args.align_only
    table_only = args.exit_after_table_creation
    fichier_de_parametres = args.parameters
    witness = args.witness
    fusion_only = args.fusiononly
    #####
    division = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(args.division)
    div1_n = str(list(division.items())[0][1])
    div1_type = list(division.items())[0][0]
    div2_n = str(list(division.items())[1][1])
    div2_type = list(division.items())[1][0]
    div3_n = str(list(division.items())[2][1])
    div3_type = list(division.items())[2][0]
    if division is None:
        division = "*"

    # On importe les paramètres en créant un objet parametres
    parametres = python.settings.Parametres(fichier_de_parametres)
    # print(f'\n\n\n ---- Paramètres globaux: \n {parametres.__str__()}\n ')
    # print("Attention, certains paramètres peuvent être modifiés par des options "
    # "de la ligne de commande.")
    print(f'Lemmatisation seule: {lemmatize_only} \n')
    print(f'Mode correction: {correction} \n ---- \n')
    print(f'Injection seule: {inject_only} \n ---- \n')
    alignement = parametres.alignement
    temoin_base = parametres.temoin_base
    structuration_automatique = parametres.structuration_auto
    if alignement == "global" and not align_only:
        print("WARNING: l'alignement global ne fonctionne pas encore (xml:id identiques sur les non-apparats). "
              "On switche à un alignement mot à mot.\n\n ---- \n\n")
        parametres.alignement = "mam"

    align_on = parametres.align_on
    synonyms_datasets = parametres.create_synonym_dataset
    compute_similarity = parametres.compute_similarity
    chemin_corpus = parametres.corpus_path
    xpath_transcriptions = parametres.files_path
    excluded_ancestors = parametres.exclude_descendant_of

    liste_fichiers_tokenises = utils.chemin_temoins_tokenises()
    if fusion_only:
        for file in glob.glob(f"divs/div{division}/*transposed.xml"):
            sigle = utils.get_sigla_from_path(file)
            print(sigle)
            pattern = re.compile(r"div\d+")
            division_n = re.search(pattern, file)[0].replace("div", "")
            utils.clean_xml_file(input_file=file,
                                 output_file=f"divs/div{division_n}/apparat_{sigle}_{division_n}_final.xml")
        print("Création des fichiers xml maîtres")
        sorties.fusion_documents_tei(chemin_fichiers=f"divs/div{str(division_n)}",
                                     chemin_corpus=chemin_corpus,
                                     xpath_transcriptions=xpath_transcriptions,
                                     output_dir=parametres.output_dir)
        exit(0)

    if test_only:
        liste_sigles = utils.sigles()
        print(f'Tests en cours...')
        for sigle in liste_sigles:
            # On teste sur les fichiers non nettoyés.
            fichier = f"divs/div{division}/apparat_{sigle}_{division}_omitted.injected.apparated.lacuned.transposed.xml"
            tokenise = f"temoins_tokenises_regularises/{sigle}.xml"
            tests.order_test(fichier_a_tester=fichier,
                             temoin_tokenise=tokenise,
                             sigle=sigle,
                             division=division,
                             div_type=parametres.type_division)
        # tests.test_word_alignment(division)
        # for sigle in liste_sigles:
        #     tests.tokentest(sigle, division)
        #     tests.witness_test(sigle, division)
        exit(0)

    if similarity_only:
        for fichier in glob.glob(
                f"divs/div{division}/apparat_Mad_G_{division}_omitted.injected.apparated.lacuned.transposed.xml"):
            # similarity.compute_similarity(fichier)
            print(fichier)
            similarity.similarity_eval_set_creator(division, fichier)
        exit(0)

    if inject_only:
        liste_sigles = utils.sigles()
        chemin = f"divs/div{division}"
        Injector = injections.Injector(debug=True,
                                       div_n=division,
                                       elements_to_inject=parametres.reinjection,
                                       saxon=saxon,
                                       chemin=chemin,
                                       coeurs=parametres.parallel_process_number,
                                       element_base=parametres.element_base,
                                       type_division=parametres.type_division,
                                       lacuna_sensibility=parametres.lacuna_sensibility,
                                       liste_sigles=liste_sigles,
                                       excluded_elements=excluded_ancestors,
                                       temoin_base=temoin_base)
        Injector.run_injections()
        chemin_fichiers = f"divs/div{str(division)}"
        # sorties.fusion_documents_tei(chemin_fichiers=chemin_fichiers,
        #                              chemin_corpus=chemin_corpus,
        #                              xpath_transcriptions=xpath_transcriptions,
        #                              output_dir=parametres.output_dir)

        print("Cleaning files, producing final documents")
        for file in glob.glob(f"divs/div{division}/*transposed.xml"):
            sigle = utils.get_sigla_from_path(file)
            print(sigle)
            utils.clean_xml_file(input_file=file, output_file=f"divs/div{division}/apparat_{sigle}_{division}_final.xml")
        exit(0)

    # We start by removing all debug files
    utils.remove_debug_files()
    if parametres.prevalidation:
        corpus = parametres.corpus_path
        schema_sch = "python/tests/validator.sch"
        if not tests.validation_xml(corpus, schema_sch)[0]:
            print("Une erreur fatale est apparue. Merci de vérifier l'encodage.")
            print(f"Erreurs: {';'.join(element.text for element in tests.validation_xml(corpus, schema_sch)[1])}")
            exit(1)
        else:
            pass

    if tokenize_only:
        tokeniser = tokenisation.Tokenizer(saxon,
                                           temoin_leader=parametres.temoin_leader,
                                           nodes_to_reinject=parametres.reinjection)
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
        utils.remove_files(f"temoins_tokenises_regularises/txt/*")
        tokeniser = tokenisation.Tokenizer(saxon=saxon,
                                           temoin_leader=parametres.temoin_leader,
                                           nodes_to_reinject=parametres.reinjection)
        tokeniser.tokenisation(parametres.corpus_path, correction)

    if parametres.xmlId and not parametres.tokeniser:  # si le corpus est tokénisé mais sans xml:id
        for temoin in glob.glob('temoins_tokenises_regularises/*.xml'):
            temoin = f"temoins_tokenises_regularises/{temoin}"
            tokeniser.ajout_xml_id(temoin)

    portee = [((div1_type, div1_n), (div2_type, div2_n), (div3_type, div3_n))]
    if parametres.lemmatiser:
        print("Lemmatisation du corpus...")
        corpus_a_lemmatiser = lemmatisation.CorpusALemmatiser(
            liste_temoins=glob.glob('temoins_tokenises_regularises/*.xml'),
            langue=parametres.lang,
            moteur_transformation=saxon,
            nombre_coeurs=parametres.parallel_process_number
        )
        # On lemmatise toujours l'intégralité du corpus, pour pouvoir copier les fichiers lemmatisés
        # dans le git principal.
        corpus_a_lemmatiser.lemmatisation_parallele(portee[0])
        # On les copie. Ily aura forcément une discordance si on ne traite pas les 23 chapitres d'un coup.
        # for temoin in glob.glob('temoins_tokenises_regularises/*.xml'):
            # shutil.copy(temoin, "/home/mgl/Bureau/These/Edition"
                                # "/hyperregimiento-de-los-principes/Dedans/XML/corpus_lemmatise")
        # corpus_a_lemmatiser.lemmatisation_parallele(division)
    context = f"//tei:div[@type='{div1_type}'][@n={div1_n}]/descendant::tei:div[@type='{div2_type}'][@n={div2_n}]/descendant::tei:div[@type='{div3_type}'][@n={div3_n}]"
    if structuration_automatique:
        print("La structuration automatique demande que le témoin base soit "
              "structuré au niveau du titre uniquement (un tei:head avec un @n). Les autres témoins"
              "ne doivent avoir aucune structure à l'intérieur de la division.")
        structurer = structuration.Structurer(target_path=f"temoins_tokenises/*.xml",
                                              source_file=f"temoins_tokenises/Rome_W.xml",
                                              output_files_prefix="",
                                              pre_structure=True)
        structurer.pre_structure_document(proportion=.30,
                                          element_to_create=parametres.element_base, remove_pc=False,
                                          context=context)
        query = f"child::node()[self::tei:head or self::tei:{parametres.element_base}]"
        print(query)
        structurer.align_structure(context=context, query=query, text_proportion=.6, use_lemmas=True, remove_pc=False)
        
        # Et on re-régularise.
        print(["java", "-jar", saxon, "-xi:on", f"temoins_tokenises/{parametres.temoin_leader}.xml",
               "xsl/pre_alignement/regularisation.xsl", "False"])
        subprocess.run(["java", "-jar", saxon, "-xi:on", f"temoins_tokenises/{parametres.temoin_leader}.xml",
                        "xsl/pre_alignement/regularisation.xsl", "correction=False"])

    if lemmatize_only:
        t1 = time.time()
        temps_total = t1 - t0
        print(f"Fait en {round(temps_total)} secondes. \n")
        exit(0)

    # if "-" in division:
        # portee = range(int(division.split("-")[0]), int(division.split("-")[1]) + 1)

    # else:
        # argument = int(division)
        # arg_plus_1 = argument + 1
        # portee = range(argument, arg_plus_1)
    corpus_preparator = collation.CorpusPreparation(saxon=saxon,
                                                    temoin_leader=parametres.temoin_leader,
                                                    type_division=parametres.type_division,
                                                    element_base=parametres.element_base,
                                                    liste_temoins=utils.chemin_temoins_tokenises_regularises(),
                                                    integrer_deplacements=deplacements)

    liste_sigles = utils.sigles()
    for localisation in portee:
        ((div1_type, div1_n), (div2_type, div2_n), (div3_type, div3_n)) = localisation
        # chemin_fichiers = f"divs/div{str(i)}"
        chemin_fichiers = f"divs/{div1_type}_{div1_n}/{div2_type}_{div2_n}/{div3_type}_{div3_n}"

        # We first remove all files in the corresponding dir to avoid any possible interference and bug
        utils.remove_files(f"{chemin_fichiers}/*")

        print(f"Traitement de la division {div1_type}_{div1_n}/{div2_type}_{div2_n}/{div3_type}_{div3_n}")
        corpus_preparator.prepare(localisation)
        pattern = re.compile(f"{chemin_fichiers}/juxtaposition_\d+\.xml")
        fichiers_xml = [fichier.split('/')[-1] for fichier in glob.glob(f"{chemin_fichiers}/*.xml") if
                        re.match(pattern, fichier)]
        assert fichiers_xml != [], ("Liste de fichiers vides, un problème est apparu "
                                    "lors de la production de chacun des fichiers à collationer.")
        print("Alignement avec CollateX.")

        aligner = collation.Aligner(liste_fichiers_xml=fichiers_xml,
                                    chemin=chemin_fichiers,
                                    moteur_transformation_xsl=saxon,
                                    correction_mode=correction,
                                    align_on=align_on,
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
            # Création du tableau d'alignement pour visualisation
        if parametres.tableauxAlignement:
            sorties.tableau_alignement(saxon, chemin_fichiers)

        tests.test_collation_tokens(chemin_fichiers, portee[0], parametres.type_division)


        if table_only:
            t1 = time.time()
            temps_total = t1 - t0
            print(f"Fait en {round(temps_total)} secondes. \n")
            exit(0)
        if not tests.test_lemmatization(localisation=localisation,
                                        div_type=parametres.type_division,
                                        temoin_leader=parametres.temoin_leader):
            print("This division is not lemmatized; exiting.")
            exit(0)
        collationeur = collation.Collateur(log=False,
                                           chemin_fichiers=chemin_fichiers,
                                           div_n=division,
                                           div_type=parametres.type_division,
                                           temoin_base=temoin_base)
        collationeur.run_collation()
        print("Création des apparats ✓")

        # On bouge tous les fichiers d'alignement dans un dossier à part
        fichiers_alignement = glob.glob(f"{chemin_fichiers}/align*")
        fichiers_alignement.extend(glob.glob(f"{chemin_fichiers}/juxtaposition*"))
        fichiers_alignement.append(f"{chemin_fichiers}/apparat_final.json")
        fichiers_alignement.append(f"{chemin_fichiers}/apparat_collatex.xml")

        utils.move_files(fichiers_alignement, f"{chemin_fichiers}/alignement")

        if align_only:
            t1 = time.time()
            temps_total = t1 - t0
            print(f"Fait en {round(temps_total)} secondes. \n")
            exit(0)

        injecteur = injections.Injector(debug=True,
                                        div_n=localisation,
                                        elements_to_inject=parametres.reinjection,
                                        saxon=saxon,
                                        chemin=chemin_fichiers,
                                        coeurs=parametres.parallel_process_number,
                                        element_base=parametres.element_base,
                                        type_division=parametres.type_division,
                                        lacuna_sensibility=parametres.lacuna_sensibility,
                                        liste_sigles=liste_sigles,
                                        excluded_elements=excluded_ancestors,
                                        temoin_base=temoin_base)
        injecteur.run_injections()
        # Ici on indique d'autres éléments tei à réinjecter.

        # On copie les fichiers finaux produits pour ne pas avoir à refaire à chaque fois le processus
        for file in glob.glob(f"{chemin_fichiers}/*_injected_punct.transposed.lacuned.xml"):
            shutil.copy(file, f'divs/results')

        if synonyms_datasets:
            similarity.similarity_eval_set_creator(localisation)

        liste_fichiers_finaux = utils.chemin_fichiers_finaux(localisation)

        print("Cleaning files, producing final documents")
        for file in glob.glob(f"divs/div{localisation}/*transposed.xml"):
            sigle = utils.get_sigla_from_path(file)
            print(sigle)
            utils.clean_xml_file(input_file=file, output_file=f"divs/div{localisation}/apparat_{sigle}_{localisation}_final.xml")

        for file in glob.glob(f"div{chemin_fichiers}/*final.xml"):
            shutil.copy(file, f'divs/results')

        if parametres.fusion_documents:
            sorties.fusion_documents_tei(chemin_fichiers=chemin_fichiers,
                                         chemin_corpus=chemin_corpus,
                                         xpath_transcriptions=xpath_transcriptions,
                                         output_dir=parametres.output_dir)

        # Tests de conformité
        # for sigle in liste_sigles:
        # tests.tokentest(sigle, i)
        # tests.witness_test(sigle, i)
        # tests.test_word_alignment(i)
        print(f'Tests en cours...')
        for sigle in liste_sigles:
            # On teste sur les fichiers non nettoyés.
            fichier = f"divs/div{division}/apparat_{sigle}_{division}_omitted.injected.apparated.lacuned.transposed.xml"
            tokenise = f"temoins_tokenises_regularises/{sigle}.xml"
            tests.order_test(fichier_a_tester=fichier,
                             temoin_tokenise=tokenise,
                             sigle=sigle,
                             division=division,
                             div_type=parametres.type_division)

    sorties.nettoyage("divs")
    t1 = time.time()
    temps_total = t1 - t0
    print(f"Fait en {round(temps_total)} secondes. \n")


if __name__ == "__main__":
    main()
