import json
import numpy as np
import torch
import random
from sklearn.decomposition import PCA

import plotly
import numpy as np
import plotly.graph_objs as go


class Embeddings:
    def __init__(self, model, device='cpu'):
        # On a besoin du vocabulaire qui est la base de l'entraînement du plongement de mots
        with open("python/post_traitement/vocab.json", "r") as vocab_json:
            self.vocab = json.load(vocab_json)
        self.model_dict = torch.load(model)
        self.device = device

        # On récupère les embeddings
        self.embeddings = self.model_dict['embeddings.weight'].data
        self.embeddings.to(device)
        self.dimensionality = self.embeddings[0].shape[0]  # on cherche la dimensionalité du plongement de mots
        self.norm_vocab = dict((word, idx) for (word, idx) in self.vocab.items())
        self.rev_vocab = dict((idx, word) for (word, idx) in self.vocab.items())
        self.mean_similarity = None
        self.median_similarity = None
        self.random_mean_similarity()

    def random_mean_similarity(self):
        """
        On crée la moyenne de 100 calculs de similarité entre des vecteurs
        choisis au hasard. Il y a une forte probabilité pour que cette moyenne
        soit basse: en comparaison, une valeur plus importante peut marquer
        une similarité entre deux mots du vocabulaire. À l'inverse,
        une valeur proche ou inférieure à cette moyenne marquerait une dissimilitudes entre
        les deux formes.
        """
        random.seed(2348)
        test_population = [(
            random.randint(0, len(self.vocab) - 1),
            random.randint(0, len(self.vocab) - 1)
        )
            for _ in range(10000)]
        similarities = []

        for a, b in test_population:
            a_as_vector = self.embeddings[a]
            b_as_vector = self.embeddings[b]
            similarities.append(
                self.cosine_similarity(a_as_vector, b_as_vector).item()
            )
        print(similarities)
        self.mean_similarity = np.mean(similarities)
        self.median_similarity = np.median(similarities)

    def dot_product(self, a, b):
        a = a.to(self.device)
        b = b.to(self.device)
        return torch.dot(a, b)

    def cosine_similarity(self, a, b):
        """
        La similarité cosine se calcule par le produit des vecteurs divisé par le produit
        De la norme des vecteurs
        """
        a = a.to(self.device)
        b = b.to(self.device)
        # https://pytorch.org/docs/stable/generated/torch.norm.html
        return torch.dot(a, b) / (torch.linalg.norm(a) * torch.linalg.norm(b))

    def compute_similarity(self, cosine_similarity: bool, pair: tuple):
        """
        on calcule l'angle entre les deux vecteurs, ce qui donne une idée de leur proximité sémantique.
        La similarité est proportionnelle à l'angle:
        https://developers.google.com/machine-learning/clustering/similarity/measuring-similarity
        :cosine_similarity: calcule-t-on une similarité cosine (True) ou un produit vectoriel (False) ?
        """
        a, b = pair

        # On initialise des vecteurs vides si le vocabulaire n'existe pas.
        try:
            a_as_vector = self.embeddings[self.norm_vocab[a]]
        except:
            a_as_vector = torch.zeros(self.dimensionality).to(self.device)
        try:
            b_as_vector = self.embeddings[self.norm_vocab[b]]
        except:
            b_as_vector = torch.zeros(self.dimensionality).to(self.device)

        if cosine_similarity:
            cosine_metric = self.cosine_similarity(a_as_vector, b_as_vector)
        else:
            cosine_metric = self.dot_product(a_as_vector, b_as_vector)

        # We compare to two random words
        test_word_a_index = random.randint(0, len(self.vocab) - 1)
        test_word_b_index = random.randint(0, len(self.vocab) - 1)
        test_word_a = self.rev_vocab[test_word_a_index]
        test_word_b = self.rev_vocab[test_word_b_index]
        test_a_as_vector = self.embeddings[test_word_a_index]
        test_b_as_vector = self.embeddings[test_word_b_index]
        test_cosine_metric = self.cosine_similarity(test_a_as_vector, test_b_as_vector)

        return cosine_metric, test_cosine_metric, (test_word_a, test_word_b)

    def visualize_embeddings(self):
        """
        https://towardsdatascience.com/visualizing-word-embedding-with-pca-and-t-sne-961a692509f5
        Cette fonction permet de visualiser les plongements de mots
        après analyse des composants principaux (PCA) qui permet de diminuer la
        dimensionalité des vecteurs à 2.
        :dimension: la dimension de visualisation (2D ou 3D)
        """
        reduced_dimensionality = PCA(random_state=0).fit_transform(self.embeddings)[:, :2]
        reversed_vocab = [key for key, _ in self.vocab.items()]

        data = []
        trace = go.Scatter(
            x=reduced_dimensionality[:len(reversed_vocab) - 1, 0],
            y=reduced_dimensionality[:len(reversed_vocab) - 1, 1],
            text=reversed_vocab[:len(reversed_vocab) - 1],
            name="My plot",
            textposition="top center",
            textfont_size=20,
            mode='markers+text',
            marker={
                'size': 10,
                'opacity': 0.8,
                'color': 2
            }

        )
        data.append(trace)




        # Configure the layout

        layout = go.Layout(
            margin={'l': 0, 'r': 0, 'b': 0, 't': 0},
            showlegend=True,
            legend=dict(
                x=1,
                y=0.5,
                font=dict(
                    family="Courier New",
                    size=25,
                    color="black"
                )),
            font=dict(
                family=" Courier New ",
                size=15),
            autosize=False,
            width=1000,
            height=1000
        )

        plot_figure = go.Figure(data=data, layout=layout)
        plot_figure.show()
