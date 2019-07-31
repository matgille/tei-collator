import sys
from lxml import etree
import sys
import json
import subprocess
from collatex import *
from halo import Halo
import json
import dicttoxml




def apparat(fichier_entree):

# Création de l'apparat au format xml. 


# Étape 1: pour chaque lieu variant

# Faire une liste de dictionnaires, doit être au format JSON
# Chaque item du dictionnaire d'entrée doit respecter la forme suivante.
# Les clés doivent correspondre à la position des items.
#liste_dict = [{
#"0" : ["", "", "Phil_J"], 
#"1" : ["a0a6f5ec2-a98u9ds98yh", "Ca iiii", "Mad_G"],
#"2" : ["a0a9f5dsc2-a9sdnjxcznk", "Ca iiii", "Phil_Z"]
#}, {
#"0" : ["a4d2587a-a98u98yh", "do", "Phil_J"], 
#"1" : ["a0a6f5ec2-a98u9ds98yh", "do", "Mad_G"],
#"2" : ["a0a9f5dsc2-a9sdnjxcznk", "donde", "Phil_Z"], 
#"3" : ["prout-cacau98yh", "onde", "Phil_K"], 
#"4" : ["a4sde2587a-a9fu98yh", "donde", "Phil_Ñ"], 
#"5" : ["a4sd88888e2587a-a999999h", "do", "Phil_M"]
#}, {
#"0" : ["a4d2587a-a98u98yh", "muesstra", "Phil_J"], 
#"1" : ["a0a6f5ec2-a98u9ds98yh", "muestra", "Mad_G"],
#"2" : ["a0a9f5dsc2-a9sdnjxcznk", "prueua", "Phil_Z"]
#}]


    with open(fichier_entree, 'r+') as fichier:
        liste_dict = json.load(fichier)
        root = etree.Element("root")
        for dic in liste_dict: 
            dict_sortie = {}
            liste_entree = []


            # Étape 1: déterminer si il y a variation ou pas
            for key in dic:
                id_token = dic.get(key)[0]
                lecon_depart = dic.get(key)[1]
                temoin = dic.get(key)[2]
                liste_entree.append(lecon_depart)
    
            result = False;
            if len(liste_entree) > 0 :
            # Comparer chaque lecon à la première
                result = all(elem == liste_entree[0] for elem in liste_entree)

                # Première étape. Si tous les lieux variants sont égaux 
                # entre eux,ne pas créer d'apparat mais imprimer 
                # directement le texte    
                if result :
                    myElement = root.find('app')
                    if myElement is None:
                        root.text=lecon_depart
                    else:
                        # root.xpath va sortir une liste: il faut aller chercher les items 
                        # individuels de cette liste, même si il n'y en n'a qu'un
                        dernier_app = root.xpath('app[last()]')
                        for i in dernier_app:
                            i.tail=lecon_depart
    
            
            # C'est ici que l'on pourrait faire intervenir le lemmatiseur 
            # et le POS, pour créer des apparats de diverses sortes 
            # (linguistiques, etc). 
            
            
                else:# Si les leçons sont différentes: étape 2
                    app = etree.SubElement(root, "app")                
                
        
                    # La liste créée va permettre de vérifier si une leçon identique
                    # a déjà été traitée auparavant. On la réinitialise à nouveau
                    # car on l'a déjà utilisée pour vérifier l'égalité entre leçons
                    liste_entree = []
                    for key in dic:
                        id_token = dic.get(key)[0]
                        lecon_depart = dic.get(key)[1]
                        temoin = dic.get(key)[2]
   
                        # Si le lieu variant n'existe pas dans la liste, 
                        # créer un item de dictionnaire
                        if lecon_depart not in liste_entree:
                            dict_sortie[lecon_depart] = [id_token,temoin]
                            # Ajouter le lieu variant dans la liste
                            liste_entree.append(lecon_depart)    
    
                        # Si le lieu variant a déjà été rencontré
                        else:
                            # Trouver la position de la dernière occurrence de cette  
                            # leçon (= la première), dans la liste et qui 
                            # correspond à la clé du dictionnaire d'entrée
                            position = len(liste_entree) - 1 - liste_entree[::-1].index(lecon_depart)
                            # On actualise les valeurs
                            token1 = dict_sortie.get(lecon_depart)[0]
                            temoin1 = dict_sortie.get(lecon_depart)[1]
                            token2 = token1 + "_" + id_token
                            temoin2 = temoin1 + " " + temoin
                            dict_sortie[lecon_depart] = [token2,temoin2]
                            # Mise à jour la liste
                            liste_entree.append(lecon_depart)



            # Une fois le dictionnaire de sortie produit, le transformer en XML.
            for key in dict_sortie:
                lecon = str(key)
                xml_id = dict_sortie.get(key)[0]
                temoin = dict_sortie.get(key)[1]
                rdg = etree.SubElement(app, "rdg")
                rdg.set("wit", temoin)
                rdg.set("{http://www.w3.org/XML/1998/namespace}id", xml_id)
                rdg.text=lecon
    
        # L'apparat est produit. Écriture du fichier xml            
        # print(etree.tostring(root))
        sortie_xml = open("apparat_collatex.xml", "w+")
        string = etree.tostring(root, pretty_print=True,encoding='utf-8', xml_declaration=True).decode('utf8')
        sortie_xml.write(str(string))
        sortie_xml.close()



def main(fichier_a_collationer):

# Exception: si le fichier indiqué n'est pas au format JSON, 
# demander un nouveau fichier.
    try:
        assert fichier_a_collationer.endswith(".json")
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


    with Halo(text = 'Création des apparats', spinner='dots'):
        # Étape suivante: transformer le JSON en xml. Pour cela on peut utiliser dict2xml. 
        sortie_xml = open("alignement_collatex.xml", "w+")
        fichier_json_a_xmliser=open('alignement_collatex.json').read()
        obj = json.loads(fichier_json_a_xmliser)
        vers_xml = dicttoxml.dicttoxml(obj)
        vers_xml = vers_xml.decode("utf-8") 
        sortie_xml.write(vers_xml)
        sortie_xml.close()
        # Regroupement des lieux variants (témoin A puis témoin B puis témoin C 
        # > lieu variant 1: A, B, C ; lieu variant 2: A, B, C)
        subprocess.run(["java","-jar", "../../Saxon-HE-9.8.0-14.jar", "-o:aligne_regroupe.xml", "alignement_collatex.xml", "../../xsl/post_alignement/regroupement.xsl"])
        # C'est à ce niveau que l'étape de correction devrait avoir lieu. Y réfléchir.    
        # Création de l'apparat: transformation de aligne_regroupe.xml en JSON
        subprocess.run(["java","-jar", "../../Saxon-HE-9.8.0-14.jar", "-o:apparat_final.json", "aligne_regroupe.xml", "../../xsl/post_alignement/creation_apparat.xsl"])
        # Création de l'apparat: suppression de la redondance, identification des lieux variants, 
        # regroupement des lemmes
    
        apparat("apparat_final.json")
        #subprocess.run(["python3", "../../python/apparat.py", "apparat_final.json"])
    print("Création des apparats ✓")


    # Réinjection des apparats. Ne marche pas pour l'instant.
    with Halo(text = 'Injection des apparats dans chaque transcription individuelle', spinner='dots'):
        subprocess.run(["java","-jar", "../../Saxon-HE-9.8.0-14.jar", "-o:sortie_finale.xml", "juxtaposition.xml", "../../xsl/post_alignement/injection_apparats.xsl", "chapitre=3"])
    print("Injection des apparats dans chaque transcription individuelle ✓")

    # Création du tableau d'alignement pour visualisation
    with Halo(text = 'Création du tableau d\'alignement', spinner='dots'):
        subprocess.run(["java","-jar", "../../Saxon-HE-9.8.0-14.jar", "-o:tableau_alignement.html", "aligne_regroupe.xml", "../../xsl/post_alignement/tableau_alignement.xsl"])
    print("Création du tableau d\'alignement ✓")