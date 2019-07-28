#!bin/sh
# Script à lancer depuis le répertoire bash. 
oxygen="Saxon-HE-9.8.0-14.jar"

# Nettoyage et tokénisation du corpus parallélisé
## !! Ne marche pas, la fonction de création d'identifiants uniques (java:java.util.UUID) suppose d'utiliser la GUI d'oxygen, ou il faut acheter une licence de saxon
#echo "Nettoyage et tokénisation du corpus"
#fichier_origine="/home/gille-levenson/Bureau/These/Edition/Edition_Pseudojeriz/Dedans/XML/corpus/corpus.xml"
#java -jar "$oxygen" -o:temoins/groupe.xml $fichier_origine ../xsl/tokenisation.xsl
## Nettoyage et tokénisation du corpus parallélisé


echo -n "Il n'est pas possible d'automatiser la tokénisation sans licence saxon indépendante: il faut le faire depuis oxygen. La feuille de transformation à utiliser est tokenisation.xsl"
echo "Voulez-vous continuer ? [o/n]\n"
read reponse


if [ $reponse = "o" ]
then
# Scission du corpus en dossiers de chapitres
#echo "0 - Scission du corpus, création de dossiers et de fichiers par chapitre"
#java -jar ../$oxygen -o:../tmp/tmp.tmp ../temoins/groupe.xml ../xsl/pre_alignement/scission_chapitres.xsl


# Création des fichiers d'apparat
echo "I - collation automatique"
cd ..
for i in chapitres/chapitre*/juxtaposition.xml; do
chemin=$(dirname "${i}")
echo "\nI.1 transformation en json"
java -jar $oxygen -o:$chemin/juxtaposition.json $i xsl/pre_alignement/transformation_json.xsl

echo "\nI.2 collation du chapitre $chemin"
cd $chemin
echo "python3 ../../python/collation_python.py juxtaposition.json"
python3 ../../python/collation_python.py juxtaposition.json;
echo "Nettoyage du dossier\n\n"
rm juxtaposition.json
rm alignement_collatex.json
cd ../../; 


done



else    
        exit 0

fi
