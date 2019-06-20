#!bin/sh

oxygen="/home/gille-levenson/bin/saxon9ee.jar"

# Nettoyage et tokénisation du corpus parallélisé
## !! Ne marche pas, la fonction de création d'identifiants uniques (java:java.util.UUID) suppose d'utiliser la GUI d'oxygen
#echo "Nettoyage et tokénisation du corpus"
#fichier_origine="/home/gille-levenson/Bureau/These/Edition/Edition_Pseudojeriz/Dedans/XML/corpus/corpus.xml"
#java -jar "$oxygen" -o:temoins/groupe.xml $fichier_origine ~/Bureau/These/Edition/Edition_Pseudojeriz/Collation/Sortie_17_juin/xsl/tokenisation.xsl
## Nettoyage et tokénisation du corpus parallélisé


# Scission du corpus en dossiers de chapitres
echo "Création de dossiers par chapitre"
java -jar $oxygen -o:tmp/tmp.tmp temoins/groupe.xml ~/Bureau/These/Edition/Edition_Pseudojeriz/Collation/Sortie_17_juin/xsl/scission_chapitres.xsl
# Scission du corpus en dossiers de chapitres

# Création des fichiers d'apparat
echo "collation automatique"
for i in chapitres/chapitre*/collation.xml; do
chemin=$(dirname "${i}")
echo "transformation de $chemin/$i"
java -jar $oxygen -o:$chemin/collation.json $i ~/Bureau/These/Edition/Edition_Pseudojeriz/Collation/Sortie_17_juin/xsl/transformation_json.xsl
echo "java -jar ~/bin/saxon9pe.jar -o:$chemin/collation.json $i ~/Bureau/These/Edition/Edition_Pseudojeriz/Collation/Sortie_17_juin/xsl/transformation_json.xsl"
cd $chemin
echo "cd $chemin"
echo "python3 ../../collation_python.py collation.json"
python3 ../../collation_python.py collation.json
cd ../..
echo "collation !"; done
# Création des fichiers d'apparat

