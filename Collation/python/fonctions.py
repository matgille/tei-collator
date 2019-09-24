import sys
from lxml import etree
import os
import json
import subprocess
from collatex import *
from halo import Halo
import dicttoxml
import random
import unicodedata
import string

def generateur_lettre_initiale(size=1, chars = string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))

def generateur_id(size=4, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return generateur_lettre_initiale() + ''.join(random.choice(chars) for _ in range(size))


def ajout_xmlid(fichier_entree, fichier_sortie):
    tei = {'tei':'http://www.tei-c.org/ns/1.0'}
    f = etree.parse(fichier_entree)
    root = f.getroot()
    tokens = root.xpath("//tei:w", namespaces=tei)
    for w in tokens:
        w.set("{http://www.w3.org/XML/1998/namespace}id", generateur_id())
    sortie_xml = open(fichier_sortie, "w+")
    string = etree.tostring(root, pretty_print=True,encoding='utf-8', xml_declaration=True).decode('utf8')
    sortie_xml.write(str(string))
    sortie_xml.close()           

# Attention à l'option -xi:(on|off) de saxon pour activer Xinclude le cas échéant 
def tokenisation(saxon):
    with Halo(text = 'Tokénisation du corpus parallélisé.', spinner='dots'):
        subprocess.run(["java","-jar", saxon, "-xi:on", "../../Dedans/XML/corpus/corpus.xml", "../xsl/pre_alignement/tokenisation.xsl"])
        ajout_xmlid("../temoins/groupe.xml", "../temoins/groupe-xmlise.xml")
    print("Tokénisation du corpus ✓")                

def scission_corpus(saxon):
    with Halo(text = 'Scission du corpus, création de dossiers et de fichiers par chapitre', spinner='dots'):
        subprocess.run(["java","-jar", saxon, "-o:../tmp/tmp.tmp", "../temoins/groupe-xmlise.xml", "../xsl/pre_alignement/scission_chapitres.xsl"])
    print("Scission du corpus, création de dossiers et de fichiers par chapitre ✓ \n")


# Étape avant la collation: transformation en json selon la structure voulue par CollateX.
# Voir https://collatex.net/doc/#json-input
def transformation_json(saxon, output_fichier_json, input_fichier_xml):
    with Halo(text = 'Transformation en json', spinner='dots'):
        subprocess.run(["java","-jar", saxon, output_fichier_json, input_fichier_xml, "xsl/pre_alignement/transformation_json.xsl"])
    print("Transformation en json pour alignement ✓")  


def alignement(fichier_a_collationer, saxon, chemin_xsl):
    """
        Alignement CollateX, puis regroupement des leçons communes en lieux variants
    """

    try:
        assert fichier_a_collationer.endswiths(".json")
    except:
        while not fichier_a_collationer.endswith('.json'):
            fichier_a_collationer = input("Le fichier indiqué n'est pas un fichier JSON. Veuillez indiquer un fichier. \n")



    entree_json0 = open(fichier_a_collationer, "r") # ouvrir le fichier en mode lecture et le mettre dans une variable
    entree_json1 = entree_json0.read()
    entree_json0.close()

    # Export au format TEI (plus lisible)
    def collation_tei():
        with Halo(text = 'Collation au format TEI - CollateX', spinner='dots'):
            resultat_tei = collate(json.loads(entree_json1), output="tei")
            sortie_tei = open("apparat_collatex_tei.xml", "w")
            sortie_tei.write(resultat_tei)
            sortie_tei.close()


    # Export au format JSON (permet de conserver les xml:id)
    def alignement_json():
        with Halo(text = 'Alignement CollateX', spinner='dots'):
            resultat_json = collate(json.loads(entree_json1), output="json")
            sortie_json = open("alignement_collatex.json", "w")
            sortie_json.write(resultat_json)
            sortie_json.close()
        print("Alignement CollateX ✓")
    alignement_json()
    
    
    
    # Les résultats de la collation ne sont pas directement visibles: on a la liste A puis la liste B: il faut transformer le tout pour avoir un réel alignement. Voir http://collatex.obdurodon.org/xml-json-conversion.xhtml pour la structure du résultat. 
    # Le résultat de cette dernière transformation est une liste qui comprend elle-même une liste avec l'alignement. 

    # Création des apparats proprement dite: on compare les lieux variants et on réduit les app.
    with Halo(text = 'Création des apparats', spinner='dots'):
        # Étape suivante: transformer le JSON en xml. Pour cela on peut utiliser dict2xml. 
        sortie_xml = open("alignement_collatex.xml", "w+")
        fichier_json_a_xmliser=open('alignement_collatex.json').read()
        obj = json.loads(fichier_json_a_xmliser)
        vers_xml = dicttoxml.dicttoxml(obj)
        vers_xml = vers_xml.decode("utf-8") 
        sortie_xml.write(vers_xml)
        sortie_xml.close()
        
        chemin_regroupement = chemin_xsl + "xsl/post_alignement/regroupement.xsl"
        chemin_xsl_apparat = chemin_xsl + "xsl/post_alignement/creation_apparat.xsl"
        # Regroupement des lieux variants (témoin A puis témoin B puis témoin C 
        # > lieu variant 1: A, B, C ; lieu variant 2: A, B, C)
        subprocess.run(["java","-jar", saxon, "-o:aligne_regroupe.xml", "alignement_collatex.xml", chemin_regroupement])
        
        # C'est à ce niveau que l'étape de correction devrait avoir lieu. Y réfléchir.    
        # Création de l'apparat: transformation de aligne_regroupe.xml en JSON
        subprocess.run(["java","-jar", saxon, "-o:apparat_final.json", "aligne_regroupe.xml", chemin_xsl_apparat])
        # Création de l'apparat: suppression de la redondance, identification des lieux variants, 
        # regroupement des lemmes



# Cette fonction concentre toutes les manipulations à effectuer pour annuler
# les phénomènes graphiques surtout qui sont le fruit de l'édition et non 
# pas le reflet du texte. 
# Pour l'instant: annulation de l'accentuation, de la segmentation, de la casse


def remplacements_en_chaîne(texte):
    return texte.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace(" ", "")

def annulation_phenomenes(chaine_a_transformer):
    return remplacements_en_chaîne(chaine_a_transformer).lower()

def apparat_final(fichier_entree):
    """
        Cette fonction permet de passer de la table d'alignement à 
        l'apparat proprement dit, avec création d'apparat s'il y a
        variation, et regroupement des leçons identiques. 
        Elle fonctionne avec une lsite de dictionnaires au format JSON, 
        chaque dictionnaire représentant un lieu variant. 
        
         liste_dict = 
            [{
                "0" : ["", "", "Phil_J"], 
                "1" : ["a0a6f5ec2-a98u9ds98yh", "Ca iiii", "Mad_G"],
                "2" : ["a0a9f5dsc2-a9sdnjxcznk", "Ca iiii", "Phil_Z"]
                }, {
                "0" : ["a4d2587a-a98u98yh", "do", "Phil_J"], 
                "1" : ["a0a6f5ec2-a98u9ds98yh", "do", "Mad_G"],
                "2" : ["a0a9f5dsc2-a9sdnjxcznk", "donde", "Phil_Z"], 
                "3" : ["prout-cacau98yh", "onde", "Phil_K"], 
                "4" : ["a4sde2587a-a9fu98yh", "donde", "Phil_Ñ"], 
                "5" : ["a4sd88888e2587a-a999999h", "do", "Phil_M"]
                }, {
                "0" : ["a4d2587a-a98u98yh", "muesstra", "Phil_J"], 
                "1" : ["a0a6f5ec2-a98u9ds98yh", "muestra", "Mad_G"],
                "2" : ["a0a9f5dsc2-a9sdnjxcznk", "prueua", "Phil_Z"]
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
            informations d'apparat. On va créer une liste liste_entree qui va nous permettre de comparer chaque chaîne
            aux chaînes précédentes. 
            
            *Pour chaque item* du dictionnaire d'entrée, on vérifie que la chaîne, en position 1, n'est pas déjà présente
            dans la liste liste_entree. 
                - Si elle n'est pas présente, on l'ajoute à la liste, et on crée un item
                dans le dictionnaire de sortie dict_sortie. Cet item est organisé de la façon suivante:
                    "lieu_variant1": ["témoin(s)", "id_token(s)"]
                - Si la chaîne existe déjà dans la liste liste_entree, c'est qu'elle est aussi dans le 
                dictionnaire de sortie: on va donc modifier la valeur de l'item dont la clé est cette chaîne, 
                en ajoutant le témoin correspondant ainsi que les identifiants de token.
        
            L'idée est aussi de pouvoir neutraliser certains phénomènes qui ne peuvent être comparés, comme
            l'accentuation, la casse, ou la segmentation, car pour mon projet elles sont de mon fait et ce 
            ne sont pas des phénomènes propres aux témoins. Mis en pause pour le moment car cela pose des 
            problèmes assez importants. 
            
        3 ) Une fois le dictionnaire créé, on le transforme en xml en suivant la grammaire de la TEI pour les apparat. 
            Il reste encore quelques points 
            problématiques (les espaces de noms sont assez mal gérés en particulier), mais 
            cela marche assez bien.
        4 ) La dernière étape est la réinitialisation de la liste liste_entree et du dictionnaire dict_sortie,
            qui est en réalité en début de boucle. 
            
            
        Pour l'instant, n'est traité que l'xml:id, mais on peut ajouter d'autres fonctions
        
           
    """

    with open(fichier_entree, 'r+') as fichier:
        liste_dict = json.load(fichier)
        ns_tei = "http://www.tei-c.org/ns/1.0"
        nsmap = {'tei': ns_tei}
        root = etree.Element("root", nsmap=nsmap)
        for dic in liste_dict: 
            dict_sortie = {}
            liste_entree = []
            


            # Étape 1: déterminer si il y a variation ou pas
            for key in dic:
                id_token = dic.get(key)[0]
                lecon_depart = dic.get(key)[1]
                temoin = dic.get(key)[2]
                #lecon_depart_neutralisee = annulation_phenomenes(lecon_depart)
                #liste_entree.append(lecon_depart_neutralisee)
                liste_entree.append(lecon_depart)
    
            result = False;
            if len(liste_entree) > 0 :
            # Comparer chaque lecon à la première
                result = all(elem == liste_entree[0] for elem in liste_entree)

                # Première étape. Si tous les lieux variants sont égaux 
                # entre eux,ne pas créer d'apparat mais imprimer 
                # directement le texte    
                if result :
                    myElement = root.find('tei:app', nsmap)
                    if myElement is None:
                        root.text=lecon_depart
                    else:
                        # root.xpath va sortir une liste: il faut aller chercher les items 
                        # individuels de cette liste, même si il n'y en n'a qu'un
                        dernier_app = root.xpath('tei:app[last()]', namespaces=nsmap)
                        for i in dernier_app:
                            i.tail=lecon_depart
                
            # C'est ici que l'on pourrait faire intervenir le lemmatiseur 
            # et le POS, pour créer typer les apparats voire en créer de diverses sortes 
            # (linguistiques, etc): 
			# - si tous les tokens ont le même lemme et le même POS, créer un type (graphique) 
			# - si les tokens ont un lemme distinct ou le même lemme et un POS distint (= changement de genre / de
			# nombre de l'objet référent), typer "variante"
                        
                else:# Si les leçons sont différentes: étape 2
                    
                    # app = etree.SubElement(root, "app", nsmap=nsmap)
                    app = etree.SubElement(root, "{%s}app" % ns_tei)
                    #  https://stackoverflow.com/questions/7703018/how-to-write-namespaced-element-attributes-with-lxml               
                        
                    # La liste créée va permettre de vérifier si une leçon identique
                    # a déjà été traitée auparavant. On la réinitialise
                    # car on l'a déjà utilisée pour vérifier l'égalité entre leçons
					# dans le lieu variant précédent
                    liste_entree = []
                    for key in dic:
                        id_token = dic.get(key)[0]
                        lecon_depart = dic.get(key)[1]
                        temoin = dic.get(key)[2]
                        #lecon_depart_neutralisee = annulation_phenomenes(lecon_depart)
                        # Si le lieu variant n'existe pas dans la liste, 
                        # créer un item de dictionnaire
                        
                        if lecon_depart not in liste_entree:
                        #if lecon_depart_neutralisee not in liste_entree:
                            dict_sortie[lecon_depart] = [id_token,temoin]
                            # Ajouter le lieu variant dans la liste.
                            liste_entree.append(lecon_depart)
                            #liste_entree.append(lecon_depart_neutralisee) 
                            
                        # Si le lieu variant a déjà été rencontré
                        else:
                            #dict_comparaison = {}
                            #for item in dict_sortie:
                            #    dict_comparaison[annulation_phenomenes(item)] = item
                            #lecon_depart2 = dict_comparaison.get(lecon_depart_neutralisee)
                            temoin1 = dict_sortie.get(lecon_depart)[1]
                            token1 = dict_sortie.get(lecon_depart)[0]
                            print("token1" + token1)
                            token2 = token1 + "_" + id_token
                            temoin2 = temoin1 + " " + temoin
                            dict_sortie[lecon_depart] = [token2,temoin2]
                            # Mise à jour la liste
                            # liste_entree.append(lecon_depart_neutralisee)
                            liste_entree.append(lecon_depart)


            # Une fois le dictionnaire de sortie produit, le transformer en XML.
            for key in dict_sortie:
                lecon = str(key)
                xml_id = dict_sortie.get(key)[0]
                temoin = dict_sortie.get(key)[1]
                # rdg = etree.SubElement(app, "rdg", nsmap=nsmap)
                rdg = etree.SubElement(app, "{%s}rdg" % ns_tei)
                rdg.set("wit", temoin)
                rdg.set("{http://www.w3.org/XML/1998/namespace}id", xml_id)
                rdg.text=lecon
    
        # L'apparat est produit. Écriture du fichier xml            
        # print(etree.tostring(root))
        sortie_xml = open("apparat_collatex.xml", "w+")
        string = etree.tostring(root, pretty_print=True,encoding='utf-8', xml_declaration=True).decode('utf8')
        sortie_xml.write(str(string))
        sortie_xml.close()




def injection(saxon, chemin, chapitre):
    chapitre = "chapitre="+ str(chapitre)
    chemin_injection = chemin + "xsl/post_alignement/injection_apparats.xsl"
    with Halo(text = 'Injection des apparats dans chaque transcription individuelle', spinner='dots'):
        subprocess.run(["java","-jar", saxon, "-o:sortie_finale.xml", "juxtaposition.xml", chemin_injection, chapitre])
    print("Injection des apparats dans chaque transcription individuelle ✓")
        
def tableau_alignement(saxon, chemin):
    chemin_xsl_apparat = chemin + "xsl/post_alignement/tableau_alignement.xsl"
    with Halo(text ='Création du tableau d\'alignement', spinner='dots'):
        subprocess.run(["java","-jar", saxon, "-o:tableau_alignement.html", "aligne_regroupe.xml", chemin_xsl_apparat])
    print("Création du tableau d\'alignement ✓")
        
def nettoyage():
    #with Halo(text = "Nettoyage du dossier", spinner='dots'):
        #os.remove("alignement_collatex.json") 
        #os.remove("alignement_collatex.xml") 
        #os.remove("apparat_final.json")
        #os.remove("sortie_finale.xml")
    print("Nettoyage du dossier ✓")
    
def transformation_latex(saxon,fichier_xml, chemin):
    fichier_tex = fichier_xml.split('.')[0] + ".tex"
    chemin_xsl_apparat = chemin + "xsl/post_alignement/conversion_latex.xsl"
    fichier_tex_sortie = "-o:" + fichier_tex
    print("Création des fichiers pdf ✓")
    subprocess.run(["java","-jar", saxon, fichier_tex_sortie, fichier_xml, chemin_xsl_apparat])
    subprocess.run(["pdflatex", fichier_tex])
    subprocess.run(["pdflatex", fichier_tex])


def concatenation_pdf():
	with Halo(text ='Création d\'un fichier unique d\'apparat ✓', spinner='dots'):
		subprocess.run(["pdftk","chapitres/chapitre*/*.pdf", "output", "III_3_apparat.pdf"])
	print("Création d'un fichier unique d'apparat ✓")




