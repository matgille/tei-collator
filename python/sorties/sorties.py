import os
from halo import Halo
import re
import glob
import subprocess
from lxml import etree
import xml.etree.ElementTree as ET




def transformation_latex(saxon, fichier_xml, chemin):
    fichier_tex = f"{fichier_xml.split('.')[0]}.tex"
    fichier_tex_seul = fichier_tex.split("/")[-1]
    chemin_xsl_apparat = "xsl/post_alignement/conversion_latex.xsl"
    fichier_tex_sortie = f"-o:{fichier_tex}"
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

