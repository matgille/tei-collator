import subprocess
import re
from lxml import etree
import glob
import operator
import traceback

def injections_element(temoin, n, tei_elements, position):
    """
    Cette fonction permet la réinjection d'éléments présents dans un témoin dans tous les autres témoins.
    Il s'appuie pour ce faire sur le tei:w qui suit ou précède l'élément ciblé, en fonction
    de cet élément.
    :param temoin: le témoin sur lequel appliquer les injections
    :param div: la division courante
    :param tei_elements: l'élément tei à injecter.
    :param position: Possibilités: "before" (le point d'ancrage est avant un tei:w, exemple: tei:milestone)
    ou "after" (le point d'ancrage se trouve après le tei:w, exemple, tei:note)
    :return: Un tuple comprenant l'objet lxml final et le nom du fichier à écrire correspondant.
    """
    print(f'\nInserting {tei_elements} into {temoin}')

    if position == "before":
        following_or_preceding = "following" # on va chercher le tei:w suivant
        sign = operator.sub # et on injectera donc avant ce tei:w (index(tei:w) - 1)
    else:
        following_or_preceding = "preceding" # on va chercher le tei:w précédent
        sign = operator.add # et on injectera donc après ce tei:w (index(tei:w) + 1)


    final_notes_list = []
    final_w_list = []
    final_witness_list = []
    for file in glob.iglob(f"/home/mgl/Bureau/These/Edition/collator/divs/div{n}/*final.xml"):
        f = etree.parse(file)
        tei_namespace = 'http://www.tei-c.org/ns/1.0'
        NSMAP1 = {'tei': tei_namespace}  # pour la recherche d'éléments avec la méthode xpath

        # On va d'abord récuperer et aligner chaque élément tei:note, l'xml:id du tei:w qui précède et le témoin concerné
        notes_list = f.xpath(f'//tei:div[@n=\'{n}\']//{tei_elements}', namespaces=NSMAP1)
        nombre_de_notes = len(notes_list)
        w_list = f.xpath(f'//tei:div[@n=\'{n}\']//{tei_elements}/{following_or_preceding}::tei:w[1]/@xml:id', namespaces=NSMAP1)
        temoin_id = f.xpath(f'//tei:div[@n=\'{n}\']//{tei_elements}/ancestor::tei:div[@type=\'chapitre\']/@xml:id', namespaces=NSMAP1)
        if temoin_id:
            temoin_id = "_".join(temoin_id[0].split("_")[0:2])
            final_witness_list.extend([temoin_id for x in range(nombre_de_notes)]) # https://stackoverflow.com/a/4654446
        final_w_list.extend(w_list)
        final_notes_list.extend(notes_list)
    notes_tuples =  list(zip(final_w_list, final_notes_list, final_witness_list))
    # On produit une liste de tuples de la forme :
    # [
    # ('kNMdVRz', <Element {http://www.tei-c.org/ns/1.0}note at 0x7f08a90f9ac8>, 'Sev_R'),
    # ('oqcqYPq', <Element {http://www.tei-c.org/ns/1.0}note at 0x7f08a90f9c08>, 'Sal_J')
    # ]
    print(f'{len(notes_tuples)} to insert.')
    for i in notes_tuples:
        print(f'{etree.tostring(i[1])} is {position} w[@xml:id=\'{i[0]}\']')
    # Puis on va parcourir le dictionnaire et insérer toutes les notes dans le témoin traité.
    current_xml_file = etree.parse(temoin)
    temoin_id_courant = "_".join(current_xml_file.xpath(f'//tei:div[@type=\'chapitre\']/@xml:id', namespaces=NSMAP1)[0].split("_")[0:2])
    print("--- Injection ---")
    print(len(notes_tuples))
    for item in notes_tuples:
        id_item, element, temoin_de_l_element = item[0], item[1], item[2]
        print(f'Élément à injecter : {etree.tostring(element)}')
        element.set("corresp", f'#{temoin_de_l_element}') # on indique de quel témoin provient la note.
        # Il y a un bug ici: puisque l'on modifie à la volée les textes, à chaque fois qu'on change de témoin
        # ça pose problème et le témoin dans le corresp est faux, ce qui
        # va biaiser la suite du processus... Il faut que cette fonction produise un nouveau document de sortie
        # On passe si le témoin de la réinjection est le même que le témoin de la note
        if temoin_de_l_element == temoin_id_courant:
            pass
        else:
            try:
                # print(f"témoin: {temoin_id_courant}; id: {id_item}\n"
                      # f"contenu de l'élément: {etree.tostring(element)}")
                word_to_change = current_xml_file.xpath(f'//tei:w[@xml:id=\'{id_item}\']', namespaces=NSMAP1)[0]
                item_element = word_to_change.getparent()  # https://stackoverflow.com/questions/7474972/python-lxml-append
                # -element-after-another-element
                # print(sign)
                index = sign(item_element.index(word_to_change), 1)# https://stackoverflow.com/a/54559513
                # print(f'index => {index}')
                if index == -1:
                    index = 0
                # On va tester la présence de l'élément à l'emplacement de l'injection
                test_existence = current_xml_file.xpath(f'//tei:div[@n=\'{n}\']//{tei_elements}[{following_or_preceding}::tei:w[@xml:id = \'{id_item}\']]', namespaces=NSMAP1)
                if len(test_existence) == 0:
                    item_element.insert(index, element)
                else:
                    print(f'On n\'injecte pas l\'élément {etree.tostring(element)} dans {temoin}')
            except Exception as e:
                print(f"Il y a une omission dans {temoin.split('/')[-1]} qui empêche l'injection:"
                      f"\n {traceback.format_exc()}")
    print("--- Injection terminée ---")
    return current_xml_file, temoin



def injection_python(chemin, chapitre):
    print("On réinjecte les apparats")
    tei_namespace = 'http://www.tei-c.org/ns/1.0'
    NSMAP1 = {'tei': tei_namespace}  # pour la recherche d'éléments avec la méthode xpath
    file =  f"/home/mgl/Bureau/These/Edition/collator/divs/div{chapitre}/juxtaposition_orig.xml"
    apparat_file = f"/home/mgl/Bureau/These/Edition/collator/divs/div{chapitre}/apparat_collatex.xml"

    with open(file, "r") as opened_file:
        parsed_group_file = etree.parse(opened_file)
    with open(apparat_file, "r") as opened_apparat_file:
        parsed_apparat_file = etree.parse(opened_apparat_file)

    # On travaille sur chaque témoin
    for witness in parsed_group_file.xpath("//temoin"):
        siglum = witness.xpath("@n")[0]
        for word in witness.xpath("//tei:w", namespaces = NSMAP1):
            xml_id = word.xpath("@xml:id")[0]

        # On écrit finalement le fichier
        witness[0].getparent().tag = "div"
        witness[0].getparent().set("{http://www.w3.org/XML/1998/namespace}id", f'{siglum}_3_3_{chapitre}')
        witness[0].getparent().set("type", "chapitre")
        witness[0].getparent().set("n", str(chapitre))
        witness[0].set("xmlns", tei_namespace) # on crée le namespace adéquat.

        list_word_id_apparat_collatex = zip(parsed_apparat_file.xpath("//tei:w", namespaces=NSMAP1),
                                            parsed_apparat_file.xpath("//tei:w/@xml:id", namespaces=NSMAP1))


        for word in witness.xpath("//tei:w", namespaces=NSMAP1):
            pass


        with open(f"/home/mgl/Documents/apparat_{siglum}_{chapitre}.xml", "w") as output_file:
            print("Outputting...")
            output_file.write(etree.tostring(witness).decode())




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
    # injection1(chapitre, chemin)
    print("---- INJECTION 1: apparats ----")
    param_chapitre = f"chapitre={str(chapitre)}"  # Premier paramètre passé à la xsl: le chapitre à processer
    param_chemin_sortie = f"chemin_sortie={chemin}/"  # Second paramètre: le chemin vers le fichier de sortie
    fichier_entree = f"{chemin}/juxtaposition_orig.xml"
    # with Halo(text="Injection des apparats dans chaque transcription individuelle", spinner='dots'):
    #  première étape de l'injection. Apparats, noeuds textuels et suppression de la redondance
    chemin_injection = "xsl/post_alignement/injection_apparats.xsl"
    subprocess.run(["java", "-jar", saxon, fichier_entree, chemin_injection, param_chapitre, param_chemin_sortie])

    # seconde étape: noeuds non textuels
    print("\n---- INJECTION 2: suppression de la redondance ----")
    fichiers_apparat = f'{chemin}/apparat_*_*.xml'
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
    fichiers_apparat = f'{chemin}/apparat_*_*outb.xml'
    liste = glob.glob(fichiers_apparat)
    for i in liste:  # on crée une boucle car les fichiers on été divisés par la feuille précédente.
        sigle = i.split("apparat_")[1].split(".xml")[0].split("_")[0] + "_" \
                + i.split("apparat_")[1].split(".xml")[0].split("_")[1]
        param_sigle = "sigle=" + sigle
        subprocess.run(["java", "-jar", saxon, i, chemin_injection2, param_chapitre, param_sigle])

    #  troisième étape: ponctuation
    print("\n---- INJECTION 3: ponctuation ----")
    chemin_injection_ponctuation = "xsl/post_alignement/injection_ponctuation.xsl"
    fichiers_apparat = f'{chemin}/apparat_*_*outc.xml'
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
    fichiers_apparat = f'{chemin}/apparat_*_*out.xml'
    liste = glob.glob(fichiers_apparat)
    for i in liste:
        sigle = i.split("apparat_")[1].split(".xml")[0].split("_")[0] + "_" \
                + i.split("apparat_")[1].split(".xml")[0].split("_")[1]
        param_sigle = "sigle=" + sigle
        subprocess.run(["java", "-jar", saxon, i, chemin_injection_ponctuation, param_chapitre, param_sigle])
    print("Création des balises de lacunes ✓")

