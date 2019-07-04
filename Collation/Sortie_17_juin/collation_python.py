import sys
from collatex import *
import json
import dicttoxml
collation=Collation()

fichier_a_collationer=sys.argv[1]

entree_json0 = open(fichier_a_collationer, "r") # ouvrir le fichier en mode lecture et le mettre dans une variable
entree_json1 = entree_json0.read()
entree_json0.close()

# Export au format TEI (plus lisible)
print("Collation au format TEI")
resultat_tei= collate(json.loads(entree_json1), output="tei")
sortie_tei = open("apparat_collatex.xml", "w")
sortie_tei.write(resultat_tei)
sortie_tei.close()

# Export au format HTML2 (voir les résultats) [ne marche pas]
#print("Collation au format HTML")
#resultat_html= collate(json.loads(entree_json1), output="html")
#sortie_html = open("apparat_collatex.html", "w")
#sortie_html.write(resultat_html)
#sortie_html.close()

# Export au format JSON (permet de conserver les xml:id)
print("Collation au format JSON")
resultat_json= collate(json.loads(entree_json1), output="json")
sortie_json = open("apparat_collatex.json", "w")
sortie_json.write(resultat_json)
sortie_json.close()



