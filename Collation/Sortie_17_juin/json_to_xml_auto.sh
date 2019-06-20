#!bin/sh



echo "Transformation des fichiers json en fichiers xml"

# Appel du script transformation_xml_json.py
for i in chapitres/chapitre*/apparat_collatex.json; do
chemin=$(dirname "${i}")
nom_fichier=$(basename -- "$i")
echo "transformation de $chemin/$i"
echo "cd $chemin"
cd $chemin
echo "python3 ../../transformation_xml_json.py $nom_fichier"
python3 ../../transformation_xml_json.py $nom_fichier
cd ../..
echo "Transformation réussie"; done
# Appel du script transformation_xml_json.py

