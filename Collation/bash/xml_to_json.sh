#!bin/sh
# Script à lancer depuis le répertoire bash. 
oxygen="Saxon-HE-9.8.0-14.jar"

# Nettoyage et tokénisation du corpus parallélisé.
# Ne fonctionne pas. Il faut Saxon PE pour pouvoir bénéficier des fonctions étendues comme exslt:random()
# echo "Nettoyage et tokénisation du corpus"
# fichier_origine="../../Dedans/XML/corpus/corpus.xml"
# java -jar "../$oxygen" -o:../temoins/groupe.xml $fichier_origine ../xsl/pre_alignement/tokenisation.xsl


# Scission du corpus en dossiers de chapitres
echo "0 - Scission du corpus, création de dossiers et de fichiers par chapitre"
java -jar ../$oxygen -o:../tmp/tmp.tmp ../temoins/groupe.xml ../xsl/pre_alignement/scission_chapitres.xsl


# Création des fichiers d'apparat
echo "I - alignement automatique"
cd ..
for i in {2..23}; do 


chemin=$(dirname "chapitres/chapitre${i}/juxtaposition.xml")
echo "I.1 transformation en json"
java -jar $oxygen -o:$chemin/juxtaposition.json $chemin/juxtaposition.xml xsl/pre_alignement/transformation_json.xsl

echo "I.2 collation du chapitre $chemin"
cd $chemin
echo "python3 ../../python/collation_python.py juxtaposition.json"
python3 ../../python/collation_python.py juxtaposition.json;
echo "Nettoyage du dossier\n\n"
rm juxtaposition.json
rm alignement_collatex.json
cd ../../; 


done



