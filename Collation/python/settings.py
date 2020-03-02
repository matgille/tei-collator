import json
from json_minify import json_minify


def parse_parameters():
    with open("parameters.json", "r") as f:
        settings = json.loads(json_minify(f.read()))
    return settings


settings = parse_parameters()

tokeniser = not settings['corpus']['tokenized']

xmlId = not settings['corpus']['xmlIdentifiers']

if not settings['corpus']['lemmatized'] and settings['lemmatize']:
    lemmatiser = True
else:
    lemmatiser = False

path = settings['structure']
lang = settings['lang']
teiCorpus = settings['tei:teiCorpus']
tableauxAlignement = settings['sortie']['tableaux_alignement']