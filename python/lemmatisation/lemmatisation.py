import subprocess
import sys
import string
import re
import random
from lxml import etree
import xml.etree.ElementTree as ET
import os
from IPython.display import clear_output
from cltk.lemmatize.latin.backoff import BackoffLatinLemmatizer


def principal(fichier, argument):
    nom_fichier = os.path.basename(fichier)
    moteur_xslt = "saxon9he.jar"
    if argument == "--latin-medieval":
        langue = "lat_o"
    elif argument == "--latin-classique":
        langue = "lat"
    else:
        langue = "spa_o"
    lemmatisation(nom_fichier, moteur_xslt, langue)
    production_doc_final(nom_fichier, moteur_xslt)


def lemmatisation(fichier, moteur_xslt, langue):
    """
    Lemmatisation du fichier XML et réinjection dans le document xml originel.
    :param fichier: le fichier à lemmatiser
    :param moteur_xslt: le moteur de transformation à utiliser
    :param langue: la langue du fichier
    :return: retourne un fichier lemmatisé
    """
    fichier = os.path.basename(fichier)
    fichier_sans_extension = os.path.splitext(fichier)[0]
    fichier_xsl = "xsl/lemmatisation/transformation_pre_lemmatisation.xsl"
    chemin_vers_fichier = "temoins_tokenises_regularises/" + str(fichier)
    fichier_entree_txt = 'temoins_tokenises_regularises/txt/' + fichier_sans_extension + '.txt'
    param_sortie = "sortie=" + fichier_entree_txt
    subprocess.run(["java", "-jar", moteur_xslt, chemin_vers_fichier, fichier_xsl, param_sortie])
    if langue == "spa_o":
        fichier_lemmatise = 'temoins_tokenises_regularises/txt/' + fichier_sans_extension + '_lemmatise' + '.txt'
        cmd_sh = ["sh", "python/lemmatisation/analyze.sh", fichier_entree_txt,
                  fichier_lemmatise]  # je dois passer par un script externe car un subprocess tourne dans le vide,
        # pas trouvé pourquoi
        subprocess.run(cmd_sh)  # analyze est dans /usr/bin
        maliste = txt_to_liste(fichier_lemmatise)
        parser = etree.XMLParser(load_dtd=True,
                                 resolve_entities=True)  # inutile car les entités ont déjà été résolues
        # auparavant normalement, mais au cas où.
        temoin_tokenise = "temoins_tokenises_regularises/" + fichier
        f = etree.parse(temoin_tokenise, parser=parser)
        root = f.getroot()
        tei = {'tei': 'http://www.tei-c.org/ns/1.0'}
        groupe_words = "//tei:w"
        tokens = root.xpath(groupe_words, namespaces=tei)
        fichier_lemmatise = temoin_tokenise
        n = 1
        for mot in tokens:
            nombre_mots_precedents = int(mot.xpath("count(preceding::tei:w) + 1", namespaces=tei))
            nombre_ponctuation_precedente = int(mot.xpath("count(preceding::tei:pc) + 1", namespaces=tei))
            position_absolue_element = nombre_mots_precedents + nombre_ponctuation_precedente  # attention à
            try:
                liste_correcte = maliste[position_absolue_element - 2]  # Ça marche bien si la lemmatisation se fait
            except Exception as ecxp:
                print("Error in line %s: \n %s" % (position_absolue_element, ecxp))
                exit(1)
            # sans retokenisation. Pour l'instant, ça bloque avec les chiffre (ochenta mill est fusionné). Voir
            # avec les devs de Freeling.
            n += 1
            lemme_position = liste_correcte[1]
            pos_position = liste_correcte[2]

            if mot.xpath("@lemma") and mot.xpath("@pos"): # si l'analyse est déjà présente (cas des lemmes
                # mal analysés par Freeling et donc corrigés à la main en amont), ne rien faire
                pass
            elif mot.xpath("@lemma") and not mot.xpath("@pos"):
                mot.set("pos", pos_position)
            else:
                mot.set("lemma", lemme_position)
                mot.set("pos", pos_position)

    elif langue == "lat_o":
        modele_latin = "model.tar"
        cmd = "pie tag <%s,lemma,pos,Person,Numb,Tense,Case,Mood> %s" % (
            modele_latin, fichier_entree_txt)
        subprocess.run(cmd.split())
        fichier_seul = os.path.splitext(fichier_entree_txt)[0]
        fichier_lemmatise = str(fichier_seul) + "-pie.txt"
        maliste = txt_to_liste(fichier_lemmatise)
        # Nettoyage de la liste
        maliste.pop(0)  # on supprime les titres de colonnes

        parser = etree.XMLParser(load_dtd=True,
                                 resolve_entities=True)  # inutile car les entités ont déjà été résolues
        # auparavant normalement, mais au cas où.
        temoin_tokenise = "temoins_tokenises_regularises/" + fichier
        f = etree.parse(temoin_tokenise, parser=parser)
        root = f.getroot()
        tei = {'tei': 'http://www.tei-c.org/ns/1.0'}
        groupe_words = "//tei:w"
        tokens = root.xpath(groupe_words, namespaces=tei)
        nombre_mots = int(root.xpath("count(//tei:w)", namespaces=tei))
        nombre_pc = int(root.xpath("count(//tei:pc)", namespaces=tei))
        nombre_tokens = nombre_mots + nombre_pc
        fichier_lemmatise = temoin_tokenise
        for mot in tokens:
            nombre_mots_precedents = int(mot.xpath("count(preceding::tei:w) + 1", namespaces=tei))
            nombre_ponctuation_precedente = int(
                mot.xpath("count(preceding::tei:pc) + 1", namespaces=tei))
            position_absolue_element = nombre_mots_precedents + nombre_ponctuation_precedente  # attention à
            # enlever 1 quand on cherche dans la liste
            liste_correcte = maliste[position_absolue_element - 2]
            cas = liste_correcte[1]
            mode = liste_correcte[2]
            number = liste_correcte[3]
            person = liste_correcte[4]
            temps = liste_correcte[5]
            lemme = liste_correcte[6]
            pos = liste_correcte[7]
            # on nettoie la morphologie pour supprimer les entrées vides
            morph = "CAS=%s|MODE=%s|NOMB.=%s|PERS.=%s|TEMPS=%s" % (cas, mode, number, person, temps)
            morph = re.sub("((?!\|).)*?_(?=\|)", "", morph)  # on supprime les traits non renseignés du milieu
            morph = re.sub("^\|*", "", morph)  # on supprime les pipes qui commencent la valeur
            morph = re.sub("(\|)+", "|", morph)  # on supprime les pipes suivis
            morph = re.sub("\|((?!\|).)*?_$", "", morph)  # on supprime les traits non renseignés de fin
            morph = re.sub("(?!\|).*_(?!\|)", "", morph)  # on supprime les traits non renseignés uniques
            #
            mot.set("lemma", lemme)
            mot.set("pos", pos)
            if morph:
                mot.set("morph", morph)

    elif langue == "lat":  # 1) on transforme le fichier txt tokenise en txt_to_liste()
        nom_fichier_sans_rien = fichier.split(".")[0]
        ma_liste_tokenisee = txt_to_liste_latinclassique(
            "temoins_tokenises_regularises/txt/%s.txt" % nom_fichier_sans_rien)
        lemmatizer = BackoffLatinLemmatizer()
        ma_liste_lemmatisee = lemmatizer.lemmatize(ma_liste_tokenisee)
        parser = etree.XMLParser(load_dtd=True,
                                 resolve_entities=True)  # inutile car les entités ont déjà été résolues
        # auparavant normalement, mais au cas où.
        temoin_tokenise = "temoins_tokenises_regularises/" + fichier
        f = etree.parse(temoin_tokenise, parser=parser)
        root = f.getroot()
        tei = {'tei': 'http://www.tei-c.org/ns/1.0'}
        groupe_words = "//tei:w"
        tokens = root.xpath(groupe_words, namespaces=tei)
        nombre_mots = int(root.xpath("count(//tei:w)", namespaces=tei))
        nombre_pc = int(root.xpath("count(//tei:pc)", namespaces=tei))
        nombre_tokens = nombre_mots + nombre_pc
        fichier_lemmatise = temoin_tokenise
        for mot in tokens:
            nombre_mots_precedents = int(mot.xpath("count(preceding::tei:w) + 1", namespaces=tei))
            nombre_ponctuation_precedente = int(
                mot.xpath("count(preceding::tei:pc) + 1", namespaces=tei))
            position_absolue_element = nombre_mots_precedents + nombre_ponctuation_precedente  # attention à
            # enlever 1 quand on cherche dans la liste
            liste_correcte = ma_liste_lemmatisee[position_absolue_element - 2]
            lemme = liste_correcte[1]
            mot.set("lemma", lemme)

    sortie_xml = open(fichier_lemmatise, "w+")
    a_ecrire = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True).decode(
        'utf8')
    sortie_xml.write(str(a_ecrire))
    sortie_xml.close()
    print("%s ✓" % fichier)


def txt_to_liste(filename):
    """
    Transforme le fichier txt produit par Freeling ou pie en liste de listes pour processage ultérieur.
    :param filename: le nom du fichier txt à transformer
    :return: une liste de listes: pour chaque forme, les différentes analyses
    """
    maliste = []
    fichier = open(filename, 'r')
    for line in fichier.readlines():
        if not re.match(r'^\s*$',
                        line):  # https://stackoverflow.com/a/3711884 élimination des lignes vides (séparateur de phrase)
            resultat = re.split(r'\s+', line)
            maliste.append(resultat)
    return maliste


def txt_to_liste_latinclassique(filename):
    """
    Transforme le fichier txt produit par Freeling ou pie en liste de listes pour processage ultérieur.
    :param filename: le nom du fichier txt à transformer
    :return: une liste de listes: pour chaque forme, les différentes analyses
    """
    maliste = []
    fichier = open(filename, 'r')
    for line in fichier.readlines():
        if not re.match(r'^\s*$',
                        line):  # https://stackoverflow.com/a/3711884 élimination des lignes vides (séparateur de phrase)
            resultat = re.split(r'\s+', line)
            maliste.append(resultat[0])
    return maliste


def production_doc_final(nom_fichier, moteur_xslt):
    """
    Production du document final: on compare les fichiers régularisés et non régularisés pour remettre
    les annotations dans le fichier non régularisé.
    Ici il y a un problème: que veut dire régularisation ? reprendre tout ça.
    :param fichier: le nom du fichier sans sa base
    :return: le fichier final lemmatisé
    """
    temoin_tokenise = "temoins_tokenises/%s" % nom_fichier
    print("Injection dans le XML...")
    param = "nom_fichier=" + nom_fichier
    commande = "java -jar %s -xi:on %s xsl/lemmatisation/doc_final.xsl %s" % (moteur_xslt, temoin_tokenise, param)
    subprocess.run(commande.split())
    
    print("Tokénisation et régularisation du fichier ✓\nLemmatisation du fichier ✓\nInjection dans le XML... ✓")


def clear():
    os.system('clear')


if __name__ == "__main__":
    fichier = sys.argv[1]
    argument = sys.argv[2]
    principal(fichier, argument)
