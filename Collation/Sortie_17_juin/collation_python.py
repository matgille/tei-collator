from collatex import *
import json
collation=Collation()
#with open('essai1.json') as json_file:  
#	data = json.load(json_file)
#	data2 = json.dumps(data)
#	json_input = '"""' + str(data2) + '"""'
#	print(json_input)
json_input = """ fichier json """ # trouver un moyen d'importer le fichier plutôt que de le copier. 



resultat= collate(json.loads(json_input), output="tei")
print(resultat)

# trouver un moyen d'enregistrer le fichier automatiquement plutôt que de l'imprimer
