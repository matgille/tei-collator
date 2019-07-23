#!bin/sh

oxygen="/home/mgl/Desktop/these/hyperregimiento-de-los-principes/Collation/Sortie_17_juin/Saxon-HE-9.8.0-14.jar"

# Nettoyage et tokénisation du corpus parallélisé
## !! Ne marche pas, la fonction de création d'identifiants uniques (java:java.util.UUID) suppose d'utiliser la GUI d'oxygen
#echo "Nettoyage et tokénisation du corpus"
#fichier_origine="/home/gille-levenson/Bureau/These/Edition/Edition_Pseudojeriz/Dedans/XML/corpus/corpus.xml"
#java -jar "$oxygen" -o:temoins/groupe.xml $fichier_origine ~/Bureau/These/Edition/Edition_Pseudojeriz/Collation/Sortie_17_juin/xsl/tokenisation.xsl
## Nettoyage et tokénisation du corpus parallélisé

# Message d'avertissement: il faut faire la tokénisation manuellement

echo -n "Il n'est pas possible d'automatiser la tokénisation: il faut le faire depuis oxygen. Voulez-vous continuer ? [o/n]\n"
read reponse

if [ $reponse = "o" ]
then
# Scission du corpus en dossiers de chapitres
echo "Création de dossiers par chapitre"
java -jar $oxygen -o:tmp/tmp.tmp temoins/groupe.xml ~/Bureau/These/Edition/Edition_Pseudojeriz/Collation/Sortie_17_juin/xsl/scission_chapitres.xsl
# Scission du corpus en dossiers de chapitres

# Création des fichiers d'apparat
echo "collation automatique"
for i in chapitres/chapitre*/collation.xml; do
chemin=$(dirname "${i}")
echo "transformation en json"
java -jar $oxygen -o:$chemin/collation.json $i ~/Bureau/These/Edition/Edition_Pseudojeriz/Collation/Sortie_17_juin/xsl/transformation_json.xsl

echo "collation du chapitre $chemin"
cd $chemin
echo "python3 ../../collation_python.py collation.json"
python3 ../../collation_python.py collation.json
cd ../..; 
done
#Création des fichiers d'apparat


else
        exit 0

fi
