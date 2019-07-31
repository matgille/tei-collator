from lxml import etree
import sys
import json

# Création de l'apparat: proof of concept


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


fichier_a_apparater=sys.argv[1]

with open(fichier_a_apparater, 'r+') as fichier:
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
            lecon=str(key)
            xml_id = dict_sortie.get(key)[0]
            temoin = dict_sortie.get(key)[1]
            rdg = etree.SubElement(app, "rdg")
            rdg.set("wit", temoin)
            rdg.set("{http://www.w3.org/XML/1998/namespace}id", xml_id)
            rdg.text=lecon
    
    # L'apparat est produit. Écriture du fichier xml            
    print(etree.tostring(root))
    sortie_xml=open("apparat_collatex.xml", "w+")
    string = etree.tostring(root, pretty_print=True,encoding='utf-8', xml_declaration=True).decode('utf8')
    sortie_xml.write(str(string))
    sortie_xml.close()
    
   
    
