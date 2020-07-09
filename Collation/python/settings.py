import json
from json_minify import json_minify


def parse_parameters():
    with open("parameters.json", "r") as f:
        return json.loads(json_minify(f.read()))


settings = parse_parameters()

tokeniser = not settings['corpus']['tokenized']

xmlId = not settings['corpus']['xmlIdentifiers']

if not settings['corpus']['lemmatized'] and settings['lemmatize'] is True:
    lemmatiser = True
else:
    lemmatiser = False

temoin_leader = settings['fichier_leader'].split(".")[0]
element_base = settings['scission']['element_base']
scinder_par = settings['scission']['scinder_par']

alignement = settings['alignement']
path = settings['structure']
lang = settings['lang']
teiCorpus = settings['tei:teiCorpus']
tableauxAlignement = settings['sortie']['tableaux_alignement']
latex = settings['sortie']['LaTeX']
