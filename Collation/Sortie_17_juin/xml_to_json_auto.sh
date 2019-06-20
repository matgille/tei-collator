#!bin/sh

oxygen="/opt/Oxygen\_XML\_Editor\_20/frameworks/dita/DITA-OT2.x/lib/saxon-9.1.0.8.jar"

# Nettoyage et tokénisation du corpus parallélisé
echo "Nettoyage et tokénisation du corpus"
fichier_origine="/home/gille-levenson/Bureau/These/Edition/Edition_Pseudojeriz/Dedans/XML/corpus/corpus.xml"
java -jar $oxygen -o:temoins/groupe.xml $fichier_origine ~/Bureau/These/Edition/Edition_Pseudojeriz/Collation/Sortie_17_juin/xsl/tokenisation.xsl
# Nettoyage et tokénisation du corpus parallélisé


 Scission du corpus en dossiers de chapitres
 !! Ne marche pas, car on ne peut appeler java dans un xsl sans la version premium de saxon, qu'on ne peut utiliser hors de la GUI d'Oxygen. 
echo "Création de dossiers par chapitre"
java -jar $oxygen -o:tmp/tmp.tmp $fichier_origine ~/Bureau/These/Edition/Edition_Pseudojeriz/Collation/Sortie_17_juin/xsl/scission_chapitres.xsl
 Scission du corpus en dossiers de chapitres

# Création des fichiers d'apparat
echo "collation automatique"
for i in chapitres/chapitre*/collation.xml; do
chemin=$(dirname "${i}")
echo "transformation de $chemin/$i"
java -jar $oxygen -o:$chemin/collation.json $i ~/Bureau/These/Edition/Edition_Pseudojeriz/Collation/Sortie_17_juin/xsl/transformation_json.xsl
echo "java -jar ~/bin/saxon9pe.jar -o:$chemin/collation.json $i ~/Bureau/These/Edition/Edition_Pseudojeriz/Collation/Sortie_17_juin/xsl/transformation_json.xsl"
cd $chemin
echo "cd $chemin"
python3 ../../collation_python.py collation.json
cd ../..
echo "collation !"; done
# Création des fichiers d'apparat

