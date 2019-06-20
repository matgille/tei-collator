#!bin/sh



echo "Transformation des fichiers json en fichiers xml"

# Appel du script transformation_xml_json.py
for i in chapitres/chapitre*/apparat_collatex.json; do
chemin=$(dirname "${i}")
echo "transformation de $chemin/$i"
cd $chemin
echo "python3 ../../transformation_xml_json.py $i"
python3 ../../transformation_xml_json.py $i
cd ../..
echo "Transformation réussie"; done
# Appel du script transformation_xml_json.py

