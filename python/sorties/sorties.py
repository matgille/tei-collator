import os
from halo import Halo
import re
import subprocess




def transformation_latex(saxon, fichier_xml, chemin):
    fichier_tex = "%s.tex" % fichier_xml.split('.')[0]
    fichier_tex_seul = fichier_tex.split("/")[-1]
    chemin_xsl_apparat = "xsl/post_alignement/conversion_latex.xsl"
    fichier_tex_sortie = "-o:%s" % fichier_tex
    print("Création des fichiers pdf ✓")
    subprocess.run(["java", "-jar", saxon, fichier_tex_sortie, fichier_xml, chemin_xsl_apparat])
    os.chdir(chemin)
    subprocess.run(["xelatex", fichier_tex_seul])
    subprocess.run(["xelatex", fichier_tex_seul])
    os.chdir("../..")


def concatenation_pdf():
    with Halo(text='Création d\'un fichier unique d\'apparat ✓', spinner='dots'):
        subprocess.run(["pdftk", "divs/div*/*.pdf", "output", "III_3_apparat.pdf"])
    print("Création d'un fichier unique d'apparat ✓")

# def fusion_divs(): # on recrée ici le xml complet
#     for fichier_entree in os.listdir("temoins_tokenises/"):
#         with open("resultat/%s" % fichier_entree, 'w') as fichier_sortie:
#             for div in os.listdir("divs/"):
#                 for file in os.listdir("divs/%s" % div):
#                     nom_fichier = fichier_entree.split(".")[0]
#                     pattern = re.compile("^apparat.*%s.out\.xml$" % nom_fichier)
#                     if pattern.match(file):
#                         with open("divs/%s/%s" % (div, file), 'r') as division:
#                             # on parse avec lxml, on copie dans une variable, et on remplace