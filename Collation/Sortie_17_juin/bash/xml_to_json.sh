#!bin/sh

oxygen="../Saxon-HE-9.8.0-14.jar"

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
echo "0 - Scission du corpus, création de dossiers et de fichiers par chapitre"
java -jar $oxygen -o:../tmp/tmp.tmp ../temoins/groupe.xml ../xsl/pre_collation/scission_chapitres.xsl
# Scission du corpus en dossiers de chapitres

# Création des fichiers d'apparat
echo "I - collation automatique"
for i in ../chapitres/chapitre*/collation.xml; do
chemin=$(dirname "${i}")
echo "I.1 transformation en json"
java -jar $oxygen -o:$chemin/collation.json $i ../xsl/pre_collation/transformation_json.xsl

echo "I.2 collation du chapitre $chemin"
cd $chemin
echo "python3 ../../python/collation_python.py collation.json"
python3 ../../python/collation_python.py collation.json
cd ../..; 

echo "II - production de l'apparat"
echo "II.1 Premier alignement"  
java -jar $oxygen -o:$chemin/apparat_final1.xml $chemin/apparat_final.xml ../xsl/post_collation/apparat0.xsl

#AF echo "II.2 Suppression de la redondance"
#AF java -jar $oxygen -o:$chemin/apparat_final.xml $chemin/apparat_final1.xml ../xsl/post_collation/apparat1.xsl

done



else    
        exit 0

fi
