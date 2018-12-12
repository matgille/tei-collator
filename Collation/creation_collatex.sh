



for fichier in chapitre*/par_*/*.txt; do DIR=$(dirname "${fichier}"), java -jar ~/Bureau/Programme/collatex-tools-1.7.1.jar -a dekker -f dot $fichier -o $DIR/collation.dot; done 


for fichier in chapitre*/par_*/collation.dot, do 
DIR=$(dirname "${fichier}"); dot -Tpdf $fichier -o $DIR/collation.pdf; done 


